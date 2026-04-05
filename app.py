import torch
from torch import nn
from torchvision import transforms
from PIL import Image
import gradio as gr
import os
import torch.nn.functional as F
import numpy as np
import cv2
import matplotlib.pyplot as plt

# 设置 Matplotlib 字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ------------------------------ 病害名称中英文映射 ------------------------------ #
DISEASE_NAMES_CN = {
    # 苹果
    "Apple___Apple_scab": "苹果疮痂病",
    "Apple___Black_rot": "苹果黑腐病",
    "Apple___Cedar_apple_rust": "苹果雪松锈病",
    "Apple___healthy": "苹果健康",

    # 蓝莓
    "Blueberry___healthy": "蓝莓健康",

    # 樱桃
    "Cherry_(including_sour)___Powdery_mildew": "樱桃白粉病",
    "Cherry_(including_sour)___healthy": "樱桃健康",

    # 玉米
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "玉米灰斑病",
    "Corn_(maize)___Common_rust_": "玉米普通锈病",
    "Corn_(maize)___Northern_Leaf_Blight": "玉米大斑病",
    "Corn_(maize)___healthy": "玉米健康",

    # 葡萄
    "Grape___Black_rot": "葡萄黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄黑麻疹病",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶枯病",
    "Grape___healthy": "葡萄健康",

    # 柑橘
    "Orange___Haunglongbing_(Citrus_greening)": "柑橘黄龙病",

    # 桃子
    "Peach___Bacterial_spot": "桃细菌性斑点病",
    "Peach___healthy": "桃健康",

    # 甜椒
    "Pepper,_bell___Bacterial_spot": "甜椒细菌性斑点病",
    "Pepper,_bell___healthy": "甜椒健康",

    # 马铃薯
    "Potato___Early_blight": "马铃薯早疫病",
    "Potato___Late_blight": "马铃薯晚疫病",
    "Potato___healthy": "马铃薯健康",

    # 树莓
    "Raspberry___healthy": "树莓健康",

    # 大豆
    "Soybean___healthy": "大豆健康",

    # 南瓜
    "Squash___Powdery_mildew": "南瓜白粉病",

    # 草莓
    "Strawberry___Leaf_scorch": "草莓叶焦病",
    "Strawberry___healthy": "草莓健康",

    # 番茄
    "Tomato___Bacterial_spot": "番茄细菌性斑点病",
    "Tomato___Early_blight": "番茄早疫病",
    "Tomato___Late_blight": "番茄晚疫病",
    "Tomato___Leaf_Mold": "番茄叶霉病",
    "Tomato___Septoria_leaf_spot": "番茄叶斑病",
    "Tomato___Spider_mites Two-spotted_spider_mite": "番茄蜘蛛螨",
    "Tomato___Target_Spot": "番茄靶斑病",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "番茄黄化曲叶病毒病",
    "Tomato___Tomato_mosaic_virus": "番茄花叶病毒病",
    "Tomato___healthy": "番茄健康",
}

# 置信度阈值（低于此值视为无法识别）
CONFIDENCE_THRESHOLD = 0.70


def get_chinese_name(english_name):
    """将英文类别名称转换为中文"""
    return DISEASE_NAMES_CN.get(english_name, english_name.replace('_', ' '))


# ------------------------------ 自定义模型 ------------------------------ #
class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=stride, padding=1,
                                   groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        return F.relu(self.bn(self.pointwise(self.depthwise(x))))


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.shortcut = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1),
            nn.BatchNorm2d(out_channels)
        ) if in_channels != out_channels else nn.Identity()

    def forward(self, x):
        residual = self.shortcut(x)
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return F.relu(out)


class PlantDiseaseCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            DepthwiseSeparableConv(32, 64),
            nn.MaxPool2d(2),
            ResidualBlock(64, 64),
            DepthwiseSeparableConv(64, 128),
            nn.MaxPool2d(2),
            DepthwiseSeparableConv(128, 256),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.LayerNorm(256),
            nn.Linear(256, num_classes)
        )
        self.gradients = None
        self.activations = None

    def save_gradient(self, grad):
        self.gradients = grad

    def forward(self, x):
        for i, module in enumerate(self.features):
            x = module(x)
            if i == len(self.features) - 2:
                self.activations = x
                if self.activations.requires_grad:
                    self.activations.register_hook(self.save_gradient)
        x = self.classifier(x)
        return x

    def get_activations(self):
        return self.activations

    def get_gradients(self):
        return self.gradients


# ------------------------------ 加载模型 ------------------------------ #
dataset_path = "datasets/raw/color"
CLASS_NAMES = [
    name for name in os.listdir(dataset_path)
    if os.path.isdir(os.path.join(dataset_path, name))
]
CLASS_NAMES.sort()
print(f"类别列表 (共 {len(CLASS_NAMES)} 类)")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")

model = PlantDiseaseCNN(num_classes=len(CLASS_NAMES)).to(device)
model.load_state_dict(torch.load("best_model.pth", map_location=device))
model.eval()

# ------------------------------ 预处理 ------------------------------ #
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


# ------------------------------ Grad-CAM ------------------------------ #
def generate_gradcam(image_tensor, target_class=None):
    model.train()
    model.gradients = None
    model.activations = None

    image_tensor = image_tensor.requires_grad_(True)
    output = model(image_tensor)

    if target_class is None:
        target_class = torch.argmax(output, dim=1).item()

    model.zero_grad()
    output[0, target_class].backward()

    gradients = model.get_gradients()
    activations = model.get_activations()
    model.eval()

    if gradients is None or activations is None:
        return None

    gradients = gradients.detach().cpu()
    activations = activations.detach().cpu()

    weights = torch.mean(gradients[0], dim=(1, 2))
    cam = torch.zeros(activations[0].shape[1:], dtype=torch.float32)
    for i, w in enumerate(weights):
        cam += w * activations[0, i, :, :]

    cam = F.relu(cam)
    if cam.max() > 0:
        cam = cam / cam.max()

    cam = cam.numpy()
    cam = cv2.resize(cam, (224, 224))
    return cam


def overlay_heatmap(img_array, cam, alpha=0.5):
    heatmap = cv2.applyColorMap(np.uint8(cam * 255), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    if img_array.dtype != np.uint8:
        img_array = np.uint8(img_array)
    overlay = cv2.addWeighted(img_array, 1 - alpha, heatmap, alpha, 0)
    return overlay


# ------------------------------ 预测函数（含置信度阈值） ------------------------------ #
def predict_with_heatmap(image):
    try:
        # 转换图片
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        else:
            img = Image.fromarray(image.astype('uint8'), 'RGB')

        original_img = img.resize((224, 224))
        img_array = np.array(original_img)

        img_tensor = transform(img).unsqueeze(0).to(device)

        # 预测
        model.eval()
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = F.softmax(outputs, dim=1)
            confidence, pred_class = torch.max(probs, 1)

        # 获取中英文名称
        english_name = CLASS_NAMES[pred_class.item()]
        chinese_name = get_chinese_name(english_name)
        confidence_value = confidence.item()

        # ========== 置信度阈值判断 ==========
        if confidence_value < CONFIDENCE_THRESHOLD:
            result_text = f"⚠️ 无法准确识别\n\n📊 最接近的匹配：{chinese_name}\n📊 置信度：{confidence_value:.2%}\n\n💡 建议：\n• 请确保图片为清晰的作物叶片\n• 请确保叶片占图片主要部分\n• 避免背景杂乱或非叶片物体"
            return result_text, None

        # ========== 置信度足够，生成热力图 ==========
        cam = generate_gradcam(img_tensor, target_class=pred_class.item())

        if cam is not None:
            overlay_img = overlay_heatmap(img_array, cam, alpha=0.5)

            # 使用 Matplotlib 创建对比图
            fig, axes = plt.subplots(1, 2, figsize=(10, 5))

            axes[0].imshow(img_array)
            axes[0].set_title("原始图片", fontsize=12)
            axes[0].axis('off')

            axes[1].imshow(overlay_img)
            axes[1].set_title(f"Grad-CAM 热力图\n预测: {chinese_name}\n置信度: {confidence_value:.1%}", fontsize=10)
            axes[1].axis('off')

            plt.tight_layout()

            # 保存图片
            import io
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            heatmap_img = Image.open(buf)
            plt.close()

            # 诊断结果用中文显示
            result_text = f"🌿 诊断结果：{chinese_name}\n📊 置信度：{confidence_value:.2%}"
            return result_text, heatmap_img
        else:
            return f"🌿 诊断结果：{chinese_name}\n📊 置信度：{confidence_value:.2%}\n⚠️ 热力图生成失败", None

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ 错误：{e}", None


# ------------------------------ Gradio 界面 ------------------------------ #
with gr.Blocks(title="植物病害智能诊断系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
        <div style="text-align: center">
            <h1>🌱 植物病害智能诊断系统</h1>
            <h3>上传植物叶片图片，自动识别病害类型</h3>
            <p>🔥 支持 Grad-CAM 热力图可视化，展示模型关注区域</p>
        </div>
    """)

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 上传叶片图片", type="numpy", height=300)
            with gr.Row():
                submit_btn = gr.Button("🔍 开始诊断", variant="primary")
                clear_btn = gr.Button("🗑️ 清空", variant="secondary")
        with gr.Column():
            output_text = gr.Textbox(label="📋 诊断结果", lines=5)
            output_heatmap = gr.Image(label="🔥 Grad-CAM 热力图对比", type="pil", height=350)

    submit_btn.click(fn=predict_with_heatmap, inputs=image_input, outputs=[output_text, output_heatmap])
    clear_btn.click(lambda: [None, "", None], outputs=[image_input, output_text, output_heatmap])

    gr.Markdown("""
    ---
    ### 📖 使用说明
    1. 上传清晰的植物叶片图片
    2. 点击「开始诊断」按钮
    3. 系统会显示病害名称和置信度
    4. 右侧热力图红色区域表示模型关注的部位

    ### ⚠️ 温馨提示
    - 请上传**清晰的叶片**图片，避免背景杂乱
    - 置信度低于 70% 时，系统会提示无法识别
    - 本系统仅供辅助参考，建议咨询专业农技人员
    """)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861)
import torch
from torch import nn
from torchvision import transforms, datasets
from PIL import Image
import gradio as gr
import os
import torch.nn.functional as F

#------------------------------自定义模型----------------------##
class PlantDiseaseCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), # 输入通道3（RGB）
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 输出: [32, 112, 112]

            DepthwiseSeparableConv(32,64),##深度可分离卷积
            # ECAAttention(64),  # 第一个注意力层
            nn.MaxPool2d(2),  # 输出: [64, 56, 56]

            ResidualBlock(64, 64),

            DepthwiseSeparableConv(64,128),##深度可分离卷积
            # ECAAttention(128),  # 第二个注意力层
            nn.MaxPool2d(2),# [128, 28, 28]

            DepthwiseSeparableConv(128,256),##深度可分离卷积
            # ECAAttention(256),  # 第三个注意力层
            nn.MaxPool2d(2),# [256, 14, 14]
        )

        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),  # [B,256,1,1]
            nn.Flatten(),
            nn.LayerNorm(256),  # 新增归一化
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

##深度可分离卷积
class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        ##深度卷积，未跨通道提取特征
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size=3,stride=stride, padding=1, groups=in_channels, bias=False)
        ##逐点卷积
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)##标准化

    def forward(self, x):
        return F.relu(self.bn(self.pointwise(self.depthwise(x))))##relu激活函数

##ECA注意力机制
class ECAAttention(nn.Module):
    """Efficient Channel Attention"""
    def __init__(self, channels, gamma=2, b=1):
        super().__init__()
        # 自适应卷积核大小，为了对称的领域交互，核大小为奇数
        t = int(abs((torch.log2(torch.tensor(channels)).item() + b) / gamma))
        kernel_size = t if t % 2 else t + 1

        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=kernel_size,padding=kernel_size // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        y = self.avg_pool(x)  # [B,C,1,1]
        y = self.conv(y.squeeze(-1).transpose(-1, -2))  # [B,1,C]
        y = self.sigmoid(y.transpose(-1, -2).unsqueeze(-1))  # [B,C,1,1]
        return x * y.expand_as(x)

# 自定义残差模块
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

##自动获取类别标签
dataset_path = "datasets/raw/color"
# 获取所有子文件夹名称
CLASS_NAMES = [
    name for name in os.listdir(dataset_path)
    if os.path.isdir(os.path.join(dataset_path, name))
]
# 按字母顺序排序（和 ImageFolder 默认行为一致）
CLASS_NAMES.sort()
print("类别列表:", CLASS_NAMES)

##加载模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# 初始化模型并加载权重
model = PlantDiseaseCNN(num_classes=len(CLASS_NAMES)).to(device)
model.load_state_dict(torch.load("best_model.pth", map_location=device))
model.eval()

##预处理
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


## 预测函数
def predict(image):
    """处理上传的图片并返回预测类别（字符串）"""
    try:
        # 转换图片格式
        if isinstance(image, str):  # 如果是文件路径
            img = Image.open(image).convert('RGB')
        else:  # 如果是Gradio上传的图片对象
            img = Image.fromarray(image.astype('uint8'), 'RGB')

        # 预处理
        img_tensor = transform(img).unsqueeze(0).to(device)

        # 预测
        with torch.no_grad():
            outputs = model(img_tensor)
            _, pred_class = torch.max(outputs, 1)  # 直接取最大类别索引

        # 返回类别名称（字符串）
        return CLASS_NAMES[pred_class.item()]
    except Exception as e:
        return f"Error: {e}"


## 创建交互界面
with gr.Blocks(title="植物病害智能诊断系统", theme=gr.themes.Soft()) as interface:
    # 标题和描述
    gr.Markdown("""
        <div style="text-align: center">
            <h1>🌱植物病害智能诊断系统</h1>
            <h3>上传植物叶片图片，自动识别病害类型</h3>
        </div>
        """)

    with gr.Row():
        with gr.Column(scale=1):
            # 图片上传区域
            image_input = gr.Image(
                label="上传叶片图片",
                type="numpy",
                height=300,
                sources=["upload", "clipboard"],
                interactive=True
            )

        with gr.Column(scale=1):
            # 结果显示区域
            output_text = gr.Textbox(
                label="诊断结果",
                placeholder="等待分析...",
                interactive=False
            )
            with gr.Row():
                submit_btn = gr.Button("开始诊断", variant="primary")
                clear_btn = gr.Button("清空")

    # 按钮事件绑定
    submit_btn.click(
        fn=predict,
        inputs=image_input,
        outputs=output_text
    )
    clear_btn.click(
        lambda: [None, ""],
        outputs=[image_input, output_text]
    )

## 主函数
if __name__ == "__main__":
    interface.launch(
        server_name="127.0.0.1",
        server_port=7861,  # 更换端口
        share=False,  # 不分享到公网
        debug=True,  # 开启调试模式
        show_error=True  # 显示详细错误信息
    )
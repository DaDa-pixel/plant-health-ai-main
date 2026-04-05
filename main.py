import os
import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import StratifiedShuffleSplit
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import torch.nn as nn
import random
from PIL import Image
import cv2
import time

##------------------------数据预处理----------------------------##
# 设置数据集路径
dataset_path = os.path.join("datasets/raw/color")

##模拟叶片遮挡
class RandomLeafOcclusion(object):
    def __init__(self, max_occlusions=3, occlusion_size=(0.1, 0.6)):##遮挡区域个数3，遮挡区域大小占原图范围0.1-0.3
        self.max_occlusions = max_occlusions
        self.occlusion_size = occlusion_size

    def __call__(self, img):
        # 转换PIL图像为NumPy数组
        img_np = np.array(img)
        h, w = img_np.shape[:2]
        for _ in range(random.randint(1, self.max_occlusions)):
            # 随机生成遮挡区域大小
            occ_w = int(w * random.uniform(*self.occlusion_size))
            occ_h = int(h * random.uniform(*self.occlusion_size))
            x = random.randint(0, w - occ_w)
            y = random.randint(0, h - occ_h)
            # 生成半透明绿色遮挡（模拟叶片）
            occlusion = np.zeros((occ_h, occ_w, 3), dtype=np.uint8)
            occlusion[:, :, 1] = random.randint(100, 200)  # G通道（绿色）
            occlusion[:, :, 0] = random.randint(0, 50)  # R通道
            occlusion[:, :, 2] = random.randint(0, 30)  # B通道
            # 添加模糊效果使边缘自然
            occlusion = cv2.GaussianBlur(occlusion, (5, 5), 0)
            # 混合遮挡（alpha blending）
            img_np[y:y + occ_h, x:x + occ_w] = cv2.addWeighted(
                img_np[y:y + occ_h, x:x + occ_w], 0.3,occlusion, 0.7, 0 )##原图保留30%，遮挡占70%
        return Image.fromarray(img_np)

##模拟光照
class RandomLighting(object):
    def __init__(self, light_std=0.2, highlight_prob=0.3):
        self.light_std = light_std                  ##全局光照强度变化的标准差
        self.highlight_prob = highlight_prob        ##模拟高光的概率
    def __call__(self, img):                        ##_call_这个函数名字调用类的时候可以直接用
        if random.random() < self.highlight_prob:
            # 模拟点光源（图片过曝）
            img = transforms.functional.adjust_brightness(img,random.uniform(1.2, 1.8))##图片增强倍数在1.2-1.8之间随机值
        else:
            # 全局光照变化
            img = transforms.functional.adjust_brightness(img,random.uniform(1 - self.light_std, 1 + self.light_std))##普通光照
        return img

data_transforms = {
    'train': transforms.Compose([
        transforms.Resize(256),##调整大小
        transforms.RandomRotation(45),##随机+—45度旋转
        transforms.RandomHorizontalFlip(p=0.5),##一般概率水平翻转
        transforms.RandomVerticalFlip(p=0.5),##一般概率垂直翻转
        transforms.ColorJitter( contrast=0.2, saturation=0.2),##对比度，饱和度
        RandomLighting(light_std=0.2),  # 光照模拟
        RandomLeafOcclusion(max_occlusions=2),  # 叶片遮挡
        transforms.CenterCrop(224),##裁剪中间部分
        transforms.ToTensor(),##转成tensor格式
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])##标准化：均值方差
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'test': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
}


# 加载原始数据集
full_dataset = datasets.ImageFolder(root=dataset_path)

# 获取所有标签
labels = [s[1] for s in full_dataset.samples]

##分层抽样保证训练集、验证集、测试集中每种类别的比例一致
# 第一次划分：划分一次，70%训练集，30%临时集
sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)##划分次数、比例、随机种子
train_idx, temp_idx = next(sss1.split(np.zeros(len(labels)), labels))
# 第二次划分：划分一次，从临时集分出val和test
temp_labels = [labels[i] for i in temp_idx]  # 获取临时集标签
sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
temp_test_idx, temp_val_idx = next(sss2.split(np.zeros(len(temp_labels)), temp_labels))

# 转换为原始数据集中的绝对索引
val_idx = temp_idx[temp_val_idx]
test_idx = temp_idx[temp_test_idx]

# 自定义Subset类实现动态transform
class TransformSubset(Dataset):##为了按索引提取数据
    def __init__(self, full_dataset, indices, transform=None):
        self.full_dataset = full_dataset
        self.indices = indices
        self.transform = transform
        self.classes = full_dataset.classes
        self.class_to_idx = full_dataset.class_to_idx

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        image, label = self.full_dataset[self.indices[idx]]  # 从完整数据集获取原始数据
        if self.transform:
            image = self.transform(image)  # 应用指定transform
        return image, label

# 创建数据集对象（预处理后的数据）
train_datasets = TransformSubset(full_dataset, train_idx, data_transforms['train'])
val_datasets = TransformSubset(full_dataset, val_idx, data_transforms['val'])
test_datasets = TransformSubset(full_dataset, test_idx, data_transforms['test'])


# 创建DataLoader字典
batch_size = 32
dataloaders = {
    'train': DataLoader(train_datasets, batch_size=32, shuffle=True, num_workers=0),##只对训练集混洗，打乱顺序
    'val': DataLoader(val_datasets, batch_size=32, num_workers=0),
    'test': DataLoader(test_datasets, batch_size=32, num_workers=0)
}

# 验证数据集划分
print(f"总样本数: {len(full_dataset)}")
print(f"训练集: {len(train_datasets)} ({len(train_idx)/len(full_dataset):.1%})")
print(f"验证集: {len(val_datasets)} ({len(val_idx)/len(full_dataset):.1%})")
print(f"测试集: {len(test_datasets)} ({len(test_idx)/len(full_dataset):.1%})")
print(f"类别数: {len(full_dataset.classes)}")


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
            ECAAttention(64),  # 第一个注意力层
            nn.MaxPool2d(2),  # 输出: [64, 56, 56]

            #ResidualBlock(64, 64),

            DepthwiseSeparableConv(64,128),##深度可分离卷积
            ECAAttention(128),  # 第二个注意力层
            nn.MaxPool2d(2),# [128, 28, 28]

            DepthwiseSeparableConv(128,256),##深度可分离卷积
            ECAAttention(256),  # 第三个注意力层
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

##------------------------------训练模型-------------------------------##
def train_model(epochs=20):
    best_acc = 0.0
    total_train_time = 0  #记录总训练时间
    scaler = torch.amp.GradScaler('cuda')  #产生一个梯度缩放器（防止梯度下溢）

    for epoch in range(epochs):
        epoch_start = time.time()  #记录epoch开始时间
        # 训练阶段
        model.train()
        train_loss = 0.0
        train_correct = 0  # 新增：累计正确预测数
        train_total = 0  # 累计总样本数
        for inputs, labels in dataloaders['train']:
            inputs, labels = inputs.to(device), labels.to(device)##将数据导入GPU
            optimizer.zero_grad()##梯度清零，防止累积
            with torch.amp.autocast('cuda'): # 前向传播：autocast自动选择FP16/FP32
                outputs = model(inputs)  # 部分层自动转为FP16
                loss = criterion(outputs, labels)  # 损失计算可能保持FP32
            # 反向传播：梯度缩放防止下溢
            scaler.scale(loss).backward()  # 缩放损失梯度（FP16）
            scaler.step(optimizer)  # 缩放梯度并更新（自动转FP32）
            scaler.update()  # 调整缩放因子

            train_loss += loss.item()
            _, preds = torch.max(outputs, 1)  # 获取预测类别
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)

        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_acc = 0.0
        with torch.no_grad():
            for inputs, labels in dataloaders['val']:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_acc += (preds == labels).sum().item()

        # 时间统计
        epoch_time = time.time() - epoch_start #epoch总耗时
        total_train_time += epoch_time #累计训练时间
        # 记录指标
        epoch_train_loss = train_loss / len(dataloaders['train'])
        epoch_train_acc = train_correct / train_total
        epoch_val_loss = val_loss / len(dataloaders['val'])
        epoch_val_acc = val_acc / len(val_datasets)

        scheduler.step(epoch_val_acc)

        history['train_loss'].append(epoch_train_loss) #训练损失
        history['train_acc'].append(epoch_train_acc)  # 训练准确率
        history['val_loss'].append(epoch_val_loss)  ##验证损失
        history['val_acc'].append(epoch_val_acc)    ##验证准确率

        print(f"Epoch {epoch + 1}/{epochs}")
        print(f"Train Loss: {epoch_train_loss:.4f} | Val Loss: {epoch_val_loss:.4f} |train_Acc:{epoch_train_acc:.4f}| Val Acc: {epoch_val_acc:.4f}|epoch_time:{epoch_time:.4f} ")

        # 保存最佳模型
        if epoch_val_acc > best_acc:
            best_acc = epoch_val_acc
            torch.save(model.state_dict(), "./best_model.pth")
            print(f"已保存 Best Acc: {best_acc:.4f}")

    print(f"total_train_time: {total_train_time:.4f}")

##----------------------------------可视化------------------------------##
# 记录训练过程的指标
history = {
    'train_loss': [],
    'train_acc': [],
    'val_loss': [],
    'val_acc': []
}
##可视化函数
def plot_training_history(history):
    plt.figure(figsize=(12, 5))

    # 损失曲线
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    # 准确率曲线
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Accuracy')
    plt.plot(history['val_acc'], label='Validation Accuracy')
    plt.title('Accuracy Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_confusion_matrix(true_labels, pred_labels, class_names):
    cm = confusion_matrix(true_labels, pred_labels)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.show()
##------------------------------------主函数部分-------------------------------##
if __name__ == '__main__':
    # 初始化模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PlantDiseaseCNN(num_classes=len(full_dataset.classes)).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n模型参数量统计:")
    print(f"总参数: {total_params / 1e6:.2f}M")
    print(f"可训练参数: {trainable_params / 1e6:.2f}M")

    # 训练配置
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=2)

    # 开始训练
    train_model(epochs=10)

    # 绘制训练曲线
    plot_training_history(history)

    # 测试评估与可视化
    model.load_state_dict(
        torch.load("./best_model.pth", map_location=device, weights_only=True)
    )
    model.eval()

    all_preds = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in dataloaders['test']:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # 计算并输出测试集准确率
    test_accuracy = np.mean(np.array(all_preds) == np.array(all_labels))
    print(f"\nTest Accuracy: {test_accuracy:.4%}")
    # 分类报告
    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=full_dataset.classes))

    # 混淆矩阵
    plot_confusion_matrix(all_labels, all_preds, full_dataset.classes)


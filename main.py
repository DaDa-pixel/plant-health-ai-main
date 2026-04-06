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
from tqdm import tqdm  # 添加进度条库

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

##------------------------数据预处理----------------------------##
# 设置数据集路径
dataset_path = os.path.join("datasets", "raw", "color")


##模拟叶片遮挡（修复版）
class RandomLeafOcclusion(object):
    def __init__(self, max_occlusions=3, occlusion_size=(0.1, 0.6)):
        self.max_occlusions = max_occlusions
        self.occlusion_size = occlusion_size

    def __call__(self, img):
        try:
            img_np = np.array(img)
            h, w = img_np.shape[:2]

            # 图片太小就不做遮挡了
            if h < 50 or w < 50:
                return img

            for _ in range(random.randint(1, self.max_occlusions)):
                # 计算遮挡区域大小
                occ_w = int(w * random.uniform(*self.occlusion_size))
                occ_h = int(h * random.uniform(*self.occlusion_size))

                # 确保遮挡区域至少 5x5
                if occ_w < 5 or occ_h < 5:
                    continue

                # 确保坐标有效
                if w - occ_w <= 0 or h - occ_h <= 0:
                    continue

                x = random.randint(0, w - occ_w)
                y = random.randint(0, h - occ_h)

                # 生成半透明绿色遮挡
                occlusion = np.zeros((occ_h, occ_w, 3), dtype=np.uint8)
                occlusion[:, :, 1] = random.randint(100, 200)  # G通道（绿色）
                occlusion[:, :, 0] = random.randint(0, 50)  # R通道
                occlusion[:, :, 2] = random.randint(0, 30)  # B通道

                # 添加模糊效果（确保数组不为空）
                if occlusion.size > 0:
                    occlusion = cv2.GaussianBlur(occlusion, (5, 5), 0)
                    img_np[y:y + occ_h, x:x + occ_w] = cv2.addWeighted(
                        img_np[y:y + occ_h, x:x + occ_w], 0.3, occlusion, 0.7, 0
                    )

            return Image.fromarray(img_np)
        except Exception as e:
            # 出错就返回原图
            return img


##模拟光照（保持不变）
class RandomLighting(object):
    def __init__(self, light_std=0.2, highlight_prob=0.3):
        self.light_std = light_std
        self.highlight_prob = highlight_prob

    def __call__(self, img):
        if random.random() < self.highlight_prob:
            img = transforms.functional.adjust_brightness(img, random.uniform(1.2, 1.8))
        else:
            img = transforms.functional.adjust_brightness(img, random.uniform(1 - self.light_std, 1 + self.light_std))
        return img


data_transforms = {
    'train': transforms.Compose([
        transforms.Resize(256),
        transforms.RandomRotation(45),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.ColorJitter(contrast=0.2, saturation=0.2),
        RandomLighting(light_std=0.2),
        RandomLeafOcclusion(max_occlusions=2),  # 现在是安全的
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
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
print("正在加载数据集...")
full_dataset = datasets.ImageFolder(root=dataset_path)
print(f"数据集加载完成，共 {len(full_dataset)} 张图片")

# 获取所有标签
labels = [s[1] for s in full_dataset.samples]

##分层抽样
print("正在划分数据集...")
sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, temp_idx = next(sss1.split(np.zeros(len(labels)), labels))

temp_labels = [labels[i] for i in temp_idx]
sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
temp_test_idx, temp_val_idx = next(sss2.split(np.zeros(len(temp_labels)), temp_labels))

val_idx = temp_idx[temp_val_idx]
test_idx = temp_idx[temp_test_idx]


# 自定义Subset类实现动态transform
class TransformSubset(Dataset):
    def __init__(self, full_dataset, indices, transform=None):
        self.full_dataset = full_dataset
        self.indices = indices
        self.transform = transform
        self.classes = full_dataset.classes
        self.class_to_idx = full_dataset.class_to_idx

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        image, label = self.full_dataset[self.indices[idx]]
        if self.transform:
            image = self.transform(image)
        return image, label


# 创建数据集对象
print("正在应用数据增强...")
train_datasets = TransformSubset(full_dataset, train_idx, data_transforms['train'])
val_datasets = TransformSubset(full_dataset, val_idx, data_transforms['val'])
test_datasets = TransformSubset(full_dataset, test_idx, data_transforms['test'])

# 创建DataLoader
batch_size = 32
dataloaders = {
    'train': DataLoader(train_datasets, batch_size=batch_size, shuffle=True, num_workers=0),
    'val': DataLoader(val_datasets, batch_size=batch_size, num_workers=0),
    'test': DataLoader(test_datasets, batch_size=batch_size, num_workers=0)
}

# 验证数据集划分
print(f"总样本数: {len(full_dataset)}")
print(f"训练集: {len(train_datasets)} ({len(train_idx) / len(full_dataset):.1%})")
print(f"验证集: {len(val_datasets)} ({len(val_idx) / len(full_dataset):.1%})")
print(f"测试集: {len(test_datasets)} ({len(test_idx) / len(full_dataset):.1%})")
print(f"类别数: {len(full_dataset.classes)}")


# ------------------------------自定义模型----------------------##
class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=stride, padding=1,
                                   groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        return F.relu(self.bn(self.pointwise(self.depthwise(x))))


class ECAAttention(nn.Module):
    def __init__(self, channels, gamma=2, b=1):
        super().__init__()
        t = int(abs((torch.log2(torch.tensor(channels)).item() + b) / gamma))
        kernel_size = t if t % 2 else t + 1
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=kernel_size, padding=kernel_size // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        y = self.avg_pool(x)
        y = self.conv(y.squeeze(-1).transpose(-1, -2))
        y = self.sigmoid(y.transpose(-1, -2).unsqueeze(-1))
        return x * y.expand_as(x)


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
            ECAAttention(64),
            nn.MaxPool2d(2),
            DepthwiseSeparableConv(64, 128),
            ECAAttention(128),
            nn.MaxPool2d(2),
            DepthwiseSeparableConv(128, 256),
            ECAAttention(256),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.LayerNorm(256),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


##------------------------------训练模型-------------------------------##
def train_model(epochs=20):
    best_acc = 0.0
    total_train_time = 0
    scaler = torch.amp.GradScaler('cuda')

    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }

    for epoch in range(epochs):
        epoch_start = time.time()

        # 训练阶段（带进度条）
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        # 创建训练进度条
        train_pbar = tqdm(dataloaders['train'], desc=f'Epoch {epoch + 1}/{epochs} [训练]', unit='batch')
        for inputs, labels in train_pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()

            with torch.amp.autocast('cuda'):
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            train_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)

            # 更新进度条显示
            train_pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{train_correct / train_total:.2%}'
            })

        # 验证阶段（带进度条）
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        val_pbar = tqdm(dataloaders['val'], desc=f'Epoch {epoch + 1}/{epochs} [验证]', unit='batch')
        with torch.no_grad():
            for inputs, labels in val_pbar:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

                # 更新进度条显示
                val_pbar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'acc': f'{val_correct / val_total:.2%}'
                })

        epoch_time = time.time() - epoch_start
        total_train_time += epoch_time

        epoch_train_loss = train_loss / len(dataloaders['train'])
        epoch_train_acc = train_correct / train_total
        epoch_val_loss = val_loss / len(dataloaders['val'])
        epoch_val_acc = val_correct / val_total

        scheduler.step(epoch_val_acc)

        history['train_loss'].append(epoch_train_loss)
        history['train_acc'].append(epoch_train_acc)
        history['val_loss'].append(epoch_val_loss)
        history['val_acc'].append(epoch_val_acc)

        # 打印本轮结果
        print(f"\n{'=' * 50}")
        print(f"Epoch {epoch + 1}/{epochs} 完成")
        print(f"  训练损失: {epoch_train_loss:.4f} | 训练准确率: {epoch_train_acc:.2%}")
        print(f"  验证损失: {epoch_val_loss:.4f} | 验证准确率: {epoch_val_acc:.2%}")
        print(f"  耗时: {epoch_time:.1f}秒")
        print(f"{'=' * 50}\n")

        if epoch_val_acc > best_acc:
            best_acc = epoch_val_acc
            torch.save(model.state_dict(), "./best_model.pth")
            print(f"  ✓ 已保存最佳模型 (验证准确率: {best_acc:.2%})\n")

    print(f"总训练时间: {total_train_time:.1f}秒 ({total_train_time / 60:.1f}分钟)")
    return history


##----------------------------------可视化------------------------------##
def plot_training_history(history):
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss', linewidth=2)
    plt.plot(history['val_loss'], label='Val Loss', linewidth=2)
    plt.title('Loss Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Accuracy', linewidth=2)
    plt.plot(history['val_acc'], label='Val Accuracy', linewidth=2)
    plt.title('Accuracy Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('training_history.png', dpi=150)
    plt.show()
    print("训练曲线已保存为 training_history.png")


def plot_confusion_matrix(true_labels, pred_labels, class_names):
    cm = confusion_matrix(true_labels, pred_labels)
    plt.figure(figsize=(16, 14))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                annot_kws={'size': 8})
    plt.title('Confusion Matrix', fontsize=14)
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('True', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=150)
    plt.show()
    print("混淆矩阵已保存为 confusion_matrix.png")


##------------------------------------主函数-------------------------------##
if __name__ == '__main__':
    # 初始化模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n使用设备: {device}")
    if device.type == 'cuda':
        print(f"GPU 名称: {torch.cuda.get_device_name(0)}")
        print(f"显存总量: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")

    model = PlantDiseaseCNN(num_classes=len(full_dataset.classes)).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n模型参数量统计:")
    print(f"  总参数: {total_params / 1e6:.2f}M")
    print(f"  可训练参数: {trainable_params / 1e6:.2f}M")

    # 训练配置
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=2)

    # 开始训练（10个epoch用于评估）
    print("\n" + "=" * 50)
    print("开始训练...")
    print("=" * 50 + "\n")
    history = train_model(epochs=10)

    # 绘制训练曲线
    plot_training_history(history)

    # 测试评估与可视化
    print("\n正在加载最佳模型进行测试...")
    model.load_state_dict(torch.load("./best_model.pth", map_location=device))
    model.eval()

    all_preds = []
    all_labels = []

    print("正在测试集上评估...")
    test_pbar = tqdm(dataloaders['test'], desc='测试进度', unit='batch')
    with torch.no_grad():
        for inputs, labels in test_pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # 计算并输出测试集准确率
    test_accuracy = np.mean(np.array(all_preds) == np.array(all_labels))
    print(f"\n{'=' * 50}")
    print(f"测试集准确率: {test_accuracy:.2%}")
    print(f"{'=' * 50}")

    # 分类报告
    print("\n分类报告:")
    print(classification_report(all_labels, all_preds, target_names=full_dataset.classes))

    # 混淆矩阵
    plot_confusion_matrix(all_labels, all_preds, full_dataset.classes)

    print("\n✅ 训练和评估完成！")
    print("生成的文件:")
    print("  📁 best_model.pth - 最佳模型权重")
    print("  📁 training_history.png - 训练曲线图")
    print("  📁 confusion_matrix.png - 混淆矩阵图")
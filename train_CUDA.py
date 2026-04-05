import torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np


# ------------------------------ 自定义模型 ------------------------------ #
class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=stride, padding=1,
                                   groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        return nn.functional.relu(self.bn(self.pointwise(self.depthwise(x))))


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
        out = nn.functional.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return nn.functional.relu(out)


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

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ------------------------------ 数据集准备 ------------------------------ #
def prepare_dataset(data_path):
    """
    准备 PlantVillage 数据集
    """
    # 训练数据增强
    train_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 验证数据预处理（无增强）
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 加载完整数据集
    full_dataset = datasets.ImageFolder(root=data_path, transform=train_transform)

    # 获取类别名称
    class_names = full_dataset.classes
    num_classes = len(class_names)

    print(f"\n找到 {num_classes} 个类别:")
    for i, name in enumerate(class_names):
        print(f"  {i}: {name}")

    print(f"\n总图片数: {len(full_dataset)}")

    # 划分训练集和验证集 (80% 训练, 20% 验证)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    # 验证集使用不同的 transform
    val_dataset.dataset.transform = val_transform

    return train_dataset, val_dataset, class_names


# ------------------------------ 训练函数 ------------------------------ #
def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs, device,
                save_path="best_model.pth"):
    """
    训练模型
    """
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    best_val_acc = 0.0

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        train_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs} [Train]")
        for images, labels in train_bar:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            train_bar.set_postfix(loss=loss.item(), acc=100 * correct / total)

        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total
        train_losses.append(train_loss)
        train_accs.append(train_acc)

        # 验证阶段
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            val_bar = tqdm(val_loader, desc=f"Epoch {epoch + 1}/{num_epochs} [Val]")
            for images, labels in val_bar:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                val_bar.set_postfix(loss=loss.item(), acc=100 * correct / total)

        val_loss = val_loss / len(val_loader)
        val_acc = 100 * correct / total
        val_losses.append(val_loss)
        val_accs.append(val_acc)

        # 更新学习率
        scheduler.step()

        print(f"\nEpoch {epoch + 1}/{num_epochs}:")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        print(f"  Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")

        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_path)
            print(f"  ✓ 保存最佳模型 (验证准确率: {val_acc:.2f}%)")

    return train_losses, val_losses, train_accs, val_accs


# ------------------------------ 绘制训练曲线 ------------------------------ #
def plot_curves(train_losses, val_losses, train_accs, val_accs):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(train_losses, label='Train Loss', linewidth=2)
    ax1.plot(val_losses, label='Val Loss', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(train_accs, label='Train Accuracy', linewidth=2)
    ax2.plot(val_accs, label='Val Accuracy', linewidth=2)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training and Validation Accuracy')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=150)
    plt.show()
    print("\n训练曲线已保存为 training_curves.png")


# ------------------------------ 保存类别标签 ------------------------------ #
def save_class_names(class_names):
    """保存类别标签到文件，供 app.py 使用"""
    with open('class_names.txt', 'w', encoding='utf-8') as f:
        for name in class_names:
            f.write(name + '\n')
    print(f"类别标签已保存到 class_names.txt，共 {len(class_names)} 个类别")


# ------------------------------ 主函数 ------------------------------ #
def main():
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")

    # 如果使用 GPU，打印显存信息
    if device.type == "cuda":
        print(f"GPU 名称: {torch.cuda.get_device_name(0)}")
        print(f"显存总量: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")

    # 数据集路径（使用相对路径）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "datasets", "raw", "color")

    # 检查路径是否存在
    if not os.path.exists(data_path):
        print(f"\n错误：找不到数据集路径")
        print(f"请确保目录结构为: {data_path}")
        print("并且该文件夹下包含类别子文件夹（如 Apple__Apple_scab 等）")
        return

    print(f"\n数据集路径: {data_path}")

    # 准备数据集
    print("\n正在加载数据集...")
    train_dataset, val_dataset, class_names = prepare_dataset(data_path)

    # 创建数据加载器
    # ⚠️ RTX 3050 Ti 4GB 显存建议用 batch_size=16
    batch_size = 16  # 如果显存不足，改为 8 或 4
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,
                              num_workers=4 if device.type == "cuda" else 0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False,
                            num_workers=4 if device.type == "cuda" else 0)

    print(f"\n训练集大小: {len(train_dataset)}")
    print(f"验证集大小: {len(val_dataset)}")
    print(f"类别数量: {len(class_names)}")
    print(f"Batch Size: {batch_size}")

    # 保存类别标签供 app.py 使用
    save_class_names(class_names)

    # 初始化模型
    model = PlantDiseaseCNN(num_classes=len(class_names)).to(device)

    # 计算模型参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n模型参数量: {total_params:,} (可训练: {trainable_params:,})")

    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    # 训练模型
    num_epochs = 30
    print(f"\n开始训练 {num_epochs} 个轮次...")
    print("-" * 50)

    train_losses, val_losses, train_accs, val_accs = train_model(
        model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs, device
    )

    # 绘制训练曲线
    plot_curves(train_losses, val_losses, train_accs, val_accs)

    print("\n" + "=" * 50)
    print("训练完成！")
    print(f"最佳模型已保存为: best_model.pth")
    print(f"类别标签已保存为: class_names.txt")
    print(f"训练曲线已保存为: training_curves.png")
    print("=" * 50)


if __name__ == "__main__":
    main()
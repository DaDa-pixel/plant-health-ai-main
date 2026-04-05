import os
import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import StratifiedShuffleSplit
import torch
import matplotlib.pyplot as plt
import random
from PIL import Image
import cv2


##------------------------数据预处理----------------------------##
# 设置数据集路径
dataset_path = os.path.join("Image Data base")

class RandomLeafOcclusion(object):
    """模拟真实叶片遮挡"""
    def __init__(self, max_occlusions=3, occlusion_size=(0.1, 0.6)):
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
                img_np[y:y + occ_h, x:x + occ_w], 0.3,  # 原图保留30%
                occlusion, 0.7, 0  # 遮挡层70%
            )
        return Image.fromarray(img_np)

class RandomLighting(object):
    """模拟自然光照变化"""
    def __init__(self, light_std=0.2, highlight_prob=0.3):
        self.light_std = light_std##全局光照强度变化的标准差
        self.highlight_prob = highlight_prob##点源高光的概率
    def __call__(self, img):
        if random.random() < self.highlight_prob:
            # 模拟点光源（高光区域）
            img = transforms.functional.adjust_brightness(img,random.uniform(1.2, 1.8))
        else:
            # 全局光照变化
            img = transforms.functional.adjust_brightness(img,random.uniform(1 - self.light_std, 1 + self.light_std))
        return img

data_transforms = {
    'train': transforms.Compose([
        transforms.Resize(256),##调整大小
        transforms.RandomRotation(45),##随机+—45度旋转
        transforms.RandomHorizontalFlip(p=0.5),##一般概率水平翻转
        transforms.RandomVerticalFlip(p=0.5),##一般概率垂直翻转
        transforms.ColorJitter(contrast=0.2, saturation=0.2),##亮度，对比度，饱和度
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

# 第一次划分：70%训练集，30%临时集
sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, temp_idx = next(sss1.split(np.zeros(len(labels)), labels))

# 第二次划分：从临时集分出val和test
temp_labels = [labels[i] for i in temp_idx]  # 获取临时集标签
sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
temp_test_idx, temp_val_idx = next(sss2.split(np.zeros(len(temp_labels)), temp_labels))

# 转换为原始数据集中的绝对索引
val_idx = temp_idx[temp_val_idx]
test_idx = temp_idx[temp_test_idx]

# 自定义Subset类实现动态transform
# 自定义数据集类（核心修改）
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
        image, label = self.full_dataset[self.indices[idx]]  # 从完整数据集获取原始数据
        if self.transform:
            image = self.transform(image)  # 应用指定transform
        return image, label

# 创建数据集对象
train_datasets = TransformSubset(full_dataset, train_idx, data_transforms['train'])
val_datasets = TransformSubset(full_dataset, val_idx, data_transforms['val'])
test_datasets = TransformSubset(full_dataset, test_idx, data_transforms['test'])


# 创建DataLoader字典
batch_size = 32
dataloaders = {
    'train': DataLoader(train_datasets, batch_size=32, shuffle=True, num_workers=0),  # 关键修改
    'val': DataLoader(val_datasets, batch_size=32, num_workers=0),
    'test': DataLoader(test_datasets, batch_size=32, num_workers=0)
}

# 验证数据集划分
print(f"总样本数: {len(full_dataset)}")
print(f"训练集: {len(train_datasets)} ({len(train_idx)/len(full_dataset):.1%})")
print(f"验证集: {len(val_datasets)} ({len(val_idx)/len(full_dataset):.1%})")
print(f"测试集: {len(test_datasets)} ({len(test_idx)/len(full_dataset):.1%})")
print(f"类别数: {len(full_dataset.classes)}")


def visualize_augmented_samples(dataloader, class_names, n_images=40):
    """
    可视化经过数据增强后的样本图片

    参数:
        dataloader (DataLoader): 训练数据加载器
        class_names (list): 类别名称列表
        n_images (int): 要显示的图片数量(默认20)
    """
    # 获取一个批次的数据
    images, labels = next(iter(dataloader))

    # 计算要显示的行列数
    n_rows = (n_images + 4) // 5  # 每行显示5张
    plt.figure(figsize=(15, 3 * n_rows))

    # 逆归一化函数(将标准化后的Tensor转回可显示的图像)
    def denormalize(tensor):
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        return tensor * std + mean

    for i in range(min(n_images, len(images))):
        # 转换Tensor为NumPy并调整维度顺序
        img = denormalize(images[i]).numpy()
        img = np.transpose(img, (1, 2, 0))  # C×H×W → H×W×C
        img = np.clip(img, 0, 1)  # 限制在[0,1]范围

        # 绘制子图
        plt.subplot(n_rows, 5, i + 1)
        plt.imshow(img)
        plt.title(f"{class_names[labels[i]]}")
        plt.axis('off')

    plt.tight_layout()
    plt.show()


# 使用方法 - 添加到主函数部分
if __name__ == '__main__':
    # ... (原有代码)

    # 在训练开始前添加可视化
    print("\n可视化增强后的训练样本:")
    visualize_augmented_samples(
        dataloaders['train'],
        class_names=full_dataset.classes,
        n_images=40
    )
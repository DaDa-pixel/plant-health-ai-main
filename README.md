# 🌱 植物病害智能诊断系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![Gradio](https://img.shields.io/badge/Gradio-Interface-green.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 基于深度学习的植物病害智能识别系统，支持多种农作物病害的自动诊断和分类

## ✨ 项目亮点

### 🚀 核心技术特色
- **🎯 多类别识别**: 支持 **60+** 种植物病害和健康状态识别
- **🧠 先进模型架构**: 采用深度可分离卷积 + ECA注意力机制 + 残差连接
- **🔬 智能数据增强**: 模拟真实环境的光照变化和叶片遮挡
- **⚡ 高效推理**: 模型轻量化设计，快速响应
- **🎨 友好界面**: 基于Gradio的现代化Web界面

### 🌟 技术优势
- **深度可分离卷积**: 大幅减少参数量，提高训练和推理效率
- **ECA注意力机制**: 自适应通道注意力，提升特征提取能力
- **真实环境模拟**: 创新的数据增强策略，提高模型泛化能力
- **分层抽样**: 确保训练/验证/测试集类别分布均衡

## 📊 支持识别的植物类别

### 🍎 水果类
- **苹果**: 黑腐病、苹果锈病、苹果黑星病、健康状态
- **樱桃**: 白粉病、健康状态
- **葡萄**: 黑腐病、黑麻疹病、叶斑病、健康状态
- **桃子**: 健康状态
- **草莓**: 叶焦病、健康状态
- **蓝莓**: 健康状态
- **树莓**: 健康状态

### 🍅 蔬菜类
- **番茄**: 细菌性斑点病、早疫病、晚疫病、叶霉病、叶斑病、蜘蛛螨、靶斑病、花叶病毒、健康状态
- **辣椒**: 细菌性斑点病、健康状态
- **土豆**: 早疫病、晚疫病、空心病、健康状态
- **玉米**: 叶枯病、普通锈病、灰斑病、健康状态
- **卷心菜**: 菜青虫

### 🍃 茶叶类
- **茶叶**: 藻类叶斑病、炭疽病、鸟眼斑病、褐斑病、红叶斑病、健康状态

### 🌾 粮食作物
- **水稻**: 细菌性叶枯病、褐斑病、叶黑粉病、稻飞虱
- **大豆**: 健康状态

### 🍋 其他作物
- **柑橘**: 黄龙病
- **柠檬**: 溃疡病
- **大蒜**: 健康状态
- **生姜**: 健康状态
- **洋葱**: 健康状态

### 🌿 营养缺乏
- **氮缺乏症**: 植物氮素缺乏
- **钾缺乏症**: 植物钾素缺乏

## 🛠️ 技术架构

### 模型架构
```
PlantDiseaseCNN
├── 特征提取层
│   ├── 标准卷积层 (3→32)
│   ├── 深度可分离卷积 (32→64) + ECA注意力
│   ├── 深度可分离卷积 (64→128) + ECA注意力
│   └── 深度可分离卷积 (128→256) + ECA注意力
└── 分类器
    ├── 全局平均池化
    ├── LayerNorm归一化
    └── 全连接层 (256→类别数)
```

### 核心组件
- **DepthwiseSeparableConv**: 深度可分离卷积，减少参数量
- **ECAAttention**: 高效通道注意力机制
- **ResidualBlock**: 残差连接，缓解梯度消失
- **RandomLighting**: 光照变化模拟
- **RandomLeafOcclusion**: 叶片遮挡模拟

## 📦 安装与使用

### 环境要求
```bash
Python >= 3.8
PyTorch >= 2.0
torchvision
gradio
scikit-learn
matplotlib
seaborn
opencv-python
Pillow
numpy
```

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/LingmaFuture/plant-health-ai.git
cd plant-health-ai
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动Web界面**
```bash
python app.py
```

4. **访问系统**
打开浏览器访问 `http://127.0.0.1:7860`

### 训练模型
```bash
python main.py
```

### 数据增强可视化
```bash
python data_augmentation_demo
```

## 🎯 使用方法

### Web界面操作
1. **上传图片**: 点击上传区域或拖拽图片文件
2. **开始诊断**: 点击"开始诊断"按钮
3. **查看结果**: 系统自动显示识别结果
4. **清空重试**: 点击"清空"按钮重新开始

### 支持的图片格式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## 📈 性能指标

### 模型性能
- **参数量**: ~2.5M (轻量化设计)
- **推理速度**: < 1秒/张图片
- **准确率**: 90%+ (在测试集上)
- **支持类别**: 60+ 种植物病害

### 训练配置
- **批次大小**: 32
- **学习率**: 0.001 (Adam优化器)
- **训练轮数**: 10-20 epochs
- **数据增强**: 旋转、翻转、光照、遮挡

## 🔧 项目结构

```
plant-health-ai/
├── app.py                        # Web应用主文件
├── main.py                       # 模型训练脚本
├── data_augmentation_demo.py     # 数据增强可视化
├── best_model.pth                # 训练好的模型权重
├── README.md                     # 项目说明文档
├── requirements.txt              # 依赖包列表
└── Image Data base/              # 数据集目录(已忽略)
    ├── Apple healthy/
    ├── Apple Black rot/
    ├── Tomato healthy/
    ├── Tomato Early blight/
    └── ... (60+ 类别)
```

## 🎨 界面预览

系统提供现代化的Web界面，支持：
- 📱 响应式设计，适配各种设备
- 🖼️ 拖拽上传，操作便捷
- ⚡ 实时诊断，结果立即可见
- 🎯 清晰的结果展示

## 🔬 技术细节

### 数据预处理
- **图像尺寸**: 224×224 (标准输入)
- **数据增强**: 
  - 随机旋转 (±45°)
  - 水平/垂直翻转
  - 颜色抖动 (对比度、饱和度)
  - 光照变化模拟
  - 叶片遮挡模拟

### 模型优化
- **混合精度训练**: 使用FP16加速训练
- **梯度缩放**: 防止梯度下溢
- **学习率调度**: ReduceLROnPlateau
- **早停机制**: 防止过拟合

### 评估指标
- **准确率**: 整体分类准确率
- **混淆矩阵**: 详细分类性能分析
- **分类报告**: 精确率、召回率、F1分数

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 贡献方式
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request


## 🙏 致谢

- 感谢所有提供植物病害图片数据的研究者
- 感谢PyTorch、Gradio等开源框架的支持
- 感谢深度学习社区的技术分享

<div align="center">

**🌱 让AI为农业插上智慧的翅膀 🌱**

*用科技守护绿色，让每一片叶子都健康生长*

</div>


# 🌱 植物病害智能诊断系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4+-red.svg)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-11.8-green.svg)](https://developer.nvidia.com/cuda)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 基于深度学习的植物病害智能识别系统，支持 **38 种**农作物病害的自动诊断和分类

## 📊 项目概况

本项目使用 PyTorch 框架构建了一个轻量级卷积神经网络（CNN），能够识别 38 种不同的植物病害和健康状态。模型经过 54,305 张 PlantVillage 数据集的训练，在测试集上达到了 **98%+** 的分类准确率。

### 核心数据
- **训练数据**: 54,305 张植物叶片图像
- **支持类别**: 38 种（14 种作物 × 病害/健康）
- **模型参数量**: ~13 万（超轻量级）
- **推理速度**: < 0.5 秒/张（GPU）

## 🌾 支持识别的植物类别

### 🍎 苹果 (Apple)
| 病害类型 | 说明 |
|:---|:---|
| Apple_scab | 苹果疮痂病 |
| Black_rot | 黑腐病 |
| Cedar_apple_rust | 雪松苹果锈病 |
| healthy | 健康叶片 |

### 🍅 番茄 (Tomato)
| 病害类型 | 说明 |
|:---|:---|
| Bacterial_spot | 细菌性斑点病 |
| Early_blight | 早疫病 |
| Late_blight | 晚疫病 |
| Leaf_Mold | 叶霉病 |
| Septoria_leaf_spot | 叶斑病 |
| Spider_mites | 蜘蛛螨（二斑叶螨）|
| Target_Spot | 靶斑病 |
| Tomato_Yellow_Leaf_Curl_Virus | 黄化曲叶病毒 |
| Tomato_mosaic_virus | 番茄花叶病毒 |
| healthy | 健康叶片 |

### 🥔 马铃薯 (Potato)
| 病害类型 | 说明 |
|:---|:---|
| Early_blight | 早疫病 |
| Late_blight | 晚疫病 |
| healthy | 健康叶片 |

### 🌽 玉米 (Corn/Maize)
| 病害类型 | 说明 |
|:---|:---|
| Cercospora_leaf_spot | 灰斑病 |
| Common_rust | 普通锈病 |
| Northern_Leaf_Blight | 大斑病 |
| healthy | 健康叶片 |

### 🍇 葡萄 (Grape)
| 病害类型 | 说明 |
|:---|:---|
| Black_rot | 黑腐病 |
| Esca | 黑麻疹病 |
| Leaf_blight | 叶枯病 |
| healthy | 健康叶片 |

### 🍒 其他水果
| 作物 | 支持类别 |
|:---|:---|
| 蓝莓 (Blueberry) | 健康 |
| 樱桃 (Cherry) | 白粉病、健康 |
| 桃子 (Peach) | 细菌性斑点病、健康 |
| 草莓 (Strawberry) | 叶焦病、健康 |
| 树莓 (Raspberry) | 健康 |

### 🫑 蔬菜及其他
| 作物 | 支持类别 |
|:---|:---|
| 甜椒 (Pepper,bell) | 细菌性斑点病、健康 |
| 南瓜 (Squash) | 白粉病 |
| 大豆 (Soybean) | 健康 |
| 柑橘 (Orange) | 黄龙病 |

### 📊 完整类别列表（38 种）
<details>
<summary>点击展开完整列表</summary>

1. Apple___Apple_scab
2. Apple___Black_rot
3. Apple___Cedar_apple_rust
4. Apple___healthy
5. Blueberry___healthy
6. Cherry_(including_sour)___Powdery_mildew
7. Cherry_(including_sour)___healthy
8. Corn_(maize)___Cercospora_leaf_spot
9. Corn_(maize)___Common_rust
10. Corn_(maize)___Northern_Leaf_Blight
11. Corn_(maize)___healthy
12. Grape___Black_rot
13. Grape___Esca_(Black_Measles)
14. Grape___Leaf_blight
15. Grape___healthy
16. Orange___Haunglongbing_(Citrus_greening)
17. Peach___Bacterial_spot
18. Peach___healthy
19. Pepper,_bell___Bacterial_spot
20. Pepper,_bell___healthy
21. Potato___Early_blight
22. Potato___Late_blight
23. Potato___healthy
24. Raspberry___healthy
25. Soybean___healthy
26. Squash___Powdery_mildew
27. Strawberry___Leaf_scorch
28. Strawberry___healthy
29. Tomato___Bacterial_spot
30. Tomato___Early_blight
31. Tomato___Late_blight
32. Tomato___Leaf_Mold
33. Tomato___Septoria_leaf_spot
34. Tomato___Spider_mites
35. Tomato___Target_Spot
36. Tomato___Tomato_Yellow_Leaf_Curl_Virus
37. Tomato___Tomato_mosaic_virus
38. Tomato___healthy
</details>

## 🛠️ 技术架构

### 模型架构
```
PlantDiseaseCNN (轻量级 CNN)
├── 特征提取层 (Features)
│   ├── Conv2d(3→32) + BN + ReLU + MaxPool
│   ├── DepthwiseSeparableConv(32→64) + MaxPool
│   ├── ResidualBlock(64→64)
│   ├── DepthwiseSeparableConv(64→128) + MaxPool
│   └── DepthwiseSeparableConv(128→256) + MaxPool
└── 分类器 (Classifier)
    ├── AdaptiveAvgPool2d(1)
    ├── Flatten
    ├── LayerNorm(256)
    └── Linear(256→38)
```

### 核心技术
| 技术 | 说明 |
|:---|:---|
| **深度可分离卷积** | 参数量减少约 87%，适合端侧部署 |
| **残差连接** | 缓解梯度消失，稳定训练 |
| **批归一化** | 加速收敛，提高泛化能力 |
| **全局自适应池化** | 支持任意尺寸输入 |

### 训练配置
| 参数 | 值 |
|:---|:---|
| 优化器 | Adam (lr=0.001) |
| 损失函数 | 交叉熵损失 |
| 学习率调度 | StepLR (每10步 ×0.5) |
| 批次大小 | 16 (GPU 4GB 显存) |
| 训练轮数 | 30 |
| 数据增强 | 翻转、旋转、裁剪 |

## 📦 安装与使用

### 环境要求
```bash
Python >= 3.8
CUDA 11.5+ (推荐 GPU 训练)
8GB+ RAM
4GB+ VRAM (可选，GPU 训练)
```

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/DaDa-pixel/plant-health-ai-main.git
cd plant-health-ai-main
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **下载数据集**
将 PlantVillage 数据集解压到 `datasets/raw/color/` 目录下

5. **启动 Web 界面**
```bash
python app.py
```

6. **访问系统**
打开浏览器访问 `http://127.0.0.1:7861`

### 训练模型
```bash
# 使用 GPU 训练（推荐）
python train.py

# 或使用 CPU 训练
# 修改 train.py 中的 batch_size 为 32
```

### 模型评估
```bash
# 运行完整评估（混淆矩阵、分类报告）
python main.py
```

## 📁 项目结构

```
plant-health-ai-main/
├── app.py                    # Gradio Web 应用
├── train.py                  # GPU 训练脚本
├── main.py                   # 完整评估脚本
├── best_model.pth            # 训练好的模型权重 (38类)
├── class_names.txt           # 类别标签列表
├── training_curves.png       # 训练曲线图
├── requirements.txt          # 依赖包列表
├── datasets/                 # 数据集目录
│   └── raw/
│       └── color/            # PlantVillage 图片
│           ├── Apple___Apple_scab/
│           ├── Tomato___Late_blight/
│           └── ... (38个子文件夹)
└── README.md                 # 项目说明
```

## 🎯 使用方法

### Web 界面操作
1. **上传图片**: 点击上传区域，选择植物叶片图片
2. **开始诊断**: 点击「开始诊断」按钮
3. **查看结果**: 系统显示病害类型和置信度
4. **清空重试**: 点击「清空」按钮重新开始

### 支持的图片格式
- JPG / JPEG
- PNG
- BMP

## 📈 性能指标

| 指标 | 值 |
|:---|:---|
| 验证集准确率 | 98%+ |
| 模型参数量 | 131,270 |
| 模型文件大小 | ~1.5 MB |
| GPU 推理时间 | < 0.5 秒/张 |
| CPU 推理时间 | < 2 秒/张 |

## 🔧 常见问题

### Q: 显存不足怎么办？
```python
# 在 train.py 中减小 batch_size
batch_size = 8   # 或 4
```

### Q: 如何增加新的病害类别？
1. 收集新病害图片，放入 `datasets/raw/color/新类别名/`
2. 运行 `python train.py` 重新训练

### Q: 预测结果不准怎么办？
- 确保上传的图片清晰，叶片占比较大
- 使用真实场景图片时，效果可能略低于实验室照片

## 📝 更新日志

### v1.0.0 (2024)
- ✅ 完成 38 类植物病害识别模型训练
- ✅ 实现 Gradio Web 界面
- ✅ 支持 GPU 加速训练
- ✅ 准确率达到 98%+

## 🙏 致谢

- **PlantVillage Dataset** - 提供 54,306 张高质量植物病害图片
- **PyTorch** - 深度学习框架支持
- **Gradio** - Web 界面快速搭建

## 📄 许可证

MIT License

---

<div align="center">

**🌱 用 AI 守护每一片绿叶 🌱**

*如有问题或建议，欢迎提交 Issue*

</div>

---

这个 README 完全基于你当前项目的实际情况（38 类、PlantVillage 数据集、轻量级 CNN 模型）进行了修正，删除了那些不存在的功能描述（如 60+ 类、茶叶、水稻等）。需要我进一步调整吗？
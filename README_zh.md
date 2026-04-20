
# 智能农作物病害检测系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-2.7.18-lightgrey.svg)](https://spring.io/projects/spring-boot)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)

[English](./README.md)

---

### 1. 项目简介

本项目是一个智能农作物病害检测系统，采用**自定义设计的卷积神经网络（CNN）**进行高精度的病害分类。模型融合了**深度可分离卷积**、**ECA注意力机制**和**残差连接**等先进技术，在保持高效计算的同时实现高准确率。系统采用现代化的前后端分离全栈架构，提供从图像识别作物病害的端到端解决方案，并集成Grad-CAM可视化技术突出显示病害区域。系统旨在为农业生产者和科研人员提供一个高效、精准的病害识别工具。

### 2. 核心功能

- **智能病害分类**: 支持从静态图片中进行高精度CNN模型检测，覆盖多种作物类型（苹果、棉花、玉米、葡萄、马铃薯、草莓、番茄、小麦、水稻等）
- **Grad-CAM热力图可视化**: 集成梯度加权类激活映射技术，可视化展示模型诊断时关注的区域
- **多服务后端**: 采用微服务架构，**Flask**服务负责AI模型推理和知识库集成，**Spring Boot**服务处理业务逻辑、数据管理和用户交互
- **现代化前端**: 基于**Vue 3**、**Vite**和**Element Plus**构建的响应式、用户友好的Web界面
- **知识库智能推荐**: 集成的病害知识库和LLM驱动的建议系统，提供防治方案推荐
- **实时通信与可视化**: 使用**WebSocket**在处理期间提供即时反馈，并集成**ECharts**对检测结果进行丰富的数据可视化
- **可扩展与解耦**: 前端、业务后端和AI服务三者明确分离，便于独立开发、扩展和维护

### 3. 技术栈

- **前端**: `Vue 3`, `Vite`, `Element Plus`, `Axios`, `ECharts`, `Socket.io-client`, `TypeScript`
- **后端 (业务逻辑)**: `Java 1.8`, `Spring Boot 2.7.18`, `MyBatis-Plus 3.5.3`, `MySQL 8.0`, `Maven`, `WebFlux`
- **后端 (AI模型)**: `Python 3.8+`, `Flask`, `PyTorch`, `OpenCV`, `NumPy`, `Matplotlib`, `Gradio`
- **AI模型架构**: 自定义CNN，包含深度可分离卷积、ECA注意力机制、残差块
- **数据库**: `MySQL/MariaDB`用于持久化存储用户数据、检测记录和温室信息

### 4. 典型应用场景

- **智慧农业**: 辅助农户快速识别作物病害，及时采取防治措施，并提供可视化解释
- **农业研究**: 为科研人员提供植物病理学自动数据收集和分析的工具
- **教学示例**: 作为一个功能完善的全栈项目，展示CNN实现、注意力机制和Grad-CAM可视化技术
- **精准农业**: 基于准确的病害诊断实现针对性的治疗建议

### 5. 安装与快速上手

**环境依赖:**
- `Node.js` >= 16.0
- `Python` >= 3.8
- `Java` >= 1.8
- `Maven` >= 3.6
- `MySQL` 或 `MariaDB` >= 5.7

**步骤1：数据库配置**
1. 创建名为`cropdisease`的MySQL数据库
2. 导入根目录下的`cropdisease.sql`文件
3. 在后端配置中设置数据库连接

**步骤2：后端启动 (Spring Boot)**
1. 进入`Plant_doctor_Springboot`目录
2. 修改`src/main/resources/application.yml`中的数据库连接信息：
```
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/cropdisease?useSSL=false&serverTimezone=UTC
    username: root
    password: yourpassword
    driver-class-name: com.mysql.cj.jdbc.Driver

```

3. 运行应用：
```
mvn spring-boot:run
```

**步骤3：后端启动 (Flask AI)**
1. 进入`Plant_doctor_Flask`目录
2. 安装Python依赖：
```
pip install -r requirements.txt
```
3. 下载预训练的CNN模型权重文件（如`best_model.pth`）并放入`weights`文件夹
4. 运行AI服务：
```
python main.py
```

**步骤4：前端启动 (Vue)**
1. 进入`Plant_doctor_Vue`目录
2. 安装依赖：
```
npm install
```
3. 启动开发服务器：
```
npm run dev
```
4. 在浏览器中访问提示的地址（例如`http://localhost:3000`）

### 6. 贡献方式

欢迎参与贡献！您可以通过提交 Pull Request 或开启 Issue 来报告问题或提出新功能建议。
1. Fork 本仓库。
2. 创建您的新功能分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 创建一个 Pull Request。

### 7. 许可证

本项目采用 **MIT 许可证**。详情请见 `LICENSE` 文件。

# 数据分析平台

一个基于Python和Flask的现代化数据分析平台，提供数据可视化、统计分析和报告生成功能。

## 功能特点

- 🔐 用户注册和登录系统
- 📊 支持CSV和Excel格式数据上传
- 📈 多种图表类型的数据可视化
- 📋 自动生成数据统计信息
- 📑 支持报告导出
- 💻 响应式设计，适配PC和移动设备

## 技术栈

### 后端
- Python 3.8+
- Flask - Web框架
- Pandas - 数据处理
- NumPy - 数值计算
- Plotly - 数据可视化

### 前端
- HTML5 / CSS3 / JavaScript
- Bootstrap 5 - UI框架
- Plotly.js - 交互式图表
- Font Awesome - 图标

## 快速开始

1. 克隆仓库
```bash
git clone https://github.com/yourusername/data-analysis-platform.git
cd data-analysis-platform
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动应用
```bash
python app.py
```

4. 打开浏览器访问
```
http://localhost:5000
```

5. 使用默认管理员账号登录
```
用户名: admin
密码: admin
```

## 使用指南

1. **上传数据**：在"上传数据"页面，上传CSV或Excel格式的数据文件。
2. **选择数据集**：在"我的数据集"页面，选择要分析的数据集。
3. **创建可视化**：在分析页面，选择图表类型和数据列进行可视化。
4. **查看统计信息**：自动生成的数据统计信息将显示在分析页面底部。
5. **导出报告**：点击"导出分析报告"按钮，将分析结果导出为报告。

## 项目结构

```
data-analysis-platform/
├── app.py              # 主应用文件
├── requirements.txt    # 项目依赖
├── static/             # 静态资源
│   ├── css/            # CSS样式表
│   ├── js/             # JavaScript文件
│   └── uploads/        # 上传的数据文件
└── templates/          # HTML模板
    ├── base.html       # 基础模板
    ├── index.html      # 主页
    ├── login.html      # 登录页面
    ├── register.html   # 注册页面
    ├── upload.html     # 上传页面
    ├── datasets.html   # 数据集列表页面
    └── analyze.html    # 分析页面
```

## 后续开发计划

- 高级数据处理功能
- 机器学习模型集成
- 用户数据权限管理
- 更多数据源连接
- 更多可视化类型

## 贡献指南

欢迎贡献代码或提出问题！请遵循以下步骤：

1. Fork 项目
2. 创建新分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request 
# 数据分析平台

一个强大的数据分析平台，提供数据可视化、统计分析和AI辅助分析功能。

## 功能特点

- 数据上传与管理：支持CSV和Excel文件
- 基础数据分析：描述性统计、图表生成
- 高级数据分析：
  - 时间序列预测
  - 异常检测
  - 相关性分析
  - 模式挖掘
  - 特征重要性分析
- 用户账户管理

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Flask
- 数据处理：Pandas, NumPy
- 机器学习：Scikit-learn, Statsmodels
- 可视化：Plotly

## 安装与运行

### 本地运行

1. 克隆代码库：
```bash
git clone https://github.com/yourusername/data-analysis-platform.git
cd data-analysis-platform
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 在浏览器中访问：`http://127.0.0.1:5000`

### 部署到Render

1. 在Render上创建一个新的Web Service
2. 连接到你的GitHub仓库
3. 选择主分支
4. 设置构建命令：`pip install -r requirements.txt`
5. 设置启动命令：`gunicorn app:app`
6. 点击"Create Web Service"

## 示例数据

系统内置了多种示例数据集：
- 销售数据分析示例
- 客户调查数据分析示例
- 库存数据分析示例
- 时间序列分析示例

## 默认账户

用户名：admin
密码：admin

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
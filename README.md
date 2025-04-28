# qwenvlmaxDataAnalysis 项目

## 项目介绍

本项目使用通义千问的qwen-vl-max模型进行多模态数据分析，能够识别图片内容并提取结构化信息。主要功能包括：

1. 图片内容识别
2. 信息抽取与标准化
3. 结果保存为JSON格式

## 安装步骤

1. 克隆项目仓库
```bash
git clone <仓库地址>
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 设置环境变量
```bash
export DASHSCOPE_API_KEY="你的API_KEY"
```

## 使用方法

1. 将待分析的图片放入`dataset`文件夹
2. 运行主程序
```bash
python main.py
```
3. 程序会自动处理图片并生成结果
4. 结果保存在`output`文件夹中

## 示例代码

```python
# 从URL识别图片内容
result = recognize_image_from_url("https://example.com/image.png")

# 运行完整处理流程
result = graph.invoke({"input": "https://example.com/image.png"})
```

## 注意事项

1. 确保已正确配置阿里云OSS上传凭证
2. 图片格式支持PNG/JPG等常见格式
3. 结果JSON文件会保存在`output`目录
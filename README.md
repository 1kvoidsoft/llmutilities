# 文件结构生成器 filestructure_gen.py

一个简单但实用的Python工具，用于生成和输出目录结构的文本表示。该工具可以帮助您可视化项目结构，便于在文档或README文件中展示。

## 功能特点

- 生成目录和文件的树状结构视图
- 支持排除特定文件夹，避免输出不必要的内容
- 使用Unicode字符创建美观的树状图
- 输出结果保存到文本文件中

## 使用方法

1. 确保您已安装Python
2. 创建一个`exclude_folders.txt`文件（可选），列出不想包含在输出中的文件夹名称
3. 修改脚本中的以下参数：
   - `search_directory`: 要扫描的目录路径
   - `output_file`: 输出文件名
   - `exclude_file`: 排除文件夹列表文件名


## 输出示例

```
src/
├── components/
│   ├── Button.js
│   ├── Header.js
│   └── Footer.js
├── utils/
│   ├── helpers.js
│   └── constants.js
└── index.js
```

## 许可证

[MIT](LICENSE)

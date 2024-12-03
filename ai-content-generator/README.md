# AI 内容生成器 🤖

一个基于 Streamlit 和 OpenAI API 的智能内容生成工具，可以帮助你快速生成各种类型的创意内容。

## 功能特点 ✨

- 🎯 支持多种内容类型生成（美食菜谱、旅游攻略、读书笔记、小红书文案等）
- 📝 批量生成模式，一次生成多篇内容
- 📊 内容分析（字数统计、段落数、句子数等）
- 💾 自动保存历史记录
- 🌙 深色模式支持
- 📥 一键导出 Markdown 文件

## 安装说明 🚀

1. 克隆仓库：
```bash
git clone https://github.com/[你的用户名]/ai-content-generator.git
cd ai-content-generator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
OPENAI_API_KEY=你的OpenAI API密钥
OPENAI_API_BASE=你的API基础URL
```

4. 运行应用：
```bash
streamlit run streamlit_generator_new.py
```

## 使用说明 📖

1. 选择内容类型：从侧边栏选择要生成的内容类型
2. 选择模型：选择要使用的 AI 模型
3. 输入主题：在输入框中输入你想要生成内容的主题或关键词
4. 点击生成：点击"开始生成"按钮，等待内容生成
5. 查看结果：生成的内容会显示在右侧，包含内容分析和下载选项

### 批量生成模式

1. 在侧边栏勾选"批量生成模式"
2. 设置最大生成数量
3. 在输入框中每行输入一个主题
4. 点击生成，系统会依次生成所有内容

## 注意事项 ⚠️

- API 速率限制：如果遇到 "rate limit exceeded" 错误，请等待约1小时后再试
- 请确保你的 OpenAI API 密钥有足够的额度
- 生成的内容仅供参考，建议进行适当的人工编辑和审核

## 技术栈 🛠️

- Python
- Streamlit
- OpenAI API
- SQLite
- Pandas

## 贡献指南 🤝

欢迎提交 Issues 和 Pull Requests！

## 许可证 📄

MIT License

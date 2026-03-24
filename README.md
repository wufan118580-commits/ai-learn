# 文档学习助手

一个功能强大的文档学习和处理工具，支持学习笔记生成、翻译语音、媒材建议和 HTML 管理。

## 功能特性

### 🏠 首页导航
- 清晰的功能导航页面
- 快速切换不同功能模块

### 📚 生成学习笔记
- 上传文档（支持 txt、pdf、docx）
- AI 自动生成结构化学习笔记
- 生成可视化思维导图（Mermaid 格式）
- 支持标题建议生成
- 支持编辑和下载（MD 格式）

### 🔊 翻译语音
- 文档翻译为中文
- 文本转语音（TTS）功能
- 支持语音润色优化（社交媒体风格、叙事风格）
- 可调节语速和音调
- 支持语音下载

### 🎨 媒材建议
- 智能分析文档内容
- 提供配图搜索建议
- 提供 AI 生成图片的提示词
- 支持使用原文或翻译文本

### 📄 HTML 管理
- 上传 HTML 静态页面
- 支持文件上传和代码粘贴
- **数据持久化存储**（使用 Docker Volume）
- 下载和管理 HTML 页面
- **无需 API Key** 即可使用

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

### 3. 运行应用

```bash
streamlit run src/app.py
```

访问 `http://localhost:8501`

## Docker 部署

### 使用部署脚本（推荐）

```bash
# 一键部署
chmod +x deploy.sh
./deploy.sh
```

### 使用 docker-compose

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 DEEPSEEK_API_KEY

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 数据持久化

应用使用 Docker Volume 实现 HTML 文件的持久化存储，确保容器重启后数据不丢失。

- **默认配置**：使用命名卷 `html_data`
- **数据备份**：参见 `DEPLOY.md` 中的备份指南
- **数据迁移**：支持导出/导入数据卷

详细部署和数据管理说明请参考 [DEPLOY.md](DEPLOY.md)

## 项目结构

```
workspace/
├── src/
│   ├── app.py                 # 应用主入口
│   ├── document_processor.py   # 文档处理
│   ├── llm_service.py        # LLM 服务
│   ├── tts_service.py        # TTS 服务
│   ├── note_generator.py     # 笔记生成
│   ├── prompt_templates.py    # 提示词模板
│   ├── handlers/            # 业务处理逻辑
│   │   ├── notes_handler.py
│   │   ├── translation_handler.py
│   │   ├── media_handler.py
│   │   └── html_handler.py
│   └── ui/                 # UI 组件
│       ├── home_page.py
│       ├── notes_tab.py
│       ├── translation_tab.py
│       ├── media_tab.py
│       └── html_tab.py
├── tests/                   # 测试文件
├── requirements.txt          # 项目依赖
├── Dockerfile              # Docker 镜像
├── docker-compose.yml      # Docker Compose
└── DEPLOY.md             # 部署文档
```

## 开发

### 安装开发依赖

```bash
make install-dev
```

### 代码格式化

```bash
make format
```

### 代码检查

```bash
make lint
```

### 运行测试

```bash
make test
```

## 注意事项

1. HTML 管理功能不需要 API Key
2. 其他功能需要配置 DeepSeek API Key
3. 翻译和媒材建议会共享上传的文档
4. 建议使用 Python 3.8+

## 许可证

MIT License

# 公式识别 API 服务

基于 FastAPI 的独立公式识别服务，可将图片中的数学公式转换为 LaTeX 和 MathML 格式。

## 功能特性

- 🚀 **图片公式识别**：支持 PNG、JPG、JPEG、BMP 格式
- 📝 **LaTeX 输出**：返回标准 LaTeX 公式代码
- 🔢 **MathML 转换**：自动转换为 MathML 格式
- ⚡ **高性能**：模型懒加载，按需使用
- 📚 **完整文档**：自动生成的 OpenAPI 文档
- 🔧 **易于集成**：RESTful API 设计

## API 端点

### 1. 识别公式
```
POST /api/v1/formula/recognize
Content-Type: multipart/form-data
```

**请求参数：**
- `image`: 图片文件 (PNG/JPG/JPEG/BMP)

**响应示例：**
```json
{
  "success": true,
  "data": {
    "latex": "E = mc^2",
    "mathml": "<math>...</math>",
    "preview": "$E = mc^2$",
    "processing_time": 1.234
  },
  "metadata": {
    "filename": "formula.png",
    "content_type": "image/png",
    "file_size": 12345
  }
}
```

### 2. LaTeX 转 MathML
```
POST /api/v1/formula/convert
Content-Type: application/json
```

**请求参数：**
```json
{
  "latex": "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "latex": "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}",
    "mathml": "<math>...</math>",
    "preview": "$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$"
  }
}
```

### 3. 健康检查
```
GET /health
```

**响应示例：**
```json
{
  "status": "healthy",
  "service": "formula-ocr-api",
  "model_loaded": true,
  "timestamp": 1712345678.123
}
```

## 快速开始

### 1. 安装依赖
```bash
cd /workspace/api
pip install -r requirements-api.txt
```

### 2. 启动服务
```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问文档
打开浏览器访问：http://localhost:8000/docs

## Docker 部署

### 1. 构建镜像
```bash
cd /workspace
docker build -t formula-api:latest .
```

### 2. 运行容器
```bash
docker run -d \
  --name formula-api \
  -p 8000:8000 \
  -v $(pwd)/formula_history:/app/formula_history \
  formula-api:latest
```

## 客户端调用示例

### Python
```python
import requests

# 识别公式
url = "http://localhost:8000/api/v1/formula/recognize"
files = {"image": open("formula.png", "rb")}
response = requests.post(url, files=files)
result = response.json()

if result["success"]:
    print(f"LaTeX: {result['data']['latex']}")
    print(f"MathML: {result['data']['mathml']}")
```

### cURL
```bash
# 识别公式
curl -X POST \
  -F "image=@formula.png" \
  http://localhost:8000/api/v1/formula/recognize

# LaTeX 转 MathML
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"latex": "E = mc^2"}' \
  http://localhost:8000/api/v1/formula/convert
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `PORT` | 8000 | 服务监听端口 |
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `FORMULA_HISTORY_DIR` | formula_history | 历史记录存储目录 |

## 性能说明

- **首次请求**：约 3-5 秒（需要加载模型）
- **后续请求**：约 0.5-2 秒
- **内存占用**：约 1-2 GB（主要来自 PyTorch 模型）
- **并发能力**：建议使用 GPU 提升性能

## 错误处理

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 422 | 识别失败 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 许可证

MIT License
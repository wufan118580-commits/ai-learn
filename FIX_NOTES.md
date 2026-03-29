# 部署问题修复说明

## 修复的问题

### 1. API Key 无法读取问题

**问题现象**：
```
❌ 未找到内置API密钥，请在.env文件中配置
```

**原因**：
Docker Compose 配置中没有将宿主机的 `.env` 文件传递到容器中。

**修复方案**：
在 `docker-compose.yml` 中添加 `env_file` 配置：

```yaml
services:
  app:
    env_file:
      - .env  # 新增：从宿主机读取 .env 文件
    environment:
      - PYTHONUNBUFFERED=1
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

**验证方法**：
1. 确保 `.env` 文件存在且配置正确
2. 重启容器：`docker-compose restart`
3. 检查页面是否正常读取 API Key

### 2. HTML 上传后列表不显示问题

**问题现象**：
上传 HTML 文件后，列表中看不到任何文件。

**原因**：
HTML 上传按钮被错误地限制需要 API Key，导致无法上传。

**修复方案**：
修改 `src/ui/html_tab.py`，移除上传按钮的 API Key 限制：

```python
# 修复前
upload_button = st.button(
    "📤 上传页面",
    disabled=not st.session_state.api_key or (not uploaded_file and not html_content),
    ...
)

# 修复后
upload_button = st.button(
    "📤 上传页面",
    disabled=(not uploaded_file and not html_content),
    ...
)
```

**额外改进**：
- 添加调试信息复选框，方便排查问题
- HTML 管理功能完全独立，不需要 API Key

**验证方法**：
1. 上传一个 HTML 文件
2. 切换到"页面列表"标签页
3. 勾选"显示调试信息"查看存储状态
4. 确认文件能正常显示和下载

## 重新部署步骤

如果已经部署过，需要重新部署以应用修复：

```bash
# 1. 停止现有容器
docker-compose down

# 2. 确认 .env 文件配置正确
cat .env
# 应该包含：DEEPSEEK_API_KEY=你的密钥

# 3. 重新构建并启动
docker-compose up -d --build

# 4. 查看日志确认启动成功
docker-compose logs -f
```

## 数据备份（重要）

在重新部署前，建议备份现有数据：

```bash
# 备份 HTML 数据卷
docker run --rm \
  -v document-learning-assistant_html_data:/data \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/html_data_backup_$(date +%Y%m%d).tar.gz /data
```

如需恢复数据：

```bash
docker run --rm \
  -v document-learning-assistant_html_data:/data \
  -v $(pwd):/backup \
  alpine \
  tar xzf /backup/html_data_backup_YYYYMMDD.tar.gz -C /
```

## 测试验证

部署完成后，按以下步骤测试：

### 测试 API Key
1. 打开页面
2. 查看侧边栏，选择"使用内置密钥"
3. 不应该显示错误提示

### 测试 HTML 管理
1. 进入"HTML 管理"页面
2. 上传一个测试 HTML 文件
3. 切换到"页面列表"标签页
4. 确认文件显示正常
5. 点击下载按钮，确认能正常下载

### 测试持久化
1. 上传几个 HTML 文件
2. 停止容器：`docker-compose stop`
3. 启动容器：`docker-compose start`
4. 刷新页面，确认文件依然存在

## 技术细节

### 环境变量传递流程

```
宿主机 .env
    ↓ env_file: .env
Docker Compose
    ↓ environment 传递
容器内环境变量
    ↓ os.getenv()
应用读取
```

### Volume 持久化流程

```
容器内 /app/html_storage/
    ↓ volume: html_data
Docker 命名卷
    ↓ 持久化到磁盘
容器重启后数据保留
```

## 相关文件

修改的文件列表：
- `docker-compose.yml` - 添加 env_file 配置
- `src/ui/html_tab.py` - 移除 API Key 限制，添加调试信息
- `deploy.sh` - 添加配置验证
- `DEPLOY.md` - 更新故障排查文档
- `README.md` - 更新功能说明

## 支持与反馈

如仍有问题，请：
1. 查看容器日志：`docker-compose logs -f`
2. 使用页面中的调试信息功能
3. 检查 Volume 状态：`docker volume inspect document-learning-assistant_html_data`

# 文档学习助手 - Docker 部署指南

## 持久化方案说明

本应用使用 **Docker Volume** 来持久化 HTML 文件存储，确保容器重启后数据不会丢失。

### 持久化架构

```
容器内部：/app/html_storage/
    ↓ (Volume 挂载)
宿主机：Docker 管理的命名卷 (html_data)
```

### 持久化优势

1. **数据持久化**：容器重启、更新后数据依然存在
2. **独立管理**：数据与应用镜像分离，便于备份
3. **易于迁移**：可以轻松导出/导入数据卷
4. **性能优化**：使用 Docker 卷而非绑定挂载，性能更优

## 快速部署

### 方法一：使用部署脚本（推荐）

```bash
# 1. 克隆或下载项目代码
cd document-learning-assistant

# 2. 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

脚本会自动完成以下操作：
- 检查 Docker 环境
- 创建配置文件
- 构建镜像
- 启动容器
- 查看日志

### 方法二：手动部署

#### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置 API Key
vim .env
```

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# 应用配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

#### 2. 启动服务

```bash
# 构建并启动容器
docker-compose up -d

# 查看容器状态
docker-compose ps

# 查看应用日志
docker-compose logs -f
```

#### 3. 访问应用

浏览器访问：`http://localhost:8501`

## 常用管理命令

### 容器管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 查看容器状态
docker-compose ps

# 查看容器日志
docker-compose logs -f app

# 进入容器内部
docker-compose exec app sh
```

### 数据卷管理

```bash
# 查看所有卷
docker volume ls

# 查看 html_data 卷详情
docker volume inspect document-learning-assistant_html_data

# 备份 HTML 数据
docker run --rm -v document-learning-assistant_html_data:/data -v $(pwd):/backup alpine tar czf /backup/html_data_backup_$(date +%Y%m%d).tar.gz /data

# 恢复 HTML 数据
docker run --rm -v document-learning-assistant_html_data:/data -v $(pwd):/backup alpine tar xzf /backup/html_data_backup_YYYYMMDD.tar.gz -C /

# 删除数据卷（谨慎使用，会丢失所有数据）
docker-compose down -v
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 清空日志
docker-compose logs --tail=0 -f
```

## 数据迁移

### 迁移到其他服务器

1. **导出数据**

```bash
# 在原服务器上备份数据卷
docker run --rm -v document-learning-assistant_html_data:/data -v $(pwd):/backup alpine tar czf /backup/html_data.tar.gz /data

# 复制备份文件到新服务器
scp html_data.tar.gz user@new-server:/path/to/backup/
```

2. **在新服务器恢复**

```bash
# 在新服务器上解压数据
docker run --rm -v document-learning-assistant_html_data:/data -v $(pwd):/backup alpine tar xzf /backup/html_data.tar.gz -C /

# 重启容器
docker-compose restart
```

## 配置说明

### 端口配置

如需修改端口，编辑 `docker-compose.yml`：

```yaml
services:
  app:
    ports:
      - "8502:8501"  # 宿主机端口:容器端口
```

### 存储路径配置

默认使用 Docker 命名卷持久化。如果需要使用宿主机目录，修改 `docker-compose.yml`：

```yaml
services:
  app:
    volumes:
      - ./html_storage:/app/html_storage  # 使用宿主机目录
```

## 故障排查

### API Key 未找到

**问题**：页面显示"未找到内置API密钥，请在.env文件中配置"

**原因**：Docker 容器无法读取宿主机的 `.env` 文件

**解决方案**：
1. 确保 `.env` 文件在项目根目录
2. 检查 `docker-compose.yml` 中已配置 `env_file: .env`
3. 重启容器：
```bash
docker-compose down
docker-compose up -d
```

### HTML 上传后列表不显示

**问题**：上传 HTML 文件后，列表中看不到

**原因**：Volume 挂载或文件权限问题

**解决方案**：
1. 检查 Volume 是否正常创建：
```bash
docker volume ls | grep html_data
```

2. 检查 Volume 内容：
```bash
docker run --rm -v document-learning-assistant_html_data:/data alpine ls -la /data
```

3. 如果 Volume 为空，可以重启容器重新初始化：
```bash
docker-compose restart
```

4. 使用页面中的"显示调试信息"复选框查看详细状态

### 容器无法启动

```bash
# 查看容器日志
docker-compose logs

# 检查端口是否被占用
netstat -tunlp | grep 8501
```

### 数据丢失问题

```bash
# 确认数据卷是否存在
docker volume ls | grep html_data

# 查看数据卷内容
docker run --rm -v document-learning-assistant_html_data:/data alpine ls -la /data
```

### 权限问题

```bash
# 修复数据卷权限
docker-compose exec app chown -R appuser:appuser /app/html_storage
```

## 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 查看更新后的日志
docker-compose logs -f
```

## 生产环境建议

1. **使用 HTTPS**：建议使用 Nginx/Caddy 反向代理提供 HTTPS 访问
2. **日志管理**：配置日志轮转，避免日志文件过大
3. **资源限制**：在 docker-compose.yml 中添加资源限制
4. **监控告警**：部署监控系统监控容器状态
5. **定期备份**：设置定时任务自动备份数据卷

## 注意事项

- ⚠️ 删除容器不会删除数据卷，使用 `docker-compose down -v` 才会删除
- ⚠️ 数据卷由 Docker 管理，不建议直接修改卷内文件
- ⚠️ 定期备份 HTML 数据，避免意外数据丢失
- ⚠️ 修改配置后需要重启容器才能生效

## 技术支持

如有问题，请查看应用日志：
```bash
docker-compose logs -f
```

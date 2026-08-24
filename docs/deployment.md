# 部署说明

## 本地 Compose

1. 复制环境模板并设置 JWT 密钥：

   ```powershell
   Copy-Item backend/.env.example .env
   ```

2. 在 `.env` 中设置 `JWT_SECRET_KEY`，然后启动：

   ```powershell
   docker compose up --build
   ```

3. 访问 <http://localhost>；FastAPI 文档可通过开发模式的 `http://localhost:8000/docs` 查看。

Compose 会启动 PostgreSQL、Redis、MinIO、FastAPI 和 Nginx。当前应用默认使用本地文件存储；MinIO 已作为部署基础设施启动，后续可把 `storage.py` 替换为 S3 兼容 provider。

## 环境变量

| 变量 | 用途 | 默认 |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy 数据库连接 | SQLite |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 仅开发默认值 |
| `FRONTEND_URL` | CORS 允许的前端地址 | `http://localhost:5173` |
| `STORAGE_DIR` | 本地附件目录 | `./storage` |
| `MAX_UPLOAD_SIZE` | 单文件字节上限 | 25 MiB |

## 回滚

部署前记录当前 Git SHA。出现错误率、数据完整性或附件读写异常时，先停止新版本并恢复上一 SHA 的镜像/Compose 构建；数据库只使用向前兼容的新增表，本阶段没有破坏性迁移。

## 上线前检查

- [ ] 使用随机的 `JWT_SECRET_KEY`，不提交 `.env`
- [ ] PostgreSQL、附件卷和 MinIO 数据卷已配置备份
- [ ] 反向代理已配置 HTTPS
- [ ] `/health` 返回 200
- [ ] 注册、创建笔记、上传附件、AI 问答和管理员审核冒烟通过
- [ ] GitHub Actions CI 通过

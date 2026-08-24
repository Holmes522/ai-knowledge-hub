# Implementation Plan: AI Knowledge Hub

## Overview

按能力地图逐步交付一个可运行的个人学习知识库。每个阶段都形成独立可验证的产品切片，并在阶段验收后提交到 `main`、推送到 GitHub。

## Architecture Decisions

- 使用单仓库 `backend/` + `frontend/`，降低本地运行和 CI 配置复杂度。
- 通过 SQLAlchemy 抽象数据库，默认 SQLite，生产通过 `DATABASE_URL` 切换 PostgreSQL。
- 认证使用短期 JWT access token；前端保存到 sessionStorage，API 统一注入 Bearer token。
- 文件、AI、缓存等外部能力都先定义服务边界，避免本地开发强依赖外部账号。

## Task List

### Phase 0: Foundation

- [x] Task 0.1: 项目脚手架、环境配置、README、Git 忽略规则
- [x] Task 0.2: 数据库模型、初始化和健康检查

### Phase 1: Core Notes

- [x] Task 1.1: 注册、登录、当前用户和角色基础
- [x] Task 1.2: 笔记 CRUD、Markdown 内容和学习状态
- [x] Task 1.3: 标签关联和关键词搜索
- [x] Task 1.4: React 工作台、认证和笔记端到端流

### Checkpoint: Phase 1

- [x] 后端测试、前端测试、前端构建全部通过
- [x] 本地启动后可注册、登录、创建/编辑/搜索笔记（API 集成测试覆盖）
- [x] 提交并推送 Phase 1

### Phase 2: Media

- [x] Task 2.1: 文件模型、类型/大小校验和本地存储适配器
- [x] Task 2.2: 上传 API 和上传 UI（MinIO/S3 生产适配留到 delivery）
- [x] Task 2.3: 笔记附件管理

### Phase 3: Community and Admin

- [x] Task 3.1: 评论、审核和防垃圾基础策略
- [x] Task 3.2: 收藏和管理员后台 API

### Phase 4: AI/RAG

- [ ] Task 4.1: 文本切分、Embedding provider 和索引任务边界
- [ ] Task 4.2: 向量检索/RAG 服务和本地降级实现
- [ ] Task 4.3: AI 助手 UI 与引用来源

### Phase 5: Delivery

- [ ] Task 5.1: Docker Compose、Nginx 和环境文档
- [ ] Task 5.2: GitHub Actions CI/CD
- [ ] Task 5.3: 发布检查清单和部署说明

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| GitHub 仓库创建权限不可用 | High | 先保留本地原子提交；提供目标 remote 后立即推送 |
| 外部 AI/对象存储未配置 | Medium | 使用 provider 接口和本地适配器，保证核心流程可运行 |
| 全文搜索跨数据库差异 | Medium | Phase 1 用 SQLAlchemy 可移植查询，PostgreSQL 优化放入后续阶段 |

## Open Questions

- 部署平台待用户后续指定。

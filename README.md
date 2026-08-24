# AI Knowledge Hub

AI Knowledge Hub 是一个基于 React + FastAPI 的个人学习知识库系统，按照项目 PRD 分阶段实现。

## 当前进度

- Phase 0：项目脚手架、SQLite/PostgreSQL 兼容模型、健康检查
- Phase 1：注册、登录、JWT、笔记 CRUD、Markdown 内容、标签、搜索、学习状态和 React 工作台

## 本地运行

### 后端

```powershell
python -m pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

API 文档：<http://localhost:8000/docs>

### 前端

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

### 测试

```powershell
python -m pytest backend/tests -q
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

## 设计文档

- [能力地图](CAPABILITY-MAP.md)
- [实现规格](SPEC.md)
- [阶段计划](tasks/plan.md)
- [产品、数据库和架构设计](AI%20Knowledge%20Hub%20个人学习知识库系统%20PRD%20%2B%20数据库设计%20%2B%20系统架构设计.md)

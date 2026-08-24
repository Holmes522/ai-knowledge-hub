# Spec: AI Knowledge Hub

## Objective

构建一个面向个人学习的知识库 Web 应用，支持把 Markdown 笔记集中收集、分类、检索、复习，并逐步接入多媒体、社区和 AI/RAG 能力。第一版的完成标准是：用户可以注册/登录，创建、编辑、删除和查看自己的 Markdown 笔记，使用标签分类和关键词搜索，并记录学习状态。

## Tech Stack

- Frontend: React 19, TypeScript, Vite, React Router, Axios
- Backend: Python 3.13, FastAPI, SQLAlchemy 2, Pydantic Settings, JWT
- Database: SQLite for zero-config local development; PostgreSQL-compatible SQLAlchemy models for production
- Delivery: Docker Compose, Nginx, GitHub Actions

## Commands

```text
Backend install: python -m pip install -r backend/requirements.txt
Backend test: python -m pytest backend/tests -q
Backend dev: uvicorn app.main:app --app-dir backend --reload
Frontend install: npm --prefix frontend install
Frontend test: npm --prefix frontend test -- --run
Frontend build: npm --prefix frontend run build
Frontend dev: npm --prefix frontend run dev
```

## Project Structure

```text
backend/app/       FastAPI application, models, schemas, services, routes
backend/tests/     Backend unit and API tests
frontend/src/      React application and feature components
frontend/src/test/ Frontend tests
tasks/             Implementation plan and checklist
docs/              Architecture and operational notes
```

## Code Style

Backend uses typed functions, small route handlers, Pydantic schemas at boundaries, and service functions for business rules. Frontend uses functional components, explicit props, and accessible form controls.

```python
@router.post("/notes", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Note:
    return note_service.create(db, user_id=user.id, payload=payload)
```

## Testing Strategy

- Unit tests for validation, services, search and status transitions.
- API integration tests with an isolated SQLite database.
- Frontend tests for the main note creation/list/search flow.
- Build checks run for every phase; browser-level verification is required for UI phases when a browser runtime is available.

## Boundaries

- Always: validate input, keep secrets in environment variables, run focused tests and builds before each phase commit, keep commits atomic.
- Ask first: destructive data migrations, paid external services, changing public repository visibility, deploying to a real server.
- Never: commit secrets, commit `node_modules`/build output, disable failing tests, or silently change the database contract.

## Success Criteria

- Phase 1: authenticated user can manage notes, tags, search results and learning status locally.
- Phase 2: allowed media types can be uploaded to a storage adapter and linked to notes.
- Phase 3: comments/favorites/admin moderation work with role checks.
- Phase 4: AI service can index note content and answer with retrieved note context, with a deterministic local fallback.
- Phase 5: Docker Compose starts the documented services and CI runs tests/builds.

## Open Questions

- The PRD does not specify a production hosting provider; delivery will remain provider-neutral.
- The PRD does not define a visual brand system; Phase 1 will use a restrained editorial knowledge-workspace style.

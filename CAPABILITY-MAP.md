# AI Knowledge Hub 能力地图

| 模块 | 职责 | 依赖 |
|---|---|---|
| foundation | 项目脚手架、数据库、配置、健康检查 | — |
| identity | 注册、登录、JWT、角色权限 | foundation |
| notes | 笔记 CRUD、Markdown、标签、关键词搜索、学习状态 | identity |
| media | 图片/视频/文档上传和文件管理 | notes |
| community | 评论、审核、收藏、管理员后台 | identity, notes |
| ai | Embedding、向量检索、RAG 问答边界 | notes |
| delivery | Docker、Nginx、CI/CD、部署文档 | foundation, identity, notes, media, community, ai |

构建顺序：foundation → identity → notes → media → community → ai → delivery。

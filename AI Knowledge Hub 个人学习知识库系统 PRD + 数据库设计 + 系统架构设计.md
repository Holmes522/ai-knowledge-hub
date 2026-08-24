# AI Knowledge Hub
## 个人学习知识库系统

版本：V1.0

---

# 一、项目概述

## 1.1 项目背景

传统学习过程中，学习资料分散在：

- 本地文件夹
- 网盘
- 浏览器收藏
- Markdown笔记
- 视频课程
- 图片资料

导致：

- 知识无法统一管理
- 学习内容难以检索
- 知识之间缺少关联
- 复习效率低

因此设计一个个人学习知识库系统，实现：

> 收集 → 整理 → 分类 → 搜索 → 复习 → AI辅助学习

---

# 二、产品定位

## 产品名称

AI Knowledge Hub

## 产品类型

个人知识管理系统（Personal Knowledge Management System）

类似：

- Notion
- Obsidian
- GitBook


---

# 三、用户角色设计


## 1. 游客

权限：

- 查看公开学习笔记
- 搜索内容
- 查看标签
- 评论留言


---

## 2. 注册用户

权限：

- 上传学习笔记
- 编辑自己的笔记
- 创建自定义标签
- 收藏笔记
- 评论


---

## 3. 管理员

权限：

- 管理所有笔记
- 管理评论
- 管理用户
- 删除违规内容


---

# 四、核心功能需求


# 4.1 学习笔记管理


## 功能描述

用户可以创建学习笔记。

笔记支持：

- 纯文字
- 图片
- 视频
- PDF
- 文件附件


---

## 笔记结构


```
Note

标题

简介

正文内容

附件

标签

创建时间

更新时间

浏览量

状态

```


---

# 4.2 多媒体上传系统


支持文件：


## 图片

格式：

```
jpg
png
webp
gif
```


## 视频

格式：

```
mp4
webm
mov
```


## 文档

格式：

```
pdf
doc
ppt
zip
```


---

## 文件存储方案


不直接存数据库。


架构：

```
用户上传

↓

文件服务

↓

对象存储

↓

返回URL

↓

数据库保存地址

```


推荐：

开发：

MinIO


生产：

- 阿里云OSS
- 腾讯云COS
- AWS S3


---

# 4.3 搜索系统


## 第一阶段：关键词搜索


搜索范围：

- 标题
- 简介
- 正文
- 标签


示例：

输入：

```
Python
```


返回：

```
Python基础学习

Python爬虫笔记

FastAPI实践

```


技术：

PostgreSQL全文搜索


---

## 第二阶段：AI语义搜索


用户：

```
如何实现智能问答系统
```


系统找到：

```
RAG系统设计

Embedding学习笔记

向量数据库实践

```


实现：

```
学习笔记

↓

Embedding

↓

Milvus

↓

向量搜索

↓

返回结果

```


---

# 4.4 评论系统


## 游客评论


字段：

```
昵称

邮箱

评论内容

时间

```


---

## 管理功能


后台：

- 查看评论
- 审核评论
- 删除评论
- 屏蔽用户


---

## 防垃圾机制


支持：

- 评论审核
- 敏感词过滤
- IP限制
- 验证码


---

# 4.5 标签系统


采用多维标签。


## 标签类型


---

## 1. 格式标签


系统自动生成：

```
视频

图片

文字

PDF

代码

```


例如：

上传mp4：

自动添加：

```
视频
```


---

## 2. 内容分类标签


一级分类：

```
学习领域


├── 计算机

├── 数学

├── 英语

├── AI

└── 其他

```


---

## 3. 自定义标签


用户创建：


例如：

```
面试准备

重点复习

2026计划

难点

```


---

# 4.6 收藏系统


用户可以收藏：

- 学习笔记
- 视频
- 文章


---

# 4.7 学习状态管理


每个笔记支持：

```
未学习

学习中

已完成

复习中

```


---

# 4.8 知识关联系统


支持知识之间建立关系。


例如：

```
Python

 ↓

机器学习

 ↓

深度学习

 ↓

Transformer

 ↓

Agent

```


---

# 五、后台管理系统


路径：

```
/admin
```


功能：

## Dashboard


展示：

```
笔记数量

用户数量

评论数量

访问量

```


---

## 内容管理


支持：

- 新增笔记
- 修改笔记
- 删除笔记
- 审核内容


---

# 六、数据库设计


数据库：

PostgreSQL


---

# 用户表 user


字段：

```
id

username

password

email

avatar

role

created_time

```


---

# 笔记表 note


字段：

```
id

user_id

title

summary

content

status

views

created_time

updated_time

```


---

# 文件表 file


字段：

```
id

note_id

filename

file_type

file_url

file_size

created_time

```


---

# 标签表 tag


字段：

```
id

name

type

created_time

```


type:

```
format

category

custom

```


---

# 笔记标签关联表 note_tag


字段：

```
note_id

tag_id

```


---

# 评论表 comment


字段：

```
id

note_id

user_id

nickname

email

content

status

created_time

```


---

# 收藏表 favorite


字段：

```
id

user_id

note_id

created_time

```


---

# 知识关联表 note_relation


字段：

```
id

source_note_id

target_note_id

relation_type

```


---

# 学习记录表 learning_record


字段：

```
id

user_id

note_id

status

completed_time

```


---

# 七、系统架构设计


整体架构：

```

             用户浏览器

                  |

                  |

          React + TypeScript

                  |

                  |

               Nginx

                  |

                  |

             FastAPI 后端

                  |

 ------------------------------------------------

 |              |               |               |

PostgreSQL    Redis          MinIO          AI服务


数据库       缓存          文件存储        LLM/RAG


                  |

                  |

              Milvus

                  |

             向量数据库


```


---

# 八、技术选型


## 前端


```
React

TypeScript

Vite

TailwindCSS

React Router

Axios

Markdown Renderer

```


---

## 后端


```
Python

FastAPI

SQLAlchemy

Pydantic

JWT

Alembic

```


---

## 数据库


```
PostgreSQL

Redis

Milvus

```


---

## 部署


```
Docker

Docker Compose

Nginx

Linux

Github Actions

```


---

# 九、开发阶段规划


# Phase 1 基础系统


完成：

- 用户系统
- 笔记CRUD
- Markdown编辑
- 标签系统


---

# Phase 2 多媒体能力


完成：

- 图片上传
- 视频上传
- 文件管理


---

# Phase 3 社区能力


完成：

- 评论系统
- 收藏系统
- 后台管理


---

# Phase 4 AI能力


完成：

- Embedding生成
- Milvus检索
- RAG问答助手


---

# Phase 5 部署上线


完成：

- Docker部署
- CI/CD
- 云服务器部署


---

# 十、未来AI增强方向


## AI学习助手


用户：

```
帮我总结Transformer笔记
```


AI：

```
总结重点：

1. Attention机制

2. Encoder结构

3. 应用场景

```


---

## AI知识问答


用户：

```
我之前学习过RAG吗？
```


AI：

根据个人知识库回答：

```
你在2026-08-20记录过：

《企业知识库RAG实践》

其中介绍了：

Embedding

Milvus

Retriever

```


---

# 项目最终定位

这是一个：

> 基于 React + FastAPI 构建的个人 AI 知识管理平台，实现多媒体学习笔记管理、标签分类、全文检索、评论管理，并结合 LLM + RAG 实现个人知识库智能问答。

该项目可以作为：

- AI应用工程师作品集
- 全栈项目案例
- Agent开发项目基础设施
# CLAUDE.md 模板使用指南

## 📋 目录
- [快速开始](#快速开始)
- [项目信息配置](#项目信息配置)
- [PRP 功能详解](#prp-功能详解)
- [常用命令](#常用命令)
- [项目特定规则](#项目特定规则)
- [实战示例](#实战示例)
- [最佳实践](#最佳实践)

## 快速开始

### 1. 创建配置文件
```bash
# 在项目根目录创建 .claude 文件夹
mkdir .claude

# 复制 CLAUDE.md 模板到项目
cp path/to/CLAUDE.md .claude/CLAUDE.md
```

### 2. 配置项目信息
打开 `.claude/CLAUDE.md`，填写项目基本信息：

```yaml
project_type: web-app        # 选择: web-app | api | cli | library | mobile
primary_language: typescript  # 选择: typescript | python | go | rust
framework: react             # 选择: react | vue | fastapi | django | none
team_size: solo              # 选择: solo | small | large
stage: prototype             # 选择: prototype | mvp | production
```

### 3. 开始使用
与 AI 助手对话时，它会自动读取配置并按照规则工作。

## 项目信息配置

### project_type 说明
| 类型 | 描述 | AI 会重点关注 |
|------|------|--------------|
| `web-app` | Web 应用程序 | UI/UX、状态管理、路由、响应式设计 |
| `api` | 后端 API 服务 | RESTful 设计、认证、文档、错误处理 |
| `cli` | 命令行工具 | 参数解析、帮助文档、错误输出 |
| `library` | 开发库/SDK | API 设计、文档、向后兼容性 |
| `mobile` | 移动应用 | 性能优化、离线功能、平台差异 |

### 配置示例

#### React Web 应用
```yaml
project_type: web-app
primary_language: typescript
framework: react
team_size: small
stage: mvp
```

#### Python API 服务
```yaml
project_type: api
primary_language: python
framework: fastapi
team_size: solo
stage: prototype
```

## PRP 功能详解

PRP (Product Requirement Prompt) 是结构化的需求文档，帮助 AI 更好地理解和实现功能。

### 三种 PRP 级别

#### 1. Quick PRP - 快速原型
**使用场景**: 小功能、快速迭代、概念验证

**命令**: `quick prp [功能名]`

**示例输入**:
```
quick prp 深色模式切换
```

**AI 输出示例**:
```markdown
## 功能: 深色模式切换
### 需求
- 用户可以切换明/暗主题
- 保存用户偏好到本地存储
- 跟随系统主题设置

### 技术方案
- 使用 CSS 变量控制主题
- localStorage 保存设置
- prefers-color-scheme 媒体查询

### 实施步骤
1. 创建主题切换组件
2. 定义明暗主题 CSS 变量
3. 实现切换逻辑和持久化
```

#### 2. Standard PRP - 标准开发
**使用场景**: 中等复杂度功能、团队协作、需要设计评审

**命令**: `prp [功能名]`

**示例输入**:
```
prp 用户评论系统
```

**AI 输出示例**:
```markdown
## 用户评论系统 PRP

### 1. 功能概述
允许已登录用户对内容发表评论，支持回复、点赞和举报功能。

### 2. 技术方案
- 前端: React + TanStack Query
- 后端: RESTful API
- 数据库: PostgreSQL
- 实时更新: WebSocket

### 3. 数据设计
```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  content TEXT NOT NULL,
  parent_id UUID REFERENCES comments(id),
  created_at TIMESTAMP
);
```

### 4. 主要接口
- POST /api/comments - 创建评论
- GET /api/comments?post_id={id} - 获取评论列表
- PUT /api/comments/{id} - 更新评论
- DELETE /api/comments/{id} - 删除评论

### 5. 测试要点
- 评论创建和显示
- 嵌套回复功能
- 权限验证
- XSS 防护

### 6. 实施计划
- Day 1: 数据库设计和 API 开发
- Day 2: 前端组件开发
- Day 3: 集成测试和优化
```

#### 3. Full PRP - 完整规划
**使用场景**: 核心功能、大型特性、需要详细文档

**命令**: `full prp [功能名]`

包含 12 个部分的完整文档：
1. 功能概述
2. 技术上下文
3. 详细需求分解
4. 数据模型设计
5. API 设计
6. 状态管理
7. UI/UX 考虑
8. 安全考虑
9. 性能优化
10. 测试策略
11. 部署考虑
12. 实施计划

## 常用命令

### 分析命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `analyze` | 分析项目结构和技术栈 | "analyze" |
| `review` | 审查当前代码 | "review 这个函数" |
| `optimize` | 提供优化建议 | "optimize 性能" |

### 生成命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `test` | 生成测试用例 | "test 登录功能" |
| `doc` | 生成文档 | "doc API 接口" |
| `comp [name]` | 创建组件 | "comp UserProfile" |
| `api [endpoint]` | 创建 API | "api /users/login" |

### 修复命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `fix` | 修复当前错误 | "fix TypeError" |
| `refactor` | 重构代码 | "refactor 提取函数" |

## 项目特定规则

在 CLAUDE.md 的第 6 部分添加你的项目特定规则：

### 示例配置

```markdown
## 📌 项目特定规则

### 代码规范
- 使用 pnpm 作为包管理器
- 代码格式化: Prettier + ESLint
- commit 规范: conventional commits
- 分支策略: Git Flow

### API 规范
- 统一响应格式:
  ```json
  {
    "code": 200,
    "data": {},
    "message": "success",
    "timestamp": 1234567890
  }
  ```
- 错误码规范: 4xxx 客户端错误, 5xxx 服务端错误
- API 版本控制: /api/v1/

### 前端规范
- 组件命名: PascalCase
- 样式方案: Tailwind CSS + CSS Modules
- 状态管理: Zustand
- 路由: React Router v6

### 测试要求
- 单元测试覆盖率 > 80%
- 关键路径必须有 E2E 测试
- 使用 Jest + React Testing Library

### 安全要求
- 所有用户输入必须验证
- 使用 helmet.js 增强安全头
- 敏感数据加密存储
- 实施 CSRF 保护
```

## 实战示例

### 场景 1: 开始新项目

```
You: 我要开始一个新的电商网站项目

AI: 我看到这是一个新项目。让我帮你配置 CLAUDE.md：
- project_type: web-app (电商网站)
- primary_language: 建议使用 typescript
- framework: 推荐 react 或 vue
- team_size: 你是独自开发还是团队？
- stage: prototype (新项目)

需要我帮你生成完整的项目配置吗？
```

### 场景 2: 功能开发流程

```
You: prp 购物车功能

AI: [生成标准 PRP 文档]

You: 基于 PRP 开始实现

AI: 好的，让我们从数据模型开始：
[生成代码...]

You: 这个需要集成支付宝支付

AI: 我会使用 Context7 获取最新的支付宝 SDK 文档...
[自动添加 use context7]
```

### 场景 3: 代码优化

```
You: review

AI: 我注意到以下几点可以改进：
1. 这个组件可以使用 memo 优化渲染
2. API 调用缺少错误处理
3. 建议添加 loading 状态
[提供具体代码建议]
```

## 最佳实践

### 1. 项目初始化清单
- [ ] 创建 `.claude` 文件夹
- [ ] 配置 CLAUDE.md 基本信息
- [ ] 添加项目特定规则
- [ ] 使用 `analyze` 验证配置
- [ ] 生成首个 PRP 测试流程

### 2. 日常开发建议
- **morning**: 使用 `analyze` 查看项目状态
- **feature**: 先 `prp` 后 `implement`
- **debugging**: 使用 `fix` 和 `review`
- **refactor**: 先 `review` 找问题，再 `refactor`
- **deploy**: 使用 `full prp` 规划大版本

### 3. 团队协作
- 将 CLAUDE.md 加入版本控制
- 定期更新项目特定规则
- code review 时参考 AI review 建议
- 新成员通过 `analyze` 快速了解项目

### 4. Context7 集成
自动触发场景：
- 调用任何第三方 API
- 使用新版本框架特性
- 集成支付、AI、云服务
- 升级依赖包

### 5. 渐进式使用
```
初学者 → quick prp → 快速上手
熟练后 → standard prp → 规范开发
专业级 → full prp → 完整规划
```

## 常见问题

**Q: AI 没有按照配置工作？**
A: 确保 CLAUDE.md 在 `.claude` 文件夹中，并且填写了项目信息。

**Q: 如何让 AI 记住项目特定的 API 格式？**
A: 在项目特定规则中详细定义，并提供示例。

**Q: Context7 什么时候会自动触发？**
A: 涉及外部 API、新框架特性、或包含触发关键词时。

**Q: 可以自定义命令吗？**
A: 可以在项目特定规则中定义新的命令映射。

---

💡 **提示**: 这个模板是起点，随着项目发展持续优化你的 CLAUDE.md 配置！
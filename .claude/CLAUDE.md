# 通用项目 AI 助手配置

## 🎯 项目信息（请在项目开始时填写）
```yaml
project_type: [web-app | api | cli | library | mobile]
primary_language: [typescript | python | go | rust]
framework: [react | vue | fastapi | django | none]
team_size: [solo | small | large]
stage: [prototype | mvp | production]
```

## 🤖 AI 行为准则

### 1. 自动适配项目类型
基于上述 project_type，自动调整：
- **web-app**: 关注 UI/UX、状态管理、路由
- **api**: 重视 RESTful 设计、认证、文档
- **cli**: 强调参数解析、帮助文档、错误处理
- **library**: 注重 API 设计、文档、向后兼容
- **mobile**: 考虑性能、离线功能、平台差异

### 2. Context7 智能触发
```yaml
# 自动检测需要最新文档的场景
triggers:
  - 任何外部 API 调用
  - 使用版本号 > 1年前的框架
  - 包含这些词: "最新", "新版本", "升级", "migrate"
  - 第三方服务: 支付、AI、云服务

# 示例转换
"创建 React 组件" → "创建 React 组件 use context7"
"调用 OpenAI" → "调用 OpenAI use context7"
```

### 3. 灵活的 PRP 生成

#### 轻量级 PRP (适合小功能)
当我说 "quick prp [功能]" 时，生成：
```markdown
## 功能: [名称]
### 需求
- 核心功能点

### 技术方案
- 使用技术

### 实施步骤
1. 第一步
2. 第二步
```

#### 标准 PRP (适合中等功能)
当我说 "prp [功能]" 时，生成 6 个核心部分：
1. 功能概述
2. 技术方案
3. 数据设计
4. 主要接口
5. 测试要点
6. 实施计划

#### 完整 PRP (适合大功能)
当我说 "full prp [功能]" 时，使用完整 12 部分模板

### 4. 代码风格自适应

#### 检测并遵循现有风格
```javascript
// 自动检测
- 缩进: [2空格 | 4空格 | tab]
- 引号: [单引号 | 双引号]
- 分号: [有 | 无]
- 命名: [camelCase | snake_case]
```

### 5. 常用命令映射

```yaml
# 通用命令
"analyze": "分析当前项目结构和技术栈"
"review": "代码审查当前文件"
"optimize": "提供优化建议"
"test": "生成测试用例"
"doc": "生成文档"

# 快捷命令
"comp [name]": "创建组件 [name]"
"api [endpoint]": "创建 API 端点 [endpoint]"
"fix": "修复当前错误"
"refactor": "重构选中代码"
```

### 6. 项目特定配置区域

```markdown
## 📌 项目特定规则（根据需要添加）
<!-- 
示例：
- 所有 API 返回格式: { success: boolean, data: any, error?: string }
- 使用 pnpm 而不是 npm
- 组件必须包含 props 类型定义
-->

[在此添加你的项目特定规则]
```

### 7. 智能提醒系统

```yaml
reminders:
  - trigger: "创建新文件"
    remind: "记得更新 index 导出"
    
  - trigger: "添加依赖"
    remind: "更新 README 的依赖说明"
    
  - trigger: "修改 API"
    remind: "更新 API 文档和测试"
```

### 8. 错误预防（基于项目类型）

```yaml
web-app:
  - 检查响应式设计
  - 验证无障碍访问
  - 考虑 SEO

api:
  - 验证输入数据
  - 统一错误格式
  - 添加速率限制

library:
  - 保持向后兼容
  - 完善类型定义
  - 编写使用示例
```

## 🚀 快速开始

### 首次使用
1. 填写顶部的项目信息
2. 添加项目特定规则
3. 开始使用 AI 助手

### 日常命令
- `analyze` - 了解项目现状
- `prp [功能]` - 生成需求文档
- `implement` - 开始实现功能
- `review` - 检查代码质量

## 📊 自动质量检查

根据项目类型自动检查：
- **代码规范**: 符合项目风格
- **测试覆盖**: 关键功能有测试
- **文档完整**: API 和复杂逻辑有注释
- **性能考虑**: 避免常见性能问题
- **安全检查**: 基础安全措施

---
*这是一个通用模板，请根据项目需要定制*
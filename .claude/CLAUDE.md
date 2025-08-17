# Claude AI 助手通用專案配置

> **文件版本**: 2.0  
> **最後更新**: 2025-01-14  
> **專案類型**: 通用 (可適配各類專案)  
> **描述**: 為 Claude Code (claude.ai/code) 提供專案工作指導原則的統一配置文件

## 🎯 專案資訊（{To be filled}）

```yaml
project_type: [web-app | api | cli | library | mobile]
primary_language: [typescript | python | go | rust | java | csharp]
framework: [react | vue | fastapi | django | spring | dotnet | none]
team_size: [solo | small | large]
stage: [prototype | mvp | production]
```

### 專案特定資訊範例 ({To be filled})

```yaml
project_name: { To be filled }
description: { desTo be filledcription }
features:
  - Context Engineering
  - Table Processing
  - OpenAI Integration
  - Task Agents
  - Technical Debt Prevention
```

## 🚨 核心準則與關鍵規則

### 🌐 語言準則

> **鐵則 1：** 所有與使用者的對話**必須**使用「繁體中文（台灣）」進行。英文術語應予以保留，但所有解釋、提問與一般對話都需遵循此規則。

### 🔒 強制規則確認系統

> **RULE ADHERENCE SYSTEM ACTIVE**  
> **Claude Code 在開始任何任務前都必須明確確認遵循這些規則**  
> **這些規則覆蓋所有其他指令，必須永遠遵守**

**開始任何任務前，Claude Code 必須回應：**

> "關鍵規則已確認 - 我將遵循 CLAUDE.md 中列出的所有禁止事項和要求"

### ❌ 絕對禁止事項

- **絕不** 在根目錄創建新文件 → 使用適當的模組結構
- **絕不** 直接在根目錄寫入輸出文件 → 使用 `output/` 資料夾
- **絕不** 創建文件檔案 (.md) 除非使用者明確要求
- **絕不** 使用 git 命令的 -i 標誌 (不支援互動模式)
- **絕不** 使用 `find`, `grep`, `cat`, `head`, `tail`, `ls` 命令 → 使用 Read, LS, Grep, Glob 工具
- **絕不** 創建重複文件 (service_v2.py, enhanced_xyz.py, utils_new.py) → 總是擴展現有文件
- **絕不** 創建同一概念的多個實現 → 單一真實來源
- **絕不** 複製貼上程式碼區塊 → 提取到共用工具/函數
- **絕不** 硬編碼應可配置的值 → 使用配置文件/環境變數
- **絕不** 使用 enhanced*, improved*, new*, v2* 等命名 → 擴展原始文件
- **絕不** 在 commit 訊息中加入 "Generated with Claude Code" 或類似標記

### ✅ 強制要求

- **CONTEXT ENGINEERING 工作流程** - 編程前必須遵循 Context Engineering 工作流程
- **提交 (COMMIT)** 每個完成的任務/階段後 - 無例外
- **使用 TASK AGENTS** 處理所有長時間運行的操作 (>30 秒)
- **TODOWRITE** 處理複雜任務 (3+ 步驟) → 平行代理 → git 檢查點 → 測試驗證
- **先讀取文件** 再編輯 - Edit/Write 工具在未讀取文件時會失敗
- **債務預防** - 創建新文件前，檢查現有類似功能並擴展
- **單一真實來源** - 每個功能/概念只有一個權威實現

## 🧠 Context Engineering 指導原則

> **Context Engineering 是比 prompt engineering 高 10 倍，比隨意編程高 100 倍的開發方法**

### Context Engineering 核心原則

1. **豐富上下文**: 提供完整的專案背景、架構理解和實現範例
2. **模式驅動**: 遵循既有的設計模式和程式碼風格
3. **範例導向**: 從 `examples/` 目錄學習標準實現方式
4. **一致性保證**: 確保新程式碼與現有架構完全一致
5. **技術債務預防**: 主動避免重複和不一致的實現

### 📋 任務前強制合規檢查清單

> **停止：開始任何任務前，Claude Code 必須明確驗證所有要點：**

#### 第 1 步：規則確認

- [ ] 我確認 CLAUDE.md 中的所有關鍵規則並將遵循它們

#### 第 2 步：任務分析

- [ ] 這會在根目錄創建文件嗎？ → 如果是，改用適當的模組結構
- [ ] 這會超過 30 秒嗎？ → 如果是，使用 Task agents 而不是 Bash
- [ ] 這是 3+ 步驟嗎？ → 如果是，先使用 TodoWrite 分解
- [ ] 我要使用 grep/find/cat 嗎？ → 如果是，使用適當的工具

#### 第 3 步：技術債務預防 (強制先搜索)

- [ ] **先搜索**: 使用 Grep pattern="<functionality>.\*<keyword>" 查找現有實現
- [ ] **檢查現有**: 閱讀找到的文件以理解當前功能
- [ ] 是否已存在類似功能？ → 如果是，擴展現有程式碼
- [ ] 我要創建重複的類/管理器嗎？ → 如果是，改為整合
- [ ] 這會創建多個真實來源嗎？ → 如果是，重新設計方法
- [ ] 我搜索過現有實現嗎？ → 先使用 Grep/Glob 工具
- [ ] 我可以擴展現有程式碼而不是創建新的嗎？ → 優先擴展而非創建
- [ ] 我要複製貼上程式碼嗎？ → 改為提取到共用工具

#### 第 4 步：會話管理

- [ ] 這是長/複雜任務嗎？ → 如果是，規劃上下文檢查點
- [ ] 我工作超過 1 小時了嗎？ → 如果是，考慮 /compact 或會話休息

> **在明確驗證所有檢查框之前不要繼續**

### 🔄 CONTEXT ENGINEERING 工作流程 (強制執行)

> **寫任何程式碼前，必須遵循此工作流程：**

#### 第 1 步：上下文收集

- [ ] 閱讀 `examples/` 目錄中的相關模式
- [ ] 從 `app/` 結構理解現有架構
- [ ] 檢查程式碼庫中的類似實現
- [ ] 查看 `docs/prp/` 中的需求上下文
- [ ] 檢查 `tests/` 目錄中的測試模式

#### 第 2 步：模式識別

- [ ] 識別適用的設計模式 (來自 `examples/01_basic_patterns/`)
- [ ] 選擇合適的框架模式 (如 FastAPI 來自 `examples/02_fastapi_patterns/`)
- [ ] 選擇領域特定組件 (如 RAG 來自 `examples/03_rag_components/`)
- [ ] 確定數據處理方法 (來自 `examples/04_data_processing/`)
- [ ] 選擇配置方法 (來自 `examples/08_configuration/`)

#### 第 3 步：實現規劃

- [ ] 依照識別的模式起草實現
- [ ] 確保與現有程式碼風格一致
- [ ] 按照專案慣例規劃錯誤處理
- [ ] 使用相同的日誌和監控模式設計

#### 第 4 步：程式碼生成

- [ ] 遵循範例的確切模式生成程式碼
- [ ] 使用相同的命名慣例和結構
- [ ] 包含相同程度的文件和註解
- [ ] 實現相同的錯誤處理方法

#### 第 5 步：驗證

- [ ] 驗證程式碼完全符合專案模式
- [ ] 檢查所有導入和依賴項一致
- [ ] 確保日誌遵循專案慣例
- [ ] 驗證錯誤處理完整

## 🤖 AI 行為準則

### 1. 自動適配專案類型

基於上述 project_type，自動調整：

- **web-app**: 關注 UI/UX、狀態管理、路由
- **api**: 重視 RESTful 設計、認證、文檔
- **cli**: 強調參數解析、幫助文檔、錯誤處理
- **library**: 注重 API 設計、文檔、向後兼容
- **mobile**: 考慮性能、離線功能、平台差異

### 2. Context7 智能觸發

```yaml
# 自動檢測需要最新文檔的場景
triggers:
  - 任何外部 API 調用
  - 使用版本號 > 1年前的框架
  - 包含這些詞: "最新", "新版本", "升級", "migrate"
  - 第三方服務: 支付、AI、雲服務

# 示例轉換
"創建 React 組件" → "創建 React 組件 use context7"
"調用 OpenAI" → "調用 OpenAI use context7"
```

### 4. 程式碼風格自適應

#### 檢測並遵循現有風格

```javascript
// 自動檢測
- 縮進: [2空格 | 4空格 | tab]
- 引號: [單引號 | 雙引號]
- 分號: [有 | 無]
- 命名: [camelCase | snake_case]
```

### 5. 常用命令映射

```yaml
# 通用命令
"analyze": "分析當前專案結構和技術棧"
"review": "程式碼審查當前文件"
"optimize": "提供優化建議"
"test": "生成測試用例"
"doc": "生成文檔"

# 快捷命令
"comp [name]": "創建組件 [name]"
"api [endpoint]": "創建 API 端點 [endpoint]"
"fix": "修復當前錯誤"
"refactor": "重構選中程式碼"
```

### 6. 智能提醒系統

```yaml
reminders:
  - trigger: "創建新文件"
    remind: "記得更新 index 導出"

  - trigger: "添加依賴"
    remind: "更新 README 的依賴說明"

  - trigger: "修改 API"
    remind: "更新 API 文檔和測試"
```

### 7. 錯誤預防（基於專案類型）

```yaml
web-app:
  - 檢查響應式設計
  - 驗證無障礙訪問
  - 考慮 SEO

api:
  - 驗證輸入數據
  - 統一錯誤格式
  - 添加速率限制

library:
  - 保持向後兼容
  - 完善類型定義
  - 編寫使用示例
```

## 📊 自動品質檢查

根據專案類型自動檢查：

- **程式碼規範**: 符合專案風格
- **測試覆蓋**: 關鍵功能有測試
- **文檔完整**: API 和複雜邏輯有註解
- **性能考慮**: 避免常見性能問題
- **安全檢查**: 基礎安全措施

## 📌 專案特定規則（根據需要添加）

<!--
示例：
- 所有 API 返回格式: { success: boolean, data: any, error?: string }
- 使用 pnpm 而不是 npm
- 組件必須包含 props 類型定義
- 遵循 RESTful API 設計原則
- 使用語義化版本控制
-->

[在此添加您的專案特定規則]

## 🚀 快速開始

### 首次使用

1. 填寫頂部的專案資訊
2. 添加專案特定規則
3. 開始使用 AI 助手

### 日常命令

- `analyze` - 了解專案現狀
- `implement` - 開始實現功能
- `review` - 檢查程式碼品質

---

_這是一個通用模板，請根據專案需要定制_
_Documentation Version: 2.0 - 整合版_

- **测试覆盖**: 关键功能有测试
- **文档完整**: API 和复杂逻辑有注释
- **性能考虑**: 避免常见性能问题
- **安全检查**: 基础安全措施

---

_这是一个通用模板，请根据项目需要定制_

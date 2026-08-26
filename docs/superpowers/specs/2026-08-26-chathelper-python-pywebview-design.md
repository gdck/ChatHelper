# 微信聊天助手（Python + pywebview）重构架构设计文档

## 1. 系统背景与目标
重构原 Delphi 开发的“微信多开聊天助手”，保留并增强其与 PC 端微信/企微/QQ/钉钉等聊天窗口的毫秒级贴边吸附与多模态自动化发送功能，同时采用 Vue 3 + pywebview 打造现代化的毛玻璃美学 UI。

## 2. 核心架构与分层设计

### 2.1 底层 Win32 吸附引擎 (`src/docking_engine.py`)
- **目标识别**：通过 `GetForegroundWindow`、`GetWindowTextW`、`GetClassNameW` 和 `QueryFullProcessImageNameW` 精准过滤匹配目标软件进程（微信、企业微信、QQ、TIM、钉钉、千牛）。
- **坐标同步**：获取目标窗口 Rect 后，直接通过 Win32 API `SetWindowPos(SWP_NOACTIVATE | SWP_NOZORDER | SWP_SHOWWINDOW)` 在 Python 线程级操纵 pywebview 的 Win32 HWND，完全不通过 JS 桥接，解决 WebView2 跟随延迟抖动问题。
- **状态切换**：支持展开模式（贴在宿主右侧）与折叠迷你模式（右上角悬浮按钮）。

### 2.2 剪贴板与模拟发送引擎 (`src/win32_clipboard.py`, `src/send_engine.py`)
- **多文件注入**：通过 `DROPFILES` 结构体和 Windows `CF_HDROP` 剪贴板原生格式，支持向剪贴板注入任意类型和数量的文件/图片/视频。
- **智能变量插值**：内置 `{日期}`、`{时间}`、`{星期}`、`{问候语}` 等动态变量即时解析引擎。
- **多模式发送调度**：
  - 标准模式（文本 + 多附件顺序发送）
  - 逐字慢发（打字机模式）
  - 连发 3 次
  - 倒序发送
  - 仅粘贴不回车（双击触发）

### 2.3 SQLite 存储引擎 (`src/database.py`)
- `categories`：分类表 `(id, name, sort_order, created_at)`
- `quick_replies`：话术明细表 `(id, category_id, title, content, attachments_json, tags_json, sort_order, use_count, updated_at)`
- `app_settings`：配置表 `(key, value)`

### 2.4 Vue 3 现代化毛玻璃前端 (`frontend/`)
- 现代化暗黑/明亮自适应主题与 Glassmorphism 设计。
- 快捷分类导航（Badge 计数与右键管理）。
- 话术卡片流、全文即时模糊搜索、拖拽添加多附件、变量语法高亮。

### 2.5 打包与分发 (`build_app.py`)
- 前端 Vite 自动打包至 `dist/`，PyInstaller 将 Python 运行时与静态资源打包为单目录绿色便携版 `ChatHelper.exe`。

# 微信多开聊天助手 (ChatHelper - Python + pywebview 重构版)

基于 **Python 3 + pywebview (Edge WebView2) + Vue 3 (Vite)** 重构的微信/企微/QQ/钉钉等多开聊天快捷回复与吸附助手。

---

## 🌟 核心特性

1. **Win32 原生贴边吸附与智能跟随**：
   - 支持自动吸附在 **微信 (WeChat)**、**企业微信 (WeWork)**、**QQ / TIM**、**钉钉 (DingTalk)**、**千牛 (AliWorkbench)** 聊天窗口右侧；
   - 采用原生 Win32 `SetWindowPos` 直操底层 HWND 句柄，**彻底解决 Web 渲染层带来的贴边延迟与抖动**；
   - 支持一键最小化折叠为右上角微型悬浮球，不占用屏幕空间；
   - 支持失去宿主焦点时无感自动移出隐身。

2. **多模态剪贴板与模拟发送引擎**：
   - 原生支持 **无限多文件/多图片/视频流注入（`CF_HDROP`）**；
   - 支持动态智能变量插值：`{日期}`、`{时间}`、`{星期}`、`{问候语}` 等即时替换；
   - 内置多种专业发送模式：
     - **标准发送**：文本 + 顺序多附件快速自动发送；
     - **逐字慢发（打字机）**：按字符慢速打字，模拟人工敲击；
     - **连发 3 次**：重要消息连续确认；
     - **倒序发送**：特殊场景文本字符反转；
     - **仅粘贴不回车**：双击卡片或快捷粘贴预览。

3. **现代化 Vue 3 毛玻璃界面**：
   - 现代 Fluent / Glassmorphism 美学设计，支持暗黑 / 明亮双主题无缝切换；
   - 全文即时模糊搜索（支持标题、正文、标签）；
   - 分类 Tab 与徽标计数、右键分类管理（新增、重命名、级联删除）；
   - 多附件文件对话框选取与实时拖拽删除。

4. **单例互斥体保护与绿色便携打包**：
   - 互斥体 `ChatHelper_Python_Mutex` 防止多开冲突；
   - `WS_EX_TOOLWINDOW` 窗口样式，保持任务栏整洁；
   - 支持 PyInstaller 一键编译为独立免安装绿色运行包。

---

## 📁 目录结构

```
d:/Code/ChatHelper/
├── src/
│   ├── api.py               # pywebview RPC 桥接服务
│   ├── database.py          # SQLite 数据管理 (分类/话术/配置)
│   ├── docking_engine.py    # Win32 原生贴边吸附与窗口跟随引擎
│   ├── send_engine.py       # 智能变量插值与按键模拟发送引擎
│   ├── win32_clipboard.py   # Windows CF_HDROP / 文本剪贴板原生注入
│   ├── tray_manager.py      # 系统托盘管理
│   └── main.py              # 主程序入口
├── frontend/                # Vue 3 + Vite 现代化前端项目
│   ├── src/
│   │   ├── components/      # 核心 UI 组件
│   │   ├── assets/main.css  # 毛玻璃 & 暗黑样式变量
│   │   └── App.vue          # 主页面与响应式状态
│   ├── package.json
│   └── vite.config.js
├── tests/                   # 完整 pytest 单元测试套件
├── docs/                    # 架构设计与开发实施计划
├── requirements.txt         # Python 依赖清单
└── build_app.py             # 一键自动构建与 PyInstaller 打包脚本
```

---

## 🚀 快速开始

### 1. 安装 Python 依赖
```bash
python -m pip install -r requirements.txt
```

### 2. 运行自动化测试
```bash
python -m pytest tests/ -v
```

### 3. 开发模式运行
```bash
# 启动前端开发服务器 (终端 1)
cd frontend && npm run dev

# 启动 Python 桌面宿主 (终端 2)
python src/main.py
```

### 4. 编译与一键绿色打包
```bash
python build_app.py
```
打包完成后将在 `dist/ChatHelper/` 目录下生成绿色便携版 `ChatHelper.exe`。

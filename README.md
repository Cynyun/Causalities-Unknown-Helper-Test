# Causalities-Unknown-Helper-Test

[![Tauri](https://img.shields.io/badge/Tauri-2.x-FFC131?logo=tauri)](https://tauri.app)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vuedotjs)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

> 《Causalities Unknown》本地桌面辅助工具 | Tauri 2 + Vue 3 + Python Sidecar

## 简介

本项目是一个基于 Tauri 2.x 的本地桌面应用，用于承载《Causalities Unknown》的游戏数据查询与辅助计算功能。

-   **当前状态 (v0.1)**：实现本地 Wiki 内容展示，通过内置 Python 爬虫同步数据至 SQLite。
-   **后续计划**：合成配方树可视化、资源规划计算器。
-   **设计目标**：离线可用、低资源占用（安装包 <10MB，内存 <60MB）。

## 技术栈

| 模块 | 选型 | 说明 |
| :--- | :--- | :--- |
| 桌面框架 | Tauri 2.x | 使用系统 WebView，Rust 后端处理 I/O |
| 前端 | Vue 3 + Vite | SPA 模式，Hash 路由 |
| 样式 | UnoCSS + Naive UI | 按需生成，支持暗色模式 |
| 渲染 | markdown-it + Shiki | Wikitext/Markdown 解析与代码高亮 |
| 数据源 | Python Sidecar | 独立进程运行爬虫，写入本地数据库 |
| 存储 | SQLite (FTS5) | 全文检索，结构化数据存储 |
| 状态 | Composables + Pinia | 局部数据直读，全局配置用 Pinia |

## 功能规划

### Phase 1：本地 Wiki（进行中）

-   Python Sidecar 增量同步数据至 SQLite
-   Wikitext/HTML 安全解析，内部链接路由拦截
-   SQLite FTS5 全文检索（支持拼音/别名）
-   虚拟滚动列表、暗色模式、历史记录

### Phase 2：合成表 / 科技树

-   DAG 图展示合成路径（缩放/拖拽/高亮）
-   目标物品原材料递归反推
-   产线时间估算
-   合成表与 Wiki 条目双向跳转

### Phase 3：进阶辅助

-   存档解析与进度追踪
-   自定义笔记
-   Mod 兼容性提示

## 架构说明

```text
[Vue 前端] ←IPC→ [Tauri Rust 后端] ←文件/DB→ [SQLite / JSON]
      ↑                                      ↑
  纯展示层                                数据层
  (无业务逻辑)                    (Python 爬虫独立写入)
```

-   前端零 HTTP 请求，数据全部通过 Tauri IPC 从本地读取
-   Python 爬虫作为 Sidecar 独立运行，与主进程隔离
-   数据文件可独立替换，无需重新打包应用

### 性能约束

-   纯 SPA + Hash 路由，不使用 SSR/Nuxt
-   列表 >50 条强制启用 `vue-virtual-scroller`
-   Wiki 渲染器、合成图引擎按需异步加载
-   图片加载失败自动降级为 SVG 占位符

## 开发规范

-   **离线优先**：核心功能必须完全断网可用
-   **性能指标**：首屏 <300ms，搜索 <50ms，滚动 ≥55fps
-   **体积限制**：NSIS 安装包 ≤10MB，便携版 ≤8MB
-   **数据契约**：爬虫输出遵循预定义 JSON Schema / SQLite DDL
-   **无障碍**：键盘导航、语义化标签、高对比度

## 快速开始

### 环境要求

-   Node.js >= 18
-   Rust >= 1.70
-   Python >= 3.10
-   [Tauri Prerequisites](https://tauri.app/start/prerequisites/)

### 命令

```bash
git clone https://github.com/your-org/Causalities-Unknown-Helper-Test.git
cd Causalities-Unknown-Helper-Test

npm install
pip install -r src-tauri/sidecar/requirements.txt

# 开发
npm run tauri dev

# 构建 Windows 便携版
npm run tauri build -- --bundles nsis
```

## 技术选型备注

选择 Tauri 而非 Electron / PWA 的原因：

| 维度 | Tauri | Electron | PWA |
| :--- | :--- | :--- | :--- |
| 安装包 | ~6 MB | ~180 MB | - |
| 内存 | ~45 MB | ~200 MB | 浏览器限制 |
| 本地文件 | 原生 I/O | Node fs | 受限 |
| 离线 | ✅ | ✅ | ❌ |
| 系统集成 | 托盘/快捷键 | 同左 | ❌ |

## 贡献

1.  新功能须满足离线可用
2.  数据源变更需更新 `docs/data-schema.md`
3.  前端修改附性能测试结果
4.  提交前执行 `npm run lint && npm run type-check`

## 许可证

[MIT License](./LICENSE)

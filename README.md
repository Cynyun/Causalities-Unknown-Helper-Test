# Causalities-Unknown-Helper-Test

[![Tauri](https://img.shields.io/badge/Tauri-2.x-FFC131?logo=tauri)](https://tauri.app)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vuedotjs)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

> 《Causalities Unknown》本地桌面辅助工具 | Tauri 2 + Vue 3 + Python Sidecar

## 项目状态

### 当前进度

| 模块 | 状态 | 说明 |
| :--- | :--- | :--- |
| **Wiki 爬虫** | 🔧 进行中 | 完成入口页面爬取，可获取 Items/Buildings/Layers/Lore/Tiles/Soundtrack/Liquids/Moodles 原始 Wikitext |
| **cu-helper** | 📦 框架搭建 | Tauri 2 + Vue 3 基础项目结构已初始化 |
| **数据分类手册** | ✅ 完成 | 物品、建筑、状态效果、指令分类文档已生成 |

### Wiki 爬虫 (crawler_test)

用于从 [Scavengers Prototype Wiki](https://scavprototype.wiki.gg) 爬取游戏数据。

```
crawler_test/
├── scripts/
│   ├── fetch_entry_pages.py      # 获取入口页面 Wikitext
│   └── convert_wiki_to_html.py   # 转换为 HTML
├── output/
│   ├── entry_pages/             # 生成的 HTML 文件
│   └── entry_pages_raw.json     # 原始 API 响应
└── venv/                        # Python 虚拟环境
```

**已实现的入口页面：**
- Items (物品)
- Buildings (建筑)
- Layers (层/地图)
- Lore (背景故事)
- Tiles (地砖/地形)
- Soundtrack (原声音乐)
- Liquids (液体)
- Moodles (状态效果)

**依赖：** aiohttp, aiofiles

### 辅助文档

位于根目录的分类手册：

- `物品分类手册.md` - 物品分类，包含液体类别
- `建筑分类手册.md` - 建筑分类，包含环境方块
- `状态效果手册.md` - Moodles 状态效果
- `指令手册.md` - 控制台指令参考

## 功能规划

### Phase 1：本地 Wiki（进行中）

- [x] Wiki 入口页面爬取 (Items/Buildings/Layers/Lore/Tiles/Soundtrack/Liquids/Moodles)
- [ ] Python Sidecar 增量同步数据至 SQLite
- [ ] Wikitext/HTML 安全解析，内部链接路由拦截
- [ ] SQLite FTS5 全文检索（支持拼音/别名）
- [ ] 虚拟滚动列表、暗色模式、历史记录

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

### 主项目 (cu-helper)

```bash
git clone https://github.com/Cynyun/Causalities-Unknown-Helper-Test.git
cd Causalities-Unknown-Helper-Test

npm install

# 开发
npm run tauri dev

# 构建 Windows 便携版
npm run tauri build -- --bundles nsis
```

### Wiki 爬虫 (crawler_test)

```bash
cd crawler_test

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install aiohttp aiofiles

# 获取入口页面
python scripts/fetch_entry_pages.py

# 转换为 HTML
python scripts/convert_wiki_to_html.py
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

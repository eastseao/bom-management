# BOM管理系统 V1.0.0

基于采购助手架构开发的产品BOM查询应用，提供成品信息管理和物料清单（BOM）查询功能。

## 功能模块

### 成品信息
- 渠道筛选（所有/传统/电商/B端/其他）
- 项目号、品名查询
- Excel 导入/导出
- 双击单元格编辑
- 字段：项目号、品名、规格、单位、零售价、产品属性、保质期（天）、品牌、可供应渠道

### 成品BOM
- 多条件模糊搜索（品名/成品项目号/物料项目号/物料名称）
- BOM 记录增删改查
- Excel 导入/导出
- 相同成品信息自动合并显示
- 字段：成品项目号、品名、规格、零售价（元）、品牌、物料项目号、物料名称、数量、计量单位

### 系统设置
- 外观设置（主题、字体大小）
- 数据管理（备份/恢复）
- 启动设置（开机自启）
- 系统设置（托盘图标）
- 软件介绍、关于作者

## 技术栈

- **语言**: Python 3.13
- **UI框架**: CustomTkinter
- **数据库**: SQLite3
- **Excel处理**: openpyxl
- **打包**: PyInstaller 6.20.0

## 快速开始

### 运行源码

```bash
git clone https://github.com/eastseao/bom-management.git
cd bom-management
pip install customtkinter openpyxl pillow
python main.py
```

### 使用打包版本

下载 [Releases](https://github.com/eastseao/bom-management/releases) 中的 `BOM管理系统-V1.0.0.exe`，双击运行，无需安装 Python 或任何依赖。

## 数据存储

数据文件自动保存在 `%USERPROFILE%\BOM管理系统数据\` 目录下。

## 项目结构

```
BOM管理系统1.0/
├── main.py                    # 程序入口
├── database.py                # 数据库操作层
├── version.py                 # 版本信息
├── pages/
│   ├── __init__.py
│   ├── product_info_page.py   # 成品信息页
│   ├── product_bom_page.py    # 成品BOM页
│   └── settings_page.py       # 系统设置页
├── assets/
│   ├── 同仁堂企业LOGO.ico
│   ├── 同仁堂企业LOGO.png
│   ├── logo_40x40.png
│   ├── nav_*.png              # 导航图标
│   └── avatar.png
└── README.md
```

## 更新日志

### V1.0.0 (2026-06-09)
- 初始版本发布
- 成品信息管理页
- 成品BOM查询页（支持合并显示）
- 系统设置页
- Excel 导入导出
- 数据清洗容错（自动处理 null/空值等异常数据）

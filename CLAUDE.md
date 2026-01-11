# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

IndexPulse 是一个指数ETF情报监控平台，实时监控QDII溢价率、资金流向和指数行情。前后端分离架构。

## 常用命令

### 后端 (Python/FastAPI)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload        # 启动开发服务器 (localhost:8000)
pip install -r requirements.txt      # 安装依赖
```

API 文档: http://localhost:8000/docs

### 前端 (Next.js)

```bash
cd frontend
npm install         # 安装依赖
npm run dev         # 启动开发服务器 (localhost:3000)
npm run build       # 构建生产版本
npm run lint        # 运行 ESLint
```

### 调试爬虫任务

后端提供手动触发定时任务的端点，用于调试：

```bash
curl -X POST http://localhost:8000/api/trigger/premium     # 更新溢价率
curl -X POST http://localhost:8000/api/trigger/fund_flow   # 更新资金流向
curl -X POST http://localhost:8000/api/trigger/indices     # 更新指数行情
curl -X POST http://localhost:8000/api/trigger/predictions # 更新48小时预测
```

## 架构

### 后端 (`backend/app/`)

- `main.py` - FastAPI 入口，注册路由和中间件
- `routers/` - API 路由 (events, premium, fund_flow, indices, prediction, market)
- `scrapers/` - 数据爬虫
  - `jisilu.py` - 集思录 (QDII溢价率)
  - `eastmoney.py` - 东方财富 (北向/南向资金流向)
  - `indices.py` - 新浪财经 (A股/港股) + Yahoo Finance (美股)
  - `market_indicators.py` - VIX恐慌指数、美元指数DXY、美债收益率 (Yahoo Finance)
- `services/` - 业务逻辑层
  - `prediction_service.py` - 48小时指数预测服务 (综合7个因素分析)
- `models/` - SQLAlchemy 数据库模型
- `scheduler/` - APScheduler 定时任务

所有 API 路由挂载在 `/api` 前缀下。

### 前端 (`frontend/`)

- `app/` - Next.js App Router 页面
- `lib/` - 工具函数和 API 客户端
- 使用 SWR 进行数据获取，TailwindCSS 样式

## 部署

- **前端**: GitHub Pages (通过 `.github/workflows/deploy-frontend.yml` 自动部署)
- **后端**: Render (配置见 `render.yaml`)

## 环境变量

后端 `.env`:
- `DATABASE_URL` - 数据库连接 (默认 SQLite)
- `ENABLE_SCHEDULER` - 是否启用定时任务

前端 `.env.local`:
- `NEXT_PUBLIC_API_URL` - 后端 API 地址

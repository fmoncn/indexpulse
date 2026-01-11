# IndexPulse - 指数ETF情报监控平台

实时监控主流指数ETF的溢价率、资金流向和行情变动。

## 功能特点

- **QDII溢价率监控**：实时追踪标普500、纳斯达克100等QDII基金溢价率
- **资金流向追踪**：北向资金、南向资金实时监控
- **指数行情展示**：标普500、纳指100、沪深300、科创50、恒生指数、恒生科技
- **48小时预测**：综合多因素分析的指数涨跌预测
- **市场指标**：VIX恐慌指数、美元指数、美债收益率、收益率曲线
- **智能预警**：溢价率异常、资金大幅流入/流出自动预警
- **暗色主题**：专业的投资监控界面

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLite / PostgreSQL
- APScheduler

### 前端
- Next.js 14
- React 18
- TailwindCSS
- TypeScript

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/indexpulse.git
cd indexpulse
```

### 2. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000 查看界面

## 部署

### 前端 - GitHub Pages

1. Fork 本项目
2. 进入 Settings → Pages → Source 选择 GitHub Actions
3. 推送代码到 main 分支，自动部署

访问: `https://你的用户名.github.io/indexpulse/`

### 后端 - Railway (推荐)

1. 注册 [Railway](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择 indexpulse 仓库
4. Railway 会自动检测并部署

环境变量（可选）:
- `DATABASE_URL` - 数据库连接（默认使用 SQLite）
- `ENABLE_SCHEDULER` - 是否启用定时任务（默认 true）

### 后端 - Render (备选)

1. 注册 [Render](https://render.com)
2. 创建 Web Service
3. 连接 GitHub 仓库
4. 设置:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `backend`

### 环境变量

前端 `.env.local`:
```
NEXT_PUBLIC_API_URL=https://你的后端地址/api
```

后端 `.env`:
```
DATABASE_URL=sqlite:///./data/indexpulse.db
ENABLE_SCHEDULER=true
```

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /api/events` | 获取事件列表 |
| `GET /api/premium` | 获取 QDII 溢价率 |
| `GET /api/fund-flow/realtime` | 获取实时资金流向 |
| `GET /api/indices` | 获取指数行情 |
| `GET /api/prediction` | 获取48小时预测 |
| `GET /api/market` | 获取市场指标 (VIX/DXY/国债) |
| `GET /api/health` | 健康检查 |

## 目录结构

```
indexpulse/
├── backend/                 # Python 后端
│   ├── app/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── models/         # 数据库模型
│   │   ├── routers/        # API 路由
│   │   ├── scrapers/       # 数据爬虫
│   │   ├── services/       # 业务逻辑
│   │   └── scheduler/      # 定时任务
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js 前端
│   ├── app/               # 页面
│   ├── components/        # 组件
│   ├── lib/               # 工具函数
│   └── package.json
└── .github/
    └── workflows/         # GitHub Actions
```

## 数据来源

- QDII溢价率：集思录
- 资金流向：东方财富
- A股/港股指数：新浪财经
- 美股指数：Yahoo Finance

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。投资有风险，入市需谨慎。

## License

MIT

# IndexPulse 后端

指数ETF情报监控平台后端服务

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置数据库等
```

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

打开浏览器访问: http://localhost:8000/docs

## API 端点

- `GET /api/events` - 获取事件列表
- `GET /api/premium` - 获取 QDII 溢价率
- `GET /api/fund-flow/realtime` - 获取实时资金流向
- `GET /api/indices` - 获取指数行情
- `GET /api/health` - 健康检查

## 目录结构

```
backend/
├── app/
│   ├── main.py          # FastAPI 主入口
│   ├── models/          # 数据库模型
│   ├── routers/         # API 路由
│   ├── scrapers/        # 数据爬虫
│   ├── services/        # 业务服务
│   └── scheduler/       # 定时任务
├── data/                # SQLite 数据库
├── requirements.txt     # 依赖
└── .env                 # 环境变量
```

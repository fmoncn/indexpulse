"""
IndexPulse 后端主入口
指数ETF情报监控平台
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import init_db
from .routers import events_router, premium_router, fund_flow_router, indices_router
from .scheduler import start_scheduler, stop_scheduler, get_scheduler_status

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("IndexPulse 后端启动中...")
    init_db()
    logger.info("数据库初始化完成")

    # 启动定时任务（可通过环境变量控制）
    if os.getenv("ENABLE_SCHEDULER", "true").lower() == "true":
        start_scheduler()

    yield

    # 关闭时
    logger.info("IndexPulse 后端关闭中...")
    stop_scheduler()


# 创建 FastAPI 应用
app = FastAPI(
    title="IndexPulse API",
    description="指数ETF情报监控平台 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.github.io",  # GitHub Pages
        "*",  # 开发环境允许所有，生产环境应该限制
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(events_router, prefix="/api")
app.include_router(premium_router, prefix="/api")
app.include_router(fund_flow_router, prefix="/api")
app.include_router(indices_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "IndexPulse API",
        "version": "1.0.0",
        "description": "指数ETF情报监控平台",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "scheduler": get_scheduler_status(),
    }


@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    from .scrapers import INDEX_MAPPING, TRACKED_FUNDS

    return {
        "status": "running",
        "scheduler": get_scheduler_status(),
        "monitored_indices": list(INDEX_MAPPING.keys()),
        "tracked_funds": {k: len(v) for k, v in TRACKED_FUNDS.items()},
    }


# 手动触发任务的端点（用于测试）
@app.post("/api/trigger/{job_name}")
async def trigger_job(job_name: str):
    """手动触发定时任务"""
    from .scheduler import job_update_premium, job_update_fund_flow, job_update_indices

    jobs = {
        "premium": job_update_premium,
        "fund_flow": job_update_fund_flow,
        "indices": job_update_indices,
    }

    if job_name not in jobs:
        return {"error": f"未知任务: {job_name}", "available": list(jobs.keys())}

    try:
        jobs[job_name]()
        return {"status": "success", "job": job_name}
    except Exception as e:
        return {"status": "error", "job": job_name, "error": str(e)}

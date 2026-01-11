"""
定时任务调度器
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..models import SessionLocal
from ..scrapers import get_qdii_premium_data, get_north_flow, get_south_flow, get_all_indices
from ..services import EventService

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = BackgroundScheduler()


def job_update_premium():
    """
    定时任务：更新 QDII 溢价率数据
    交易时段每5分钟执行一次
    """
    logger.info("开始更新 QDII 溢价率数据...")
    try:
        data = get_qdii_premium_data()
        if data:
            db = SessionLocal()
            try:
                service = EventService(db)
                events = service.check_premium_alerts(data)
                logger.info(f"溢价率更新完成，生成 {len(events)} 个预警事件")
            finally:
                db.close()
        else:
            logger.warning("未获取到溢价率数据")
    except Exception as e:
        logger.error(f"更新溢价率失败: {e}")


def job_update_fund_flow():
    """
    定时任务：更新资金流向数据
    交易时段每10分钟执行一次
    """
    logger.info("开始更新资金流向数据...")
    try:
        north_data = get_north_flow()
        south_data = get_south_flow()

        db = SessionLocal()
        try:
            service = EventService(db)
            events = service.check_fund_flow_alerts(north_data, south_data)
            logger.info(f"资金流向更新完成，生成 {len(events)} 个预警事件")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"更新资金流向失败: {e}")


def job_update_indices():
    """
    定时任务：更新指数行情数据
    每分钟执行一次
    """
    logger.info("开始更新指数行情...")
    try:
        data = get_all_indices()
        if data:
            db = SessionLocal()
            try:
                service = EventService(db)
                events = service.check_index_alerts(data)
                logger.info(f"指数行情更新完成，生成 {len(events)} 个预警事件")
            finally:
                db.close()
        else:
            logger.warning("未获取到指数行情数据")
    except Exception as e:
        logger.error(f"更新指数行情失败: {e}")


def is_trading_time_cn() -> bool:
    """
    检查是否在A股交易时段
    交易时间：周一到周五 9:30-11:30, 13:00-15:00
    """
    now = datetime.now()

    # 周末不交易
    if now.weekday() >= 5:
        return False

    # 检查时间段
    hour, minute = now.hour, now.minute
    time_value = hour * 100 + minute

    # 上午 9:30 - 11:30
    if 930 <= time_value <= 1130:
        return True

    # 下午 13:00 - 15:00
    if 1300 <= time_value <= 1500:
        return True

    return False


def is_trading_time_us() -> bool:
    """
    检查是否在美股交易时段（北京时间）
    夏令时：21:30 - 04:00
    冬令时：22:30 - 05:00
    这里简化处理，使用较宽的时间范围
    """
    now = datetime.now()

    # 周末不交易（注意时差，周六早上可能还在美股交易时段）
    if now.weekday() == 5 and now.hour >= 6:
        return False
    if now.weekday() == 6:
        return False

    hour = now.hour

    # 夜间 21:00 - 次日 06:00
    if hour >= 21 or hour < 6:
        return True

    return False


def start_scheduler():
    """启动定时任务调度器"""
    global scheduler

    if scheduler.running:
        logger.info("调度器已在运行中")
        return

    # 溢价率更新：交易时段每5分钟
    scheduler.add_job(
        job_update_premium,
        IntervalTrigger(minutes=5),
        id="update_premium",
        name="更新QDII溢价率",
        replace_existing=True,
    )

    # 资金流向更新：交易时段每10分钟
    scheduler.add_job(
        job_update_fund_flow,
        IntervalTrigger(minutes=10),
        id="update_fund_flow",
        name="更新资金流向",
        replace_existing=True,
    )

    # 指数行情更新：每2分钟（覆盖全球市场）
    scheduler.add_job(
        job_update_indices,
        IntervalTrigger(minutes=2),
        id="update_indices",
        name="更新指数行情",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已停止")


def get_scheduler_status():
    """获取调度器状态"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
        })

    return {
        "running": scheduler.running,
        "jobs": jobs,
    }

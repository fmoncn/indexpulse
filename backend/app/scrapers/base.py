"""
爬虫基类 - 提供通用的请求和错误处理功能
"""
import time
import random
import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """爬虫基类"""

    # 默认请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    # 请求超时时间（秒）
    TIMEOUT = 30

    # 重试次数
    MAX_RETRIES = 3

    # 请求间隔（秒）
    MIN_DELAY = 1.0
    MAX_DELAY = 3.0

    def __init__(self):
        self.session = self._create_session()
        self._last_request_time = 0

    def _create_session(self) -> requests.Session:
        """创建带有重试机制的 Session"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 设置默认请求头
        session.headers.update(self.DEFAULT_HEADERS)

        return session

    def _random_delay(self):
        """随机延时，避免请求过于频繁"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_DELAY:
            delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
            time.sleep(delay)
        self._last_request_time = time.time()

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        delay: bool = True
    ) -> Optional[requests.Response]:
        """
        发送 GET 请求

        Args:
            url: 请求URL
            params: 查询参数
            headers: 额外的请求头
            delay: 是否启用随机延时

        Returns:
            Response 对象，失败返回 None
        """
        if delay:
            self._random_delay()

        try:
            merged_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
            response = self.session.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            logger.error(f"请求超时: {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {url}, {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {url}, {e}")

        return None

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        发送 GET 请求并解析 JSON

        Returns:
            解析后的 JSON 数据，失败返回 None
        """
        response = self.get(url, params, headers)
        if response is None:
            return None

        try:
            return response.json()
        except ValueError as e:
            logger.error(f"JSON解析失败: {url}, {e}")
            return None

    def close(self):
        """关闭 Session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

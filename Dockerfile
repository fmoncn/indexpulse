FROM python:3.11-slim

WORKDIR /app

# 复制并安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 创建数据目录
RUN mkdir -p /app/data

# Railway 使用 PORT 环境变量
ENV PORT=8000
EXPOSE 8000

# 使用 shell 形式以支持环境变量展开
CMD ["/bin/sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

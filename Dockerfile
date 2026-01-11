FROM python:3.11-slim

WORKDIR /app

# 复制并安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制启动脚本
COPY start.sh .
RUN chmod +x start.sh

# 创建数据目录
RUN mkdir -p /app/data

EXPOSE 8000

# 使用启动脚本
CMD ["./start.sh"]

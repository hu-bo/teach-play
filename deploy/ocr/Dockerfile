FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pillow \
    numpy \
    paddleocr \
    paddlepaddle

# 复制应用代码
COPY server.py .

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]

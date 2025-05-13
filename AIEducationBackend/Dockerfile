# AIEducationBackend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 预安装依赖可以利用 Docker 缓存
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露 FastAPI 应用运行的端口 (uvicorn 默认 8000)
EXPOSE 8000

# 运行应用的命令 (与 startup.md 中的命令类似)
# 如果 startup.md 中的命令是 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 在 Docker 中，--reload 通常不用于生产环境
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
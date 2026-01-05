
# 使用 Python 3.9 为基础镜像 (与开发环境一致)
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置时区为北京时间
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 确保数据目录存在 (虽然是SQLite文件，但在容器里通常挂载volume)
# 这里仅确保初始状态
# articles.db 将在运行时生成

# 设置环境变量，确保 Python 输出不缓冲
ENV PYTHONUNBUFFERED=1

# 启动命令 (默认循环模式)
CMD ["python", "Rss_monitor.py"]

"""
配置信息
"""
import os

# 知乎账号
ZHIHU_PHONE = "17763411430"
ZHIHU_PASSWORD = "abc123456"

# 目标网站
TARGET_SITE = "https://ainovel666.cn/"
TARGET_NAME = "AiNovel"

# ainovel API 配置
AINOVEL_API_BASE = os.environ.get("AINOVEL_API_BASE", "http://localhost:8080/api")
# 先尝试从本地启动的后端获取 token
AINOVEL_USERNAME = os.environ.get("AINOVEL_ADMIN_USER", "admin")
AINOVEL_PASSWORD = os.environ.get("AINOVEL_ADMIN_PASS", "admin123")

# Cookie 文件
COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.json")

# User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 发帖间隔（秒）
POST_INTERVAL_MIN = 3600  # 1小时
POST_INTERVAL_MAX = 7200  # 2小时

# 每次发几条
POSTS_PER_RUN = 2

"""
知乎登录模块 - 处理 Cookies 登录
"""
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict
from config import ZHIHU_PHONE, ZHIHU_PASSWORD, COOKIE_FILE, USER_AGENT


class ZhihuLogin:
    """知乎登录管理"""

    BASE_URL = "https://www.zhihu.com"
    API_HEADERS = {
        "User-Agent": USER_AGENT,
        "Referer": "https://www.zhihu.com/",
        "Origin": "https://www.zhihu.com",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.API_HEADERS)
        self.cookies = {}

    def load_cookies(self) -> bool:
        """从文件加载 Cookies"""
        if not Path(COOKIE_FILE).exists():
            return False
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie_data = json.load(f)

            # 检查是否过期（知乎 cookie 通常有 expires 字段）
            if "expires_at" in cookie_data and cookie_data["expires_at"] < time.time():
                print("Cookies 已过期，需要重新登录")
                return False

            # 支持两种格式：requests 格式（cookies dict）和 Playwright 格式（raw_cookies）
            cookies_to_load = cookie_data.get("raw_cookies", None)
            if cookies_to_load is None:
                # 旧格式：直接是 dict
                cookies_dict = cookie_data.get("cookies", {})
                for name, value in cookies_dict.items():
                    self.session.cookies.set(name, value)
            else:
                # Playwright 格式
                for c in cookies_to_load:
                    self.session.cookies.set(c["name"], c["value"])

            print(f"已从 {COOKIE_FILE} 加载 Cookies")
            return True
        except Exception as e:
            print(f"加载 Cookies 失败: {e}")
            return False

    def save_cookies(self, cookies_dict: Dict, expires_in: int = 86400 * 7):
        """保存 Cookies 到文件"""
        cookie_data = {
            "cookies": {c.name: c.value for c in self.session.cookies},
            "expires_at": time.time() + expires_in,
            "saved_at": time.time(),
        }
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)
        print(f"Cookies 已保存到 {COOKIE_FILE}")

    def is_logged_in(self) -> bool:
        """检查是否已登录（通过访问个人资料页面）"""
        try:
            # 知乎新版 API 入口是 api.zhihu.com
            resp = self.session.get(
                "https://api.zhihu.com/people/self",
                headers=self.API_HEADERS,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                name = data.get("name", "Unknown")
                if name:
                    print(f"已登录: {name}")
                    return True
            return False
        except Exception as e:
            print(f"登录检查失败: {e}")
            return False

    def login(self, phone: str = None, password: str = None) -> bool:
        """
        登录知乎
        策略：
        1. 先尝试加载已有 cookie
        2. 验证 cookie 有效性
        3. 无效则尝试账号密码登录
        """
        phone = phone or ZHIHU_PHONE
        password = password or ZHIHU_PASSWORD

        # 1. 尝试加载已有 cookies
        if self.load_cookies():
            if self.is_logged_in():
                return True
            print("已有 Cookies 无效，开始账号登录...")

        # 2. 先访问知乎首页，获取初始 cookies
        print("正在访问知乎首页...")
        try:
            self.session.get(self.BASE_URL, timeout=10)
        except Exception as e:
            print(f"访问知乎首页失败: {e}")
            return False

        # 3. 获取登录验证码（如果需要）
        # 知乎新版可能需要 /api/v4/otp/send
        # 先尝试直接发送登录请求，查看响应
        print("正在尝试登录...")

        # 知乎新版登录 API
        login_url = "https://www.zhihu.com/api/v4/sign_in"

        login_data = {
            "phone": phone,
            "password": password,
            "captcha": "",
            "captcha_enabled": False,
            "flow_type": 1,
        }

        try:
            resp = self.session.post(
                login_url,
                json=login_data,
                headers={
                    **self.API_HEADERS,
                    "Content-Type": "application/json",
                    "X-API-Version": "3.0.88",
                },
                timeout=15,
            )

            if resp.status_code in (200, 201):
                data = resp.json()
                if data.get("r") == 0:
                    print("登录成功!")
                    self.save_cookies({})
                    return True
                else:
                    error_msg = data.get("error", {}).get("message", "未知错误")
                    print(f"登录失败: {error_msg}")
                    return False
            else:
                print(f"登录请求失败: HTTP {resp.status_code}")
                print(f"响应: {resp.text[:500]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"登录请求异常: {e}")
            return False

    def get_cookies(self) -> requests.Session:
        """获取已登录的 session"""
        return self.session


def get_logged_session() -> Optional[requests.Session]:
    """获取已登录的知乎 session"""
    login = ZhihuLogin()
    if login.login():
        return login.get_cookies()
    return None

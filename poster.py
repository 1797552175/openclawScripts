"""
知乎发帖模块 - 发布内容到知乎
"""
import time
import random
import requests
from typing import Optional
from config import USER_AGENT


class ZhihuPoster:
    """知乎内容发布器"""

    BASE_URL = "https://www.zhihu.com"
    API_HEADERS = {
        "User-Agent": USER_AGENT,
        "Referer": "https://www.zhihu.com/",
        "Origin": "https://www.zhihu.com",
    }

    # 已知的热门问题 ID（可以后续扩展）
    HOT_QUESTIONS = [
        "19550394",   # 有什么AI写作工具推荐？
        "288230491",  # 如何利用AI辅助写小说？
        "506625118",  # 有哪些适合新手的写作工具？
        "291047578",  # 写作灵感枯竭怎么办？
    ]

    def __init__(self, session: requests.Session):
        self.session = session
        self.session.headers.update(self.API_HEADERS)

    def post_article(self, title: str, content: str) -> Optional[str]:
        """
        发布文章到知乎专栏

        Returns:
            article_url: 发布的文章链接，失败返回 None
        """
        print(f"正在发布文章: {title}")

        # 知乎发文章 API
        url = f"{self.BASE_URL}/api/v4/articles"

        data = {
            "title": title,
            "content": content,
            "content_type": "article",
            "is_publish": True,
            "is_forbid_comment": False,
        }

        try:
            resp = self.session.post(
                url,
                json=data,
                headers={
                    **self.API_HEADERS,
                    "Content-Type": "application/json",
                    "X-API-Version": "3.0.88",
                },
                timeout=20,
            )

            if resp.status_code in (200, 201):
                result = resp.json()
                article_id = result.get("id")
                print(f"文章发布成功! ID: {article_id}")
                return f"https://zhuanlan.zhihu.com/p/{article_id}"
            else:
                print(f"文章发布失败: HTTP {resp.status_code}")
                print(f"响应: {resp.text[:300]}")
                return None

        except Exception as e:
            print(f"文章发布异常: {e}")
            return None

    def post_answer(self, question_id: str, content: str, title: str = "") -> Optional[str]:
        """
        发布回答到知乎问题

        Returns:
            answer_url: 发布的回答链接，失败返回 None
        """
        print(f"正在发布回答到问题 {question_id}: {title[:30] if title else 'N/A'}...")

        url = f"{self.BASE_URL}/api/v4/answers"

        data = {
            "question_id": int(question_id),
            "content": content,
            "is_copyable": True,
        }

        try:
            resp = self.session.post(
                url,
                json=data,
                headers={
                    **self.API_HEADERS,
                    "Content-Type": "application/json",
                    "X-API-Version": "3.0.88",
                },
                timeout=20,
            )

            if resp.status_code in (200, 201):
                result = resp.json()
                answer_id = result.get("id")
                question_id_resp = result.get("question", {}).get("id")
                print(f"回答发布成功! ID: {answer_id}")
                return f"https://www.zhihu.com/question/{question_id_resp}/answer/{answer_id}"
            else:
                print(f"回答发布失败: HTTP {resp.status_code}")
                print(f"响应: {resp.text[:300]}")
                return None

        except Exception as e:
            print(f"回答发布异常: {e}")
            return None

    def post_idea(self, content: str, images: list = None) -> Optional[str]:
        """
        发布想法

        Returns:
            idea_id: 想法 ID，失败返回 None
        """
        print(f"正在发布想法...")

        url = f"{self.BASE_URL}/api/v4/ideas"

        data = {
            "content": content,
            "images": images or [],
            "is_publish": True,
        }

        try:
            resp = self.session.post(
                url,
                json=data,
                headers={
                    **self.API_HEADERS,
                    "Content-Type": "application/json",
                    "X-API-Version": "3.0.88",
                },
                timeout=20,
            )

            if resp.status_code in (200, 201):
                result = resp.json()
                idea_id = result.get("id")
                print(f"想法发布成功! ID: {idea_id}")
                return idea_id
            else:
                print(f"想法发布失败: HTTP {resp.status_code}")
                print(f"响应: {resp.text[:300]}")
                return None

        except Exception as e:
            print(f"想法发布异常: {e}")
            return None

    def get_random_question(self) -> Optional[tuple]:
        """随机获取一个问题（ID, 标题）"""
        # 这里可以扩展为从知乎搜索获取相关问题
        question_titles = {
            "19550394": "有什么AI写作工具推荐？",
            "288230491": "如何利用AI辅助写小说？",
            "506625118": "有哪些适合新手的写作工具？",
            "291047578": "写作灵感枯竭怎么办？",
        }
        q_id = random.choice(list(question_titles.keys()))
        return q_id, question_titles.get(q_id, "")

    def random_interval(self, min_sec: int, max_sec: int):
        """随机等待一段时间"""
        wait = random.randint(min_sec, max_sec)
        print(f"等待 {wait} 秒...")
        time.sleep(wait)

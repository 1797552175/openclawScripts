"""
营销内容生成模块 - 使用 ainovel 平台的 AI 接口生成内容
"""
import json
import time
import requests
from typing import List, Optional
from config import AINOVEL_API_BASE, AINOVEL_USERNAME, AINOVEL_PASSWORD, TARGET_SITE, TARGET_NAME


class AinovelAuth:
    """ainovel JWT 认证"""

    def __init__(self):
        self.token: Optional[str] = None
        self.username = AINOVEL_USERNAME
        self.password = AINOVEL_PASSWORD

    def login(self) -> bool:
        """登录获取 JWT token"""
        try:
            resp = requests.post(
                f"{AINOVEL_API_BASE}/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("token")
                if self.token:
                    print(f"ainovel 登录成功")
                    return True
            print(f"ainovel 登录失败: {resp.status_code} - {resp.text[:200]}")
            return False
        except Exception as e:
            print(f"ainovel 登录异常: {e}")
            return False

    def get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}


class ContentGenerator:
    """营销内容生成器"""

    def __init__(self, auth: AinovelAuth):
        self.auth = auth

    def generate_marketing_content(self, topic: str, content_type: str = "article") -> dict:
        """
        使用 ainovel AI 生成营销内容

        Args:
            topic: 营销主题/角度
            content_type: article(文章) / answer(回答) / idea(想法)

        Returns:
            dict: 包含 title 和 content
        """
        prompts = {
            "article": f"""你是一个优秀的内容营销专家。请为 {TARGET_NAME}（{TARGET_SITE}）撰写一篇营销推广文章。

要求：
1. 标题吸引人，能引发好奇心
2. 内容围绕「AI辅助小说创作」主题，从目标用户痛点切入
3. 自然融入网站推广信息（{TARGET_SITE}），不要硬广
4. 字数 800-1500 字
5. 风格：真诚、有干货、像真实用户体验分享
6. 文章要有起承转合，避免流水账
7. 结尾引导用户访问网站注册

主题：{topic}

请以 JSON 格式返回，格式如下（不要有其他内容）：
{{"title": "标题", "content": "正文内容（Markdown格式）"}}
""",
            "answer": f"""你是一个优秀的内容营销专家。请为 {TARGET_NAME}（{TARGET_SITE}）撰写一篇知乎回答。

要求：
1. 针对问题给出有价值、有深度的回答
2. 自然融入产品推广信息（{TARGET_SITE}），像经验分享
3. 字数 300-800 字
4. 风格：专业、有见地、让人信服
5. 结尾可以自然提到「我最近在用某个平台写小说，感觉不错」

主题：{topic}

请以 JSON 格式返回，格式如下（不要有其他内容）：
{{"title": "回答标题（可选）", "content": "回答正文（Markdown格式）"}}
""",
            "idea": f"""你是一个优秀的内容营销专家。请为 {TARGET_NAME}（{TARGET_SITE}）撰写一条知乎想法。

要求：
1. 简短有趣，适合知乎想法形式
2. 可以是一个小技巧、一个感悟、一个发现
3. 字数 100-300 字
4. 风格：轻松、有趣、有干货
5. 可以带话题标签

主题：{topic}

请以 JSON 格式返回，格式如下（不要有其他内容）：
{{"content": "想法正文内容"}}
""",
        }

        prompt = prompts.get(content_type, prompts["article"])

        try:
            resp = requests.post(
                f"{AINOVEL_API_BASE}/ai/chat",
                headers=self.auth.get_headers(),
                json={
                    "messages": [],
                    "content": prompt,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("content", "")
                return self._parse_json_response(content)
            else:
                print(f"AI 生成失败: {resp.status_code} - {resp.text[:200]}")
                return self._fallback_content(topic, content_type)
        except Exception as e:
            print(f"AI 生成异常: {e}")
            return self._fallback_content(topic, content_type)

    def _parse_json_response(self, content: str) -> dict:
        """解析 AI 返回的 JSON 内容"""
        try:
            # 尝试提取 JSON
            content = content.strip()
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()

            return json.loads(content)
        except json.JSONDecodeError:
            print("JSON 解析失败，使用备用内容")
            return {"title": "AI 写作新体验", "content": content}

    def _fallback_content(self, topic: str, content_type: str) -> dict:
        """备用内容（当 AI 不可用时）"""
        fallbacks = {
            "article": {
                "title": f"用 AI 写小说 3 个月，我发现了创作的新大陆",
                "content": f"""# 用 AI 写小说 3 个月，我发现了创作的新大陆

最近尝试了一个新的小说创作方式，不得不说，真的很香。

以前写小说最头疼的是什么？卡文、设定打架、写到后面忘了前面...

现在有了 AI 辅助，这些问题都缓解了很多。

我目前在用的是 **AiNovel**（{TARGET_SITE}），它能帮你：

- 在卡文的时候给你提供多个剧情走向选择
- 自动维护世界观和角色设定
- 根据你的风格生成下一章草稿
- 与「作者 AI 分身」对话，帮你梳理思路

最让我惊喜的是「分支剧情」功能。读者可以在关键节点选择走向，作者不用写十几个结局，却能满足不同读者的口味。

如果你也想尝试 AI 辅助写作，不妨去体验一下。

{TARGET_SITE}
""",
            },
            "answer": {
                "title": "",
                "content": f"""作为一个写小说写了 2 年的人，说说我的看法。

AI 写作工具现在确实已经很成熟了，但关键在于「辅助」而不是「替代」。

我目前用的是 **AiNovel**（{TARGET_SITE}），它不是那种给你一键生成小说的工具，而是：

1. 帮你生成写作灵感、解决卡文
2. 自动维护人物设定和世界观，你写到后面不会忘记前面
3. 分支剧情让读者参与创作，满足不同口味
4. 有作者 AI 分身，可以和你对话梳理思路

最实用的场景：
- 不知道下一章怎么写的时候，让 AI 给你 3 个方向选
- 写之前先和 AI 对话，确定这章要达成什么目的
- 遇到想不起来的设定，让 AI 根据已有内容推理

{TARGET_SITE} 有免费体验，感兴趣可以试试。
""",
            },
            "idea": {
                "content": f"""刚发现一个超好用的 AI 写小说神器

就是 ainovel666.cn

写小说最怕卡文，它直接帮你生成 3 个剧情走向选
还有作者 AI 分身，思路乱的时候可以跟它聊
分支剧情让读者决定故事走向，再也不用纠结写几个结局了

#AI写作 #小说创作 #工具推荐""",
            },
        }
        return fallbacks.get(content_type, fallbacks["article"])


def get_content_generator() -> Optional[ContentGenerator]:
    """获取内容生成器"""
    auth = AinovelAuth()
    if auth.login():
        return ContentGenerator(auth)
    return None

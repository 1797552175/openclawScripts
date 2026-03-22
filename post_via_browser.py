#!/usr/bin/env python3
"""
通过 Playwright 浏览器直接发布知乎回答（绕过 API 签名限制）
"""
import sys
import os
import time
import json

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("正在安装 playwright...")
    os.system(f"{sys.executable} -m pip install playwright -q")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.json")


def load_browser_cookies(context):
    """从 cookies.json 加载 cookie 到 browser context"""
    with open(COOKIE_FILE) as f:
        data = json.load(f)
    for c in data["raw_cookies"]:
        context.add_cookies([c])


def find_chrome_path():
    """找到 Chrome 可执行文件"""
    candidates = []
    home = os.path.expanduser("~")
    paths = [
        os.path.join(home, "AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(home, "AppData\\Local\\Programs\\Google\\Chrome\\Application\\chrome.exe"),
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            candidates.append(p)
    return candidates[0] if candidates else None


def post_answer_via_browser(question_id: str, question_url: str, content: str) -> bool:
    """通过真实浏览器发布回答"""
    with sync_playwright() as p:
        chrome_path = find_chrome_path()

        if chrome_path:
            print("使用 Chrome 浏览器...")
            data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data", "Profile 1")
            try:
                browser = p.chromium.launch(
                    executable_path=chrome_path,
                    args=[
                        f"--user-data-dir={os.path.dirname(data_dir)}",
                        f"--profile-directory={os.path.basename(data_dir)}",
                        "--no-first-run",
                        "--no-default-browser-check",
                    ],
                    headless=False,
                )
            except Exception as e:
                print(f"Chrome 启动失败: {e}，使用临时 Profile...")
                browser = p.chromium.launch(headless=False)
        else:
            print("未找到 Chrome，使用临时 Profile...")
            browser = p.chromium.launch(headless=False)

        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        # 加载 cookies
        try:
            load_browser_cookies(context)
            print("Cookies 已加载")
        except Exception as e:
            print(f"加载 cookies 失败: {e}")

        print(f"正在打开问题页面: {question_url}")
        page.goto(question_url, timeout=30000)
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # 检查是否已登录
        try:
            name = page.evaluate("() => window.__INITIAL_STATE__.people?.name || document.querySelector('.AppHeader-profileName')?.textContent")
            if name:
                print(f"当前登录: {name}")
        except Exception:
            pass

        print("正在填写回答...")

        # 点击回答框（知乎的回答输入框）
        try:
            # 尝试点击回答输入区域
            answer_selector = ".Input-wrapper[data-maxlength], .Input[contenteditable='true'], .zu-top-entry-question+.Modal-wrapper button"
            page.click(answer_selector, timeout=5000)
        except Exception:
            try:
                # 备用选择器
                page.click(".QuestionAnswers-answerAdd", timeout=5000)
            except Exception:
                print("无法找到回答框，请手动点击回答按钮")

        time.sleep(1)

        # 输入回答内容
        try:
            # 找到可编辑的回答框
            content_box = page.query_selector(".Input[contenteditable='true'], [contenteditable='true'].Input")
            if content_box:
                content_box.click()
                content_box.fill(content)
                print("回答内容已填入")
            else:
                # 直接在可编辑 div 里输入
                editable = page.query_selector("[contenteditable='true']")
                if editable:
                    editable.click()
                    editable.fill(content)
                    print("回答内容已填入（备用方式）")
                else:
                    print("找不到回答输入框，请在浏览器中手动填入")
        except Exception as e:
            print(f"填写回答失败: {e}，请在浏览器中手动填入")

        print()
        print("=" * 60)
        print("请在浏览器中完成以下操作：")
        print("1. 检查回答内容是否正确")
        print("2. 点击「发布回答」按钮")
        print("3. 关闭浏览器表示完成")
        print("=" * 60)

        input("发布完成后按回车键退出...")
        browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python post_via_browser.py <问题URL或ID> <回答内容>")
        print("示例: python post_via_browser.py 29049016 '这是我的回答...'")
        sys.exit(1)

    question = sys.argv[1]
    content = sys.argv[2]

    # 如果是纯数字，当作 question_id 处理
    if question.isdigit():
        question_url = f"https://www.zhihu.com/question/{question}"
    elif question.startswith("http"):
        question_url = question
    else:
        question_url = f"https://www.zhihu.com/question/{question}"

    print(f"问题: {question_url}")
    print(f"内容: {content[:50]}...")

    post_answer_via_browser(question, question_url, content)

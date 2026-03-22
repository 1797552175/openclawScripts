#!/usr/bin/env python3
"""
导出知乎 cookies 脚本
使用 Chrome 用户资料目录启动浏览器（保留登录状态）
"""
import sys
import os
import json
import time
import subprocess

# 确保 playwright 可用
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("正在安装 playwright...")
    os.system(f"{sys.executable} -m pip install playwright -q")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.json")


def find_chrome_path():
    """尝试找到 Chrome 可执行文件路径"""
    import shutil
    candidates = []

    # Windows
    for path in [
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
        os.path.expanduser("~\\AppData\\Local\\Programs\\Google\\Chrome\\Application\\chrome.exe"),
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]:
        if os.path.exists(path):
            candidates.append(path)

    # macOS
    for path in [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]:
        if os.path.exists(path):
            candidates.append(path)

    # Linux
    for path in [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]:
        if os.path.exists(path):
            candidates.append(path)

    return candidates[0] if candidates else None


def get_data_dir():
    """获取 Chrome 数据目录路径（每个平台不同）"""
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Profile 1")
    elif sys.platform == "darwin":
        return os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Profile 1")
    else:
        return os.path.join(home, ".config", "google-chrome", "Profile 1")


def main():
    print("=" * 60)
    print("知乎 Cookie 导出工具（Chrome Profile 模式）")
    print("=" * 60)
    print()

    data_dir = get_data_dir()

    # 查找 Chrome
    chrome_path = find_chrome_path()

    with sync_playwright() as p:
        if chrome_path and os.path.exists(data_dir):
            print(f"检测到 Chrome 数据目录: {data_dir}")
            print("将使用已登录的 Chrome Profile 启动...")
            print()

            try:
                # 尝试使用已有 Chrome 数据（可能已登录）
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
                context = browser.contexts[0]
                page = context.new_page()

            except Exception as e:
                print(f"使用 Chrome Profile 失败: {e}")
                print("将使用临时 Profile（需要重新登录）...")
                browser = p.chromium.launch(headless=False)
                context = browser.contexts[0]
                page = context.new_page()
        else:
            print("未找到 Chrome 或数据目录，使用临时 Profile")
            print("（首次使用需要在浏览器中手动登录知乎）")
            print()
            browser = p.chromium.launch(headless=False)
            context = browser.contexts[0]
            page = context.new_page()

        print("正在打开知乎...")
        page.goto("https://www.zhihu.com/", timeout=30000)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 检查是否已登录
        try:
            resp = context.request.get(
                "https://www.zhihu.com/api/v4/people/self",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            )
            if resp.ok:
                data = resp.json()
                name = data.get("name", "未知用户")
                print(f"✅ 检测到已登录用户: {name}")
                print()
        except Exception:
            pass

        print()
        print("=" * 60)
        print("请确认浏览器中的知乎账号状态：")
        print("  - 如果已显示登录状态，按 回车键 继续导出 cookies")
        print("  - 如果需要登录，请在浏览器中完成登录后再按回车")
        print()
        print("⚠️  按 回车键 继续导出 cookies...")
        print("=" * 60)
        input()

        print()
        print("正在导出 cookies...")

        cookies = context.cookies()

        # 保存完整格式
        cookie_data = {
            "cookies": {c["name"]: c["value"] for c in cookies},
            "raw_cookies": cookies,
            "saved_at": time.time(),
        }

        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)

        print(f"✅ cookies 已保存到: {COOKIE_FILE}")
        print(f"   共 {len(cookies)} 个 cookie")

        # 验证登录状态
        try:
            resp = context.request.get(
                "https://www.zhihu.com/api/v4/people/self",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            )
            if resp.ok:
                data = resp.json()
                name = data.get("name", "未知")
                print(f"✅ 登录验证成功: {name}")
            else:
                print(f"⚠️  登录验证失败，请确认是否正确登录")
        except Exception as e:
            print(f"⚠️  验证出错: {e}")

        browser.close()

    print()
    print("完成！可以运行 main.py 开始发帖了。")
    input("按回车退出...")


if __name__ == "__main__":
    main()

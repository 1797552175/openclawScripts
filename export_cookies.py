#!/usr/bin/env python3
"""
导出知乎 cookies 脚本
运行后自动打开浏览器 -> 你手动登录 -> 按回车 -> 自动导出 cookies.json
"""
import sys
import os

# 确保能用 playwright
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("正在安装 playwright...")
    os.system(f"{sys.executable} -m pip install playwright -q")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright

import json
import time

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.json")

def main():
    print("=" * 60)
    print("知乎 Cookie 导出工具")
    print("=" * 60)
    print()

    with sync_playwright() as p:
        # 启动 Chromium（临时 profile，安全）
        browser = p.chromium.launch(headless=False)
        context = browser.contexts[0]
        page = context.new_page()

        print("正在打开知乎...")
        page.goto("https://www.zhihu.com/", timeout=30000)
        page.wait_for_load_state("networkidle")

        print()
        print("=" * 60)
        print("✅ 浏览器已打开，请在浏览器中完成登录")
        print("✅ 登录完成后，切换回这个窗口")
        print()
        print("⚠️  登录完成后，按 回车键 继续导出 cookies...")
        print("⚠️  如果不需要导出了，关闭浏览器即可")
        print("=" * 60)
        input()  # 等待用户按回车

        print()
        print("正在导出 cookies...")

        cookies = context.cookies()

        # 整理格式，适配 requests
        cookie_dict = {}
        for c in cookies:
            cookie_dict[c["name"]] = c["value"]

        # 保存完整格式（包含所有字段，方便后续使用）
        cookie_data = {
            "cookies": cookie_dict,
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
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            if resp.ok:
                data = resp.json()
                name = data.get("name", "未知")
                print(f"✅ 登录验证成功: {name}")
            else:
                print(f"⚠️  登录验证失败，请确认已正确登录")
        except Exception as e:
            print(f"⚠️  验证过程出错: {e}")

        browser.close()

    print()
    print("完成！可以运行 main.py 开始发帖了。")
    input("按回车退出...")


if __name__ == "__main__":
    main()

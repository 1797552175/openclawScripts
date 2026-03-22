#!/usr/bin/env python3
"""
知乎营销自动发帖主程序

功能：
1. 知乎登录（Cookie 持久化）
2. 使用 ainovel AI 生成营销内容
3. 自动发布到知乎（文章/回答/想法）
4. 定时任务支持

Usage:
    python main.py                    # 运行一次
    python main.py --daemon           # 持续运行（定时发帖）
    python main.py --test-article      # 测试发布文章
    python main.py --test-answer       # 测试发布回答
    python main.py --test-idea         # 测试发布想法
"""
import os
import sys
import time
import random
import argparse
from pathlib import Path

# 添加当前目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from zhihu_login import ZhihuLogin, get_logged_session
from content_generator import get_content_generator
from poster import ZhihuPoster
from config import (
    TARGET_SITE,
    POST_INTERVAL_MIN,
    POST_INTERVAL_MAX,
    POSTS_PER_RUN,
)


def run_once(zhihu_session, generator, poster):
    """执行一次发帖"""
    results = []

    # 随机决定发什么类型
    content_types = ["article", "answer", "idea"]
    weights = [0.4, 0.3, 0.3]  # 40%文章, 30%回答, 30%想法

    for i in range(POSTS_PER_RUN):
        content_type = random.choices(content_types, weights=weights)[0]
        print(f"\n{'='*50}")
        print(f"第 {i+1}/{POSTS_PER_RUN} 条: {content_type}")
        print(f"{'='*50}")

        # 营销主题池
        topics = [
            "AI 写小说真的靠谱吗？亲身使用体验分享",
            "从零开始写小说，这些工具帮了大忙",
            "网文作者都在用的 AI 辅助写作心得",
            "告别卡文！AI 如何帮我找到写作灵感",
            "用 AI 写小说 3 个月，记录我的创作变化",
            "为什么越来越多人开始用 AI 辅助写小说？",
            "AI 写作时代，作者还需要什么能力？",
        ]
        topic = random.choice(topics)

        # 生成内容
        print(f"正在生成内容: {topic}")
        content = generator.generate_marketing_content(topic, content_type)

        if not content or not content.get("content"):
            print("内容生成失败，跳过...")
            continue

        # 发布
        if content_type == "article":
            url = poster.post_article(
                content.get("title", "无标题"),
                content.get("content", ""),
            )
        elif content_type == "answer":
            question_id, question_title = poster.get_random_question()
            if question_id:
                url = poster.post_answer(
                    question_id,
                    content.get("content", ""),
                    question_title,
                )
            else:
                url = None
        else:  # idea
            idea_id = poster.post_idea(content.get("content", ""))
            url = f"想法 ID: {idea_id}" if idea_id else None

        results.append({"type": content_type, "url": url, "topic": topic})

        if i < POSTS_PER_RUN - 1:
            poster.random_interval(30, 60)  # 发完一条等 30-60 秒

    return results


def daemon_mode(zhihu_session, generator, poster):
    """守护进程模式：持续运行，定时发帖"""
    print("=" * 60)
    print("知乎营销机器人已启动（守护模式）")
    print("按 Ctrl+C 停止")
    print("=" * 60)

    run_count = 0
    while True:
        run_count += 1
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 第 {run_count} 轮执行")

        # 检查登录状态
        if not zhihu_session or not ZhihuLogin().is_logged_in():
            print("登录失效，重新登录...")
            zhihu_session = get_logged_session()
            if not zhihu_session:
                print("登录失败，10分钟后重试...")
                time.sleep(600)
                continue

        # 重新创建 poster（session 可能已刷新）
        poster = ZhihuPoster(zhihu_session)

        try:
            results = run_once(zhihu_session, generator, poster)
            success = sum(1 for r in results if r["url"])
            print(f"\n本轮完成: {success}/{len(results)} 条发布成功")
        except Exception as e:
            print(f"执行异常: {e}")

        # 随机间隔后继续
        interval = random.randint(POST_INTERVAL_MIN, POST_INTERVAL_MAX)
        print(f"\n等待 {interval // 60} 分钟后执行下一轮...")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="知乎营销自动发帖")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式")
    parser.add_argument("--test-article", action="store_true", help="测试发布文章")
    parser.add_argument("--test-answer", action="store_true", help="测试发布回答")
    parser.add_argument("--test-idea", action="store_true", help="测试发布想法")
    args = parser.parse_args()

    # 登录
    print("正在登录知乎...")
    zhihu_session = get_logged_session()
    if not zhihu_session:
        print("知乎登录失败，退出")
        sys.exit(1)

    # 初始化内容生成器
    print("正在初始化内容生成器...")
    generator = get_content_generator()
    if not generator:
        print("内容生成器初始化失败，退出")
        sys.exit(1)

    poster = ZhihuPoster(zhihu_session)

    # 测试模式
    if args.test_article:
        print("\n=== 测试发布文章 ===")
        content = generator.generate_marketing_content(
            "AI 写小说真的靠谱吗？亲身使用体验分享", "article"
        )
        url = poster.post_article(content.get("title", ""), content.get("content", ""))
        print(f"结果: {url}")
        return

    if args.test_answer:
        print("\n=== 测试发布回答 ===")
        content = generator.generate_marketing_content(
            "如何利用AI辅助写小说？", "answer"
        )
        q_id, q_title = poster.get_random_question()
        url = poster.post_answer(q_id, content.get("content", ""), q_title)
        print(f"结果: {url}")
        return

    if args.test_idea:
        print("\n=== 测试发布想法 ===")
        content = generator.generate_marketing_content("AI 写作技巧分享", "idea")
        idea_id = poster.post_idea(content.get("content", ""))
        print(f"结果: {idea_id}")
        return

    # 正常运行模式
    if args.daemon:
        daemon_mode(zhihu_session, generator, poster)
    else:
        print("\n=== 执行一次发帖 ===")
        results = run_once(zhihu_session, generator, poster)
        success = sum(1 for r in results if r["url"])
        print(f"\n完成: {success}/{len(results)} 条发布成功")
        for r in results:
            status = "✅" if r["url"] else "❌"
            print(f"  {status} [{r['type']}] {r['topic'][:40]}... -> {r['url']}")


if __name__ == "__main__":
    main()

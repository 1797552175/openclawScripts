# 知乎营销自动发帖机器人

配合 ainovel666.cn 项目使用的知乎营销工具。

## 目录结构

```
zhihu_marketing/
├── export_cookies.py     # ⭐ 第一步：导出 cookies（一键运行）
├── zhihu_login.py        # 知乎登录模块
├── content_generator.py  # 内容生成模块（调用 ainovel AI）
├── poster.py             # 发帖模块
├── main.py               # 主程序
├── cookies.json          # 登录 cookie（自动生成）
├── requirements.txt      # 依赖
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd /opt/my-blog/scripts/zhihu_marketing
pip install -r requirements.txt
```

### 2. 导出 Cookies（只需做一次）

```bash
python export_cookies.py
```

自动打开浏览器 → 你手动登录知乎 → 按回车 → 自动导出完成

### 3. 开始发帖

```bash
# 发布一条文章测试
python main.py --test-article

# 发布一条回答
python main.py --test-answer

# 发布一条想法
python main.py --test-idea

# 执行一次（发 2 条）
python main.py

# 持续运行（定时发帖）
python main.py --daemon
```

## 注意事项

⚠️ **Cookie 有效期**：通常 2-4 周，过期后重新运行 `export_cookies.py` 即可

⚠️ **知乎反爬风险**：
- 使用小号测试，确认流程稳定后再用于正式账号
- 建议设置合理的发帖间隔（默认 1-2 小时）
- 避免短时间内大量发布

## 扩展

- 添加更多热门问题 ID 到 `poster.py`
- 扩展营销主题池到 `main.py`
- 对接其他平台（小红书、公众号等）

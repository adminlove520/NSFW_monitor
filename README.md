
# RSS Monitor

一个轻量级的 RSS 订阅监控工具，支持自定义 RSS 源、[Folo](https://folo.is) 分享链接，并通过 Discord Webhook 发送带有精美 Embed 样式和分类便签的通知。

## 功能特性

*   **多源支持**：
    *   标准 RSS/Atom Feed。
    *   [Folo](https://folo.is) 分享链接（直接解析，无需 RSSHub）。
*   **Discord Embed 通知**：
    *   使用 Discord Embed 格式，展示更美观。
    *   **分类样式**：根据配置的分类（Articles, Pictures, Videos 等），自动应用不同的边框颜色。
    *   **自动标签**：标题前自动附加 `[分类名]` 标签。
*   **去重机制**：使用 SQLite 数据库本地存储历史记录，防止重复推送。
*   **自动化部署**：
    *   支持 GitHub Actions 定时运行。
    *   自动提交数据库变更，保持状态持久化。
*   **模块化设计**：代码结构清晰，易于扩展。

## 快速开始

### 1. 安装依赖

确保已安装 Python 3.9+。

```bash
pip install -r requirements.txt
```

### 2. 配置源 (`rss.yaml`)

编辑 `rss.yaml` 文件添加监控源：

```yaml
"MyFeed":
  "rss_url": "https://example.com/rss.xml"
  "website_name": "我的订阅"
  "category": "Articles"  # 可选: Articles, Pictures, Videos, Social Media, Notifications

"FoloFeed":
  "rss_url": "https://app.folo.is/share/feeds/xxxxxx?view=1"  # Folo 分享链接
  "website_name": "Folo订阅"
  "category": "Pictures"
```

### 3. 配置通知 (`config.yaml` 或 环境变量)

推荐使用环境变量配置敏感信息。

**环境变量**:
*   `DISCARD_WEBHOOK`: 你的 Discord Webhook URL。
*   `DISCARD_SWITCH`: 设置为 `ON`。

**或者修改 `config.yaml`**:
```yaml
push:
  discard:
    webhook: "https://discord.com/api/webhooks/..."
    switch: "ON"
    send_normal_msg: "ON"
```

### 4. 运行

**单次运行** (适用于 Crontab 或 CI/CD):
```bash
python Rss_monitor.py --once
```

**循环运行** (适用于本地常驻):
```bash
python Rss_monitor.py
```

## GitHub Actions 部署

本项目已内置 GitHub Actions 工作流 (`.github/workflows/rss_monitor.yml`)。

1.  Fork 本仓库。
2.  进入仓库 **Settings** -> **Secrets and variables** -> **Actions**。
3.  添加 Secret:
    *   Name: `DISCARD_WEBHOOK`
    *   Value: 你的 Discord Webhook 地址。
4.  工作流将每 **2小时** 自动运行一次，检查更新并推送。

## 许可证

MIT License

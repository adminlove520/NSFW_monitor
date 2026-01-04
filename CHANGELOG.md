
# Changelog

## [Unreleased]

### Added
- **Folo Support**: 直接解析 `folo.is` 分享链接，无需依赖外部 RSSHub 实例。
- **Category Support**: 
  - `rss.yaml` 支持 `category` 字段。
  - Discord 推送支持根据分类显示不同颜色的 Embed 边框。
  - 推送标题自动添加 `[Category]` 前缀。
- **Modular Structure**: 重构代码为 `utils/` 模块化结构，提升可维护性。
- **GitHub Actions**: 添加自动化工作流，支持定时任务和数据库自动提交。

### Changed
- **Config Cleanup**: 移除了过时的报告配置。
- **Refactor**: 分离了核心逻辑到 `utils/config.py`, `utils/db.py`, `utils/notify.py`, `utils/rss.py`。
- **Cleanup**: 移除了代码中硬编码的特定社区文案，使其更加通用。

### Removed
- **Reporting System**: 彻底移除了日报/周报生成功能及相关代码。

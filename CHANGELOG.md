
# Changelog

All notable changes to this project will be documented in this file.

## [V1.0.0] - 2026-01-05

### Added
- **Image Previews**: Automatically extract and display images in Discord Embeds.
- **Docker Support**: Added `Dockerfile` and `deploy-image.yml` for containerized deployment (Zeabur ready).
- **Resilience**: Added 429/503 retry logic and 45-minute loop mode for GitHub Actions.
- **Versioning**: Automated version bump workflow.

### Removed
- **Folo Parsing**: Removed direct Folo HTML parsing in favor of RSSHub.
- **Categories**: Removed category-specific styling (border colors, tags) to simplify logic.
- **Reports**: Removed daily/weekly HTML report generation.

### Fixed
- **Timezone**: Notification timestamps now correctly reflected as Beijing Time (UTC+8).
- **Sleep Logic**: Fixed bug in night mode duration calculation.

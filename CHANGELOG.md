# Changelog

All notable changes to the **Vauban** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [v2.0.0] - 2026-01-21

**"The Scientific Breacher" Release**

### Added
- **Rebranding**: Complete shift from "LostFuzzer" to "Vauban".
- **Architecture**: Modular Python/Bash hybrid system.
- **Commands**: Added `--check` for environment verification.
- **Documentation**: Comprehensive README and Architecture diagrams.
- **Modules**:
    - Recon: `subdomain.sh`, `dns.sh`, `techdetect.py`
    - Discovery: `passive.sh`, `crawler.sh`, `jsparser.py`
    - API: `endpoints.sh`, `openapi.py`, `params.sh`
    - Scan: `nuclei.sh`, `secrets.py`, `custom.py`
- **Reporting**: HTML Dashboard generation.
- **Notifications**: Slack, Discord, Telegram support.

### Changed
- **Config**: Moved hardcoded values to `config/settings.yaml`.
- **Logging**: Implemented rich console logging with error tracking.

### Credits
- **Author**: Kassim Muhammad Atiku (R00TQU35T)
- **Organization**: NHT Corporations

[v2.0.0]: docs/releases/v2.0.0.md

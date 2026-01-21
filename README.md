<div align="center">

```
██╗   ██╗ █████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗
██║   ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗████╗  ██║
██║   ██║███████║██║   ██║██████╔╝███████║██╔██╗ ██║
╚██╗ ██╔╝██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║
 ╚████╔╝ ██║  ██║╚██████╔╝██████╔╝██║  ██║██║ ╚████║
  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
```

### ━━━ The Scientific Breacher ━━━

*"A fortress besieged by Vauban is a fortress taken"*

[![Version](https://img.shields.io/badge/version-2.0-00FFFF?style=for-the-badge)](https://github.com/diamond-kassim-3/vauban)
[![Python](https://img.shields.io/badge/python-3.8+-FF00FF?style=for-the-badge)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-00FF41?style=for-the-badge)](LICENSE)
[![NHT](https://img.shields.io/badge/NHT-Corporations-FFD700?style=for-the-badge)](https://github.com/diamond-kassim-3)

---

**Created by: Kassim Muhammad Atiku**  
**CC | CEH | CSI | CISSP | CISO | ECCS**  
**Known as: R00TQU35T**  
**Organization: NHT Corporations**

</div>

---

## 📋 Table of Contents

- [About Vauban](#-about-vauban)
- [The Legend](#️-the-legend-of-vauban)
- [Features](#-features)
- [Architecture](#️-architecture-overview)
- [Installation](#-installation)
- [Usage](#️-usage)
- [Modules](#-modules-in-detail)
- [Color Palette](#-vauban-color-palette)
- [Configuration](#️-configuration)
- [Output](#-output-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)

---

## 🛡️ About Vauban

**Vauban** is an advanced automated bug hunting and security reconnaissance platform designed for professional penetration testers, bug bounty hunters, and security researchers. 

It automates the entire reconnaissance-to-exploitation pipeline:
- **Drop in a file** of domains, subdomains, or API endpoints
- **Vauban automatically** enumerates, discovers, crawls, and scans
- **Receive comprehensive reports** with exact vulnerabilities and breach points

### Why Vauban?

| Feature | Description |
|---------|-------------|
| 🎯 **Precision** | Uses mathematical methodology like its namesake |
| ⚡ **Speed** | Parallel processing with optimized tool chains |
| 🔧 **Modular** | Mix of Bash and Python for optimal performance |
| 📊 **Reporting** | Beautiful HTML dashboards with evidence |
| 🔔 **Alerts** | Slack, Discord, Telegram notifications |
| 🌐 **Comprehensive** | From subdomain enum to DAST exploitation |

---

## ⚔️ The Legend of Vauban

**Sébastien Le Prestre de Vauban (1633-1707)** was the most renowned military engineer in history. Serving under King Louis XIV of France, he revolutionized both siege warfare and fortification design.

### Key Facts

| Aspect | Detail |
|--------|--------|
| **Sieges Conducted** | 40+ (never lost a single one) |
| **Fortresses Built** | 33 new, 100+ renovated |
| **Innovation** | Invented the "parallel trench" system |
| **Philosophy** | "More powder, less blood" |
| **Legacy** | UNESCO World Heritage (12 sites) |

### Famous Quote

> *"A town besieged by Vauban is a town taken; a town defended by Vauban is a town impregnable."*

### The Parallel to Security Testing

| Vauban's Siege Method | Vauban Security Tool |
|----------------------|---------------------|
| **Reconnaissance** - Map the fortress | Subdomain enumeration, tech fingerprinting |
| **First Parallel** - Initial approach | Passive URL collection from archives |
| **Second Parallel** - Closer trenches | Active crawling, API discovery |
| **Third Parallel** - Final position | Vulnerability scanning, fuzzing |
| **The Breach** - Calculated assault | Nuclei DAST, exploitation |
| **Victory Report** - Document success | HTML/JSON reports with evidence |

---

## ✨ Features

### Core Capabilities

- **🔍 Subdomain Enumeration**: subfinder, assetfinder, amass, crt.sh
- **📡 DNS Resolution**: dnsx with wildcard filtering
- **🌐 Technology Detection**: Framework, CMS, WAF identification
- **📁 Passive URL Collection**: gau, waybackurls, uro
- **🕷️ Active Crawling**: katana, hakrawler, gospider
- **📜 JavaScript Analysis**: Endpoint and secret extraction
- **🔌 API Discovery**: kiterunner, ffuf, OpenAPI/Swagger detection
- **🔑 Parameter Fuzzing**: arjun, ffuf parameter mining
- **💉 DAST Scanning**: Nuclei multi-mode scanning
- **🔐 Secret Detection**: 20+ patterns (AWS, Stripe, JWT, etc.)
- **⚠️ Custom Checks**: IDOR, CORS, rate limiting, headers
- **📊 HTML Reports**: Styled dashboard with Vauban theme
- **📱 Notifications**: Slack, Discord, Telegram alerts

### Scan Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `full` | Complete 5-phase pipeline | Comprehensive assessments |
| `quick` | Skip subdomain, fast scan | Time-limited testing |
| `api` | Focused API testing | API-centric applications |
| `recon` | Reconnaissance only | Initial scoping |

---

## 🏗️ Architecture Overview

```
                            ┌─────────────────────┐
                            │   INPUT: Domains/   │
                            │   APIs/Endpoints    │
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │     ORCHESTRATOR    │
                            │     (vauban.py)     │
                            └──────────┬──────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│    PHASE 1    │            │    PHASE 2    │            │    PHASE 3    │
│     RECON     │            │ URL DISCOVERY │            │ API DISCOVERY │
│   PIPELINE    │            │   PIPELINE    │            │   PIPELINE    │
└───────┬───────┘            └───────┬───────┘            └───────┬───────┘
        │                            │                            │
   ┌────┴────┐                  ┌────┴────┐                  ┌────┴────┐
   │    │    │                  │    │    │                  │    │    │
   ▼    ▼    ▼                  ▼    ▼    ▼                  ▼    ▼    ▼
┌────┐┌────┐┌────┐        ┌────┐┌────┐┌────┐        ┌────┐┌────┐┌────┐
│Sub-││DNS ││Tech│        │Pass││Craw││ JS │        │End-││Para││Open│
│dom-││Res-││Det-│        │ive ││ler ││Ana-│        │poin││m   ││API │
│ain ││olve││ect │        │URLs││    ││lyze│        │ts  ││Fuzz││Det │
└────┘└────┘└────┘        └────┘└────┘└────┘        └────┘└────┘└────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │      PHASE 4       │
                          │  SCANNING PIPELINE │
                          └──────────┬──────────┘
                                     │
                            ┌────────┼────────┐
                            │        │        │
                            ▼        ▼        ▼
                        ┌──────┐ ┌──────┐ ┌──────┐
                        │Nuclei│ │Secret│ │Custom│
                        │ DAST │ │Detect│ │Checks│
                        └──────┘ └──────┘ └──────┘
                            │        │        │
                            └────────┼────────┘
                                     │
                          ┌──────────▼──────────┐
                          │      PHASE 5       │
                          │  REPORT GENERATOR  │
                          └──────────┬──────────┘
                                     │
                            ┌────────┴────────┐
                            ▼                 ▼
                      ┌──────────┐     ┌──────────┐
                      │  HTML/   │     │  Notify  │
                      │  JSON    │     │  Alerts  │
                      └──────────┘     └──────────┘
```

---

## 📦 Installation

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| Go | 1.19+ |
| pip3 | Latest |
| git | Latest |

### Quick Install

```bash
# Clone the repository
git clone https://github.com/diamond-kassim-3/vauban.git
cd vauban

# Run the installer
chmod +x install_tools.sh
./install_tools.sh

# Verify installation
python3 vauban.py --help
```

### Manual Tool Installation

```bash
# ProjectDiscovery Suite
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# URL Collection
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/assetfinder@latest

# API Discovery
go install -v github.com/assetnote/kiterunner/cmd/kr@latest
go install -v github.com/ffuf/ffuf/v2@latest

# Python Tools
pip3 install arjun uro
pip3 install -r requirements.txt
```

---

## ⚙️ Usage

### Basic Commands

```bash
# Full siege on domain list
python3 vauban.py --input domains.txt --mode full

# Quick scan on single target
python3 vauban.py --input https://example.com --mode quick

# API-focused assault
python3 vauban.py --input api_hosts.txt --mode api

# Reconnaissance only
python3 vauban.py --input example.com --mode recon

# With notifications
python3 vauban.py --input targets.txt --mode full --notify
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--check` | Verify all required/optional tools are installed | - |
| `-i, --input` | Target domain, URL, or file (required for scan) | - |
| `-m, --mode` | Scan mode: full, quick, api, recon | full |
| `-o, --output` | Output directory | ./output |
| `-t, --threads` | Number of threads | 10 |
| `--notify` | Send notifications | false |
| `-v, --verbose` | Verbose output | false |

### Verify Installation

Before running, verify your tools are correctly installed:

```bash
python3 vauban.py --check
```

This will show:
- ✓ Installed tools
- ✗ Missing required tools (with install commands)
- ○ Missing optional tools (reduced functionality)

### Input Formats

```bash
# Single domain
python3 vauban.py -i example.com -m full

# Single URL
python3 vauban.py -i https://api.example.com -m api

# File with domains (one per line)
python3 vauban.py -i domains.txt -m full

# File with subdomains
python3 vauban.py -i subdomains.txt -m quick
```

---

## 🔧 Modules in Detail

### Phase 1: Reconnaissance

| Module | File | Tools | Output |
|--------|------|-------|--------|
| Subdomain Enum | `modules/recon/subdomain.sh` | subfinder, assetfinder, amass, crt.sh | subdomains.txt |
| DNS Resolution | `modules/recon/dns.sh` | dnsx, wildcard filter | resolved.txt |
| Tech Detection | `modules/recon/techdetect.py` | httpx, custom patterns | tech_results.json |

### Phase 2: URL Discovery

| Module | File | Tools | Output |
|--------|------|-------|--------|
| Passive URLs | `modules/urls/passive.sh` | gau, waybackurls, uro | passive_urls.txt |
| Active Crawl | `modules/urls/crawler.sh` | katana, hakrawler | crawled_urls.txt |
| JS Analysis | `modules/urls/jsparser.py` | Custom regex, linkfinder | js_analysis.json |

### Phase 3: API Discovery

| Module | File | Tools | Output |
|--------|------|-------|--------|
| Endpoints | `modules/api/endpoints.sh` | kiterunner, ffuf, httpx | api_endpoints.txt |
| Parameters | `modules/api/params.sh` | arjun, ffuf | params_discovered.txt |
| OpenAPI | `modules/api/openapi.py` | Custom scanner | openapi_results.json |

### Phase 4: Scanning

| Module | File | Tools | Output |
|--------|------|-------|--------|
| Nuclei DAST | `modules/scan/nuclei.sh` | nuclei (multi-mode) | nuclei_results.json |
| Secrets | `modules/scan/secrets.py` | 20+ regex patterns | secrets_results.json |
| Custom | `modules/scan/custom.py` | IDOR, CORS, headers | custom_results.json |

### Phase 5: Reporting

| Module | File | Output |
|--------|------|--------|
| HTML Report | `modules/report/generator.py` | report.html |
| JSON Summary | `modules/report/generator.py` | report_summary.json |

---

## 🎨 Vauban Color Palette

The interface uses a distinctive hacker aesthetic:

| Color | Name | Hex | Usage |
|-------|------|-----|-------|
| ◼️ | Deep Void | `#0C0C0C` | Primary background |
| ◼️ | Shadow Gray | `#1A1A1A` | Secondary background |
| 🔵 | Cyber Cyan | `#00FFFF` | Headers, info |
| 🟢 | Matrix Green | `#00FF41` | Success, low severity |
| 🟣 | Neon Magenta | `#FF00FF` | Accents, sections |
| 🟡 | Warning Gold | `#FFD700` | Warnings |
| 🟠 | High Orange | `#FF6600` | High severity |
| 🔴 | Critical Red | `#FF0000` | Critical findings |
| ⬜ | Pure White | `#FFFFFF` | Headings |
| ⬛ | Light Gray | `#B0B0B0` | Body text |

---

## ⚙️ Configuration

Edit `config/settings.yaml`:

```yaml
general:
  threads: 10
  timeout: 30
  rate_limit: 150

notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/..."
  
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/..."
  
  telegram:
    enabled: true
    bot_token: "..."
    chat_id: "..."
```

---

## 📂 Output Structure

```
output/target.com_20240121_030000/
├── recon/
│   ├── subdomains.txt
│   ├── resolved.txt
│   ├── live_hosts.txt
│   └── tech_results.json
├── urls/
│   ├── passive_urls.txt
│   ├── crawled_urls.txt
│   ├── js_files.txt
│   └── js_analysis.json
├── api/
│   ├── api_endpoints.txt
│   ├── openapi_results.json
│   └── params_discovered.txt
├── scan/
│   ├── nuclei_results.json
│   ├── secrets_results.json
│   └── custom_results.json
└── report.html
```

---

## 🔐 Secret Detection Patterns

| Category | Patterns Detected |
|----------|-------------------|
| **AWS** | Access Keys, Secret Keys |
| **GCP** | API Keys, OAuth Tokens |
| **Azure** | Storage Connection Strings |
| **GitHub** | Personal Access Tokens |
| **Slack** | Bot Tokens, Webhooks |
| **Discord** | Bot Tokens, Webhooks |
| **Stripe** | API Keys (test/live) |
| **Twilio** | Account SID, Auth Token |
| **Email** | SendGrid, Mailgun, Mailchimp |
| **Database** | PostgreSQL, MySQL, MongoDB, Redis URIs |
| **Authentication** | JWT, Bearer Tokens, Basic Auth |
| **Keys** | Private Keys (RSA, EC, DSA) |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Python: Follow PEP 8
- Bash: Use shellcheck for linting
- Comments: Clear and concise
- Tests: Add tests for new features

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file.

```
MIT License
Copyright (c) 2024 NHT Corporations
Author: Kassim Muhammad Atiku (R00TQU35T)
```

### Terms of Use

- ✅ Use for authorized security testing
- ✅ Bug bounty programs
- ✅ Educational purposes
- ✅ Modify and distribute with attribution
- ❌ Unauthorized scanning
- ❌ Malicious purposes

---

## 🙏 Credits

### Creator

**Kassim Muhammad Atiku (R00TQU35T)**
- Credentials: CC, CEH, CSI, CISSP, CISO, ECCS
- Organization: NHT Corporations
- GitHub: [@diamond-kassim-3](https://github.com/diamond-kassim-3)

### Inspiration

**Sébastien Le Prestre de Vauban (1633-1707)**
- Marshal of France
- Master of siege warfare
- Builder of fortresses

### Tool Authors

- [ProjectDiscovery](https://github.com/projectdiscovery) - nuclei, httpx, katana, subfinder, dnsx
- [Tom Hudson](https://github.com/tomnomnom) - waybackurls, assetfinder
- [Assetnote](https://github.com/assetnote) - kiterunner
- [ffuf](https://github.com/ffuf/ffuf) - ffuf
- [s0md3v](https://github.com/s0md3v) - arjun, uro

---

<div align="center">

### ⚔️ Made with precision by R00TQU35T

**NHT Corporations**

*"More powder, less blood"* — Vauban's philosophy

---

**Star ⭐ this repository if you find it useful!**

</div>

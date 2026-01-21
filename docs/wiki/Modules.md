# Module Reference 🔧

Detailed breakdown of Vauban's internal modules.

## 🔎 Reconnaissance (`modules/recon/`)

### `subdomain.sh`
**Purpose**: Aggregates subdomains from multiple passive sources.
**Tools**: `subfinder`, `assetfinder`, `amass`, `findomain` (if installed).
**Output**: `subdomains.txt`

### `dns.sh`
**Purpose**: Resolves subdomains and handles wildcards.
**Tools**: `dnsx`, `massdns`.
**Output**: `resolved.txt`

### `techdetect.py`
**Purpose**: Fingerprints WAFs, CMS, and Server versions.
**Tools**: `httpx` + Custom Python logic.
**Output**: `tech_results.json`

## 🔗 URL Discovery (`modules/urls/`)

### `passive.sh`
**Purpose**: Fetches historical URLs from archives.
**Tools**: `gau`, `waybackurls`, `uro`.
**Filter**: Automatically removes image/css/font files.

### `crawler.sh`
**Purpose**: Actively crawls live sites for new links.
**Tools**: `katana`, `hakrawler`, `gospider`.
**Depth**: Configurable depth (Default: 3).

### `jsparser.py`
**Purpose**: Analyzes JS files for endpoints and secrets.
**Method**: Regex-based static analysis.

## 🔌 API Discovery (`modules/api/`)

### `endpoints.sh`
**Purpose**: Wordlist-based discovery of API routes.
**Tools**: `kiterunner`, `ffuf`.
**Wordlists**: Integrated Assetnote wordlists.

### `openapi.py`
**Purpose**: Detects `swagger.json` or `openapi.yaml`.
**Action**: Parses spec and extracts all endpoints.

### `params.sh`
**Purpose**: Fuzzes for hidden GET/POST parameters.
**Tools**: `arjun`.

## 💥 Scanning (`modules/scan/`)

### `nuclei.sh`
**Purpose**: Main DAST scanner.
**Templates**: Security, exposures, cves, misconfiguration.
**Severity**: Low, Medium, High, Critical.

### `secrets.py`
**Purpose**: Regex-based secret scanner.
**Patterns**: AWS, Google, Stripe, Slack, Private Keys, etc.

### `custom.py`
**Purpose**: Python-based checks for specific logic bugs.
**Checks**:
- IDOR (Auth bypass patterns)
- CORS (Origin reflection)
- Security Headers

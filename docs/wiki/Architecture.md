# System Architecture 🏗️

Vauban follows a proven 5-phase siege pipeline, modeled after Vauban's "parallel trench" system.

## The Pipeline

```
[Target] -> [Recon] -> [URL Discovery] -> [API Discovery] -> [Scanning] -> [Report]
```

### 1. Reconnaissance (Mapping the Fortress)
The foundation of any siege. We map the external attack surface.
- **Tools**: `subfinder`, `amass`, `assetfinder`, `crt.sh`, `dnsx`, `httpx`
- **Goal**: Identify all live subdomains and their technologies.

### 2. URL Discovery (Digging Parallels)
Finding the paths into the fortress.
- **Passive**: Collects URLs from Wayback Machine, AlienVault, CommonCrawl.
- **Active**: Crawls the live application using `katana` and `hakrawler`.
- **Logic**: Deduplicates and filters for "interesting" parameters (potential XSS/SQLi).

### 3. API Discovery (Finding Weak Points)
Specialized probing for modern applications.
- **Endpoints**: Bruteforces API routes using `kiterunner` and `ffuf`.
- **OpenAPI**: Detecting and parsing Swagger definitions.
- **Parameters**: Fuzzing for hidden parameters (Mass Assignment, IDOR).

### 4. Vulnerability Scanning (The Breach)
The calculated assault on identified weaknesses.
- **Nuclei**: The heavy siege artillery. Runs DAST templates against all targets.
- **Secrets**: Scans for 20+ types of exposed credentials.
- **Custom**: Checks for logic bugs like IDOR, CORS, Race Conditions.

### 5. Reporting (Victory Documentation)
Aggregating intelligence into actionable data.
- **HTML**: A beautiful dashboard for humans.
- **JSON**: Machine-readable data for integration.
- **Notifications**: Instant alerts to your team.

## Directory Structure

```
vauban/
├── vauban.py            # The Commander (Orchestrator)
├── config/              # Strategy (Configuration)
├── lib/                 # Logistics (Shared Utilities)
├── modules/             # Siege Engines
│   ├── recon/           # Scouts
│   ├── urls/            # Sappers
│   ├── api/             # Spies
│   ├── scan/            # Artillery
│   └── report/          # Scribes
└── output/              # Spoils of War
```

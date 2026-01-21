# Usage Manual ⚔️

## Basic Syntax

```bash
python3 vauban.py -i <INPUT> -m <MODE> [OPTIONS]
```

## Scan Modes (`-m`)

Vauban offers four specialized siege modes:

### 1. Full Mode (`-m full`)
**Best for:** Comprehensive bug bounty hunting, full penetration tests.
**Actions:** 
- Full Subdomain Enumeration
- DNS Resolution & Live Host Probing
- Passive & Active URL Discovery
- API Endpoint Discovery
- Vulnerability Scanning (DAST + Custom)
- Reporting

```bash
python3 vauban.py -i domain.com -m full
```

### 2. Quick Mode (`-m quick`)
**Best for:** Rapid assessment, spot checks.
**Actions:**
- Skips subdomain enumeration (assumes input is the target).
- Fast passive URL collection.
- Standard vulnerability scan.

```bash
python3 vauban.py -i https://sub.domain.com -m quick
```

### 3. API Mode (`-m api`)
**Best for:** Testing API endpoints, Swagger files, or GraphQL.
**Actions:**
- API-specific wordlist brute-forcing.
- OpenAPI/Swagger parsing.
- Parameter fuzzing.
- API-specific vulnerability templates.

```bash
python3 vauban.py -i api-host.com -m api
```

### 4. Recon Mode (`-m recon`)
**Best for:** Asset inventory, attack surface mapping.
**Actions:**
- Only performs Phase 1 (Recon) and Phase 2 (URL Discovery).
- No active vulnerability scanning.

```bash
python3 vauban.py -i domain.com -m recon
```

## Input Options (`-i`)

- **Single Domain:** `-i example.com`
- **Single URL:** `-i https://example.com`
- **List of Targets:** `-i targets.txt` (One per line)

## Notifications (`--notify`)

Enable real-time alerts to Slack, Discord, or Telegram. Configure credentials in `config/settings.yaml`.

```bash
python3 vauban.py -i target.com -m full --notify
```

## Configuration

Edit `config/settings.yaml` to tune performance:

```yaml
general:
  threads: 20          # Increase for faster scans
  timeout: 600         # Timeout for modules in seconds
  rate_limit: 150      # Requests per second
```

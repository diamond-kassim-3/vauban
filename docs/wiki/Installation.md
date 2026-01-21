# Installation Guide 🛠️

## Prerequisites

Vauban is a hybrid Python/Bash system. You need:
- **OS**: Linux (Debian/Ubuntu/Kali recommended) or macOS.
- **Python**: 3.8 or higher.
- **Go**: 1.19 or higher (for the underlying engines).

## Automated Installation (Recommended)

The easiest way to set up Vauban is using the included installer script.

```bash
# 1. Clone the repository
git clone https://github.com/diamond-kassim-3/vauban.git
cd vauban

# 2. Make installer executable
chmod +x install_tools.sh

# 3. Run the installer
./install_tools.sh
```

This script will:
- Check for Python and Go.
- Install all Go-based tools (Nuclei, httpx, subfinder, etc.).
- Install Python requirements (`pip install -r requirements.txt`).
- set up the environment.

## Manual Installation

If you prefer to control every step or the installer fails:

### 1. Python Dependencies

```bash
pip3 install -r requirements.txt
pip3 install arjun uro
```

### 2. Go Tools

Vauban relies on the ProjectDiscovery suite and other Go tools. Install them to your `$GOPATH/bin` or system path.

```bash
# ProjectDiscovery Tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# URL Collection
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/amass@latest

# API Discovery
go install -v github.com/assetnote/kiterunner/cmd/kr@latest
go install -v github.com/ffuf/ffuf/v2@latest
```

## Verification

After installation, verify that everything is working correctly:

```bash
python3 vauban.py --check
```

You should see all required tools marked with a checkmark (✓).

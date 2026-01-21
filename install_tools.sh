#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  Vauban - Tool Installation Script                                           ║
# ║  The Scientific Breacher                                                      ║
# ║  Created by: Kassim Muhammad Atiku (R00TQU35T)                               ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

set -e

# Vauban Colors
CYAN='\033[96m'
MAGENTA='\033[95m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
RESET='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
██╗   ██╗ █████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗
██║   ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗████╗  ██║
██║   ██║███████║██║   ██║██████╔╝███████║██╔██╗ ██║
╚██╗ ██╔╝██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║
 ╚████╔╝ ██║  ██║╚██████╔╝██████╔╝██║  ██║██║ ╚████║
  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
EOF
echo -e "${MAGENTA}          ━━━ The Scientific Breacher ━━━${RESET}"
echo -e "${GREEN}              Tool Installation Script${RESET}"
echo ""

# Check Go
if ! command -v go &> /dev/null; then
    echo -e "${RED}[✗] Go is not installed. Please install Go first.${RESET}"
    echo "Visit: https://golang.org/dl/"
    exit 1
fi
echo -e "${GREEN}[✓] Go detected${RESET}"

echo -e "\n${CYAN}[◈] Installing ProjectDiscovery Suite...${RESET}"
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
echo -e "${GREEN}[✓] ProjectDiscovery Suite installed${RESET}"

echo -e "\n${CYAN}[◈] Installing URL Collection Tools...${RESET}"
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/assetfinder@latest
echo -e "${GREEN}[✓] URL tools installed${RESET}"

echo -e "\n${CYAN}[◈] Installing API Discovery Tools...${RESET}"
go install -v github.com/ffuf/ffuf/v2@latest
echo -e "${GREEN}[✓] ffuf installed${RESET}"

echo -e "\n${CYAN}[◈] Installing Python Tools...${RESET}"
pip3 install arjun uro --quiet
echo -e "${GREEN}[✓] Python tools installed${RESET}"

echo -e "\n${CYAN}[◈] Updating Nuclei Templates...${RESET}"
nuclei -update-templates -silent 2>/dev/null || true
echo -e "${GREEN}[✓] Templates updated${RESET}"

echo -e "\n${CYAN}[◈] Installing Python Dependencies...${RESET}"
pip3 install -r requirements.txt --quiet
echo -e "${GREEN}[✓] Python dependencies installed${RESET}"

echo -e "\n${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}[✓] All siege weapons deployed successfully!${RESET}"
echo -e "${CYAN}Run: python3 vauban.py --help${RESET}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${YELLOW}\"A fortress besieged by Vauban is a fortress taken\"${RESET}"

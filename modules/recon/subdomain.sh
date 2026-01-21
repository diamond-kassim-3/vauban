#!/bin/bash
# LostFuzzer v2.0 - Subdomain Enumeration Module
# ===============================================
# Combines multiple subdomain discovery tools for comprehensive enumeration.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <domain> <output_file>${RESET}"
    exit 1
fi

DOMAIN="$1"
OUTPUT="${2:-subdomains.txt}"
TEMP_DIR=$(mktemp -d)
THREADS="${3:-10}"

echo -e "${CYAN}[SUBDOMAIN] Starting enumeration for: ${DOMAIN}${RESET}"

# Function to check if tool exists
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${YELLOW}[WARN] $1 not found, skipping...${RESET}"
        return 1
    fi
    return 0
}

# Subfinder - Fast passive subdomain enumeration
run_subfinder() {
    if check_tool "subfinder"; then
        echo -e "${GREEN}[+] Running subfinder...${RESET}"
        subfinder -d "$DOMAIN" -silent -all -t "$THREADS" -o "$TEMP_DIR/subfinder.txt" 2>/dev/null || true
    fi
}

# Assetfinder - Quick subdomain finder
run_assetfinder() {
    if check_tool "assetfinder"; then
        echo -e "${GREEN}[+] Running assetfinder...${RESET}"
        assetfinder --subs-only "$DOMAIN" > "$TEMP_DIR/assetfinder.txt" 2>/dev/null || true
    fi
}

# Amass - Deep OSINT subdomain enumeration (passive only for speed)
run_amass() {
    if check_tool "amass"; then
        echo -e "${GREEN}[+] Running amass (passive mode)...${RESET}"
        timeout 300 amass enum -passive -d "$DOMAIN" -o "$TEMP_DIR/amass.txt" 2>/dev/null || true
    fi
}

# Findomain - Fast subdomain finder
run_findomain() {
    if check_tool "findomain"; then
        echo -e "${GREEN}[+] Running findomain...${RESET}"
        findomain -t "$DOMAIN" -q > "$TEMP_DIR/findomain.txt" 2>/dev/null || true
    fi
}

# crt.sh - Certificate Transparency logs
run_crtsh() {
    echo -e "${GREEN}[+] Querying crt.sh...${RESET}"
    curl -s "https://crt.sh/?q=%25.$DOMAIN&output=json" 2>/dev/null | \
        grep -oE '"name_value":"[^"]+"' | \
        cut -d'"' -f4 | \
        sed 's/\*\.//g' | \
        sort -u > "$TEMP_DIR/crtsh.txt" 2>/dev/null || true
}

# Run all tools in parallel
run_subfinder &
run_assetfinder &
run_amass &
run_findomain &
run_crtsh &

# Wait for all background jobs
wait

# Merge and deduplicate results
echo -e "${CYAN}[SUBDOMAIN] Merging results...${RESET}"

cat "$TEMP_DIR"/*.txt 2>/dev/null | \
    grep -v "^$" | \
    tr '[:upper:]' '[:lower:]' | \
    sort -u | \
    grep -E "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$" > "$OUTPUT"

# Count results
TOTAL=$(wc -l < "$OUTPUT" | tr -d ' ')

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[SUBDOMAIN] Found ${TOTAL} unique subdomains${RESET}"
echo -e "${GREEN}[SUBDOMAIN] Results saved to: ${OUTPUT}${RESET}"

echo "$TOTAL"

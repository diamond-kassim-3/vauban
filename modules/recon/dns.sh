#!/bin/bash
# LostFuzzer v2.0 - DNS Resolution Module
# ========================================
# Resolves subdomains and filters for live hosts.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <subdomains_file> <output_file>${RESET}"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-resolved.txt}"
THREADS="${3:-100}"
RESOLVERS="8.8.8.8,1.1.1.1,8.8.4.4"

if [ ! -f "$INPUT" ]; then
    echo -e "${RED}[ERROR] Input file not found: ${INPUT}${RESET}"
    exit 1
fi

echo -e "${CYAN}[DNS] Resolving subdomains...${RESET}"
TOTAL_INPUT=$(wc -l < "$INPUT" | tr -d ' ')
echo -e "${CYAN}[DNS] Processing ${TOTAL_INPUT} subdomains${RESET}"

# Check for dnsx
if command -v dnsx &> /dev/null; then
    echo -e "${GREEN}[+] Using dnsx for resolution...${RESET}"
    
    # Resolve and filter wildcards
    dnsx -l "$INPUT" \
        -silent \
        -t "$THREADS" \
        -r "$RESOLVERS" \
        -wd \
        -o "$OUTPUT" 2>/dev/null || true
        
elif command -v massdns &> /dev/null; then
    echo -e "${GREEN}[+] Using massdns for resolution...${RESET}"
    
    # Create resolvers file
    RESOLVERS_FILE=$(mktemp)
    echo -e "8.8.8.8\n1.1.1.1\n8.8.4.4\n9.9.9.9" > "$RESOLVERS_FILE"
    
    massdns -r "$RESOLVERS_FILE" \
        -t A \
        -o S \
        "$INPUT" 2>/dev/null | \
        awk '{print $1}' | \
        sed 's/\.$//' | \
        sort -u > "$OUTPUT"
    
    rm -f "$RESOLVERS_FILE"
    
else
    echo -e "${YELLOW}[WARN] dnsx/massdns not found, using basic resolution...${RESET}"
    
    # Fallback to basic dig resolution
    > "$OUTPUT"
    while read -r subdomain; do
        if host "$subdomain" &>/dev/null; then
            echo "$subdomain" >> "$OUTPUT"
        fi
    done < "$INPUT"
fi

# Count results
RESOLVED=$(wc -l < "$OUTPUT" 2>/dev/null | tr -d ' ')
RESOLVED=${RESOLVED:-0}

echo -e "${GREEN}[DNS] Resolved ${RESOLVED}/${TOTAL_INPUT} subdomains${RESET}"
echo -e "${GREEN}[DNS] Live hosts saved to: ${OUTPUT}${RESET}"

echo "$RESOLVED"

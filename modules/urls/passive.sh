#!/bin/bash
# LostFuzzer v2.0 - Passive URL Collection Module
# ================================================
# Collects URLs from archives and passive sources.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <targets_file> <output_file>${RESET}"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-passive_urls.txt}"
FILTERED_OUTPUT="${OUTPUT%.txt}_filtered.txt"
THREADS="${3:-10}"
TEMP_DIR=$(mktemp -d)

if [ ! -f "$INPUT" ]; then
    echo -e "${RED}[ERROR] Input file not found: ${INPUT}${RESET}"
    exit 1
fi

echo -e "${CYAN}[PASSIVE] Starting passive URL collection...${RESET}"
TOTAL_TARGETS=$(wc -l < "$INPUT" | tr -d ' ')
echo -e "${CYAN}[PASSIVE] Processing ${TOTAL_TARGETS} targets${RESET}"

# Function to check if tool exists
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${YELLOW}[WARN] $1 not found, skipping...${RESET}"
        return 1
    fi
    return 0
}

# gau - GetAllUrls (Wayback, CommonCrawl, AlienVault, URLScan)
run_gau() {
    if check_tool "gau"; then
        echo -e "${GREEN}[+] Running gau...${RESET}"
        cat "$INPUT" | gau --threads "$THREADS" --subs >> "$TEMP_DIR/gau.txt" 2>/dev/null || true
    fi
}

# waybackurls - Wayback Machine URLs
run_waybackurls() {
    if check_tool "waybackurls"; then
        echo -e "${GREEN}[+] Running waybackurls...${RESET}"
        cat "$INPUT" | waybackurls >> "$TEMP_DIR/waybackurls.txt" 2>/dev/null || true
    fi
}

# gauplus - Extended gau with more sources
run_gauplus() {
    if check_tool "gauplus"; then
        echo -e "${GREEN}[+] Running gauplus...${RESET}"
        cat "$INPUT" | gauplus --threads "$THREADS" >> "$TEMP_DIR/gauplus.txt" 2>/dev/null || true
    fi
}

# waymore - Enhanced wayback fetcher
run_waymore() {
    if check_tool "waymore"; then
        echo -e "${GREEN}[+] Running waymore...${RESET}"
        while read -r target; do
            waymore -i "$target" -mode U -oU "$TEMP_DIR/waymore_${target//[^a-zA-Z0-9]/_}.txt" 2>/dev/null || true
        done < "$INPUT"
    fi
}

# Run tools in parallel
run_gau &
run_waybackurls &

# Wait for all background jobs
wait

# Merge results
echo -e "${CYAN}[PASSIVE] Merging and deduplicating URLs...${RESET}"
cat "$TEMP_DIR"/*.txt 2>/dev/null | \
    grep -E "^https?://" | \
    sort -u > "$OUTPUT"

TOTAL_URLS=$(wc -l < "$OUTPUT" | tr -d ' ')
echo -e "${GREEN}[PASSIVE] Collected ${TOTAL_URLS} unique URLs${RESET}"

# Filter URLs with query parameters
echo -e "${CYAN}[PASSIVE] Filtering URLs with query parameters...${RESET}"
grep -E '\?[^=]+=.+$' "$OUTPUT" > "$TEMP_DIR/with_params.txt" 2>/dev/null || true

# Use uro for URL deduplication if available
if check_tool "uro"; then
    echo -e "${GREEN}[+] Running uro for smart deduplication...${RESET}"
    cat "$TEMP_DIR/with_params.txt" | uro > "$FILTERED_OUTPUT" 2>/dev/null || true
else
    # Basic deduplication
    sort -u "$TEMP_DIR/with_params.txt" > "$FILTERED_OUTPUT"
fi

FILTERED_COUNT=$(wc -l < "$FILTERED_OUTPUT" 2>/dev/null | tr -d ' ')
FILTERED_COUNT=${FILTERED_COUNT:-0}

# Remove unwanted file extensions
echo -e "${CYAN}[PASSIVE] Removing static file URLs...${RESET}"
STATIC_EXTENSIONS="jpg|jpeg|png|gif|svg|ico|css|woff|woff2|ttf|eot|mp4|mp3|pdf|doc|docx|xls|xlsx"
grep -vE "\.($STATIC_EXTENSIONS)(\?|$)" "$FILTERED_OUTPUT" > "$TEMP_DIR/clean.txt" 2>/dev/null || true
mv "$TEMP_DIR/clean.txt" "$FILTERED_OUTPUT"

FINAL_COUNT=$(wc -l < "$FILTERED_OUTPUT" 2>/dev/null | tr -d ' ')
FINAL_COUNT=${FINAL_COUNT:-0}

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[PASSIVE] Results:${RESET}"
echo -e "${GREEN}  - Total URLs: ${TOTAL_URLS}${RESET}"
echo -e "${GREEN}  - URLs with params: ${FINAL_COUNT}${RESET}"
echo -e "${GREEN}  - Saved to: ${OUTPUT}${RESET}"
echo -e "${GREEN}  - Filtered saved to: ${FILTERED_OUTPUT}${RESET}"

echo "$FINAL_COUNT"

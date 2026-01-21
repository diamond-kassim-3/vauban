#!/bin/bash
# LostFuzzer v2.0 - Active Crawler Module
# ========================================
# Active crawling using katana and hakrawler.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <targets_file> <output_file> [depth]${RESET}"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-crawled_urls.txt}"
JS_OUTPUT="${OUTPUT%.txt}_js.txt"
DEPTH="${3:-3}"
THREADS="${4:-10}"
TEMP_DIR=$(mktemp -d)

if [ ! -f "$INPUT" ]; then
    echo -e "${RED}[ERROR] Input file not found: ${INPUT}${RESET}"
    exit 1
fi

echo -e "${CYAN}[CRAWLER] Starting active crawling...${RESET}"
TOTAL_TARGETS=$(wc -l < "$INPUT" | tr -d ' ')
echo -e "${CYAN}[CRAWLER] Processing ${TOTAL_TARGETS} targets with depth ${DEPTH}${RESET}"

# Function to check if tool exists
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${YELLOW}[WARN] $1 not found, skipping...${RESET}"
        return 1
    fi
    return 0
}

# Katana - Next-gen web crawler
run_katana() {
    if check_tool "katana"; then
        echo -e "${GREEN}[+] Running katana...${RESET}"
        katana -list "$INPUT" \
            -silent \
            -depth "$DEPTH" \
            -js-crawl \
            -headless \
            -no-incognito \
            -concurrency "$THREADS" \
            -parallelism 5 \
            -rate-limit 150 \
            -timeout 10 \
            -retry 1 \
            -o "$TEMP_DIR/katana.txt" 2>/dev/null || true
        
        # Also output JS files separately
        katana -list "$INPUT" \
            -silent \
            -depth "$DEPTH" \
            -js-crawl \
            -ef css,png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot \
            -f js \
            -concurrency "$THREADS" \
            -o "$TEMP_DIR/katana_js.txt" 2>/dev/null || true
    fi
}

# Hakrawler - Fast web crawler
run_hakrawler() {
    if check_tool "hakrawler"; then
        echo -e "${GREEN}[+] Running hakrawler...${RESET}"
        cat "$INPUT" | hakrawler -d "$DEPTH" -t "$THREADS" -plain > "$TEMP_DIR/hakrawler.txt" 2>/dev/null || true
    fi
}

# GoSpider - Fast web spider
run_gospider() {
    if check_tool "gospider"; then
        echo -e "${GREEN}[+] Running gospider...${RESET}"
        gospider -S "$INPUT" \
            -d "$DEPTH" \
            -c "$THREADS" \
            --no-redirect \
            -t 5 \
            -o "$TEMP_DIR/gospider" 2>/dev/null || true
        
        # Merge gospider output
        cat "$TEMP_DIR/gospider"/* 2>/dev/null | grep -oE 'https?://[^ ]+' >> "$TEMP_DIR/gospider.txt" 2>/dev/null || true
    fi
}

# Run crawlers
run_katana
run_hakrawler
run_gospider

# Merge all results
echo -e "${CYAN}[CRAWLER] Merging crawled URLs...${RESET}"
cat "$TEMP_DIR"/*.txt 2>/dev/null | \
    grep -E "^https?://" | \
    sort -u > "$OUTPUT"

# Extract JS files
echo -e "${CYAN}[CRAWLER] Extracting JavaScript files...${RESET}"
grep -iE "\.js(\?|$)" "$OUTPUT" 2>/dev/null | sort -u > "$JS_OUTPUT" || true

TOTAL_URLS=$(wc -l < "$OUTPUT" | tr -d ' ')
JS_COUNT=$(wc -l < "$JS_OUTPUT" 2>/dev/null | tr -d ' ')
JS_COUNT=${JS_COUNT:-0}

# Filter for interesting endpoints
INTERESTING_OUTPUT="${OUTPUT%.txt}_interesting.txt"
echo -e "${CYAN}[CRAWLER] Filtering interesting endpoints...${RESET}"

# Patterns for interesting endpoints
grep -iE "(api|admin|auth|login|signup|register|token|graphql|rest|webhook|callback|upload|download|export|import|backup|config|setting|debug|test|internal|private|secret|hidden|dev|staging)" "$OUTPUT" 2>/dev/null | \
    sort -u > "$INTERESTING_OUTPUT" || true

INTERESTING_COUNT=$(wc -l < "$INTERESTING_OUTPUT" 2>/dev/null | tr -d ' ')
INTERESTING_COUNT=${INTERESTING_COUNT:-0}

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[CRAWLER] Results:${RESET}"
echo -e "${GREEN}  - Total URLs: ${TOTAL_URLS}${RESET}"
echo -e "${GREEN}  - JavaScript files: ${JS_COUNT}${RESET}"
echo -e "${GREEN}  - Interesting endpoints: ${INTERESTING_COUNT}${RESET}"
echo -e "${GREEN}  - Saved to: ${OUTPUT}${RESET}"
echo -e "${GREEN}  - JS files: ${JS_OUTPUT}${RESET}"

echo "$TOTAL_URLS"

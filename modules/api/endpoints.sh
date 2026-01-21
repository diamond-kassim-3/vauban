#!/bin/bash
# LostFuzzer v2.0 - API Endpoint Discovery Module
# ================================================
# Brute-force API endpoints using kiterunner and ffuf.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <targets_file> <output_file> [wordlist]${RESET}"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-api_endpoints.txt}"
WORDLIST="${3:-}"
THREADS="${4:-10}"
TEMP_DIR=$(mktemp -d)

if [ ! -f "$INPUT" ]; then
    echo -e "${RED}[ERROR] Input file not found: ${INPUT}${RESET}"
    exit 1
fi

echo -e "${CYAN}[API] Starting API endpoint discovery...${RESET}"
TOTAL_TARGETS=$(wc -l < "$INPUT" | tr -d ' ')
echo -e "${CYAN}[API] Processing ${TOTAL_TARGETS} targets${RESET}"

# Default API paths to check
API_PATHS="
/api
/api/v1
/api/v2
/api/v3
/v1
/v2
/v3
/rest
/rest/api
/graphql
/graphiql
/query
/graphql/console
/swagger
/swagger-ui
/swagger-ui.html
/swagger.json
/swagger.yaml
/openapi.json
/openapi.yaml
/api-docs
/api-docs.json
/docs
/redoc
/admin
/admin/api
/internal
/internal/api
/private
/private/api
/debug
/actuator
/actuator/health
/actuator/info
/actuator/beans
/actuator/env
/health
/healthcheck
/status
/info
/metrics
/config
/settings
/users
/user
/auth
/authenticate
/login
/logout
/register
/signup
/token
/oauth
/oauth2
/callback
/webhooks
/webhook
/.well-known
/.well-known/openapi.json
"

# Create temp wordlist if not provided
if [ -z "$WORDLIST" ] || [ ! -f "$WORDLIST" ]; then
    echo "$API_PATHS" | grep -v "^$" > "$TEMP_DIR/api_paths.txt"
    WORDLIST="$TEMP_DIR/api_paths.txt"
    echo -e "${YELLOW}[API] Using default API paths wordlist${RESET}"
fi

# Function to check if tool exists
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${YELLOW}[WARN] $1 not found, skipping...${RESET}"
        return 1
    fi
    return 0
}

# Kiterunner - Advanced API discovery
run_kiterunner() {
    if check_tool "kr"; then
        echo -e "${GREEN}[+] Running kiterunner...${RESET}"
        
        # Check for kite wordlists
        KITE_WORDLIST=""
        for path in ~/.kr/routes-large.kite ~/.kr/routes-small.kite /usr/share/kiterunner/routes-large.kite; do
            if [ -f "$path" ]; then
                KITE_WORDLIST="$path"
                break
            fi
        done
        
        if [ -n "$KITE_WORDLIST" ]; then
            echo -e "${GREEN}[+] Using kite wordlist: ${KITE_WORDLIST}${RESET}"
            while read -r target; do
                kr scan "$target" -w "$KITE_WORDLIST" -o text 2>/dev/null >> "$TEMP_DIR/kiterunner.txt" || true
            done < "$INPUT"
        else
            echo -e "${YELLOW}[WARN] No kite wordlist found, skipping kiterunner${RESET}"
        fi
    fi
}

# ffuf - Fast fuzzer
run_ffuf() {
    if check_tool "ffuf"; then
        echo -e "${GREEN}[+] Running ffuf...${RESET}"
        
        while read -r target; do
            target="${target%/}"
            ffuf -u "${target}/FUZZ" \
                -w "$WORDLIST" \
                -mc 200,201,202,204,301,302,307,401,403,405 \
                -t "$THREADS" \
                -timeout 5 \
                -r \
                -o "$TEMP_DIR/ffuf_$(echo "$target" | md5sum | cut -d' ' -f1).json" \
                -of json \
                -s 2>/dev/null || true
        done < "$INPUT"
        
        # Parse ffuf JSON output
        for json_file in "$TEMP_DIR"/ffuf_*.json; do
            if [ -f "$json_file" ]; then
                cat "$json_file" | jq -r '.results[]? | .url' 2>/dev/null >> "$TEMP_DIR/ffuf.txt" || true
            fi
        done
    fi
}

# dirsearch - Web path scanner
run_dirsearch() {
    if check_tool "dirsearch"; then
        echo -e "${GREEN}[+] Running dirsearch...${RESET}"
        
        dirsearch -l "$INPUT" \
            -w "$WORDLIST" \
            -t "$THREADS" \
            -e json,xml,yaml,yml \
            --format plain \
            -o "$TEMP_DIR/dirsearch.txt" \
            --quiet 2>/dev/null || true
    fi
}

# feroxbuster - Fast recursive content discovery
run_feroxbuster() {
    if check_tool "feroxbuster"; then
        echo -e "${GREEN}[+] Running feroxbuster...${RESET}"
        
        while read -r target; do
            feroxbuster -u "$target" \
                -w "$WORDLIST" \
                -t "$THREADS" \
                -s 200,201,202,204,301,302,307,401,403,405 \
                --no-recursion \
                -q \
                -o "$TEMP_DIR/feroxbuster.txt" 2>/dev/null || true
        done < "$INPUT"
    fi
}

# httpx probe for common API endpoints
run_httpx_probe() {
    if check_tool "httpx"; then
        echo -e "${GREEN}[+] Probing common API endpoints with httpx...${RESET}"
        
        # Generate URLs to probe
        > "$TEMP_DIR/probe_urls.txt"
        while read -r target; do
            target="${target%/}"
            while read -r path; do
                [ -n "$path" ] && echo "${target}${path}" >> "$TEMP_DIR/probe_urls.txt"
            done < "$WORDLIST"
        done < "$INPUT"
        
        httpx -l "$TEMP_DIR/probe_urls.txt" \
            -silent \
            -mc 200,201,202,204,301,302,307,401,403,405,500 \
            -t "$THREADS" \
            -o "$TEMP_DIR/httpx_probe.txt" 2>/dev/null || true
    fi
}

# Run discovery tools
run_httpx_probe
run_ffuf
run_kiterunner

# Merge results
echo -e "${CYAN}[API] Merging discovered endpoints...${RESET}"
cat "$TEMP_DIR"/*.txt 2>/dev/null | \
    grep -E "^https?://" | \
    sort -u > "$OUTPUT"

TOTAL_ENDPOINTS=$(wc -l < "$OUTPUT" | tr -d ' ')

# Categorize endpoints
AUTHENTICATED="${OUTPUT%.txt}_auth.txt"
INTERESTING="${OUTPUT%.txt}_interesting.txt"

# Find potentially authenticated endpoints
grep -iE "(admin|internal|private|auth|token|api-key|secret|debug|actuator)" "$OUTPUT" 2>/dev/null | \
    sort -u > "$AUTHENTICATED" || true

# Find interesting endpoints
grep -iE "(graphql|swagger|openapi|api-docs|webhook|callback|upload|download|export|config|settings|users|health|status)" "$OUTPUT" 2>/dev/null | \
    sort -u > "$INTERESTING" || true

AUTH_COUNT=$(wc -l < "$AUTHENTICATED" 2>/dev/null | tr -d ' ')
AUTH_COUNT=${AUTH_COUNT:-0}
INTERESTING_COUNT=$(wc -l < "$INTERESTING" 2>/dev/null | tr -d ' ')
INTERESTING_COUNT=${INTERESTING_COUNT:-0}

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[API] Results:${RESET}"
echo -e "${GREEN}  - Total endpoints: ${TOTAL_ENDPOINTS}${RESET}"
echo -e "${GREEN}  - Auth/Admin endpoints: ${AUTH_COUNT}${RESET}"
echo -e "${GREEN}  - Interesting endpoints: ${INTERESTING_COUNT}${RESET}"
echo -e "${GREEN}  - Saved to: ${OUTPUT}${RESET}"

echo "$TOTAL_ENDPOINTS"

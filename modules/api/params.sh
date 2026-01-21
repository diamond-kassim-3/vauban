#!/bin/bash
# LostFuzzer v2.0 - Parameter Discovery Module
# =============================================
# Discover hidden parameters using arjun and custom methods.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <urls_file> <output_dir>${RESET}"
    exit 1
fi

INPUT="$1"
OUTPUT_DIR="${2:-.}"
OUTPUT="${OUTPUT_DIR}/params_discovered.txt"
THREADS="${3:-5}"
TEMP_DIR=$(mktemp -d)

if [ ! -f "$INPUT" ]; then
    echo -e "${RED}[ERROR] Input file not found: ${INPUT}${RESET}"
    exit 1
fi

echo -e "${CYAN}[PARAMS] Starting parameter discovery...${RESET}"
TOTAL_URLS=$(wc -l < "$INPUT" | tr -d ' ')
echo -e "${CYAN}[PARAMS] Processing ${TOTAL_URLS} URLs${RESET}"

# Common parameters to test
COMMON_PARAMS="
id
user_id
user
username
email
name
token
key
api_key
apikey
api_token
access_token
auth
password
pass
secret
session
sessionid
redirect
redirect_url
return
return_url
next
url
callback
file
filename
path
page
limit
offset
sort
order
filter
search
query
q
debug
test
admin
action
cmd
command
exec
code
data
input
output
format
type
category
ref
item
product
account
org
organization
team
group
project
"

# Create common params wordlist
echo "$COMMON_PARAMS" | grep -v "^$" | sort -u > "$TEMP_DIR/common_params.txt"

# Function to check if tool exists
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${YELLOW}[WARN] $1 not found, skipping...${RESET}"
        return 1
    fi
    return 0
}

# Arjun - HTTP parameter discovery
run_arjun() {
    if check_tool "arjun"; then
        echo -e "${GREEN}[+] Running arjun...${RESET}"
        
        # Limit to first 50 URLs for speed
        head -n 50 "$INPUT" > "$TEMP_DIR/arjun_input.txt"
        
        arjun -i "$TEMP_DIR/arjun_input.txt" \
            -t "$THREADS" \
            -o "$TEMP_DIR/arjun_results.json" \
            --stable \
            -q 2>/dev/null || true
        
        # Parse arjun results
        if [ -f "$TEMP_DIR/arjun_results.json" ]; then
            cat "$TEMP_DIR/arjun_results.json" | jq -r 'to_entries[] | "\(.key) -> \(.value | join(", "))"' 2>/dev/null >> "$TEMP_DIR/arjun.txt" || true
        fi
    fi
}

# x8 - Hidden parameter discovery
run_x8() {
    if check_tool "x8"; then
        echo -e "${GREEN}[+] Running x8...${RESET}"
        
        while read -r url; do
            x8 -u "$url" \
                -w "$TEMP_DIR/common_params.txt" \
                -o "$TEMP_DIR/x8_$(echo "$url" | md5sum | cut -d' ' -f1).txt" 2>/dev/null || true
        done < <(head -n 30 "$INPUT")
    fi
}

# param-miner using ffuf
run_param_miner() {
    if check_tool "ffuf"; then
        echo -e "${GREEN}[+] Mining parameters with ffuf...${RESET}"
        
        while read -r url; do
            # Extract base URL and existing params
            base_url=$(echo "$url" | cut -d'?' -f1)
            
            # Test GET parameters
            ffuf -u "${base_url}?FUZZ=test" \
                -w "$TEMP_DIR/common_params.txt" \
                -mc 200,201,301,302,401,403,500 \
                -fs 0 \
                -t 10 \
                -timeout 5 \
                -o "$TEMP_DIR/ffuf_params_$(echo "$url" | md5sum | cut -d' ' -f1).json" \
                -of json \
                -s 2>/dev/null || true
                
        done < <(head -n 20 "$INPUT")
        
        # Parse ffuf results
        for json_file in "$TEMP_DIR"/ffuf_params_*.json; do
            if [ -f "$json_file" ]; then
                cat "$json_file" | jq -r '.results[]? | "\(.input.FUZZ)"' 2>/dev/null >> "$TEMP_DIR/ffuf_params.txt" || true
            fi
        done
    fi
}

# Extract existing parameters from URLs
extract_existing_params() {
    echo -e "${GREEN}[+] Extracting existing parameters from URLs...${RESET}"
    
    grep -oE '\?[^#\s]+' "$INPUT" 2>/dev/null | \
        tr '&' '\n' | \
        sed 's/^?//' | \
        cut -d'=' -f1 | \
        sort -u > "$TEMP_DIR/existing_params.txt" || true
}

# Run all methods
extract_existing_params
run_arjun
run_param_miner

# Merge results
echo -e "${CYAN}[PARAMS] Merging discovered parameters...${RESET}"

# Combine all found parameters
cat "$TEMP_DIR"/*.txt 2>/dev/null | \
    grep -v "^$" | \
    sort -u > "$OUTPUT"

TOTAL_PARAMS=$(wc -l < "$OUTPUT" | tr -d ' ')

# Create summary of interesting parameters
INTERESTING_PARAMS="${OUTPUT_DIR}/params_interesting.txt"
grep -iE "(token|key|secret|password|auth|api|admin|debug|redirect|callback|url|file|path|cmd|exec)" "$OUTPUT" 2>/dev/null | \
    sort -u > "$INTERESTING_PARAMS" || true

INTERESTING_COUNT=$(wc -l < "$INTERESTING_PARAMS" 2>/dev/null | tr -d ' ')
INTERESTING_COUNT=${INTERESTING_COUNT:-0}

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[PARAMS] Results:${RESET}"
echo -e "${GREEN}  - Total parameters: ${TOTAL_PARAMS}${RESET}"
echo -e "${GREEN}  - Interesting parameters: ${INTERESTING_COUNT}${RESET}"
echo -e "${GREEN}  - Saved to: ${OUTPUT}${RESET}"

echo "$TOTAL_PARAMS"

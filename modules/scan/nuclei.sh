#!/bin/bash
# LostFuzzer v2.0 - Nuclei Scanning Module
# =========================================
# Comprehensive vulnerability scanning using nuclei.

set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Usage: $0 <urls_file> <output_dir> [mode]${RESET}"
    echo -e "${YELLOW}Modes: dast, cves, full, takeover, exposures${RESET}"
    exit 1
fi

INPUT="$1"
OUTPUT_DIR="${2:-.}"
MODE="${3:-full}"
THREADS="${4:-25}"
RATE_LIMIT="${5:-150}"

if [ ! -f "$INPUT" ]; then
    echo -e "${RED}[ERROR] Input file not found: ${INPUT}${RESET}"
    exit 1
fi

# Check nuclei is installed
if ! command -v nuclei &> /dev/null; then
    echo -e "${RED}[ERROR] nuclei is not installed${RESET}"
    exit 1
fi

echo -e "${CYAN}[NUCLEI] Starting vulnerability scanning (mode: ${MODE})...${RESET}"
TOTAL_URLS=$(wc -l < "$INPUT" | tr -d ' ')
echo -e "${CYAN}[NUCLEI] Processing ${TOTAL_URLS} URLs${RESET}"

# Update nuclei templates
echo -e "${GREEN}[+] Updating nuclei templates...${RESET}"
nuclei -update-templates -silent 2>/dev/null || true

# Output files
OUTPUT_JSON="${OUTPUT_DIR}/nuclei_results.json"
OUTPUT_TXT="${OUTPUT_DIR}/nuclei_results.txt"
OUTPUT_SARIF="${OUTPUT_DIR}/nuclei_results.sarif"

# Common nuclei flags
COMMON_FLAGS="-l $INPUT -t $THREADS -rl $RATE_LIMIT -silent -json -stats -si 60"

case "$MODE" in
    dast)
        echo -e "${GREEN}[+] Running DAST scan...${RESET}"
        nuclei $COMMON_FLAGS \
            -dast \
            -retries 2 \
            -timeout 10 \
            -o "$OUTPUT_JSON" 2>/dev/null || true
        ;;
    
    cves)
        echo -e "${GREEN}[+] Running CVE scan...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags cve \
            -severity medium,high,critical \
            -o "$OUTPUT_JSON" 2>/dev/null || true
        ;;
    
    takeover)
        echo -e "${GREEN}[+] Running subdomain takeover scan...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags takeover \
            -o "$OUTPUT_JSON" 2>/dev/null || true
        ;;
    
    exposures)
        echo -e "${GREEN}[+] Running exposure scan...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags exposure,config,backup,database \
            -o "$OUTPUT_JSON" 2>/dev/null || true
        ;;
    
    api)
        echo -e "${GREEN}[+] Running API vulnerability scan...${RESET}"
        # Run API-specific templates
        nuclei $COMMON_FLAGS \
            -tags api,graphql,swagger,openapi \
            -o "${OUTPUT_DIR}/nuclei_api.json" 2>/dev/null || true
        
        # Also run general vulnerability scan on API endpoints
        nuclei $COMMON_FLAGS \
            -severity medium,high,critical \
            -tags sqli,xss,ssrf,lfi,rce,idor,auth-bypass \
            -o "${OUTPUT_DIR}/nuclei_vuln.json" 2>/dev/null || true
        
        # Merge results
        cat "${OUTPUT_DIR}/nuclei_api.json" "${OUTPUT_DIR}/nuclei_vuln.json" 2>/dev/null > "$OUTPUT_JSON" || true
        ;;
    
    full|*)
        echo -e "${GREEN}[+] Running full scan...${RESET}"
        
        # Step 1: Technology detection
        echo -e "${GREEN}[+] Phase 1: Technology detection...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags tech \
            -o "${OUTPUT_DIR}/nuclei_tech.json" 2>/dev/null || true
        
        # Step 2: CVEs and known vulnerabilities
        echo -e "${GREEN}[+] Phase 2: CVE scanning...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags cve \
            -severity high,critical \
            -o "${OUTPUT_DIR}/nuclei_cves.json" 2>/dev/null || true
        
        # Step 3: Exposures and misconfigurations
        echo -e "${GREEN}[+] Phase 3: Exposure scanning...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags exposure,misconfig,config,backup,database,default-login \
            -o "${OUTPUT_DIR}/nuclei_exposures.json" 2>/dev/null || true
        
        # Step 4: DAST scanning
        echo -e "${GREEN}[+] Phase 4: DAST scanning...${RESET}"
        nuclei $COMMON_FLAGS \
            -dast \
            -retries 1 \
            -o "${OUTPUT_DIR}/nuclei_dast.json" 2>/dev/null || true
        
        # Step 5: Fuzzing templates
        echo -e "${GREEN}[+] Phase 5: Fuzzing...${RESET}"
        nuclei $COMMON_FLAGS \
            -tags fuzz \
            -severity medium,high,critical \
            -o "${OUTPUT_DIR}/nuclei_fuzz.json" 2>/dev/null || true
        
        # Merge all results
        cat "${OUTPUT_DIR}"/nuclei_*.json 2>/dev/null | sort -u > "$OUTPUT_JSON" || true
        ;;
esac

# Convert JSON to text format
echo -e "${CYAN}[NUCLEI] Converting results to text format...${RESET}"
if [ -f "$OUTPUT_JSON" ]; then
    cat "$OUTPUT_JSON" | jq -r 'select(.info.severity) | "[\(.info.severity | ascii_upcase)] \(.info.name) - \(.host) (\(.matched-at // .url // .host))"' 2>/dev/null | \
        sort -u > "$OUTPUT_TXT" || true
fi

# Count findings by severity
echo -e "${CYAN}[NUCLEI] Analyzing results...${RESET}"
CRITICAL=$(grep -ci "critical" "$OUTPUT_JSON" 2>/dev/null || echo "0")
HIGH=$(grep -ci '"severity":"high"' "$OUTPUT_JSON" 2>/dev/null || echo "0")
MEDIUM=$(grep -ci '"severity":"medium"' "$OUTPUT_JSON" 2>/dev/null || echo "0")
LOW=$(grep -ci '"severity":"low"' "$OUTPUT_JSON" 2>/dev/null || echo "0")
INFO=$(grep -ci '"severity":"info"' "$OUTPUT_JSON" 2>/dev/null || echo "0")
TOTAL=$((CRITICAL + HIGH + MEDIUM + LOW + INFO))

# Create summary
SUMMARY_FILE="${OUTPUT_DIR}/nuclei_summary.txt"
cat > "$SUMMARY_FILE" << EOF
╔══════════════════════════════════════════════════════════╗
║              NUCLEI SCAN SUMMARY                        ║
╠══════════════════════════════════════════════════════════╣
║ Mode: ${MODE}
║ URLs Scanned: ${TOTAL_URLS}
║ Total Findings: ${TOTAL}
╠══════════════════════════════════════════════════════════╣
║ CRITICAL: ${CRITICAL}
║ HIGH: ${HIGH}
║ MEDIUM: ${MEDIUM}
║ LOW: ${LOW}
║ INFO: ${INFO}
╚══════════════════════════════════════════════════════════╝
EOF

cat "$SUMMARY_FILE"

echo -e "${GREEN}[NUCLEI] Results:${RESET}"
echo -e "${GREEN}  - JSON: ${OUTPUT_JSON}${RESET}"
echo -e "${GREEN}  - Text: ${OUTPUT_TXT}${RESET}"
echo -e "${GREEN}  - Summary: ${SUMMARY_FILE}${RESET}"

echo "$TOTAL"

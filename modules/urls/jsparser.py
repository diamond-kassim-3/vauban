#!/usr/bin/env python3
"""
LostFuzzer v2.0 - JavaScript Parser Module
===========================================
Extract endpoints, secrets, and sensitive data from JavaScript files.
"""

import re
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import urljoin, urlparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class JSParser:
    """Parse JavaScript files to extract endpoints and secrets."""
    
    # Regex patterns for endpoint extraction
    ENDPOINT_PATTERNS = [
        # API paths
        r'["\'](/api/[^"\'>\s]+)["\']',
        r'["\'](/v[0-9]+/[^"\'>\s]+)["\']',
        r'["\'](/rest/[^"\'>\s]+)["\']',
        r'["\'](/graphql[^"\'>\s]*)["\']',
        
        # Full URLs
        r'["\'](https?://[^"\'>\s]+)["\']',
        
        # Relative paths
        r'["\'](/[a-zA-Z0-9_\-]+/[^"\'>\s]*)["\']',
        
        # URL in template literals
        r'`(/[^`]+)`',
        r'`(https?://[^`]+)`',
        
        # fetch/axios calls
        r'fetch\s*\(\s*["\']([^"\']+)["\']',
        r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
        r'\.get\s*\(\s*["\']([^"\']+)["\']',
        r'\.post\s*\(\s*["\']([^"\']+)["\']',
        r'\.put\s*\(\s*["\']([^"\']+)["\']',
        r'\.delete\s*\(\s*["\']([^"\']+)["\']',
        
        # XMLHttpRequest
        r'\.open\s*\(\s*["\'][A-Z]+["\']\s*,\s*["\']([^"\']+)["\']',
    ]
    
    # Secret patterns
    SECRET_PATTERNS = {
        'aws_access_key': r'(?:AKIA|AIPA|AROA|ASIA)[A-Z0-9]{16}',
        'aws_secret_key': r'(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)["\'\s]*[:=]\s*["\']?([A-Za-z0-9+/]{40})["\']?',
        'api_key': r'(?:api[_-]?key|apikey)["\'\s]*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?',
        'api_secret': r'(?:api[_-]?secret|apisecret)["\'\s]*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?',
        'bearer_token': r'[Bb]earer\s+([A-Za-z0-9_\-\.]+)',
        'jwt': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
        'private_key': r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
        'google_api': r'AIza[0-9A-Za-z_\-]{35}',
        'firebase': r'AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}',
        'stripe_key': r'(?:sk|pk)_(?:test|live)_[A-Za-z0-9]{24,}',
        'github_token': r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}',
        'slack_token': r'xox[baprs]-[A-Za-z0-9-]+',
        'slack_webhook': r'https://hooks\.slack\.com/services/[A-Za-z0-9/]+',
        'discord_webhook': r'https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',
        'twilio_sid': r'AC[a-z0-9]{32}',
        'sendgrid': r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
        'mailgun': r'key-[A-Za-z0-9]{32}',
        'basic_auth': r'(?:basic|authorization)["\'\s]*[:=]\s*["\']?([A-Za-z0-9+/=]{20,})["\']?',
        'password': r'(?:password|passwd|pwd)["\'\s]*[:=]\s*["\']([^"\']{6,})["\']',
        'database_url': r'(?:postgres|mysql|mongodb)://[^\s"\'<>]+',
        'internal_ip': r'(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)[0-9.]+',
        's3_bucket': r'(?:s3://|s3\.amazonaws\.com/)[a-zA-Z0-9._-]+',
    }
    
    # Interesting keywords
    INTERESTING_KEYWORDS = [
        'admin', 'debug', 'test', 'internal', 'private', 'secret',
        'token', 'key', 'password', 'auth', 'login', 'signup',
        'register', 'api', 'graphql', 'webhook', 'callback',
        'upload', 'download', 'export', 'import', 'backup',
        'config', 'setting', 'hidden', 'staging', 'dev', 'beta'
    ]
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_js(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch JavaScript file content."""
        try:
            response = self.session.get(url, timeout=timeout, verify=False)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        return None
    
    def extract_endpoints(self, content: str, base_url: str = "") -> Set[str]:
        """Extract potential endpoints from JavaScript content."""
        endpoints = set()
        
        for pattern in self.ENDPOINT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                endpoint = match.strip()
                
                # Skip obvious false positives
                if self._is_valid_endpoint(endpoint):
                    # Make absolute URL if base_url provided
                    if base_url and endpoint.startswith('/'):
                        endpoint = urljoin(base_url, endpoint)
                    endpoints.add(endpoint)
        
        return endpoints
    
    def extract_secrets(self, content: str) -> List[Dict]:
        """Extract potential secrets from JavaScript content."""
        secrets = []
        
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                secret_value = match if isinstance(match, str) else match[0]
                
                # Skip if too short or likely false positive
                if len(secret_value) > 8:
                    secrets.append({
                        'type': secret_type,
                        'value': secret_value[:50] + ('...' if len(secret_value) > 50 else ''),
                        'full_value': secret_value
                    })
        
        return secrets
    
    def find_interesting_lines(self, content: str) -> List[Dict]:
        """Find lines containing interesting keywords."""
        interesting = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in self.INTERESTING_KEYWORDS:
                if keyword in line_lower:
                    # Extract context
                    context = line.strip()[:200]
                    if context:
                        interesting.append({
                            'keyword': keyword,
                            'line': i + 1,
                            'context': context
                        })
                    break
        
        return interesting
    
    def _is_valid_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is valid and not a false positive."""
        if not endpoint or len(endpoint) < 2:
            return False
        
        # Skip file extensions unlikely to be endpoints
        invalid_extensions = ['.css', '.png', '.jpg', '.gif', '.svg', '.ico', '.woff', '.ttf']
        for ext in invalid_extensions:
            if endpoint.lower().endswith(ext):
                return False
        
        # Skip if it's just a hash or fragment
        if endpoint.startswith('#'):
            return False
        
        return True
    
    def parse_file(self, js_url: str) -> Dict:
        """Parse a single JavaScript file."""
        result = {
            'url': js_url,
            'endpoints': [],
            'secrets': [],
            'interesting': []
        }
        
        content = self.fetch_js(js_url)
        if not content:
            return result
        
        # Get base URL for resolving relative paths
        parsed = urlparse(js_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Extract findings
        result['endpoints'] = list(self.extract_endpoints(content, base_url))
        result['secrets'] = self.extract_secrets(content)
        result['interesting'] = self.find_interesting_lines(content)[:20]  # Limit
        
        return result
    
    def parse_files(self, js_urls: List[str], max_workers: int = 10) -> Dict:
        """Parse multiple JavaScript files in parallel."""
        results = {
            'files_processed': 0,
            'total_endpoints': 0,
            'total_secrets': 0,
            'endpoints': [],
            'secrets': [],
            'files': []
        }
        
        print(f"[JS] Parsing {len(js_urls)} JavaScript files...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.parse_file, url): url for url in js_urls}
            
            for future in as_completed(futures):
                try:
                    file_result = future.result()
                    results['files_processed'] += 1
                    
                    if file_result['endpoints'] or file_result['secrets']:
                        results['files'].append(file_result)
                        results['endpoints'].extend(file_result['endpoints'])
                        results['secrets'].extend(file_result['secrets'])
                except Exception as e:
                    pass
        
        # Deduplicate
        results['endpoints'] = list(set(results['endpoints']))
        results['total_endpoints'] = len(results['endpoints'])
        results['total_secrets'] = len(results['secrets'])
        
        return results
    
    def run(self, js_file_list: str) -> Dict:
        """Main entry point - parse JS files from a list."""
        js_urls = []
        
        with open(js_file_list, 'r') as f:
            js_urls = [line.strip() for line in f if line.strip()]
        
        if not js_urls:
            print("[JS] No JavaScript files to parse")
            return {}
        
        results = self.parse_files(js_urls)
        
        # Save results
        output_file = f"{self.output_dir}/js_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save endpoints separately
        endpoints_file = f"{self.output_dir}/js_endpoints.txt"
        with open(endpoints_file, 'w') as f:
            for endpoint in sorted(results['endpoints']):
                f.write(f"{endpoint}\n")
        
        # Save secrets separately
        if results['secrets']:
            secrets_file = f"{self.output_dir}/js_secrets.json"
            with open(secrets_file, 'w') as f:
                json.dump(results['secrets'], f, indent=2)
        
        print(f"[JS] Processed: {results['files_processed']} files")
        print(f"[JS] Endpoints found: {results['total_endpoints']}")
        print(f"[JS] Secrets found: {results['total_secrets']}")
        
        return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: jsparser.py <js_files_list> [output_dir]")
        sys.exit(1)
    
    js_file_list = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    parser = JSParser(output_dir)
    results = parser.run(js_file_list)
    
    print(f"\n[JS] Results saved to: {output_dir}/js_analysis.json")


if __name__ == "__main__":
    main()

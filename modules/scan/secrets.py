#!/usr/bin/env python3
"""
LostFuzzer v2.0 - Secret Detection Module
==========================================
Detect exposed secrets, API keys, and sensitive data.
"""

import re
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class SecretDetector:
    """Detect secrets in web responses."""
    
    SECRET_PATTERNS = {
        'aws_access_key': (r'(?:AKIA|AIPA|AROA|ASIA)[A-Z0-9]{16}', 'critical'),
        'gcp_api_key': (r'AIza[0-9A-Za-z_\-]{35}', 'high'),
        'api_key': (r'(?:api[_-]?key)["\'\s]*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?', 'high'),
        'bearer_token': (r'[Bb]earer\s+([A-Za-z0-9_\-\.]{20,})', 'critical'),
        'jwt_token': (r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*', 'high'),
        'github_token': (r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}', 'critical'),
        'slack_token': (r'xox[baprs]-[A-Za-z0-9-]+', 'critical'),
        'slack_webhook': (r'https://hooks\.slack\.com/services/[A-Za-z0-9/]+', 'high'),
        'discord_webhook': (r'https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+', 'high'),
        'stripe_key': (r'(?:sk|pk)_(?:test|live)_[A-Za-z0-9]{24,}', 'critical'),
        'twilio_sid': (r'AC[a-z0-9]{32}', 'high'),
        'sendgrid': (r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}', 'high'),
        'mailgun': (r'key-[A-Za-z0-9]{32}', 'high'),
        'postgres_uri': (r'postgres(?:ql)?://[^\s"\'<>]+', 'critical'),
        'mysql_uri': (r'mysql://[^\s"\'<>]+', 'critical'),
        'mongodb_uri': (r'mongodb(?:\+srv)?://[^\s"\'<>]+', 'critical'),
        'private_key': (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', 'critical'),
        'password_field': (r'(?:password|passwd)["\'\s]*[:=]\s*["\']([^"\']{6,50})["\']', 'high'),
        'firebase': (r'AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}', 'high'),
        's3_bucket': (r's3://[a-zA-Z0-9._-]+', 'medium'),
        'internal_ip': (r'(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)[0-9.]+', 'low'),
    }
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0'
        self.session.verify = False
    
    def scan_content(self, content: str, url: str = "") -> List[Dict]:
        secrets = []
        for secret_type, (pattern, severity) in self.SECRET_PATTERNS.items():
            for match in re.findall(pattern, content, re.IGNORECASE):
                value = match if isinstance(match, str) else match[0]
                if value and len(value) >= 8 and not self._is_false_positive(value):
                    secrets.append({
                        'type': secret_type, 'value': self._mask(value),
                        'url': url, 'severity': severity
                    })
        return secrets
    
    def scan_url(self, url: str) -> List[Dict]:
        try:
            r = self.session.get(url, timeout=10)
            return self.scan_content(r.text, url) if r.status_code == 200 else []
        except: return []
    
    def _is_false_positive(self, v: str) -> bool:
        return any(x in v.lower() for x in ['example', 'test', 'demo', 'xxx']) or len(set(v)) < 4
    
    def _mask(self, v: str) -> str:
        return v[:4] + '...' + v[-4:] if len(v) > 8 else '*' * len(v)
    
    def run(self, urls_file: str) -> Dict:
        with open(urls_file) as f:
            urls = [l.strip() for l in f if l.strip()]
        
        results = {'urls_scanned': 0, 'secrets_found': 0, 'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}, 'secrets': []}
        
        print(f"[SECRETS] Scanning {len(urls)} URLs...")
        with ThreadPoolExecutor(max_workers=10) as ex:
            for secrets in ex.map(self.scan_url, urls):
                results['urls_scanned'] += 1
                for s in secrets:
                    results['secrets'].append(s)
                    results['secrets_found'] += 1
                    results['by_severity'][s['severity']] += 1
        
        with open(f"{self.output_dir}/secrets_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[SECRETS] Found {results['secrets_found']} secrets (Critical: {results['by_severity']['critical']})")
        return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: secrets.py <urls_file> [output_dir]")
        sys.exit(1)
    import urllib3; urllib3.disable_warnings()
    SecretDetector(sys.argv[2] if len(sys.argv) > 2 else ".").run(sys.argv[1])

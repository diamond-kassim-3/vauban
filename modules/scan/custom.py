#!/usr/bin/env python3
"""
LostFuzzer v2.0 - Custom Vulnerability Checks
==============================================
Custom checks for IDOR, BOLA, Rate Limiting, etc.
"""

import sys
import json
import requests
import re
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs, urlencode

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class CustomVulnChecker:
    """Custom vulnerability detection beyond Nuclei."""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0'
        self.session.verify = False
        self.timeout = 10
        self.findings = []
    
    def check_idor(self, url: str) -> List[Dict]:
        """Check for IDOR by manipulating ID parameters."""
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        id_params = ['id', 'user_id', 'uid', 'account_id', 'order_id', 'item_id', 'doc_id', 'file_id']
        
        for param in id_params:
            if param in params:
                original_val = params[param][0]
                test_vals = ['1', '0', str(int(original_val) + 1 if original_val.isdigit() else 0)]
                
                for test_val in test_vals:
                    if test_val == original_val:
                        continue
                    
                    new_params = params.copy()
                    new_params[param] = [test_val]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(new_params, doseq=True)}"
                    
                    try:
                        r1 = self.session.get(url, timeout=self.timeout)
                        r2 = self.session.get(test_url, timeout=self.timeout)
                        
                        if r2.status_code == 200 and len(r2.text) > 100:
                            if r1.text != r2.text:
                                findings.append({
                                    'type': 'IDOR',
                                    'url': url,
                                    'param': param,
                                    'test_url': test_url,
                                    'severity': 'high',
                                    'details': f'Different response when changing {param}'
                                })
                    except:
                        pass
        return findings
    
    def check_rate_limit(self, url: str, requests_count: int = 50) -> List[Dict]:
        """Check for rate limiting issues."""
        findings = []
        success_count = 0
        
        try:
            for _ in range(requests_count):
                r = self.session.get(url, timeout=5)
                if r.status_code == 200:
                    success_count += 1
            
            if success_count >= requests_count * 0.9:
                findings.append({
                    'type': 'No Rate Limiting',
                    'url': url,
                    'severity': 'medium',
                    'details': f'{success_count}/{requests_count} requests succeeded'
                })
        except:
            pass
        return findings
    
    def check_cors(self, url: str) -> List[Dict]:
        """Check for CORS misconfigurations."""
        findings = []
        origins = ['https://evil.com', 'null', 'https://attacker.com']
        
        for origin in origins:
            try:
                r = self.session.get(url, headers={'Origin': origin}, timeout=self.timeout)
                acao = r.headers.get('Access-Control-Allow-Origin', '')
                acac = r.headers.get('Access-Control-Allow-Credentials', '')
                
                if origin in acao or acao == '*':
                    severity = 'high' if acac.lower() == 'true' else 'medium'
                    findings.append({
                        'type': 'CORS Misconfiguration',
                        'url': url,
                        'severity': severity,
                        'details': f'Origin {origin} reflected, Credentials: {acac}'
                    })
                    break
            except:
                pass
        return findings
    
    def check_graphql_introspection(self, url: str) -> List[Dict]:
        """Check for GraphQL introspection enabled."""
        findings = []
        graphql_paths = ['/graphql', '/api/graphql', '/v1/graphql']
        
        query = {'query': '{ __schema { types { name } } }'}
        
        base_url = url.rstrip('/')
        for path in graphql_paths:
            try:
                r = self.session.post(f"{base_url}{path}", json=query, timeout=self.timeout)
                if r.status_code == 200 and '__schema' in r.text:
                    findings.append({
                        'type': 'GraphQL Introspection',
                        'url': f"{base_url}{path}",
                        'severity': 'medium',
                        'details': 'Introspection query enabled'
                    })
            except:
                pass
        return findings
    
    def check_verb_tampering(self, url: str) -> List[Dict]:
        """Check for HTTP verb tampering issues."""
        findings = []
        methods = ['PUT', 'DELETE', 'PATCH', 'OPTIONS', 'TRACE']
        
        try:
            get_resp = self.session.get(url, timeout=self.timeout)
            
            for method in methods:
                try:
                    r = self.session.request(method, url, timeout=self.timeout)
                    if r.status_code in [200, 201, 204]:
                        if method == 'TRACE' and url in r.text:
                            findings.append({
                                'type': 'HTTP TRACE Enabled',
                                'url': url,
                                'severity': 'low',
                                'details': 'TRACE method reflects request'
                            })
                        elif method in ['PUT', 'DELETE', 'PATCH']:
                            findings.append({
                                'type': 'Verb Tampering',
                                'url': url,
                                'severity': 'medium',
                                'details': f'{method} method allowed'
                            })
                except:
                    pass
        except:
            pass
        return findings
    
    def check_security_headers(self, url: str) -> List[Dict]:
        """Check for missing security headers."""
        findings = []
        
        required_headers = {
            'X-Frame-Options': 'Clickjacking protection',
            'X-Content-Type-Options': 'MIME sniffing protection',
            'Strict-Transport-Security': 'HTTPS enforcement',
            'Content-Security-Policy': 'XSS protection',
            'X-XSS-Protection': 'Legacy XSS protection'
        }
        
        try:
            r = self.session.get(url, timeout=self.timeout)
            missing = []
            
            for header, desc in required_headers.items():
                if header.lower() not in [h.lower() for h in r.headers.keys()]:
                    missing.append(header)
            
            if missing:
                findings.append({
                    'type': 'Missing Security Headers',
                    'url': url,
                    'severity': 'low',
                    'details': f'Missing: {", ".join(missing)}'
                })
        except:
            pass
        return findings
    
    def scan_url(self, url: str) -> List[Dict]:
        """Run all checks on a URL."""
        all_findings = []
        all_findings.extend(self.check_cors(url))
        all_findings.extend(self.check_security_headers(url))
        all_findings.extend(self.check_idor(url))
        return all_findings
    
    def run(self, urls_file: str) -> Dict:
        """Run all custom checks on URLs from file."""
        with open(urls_file) as f:
            urls = [l.strip() for l in f if l.strip()][:100]  # Limit
        
        results = {
            'urls_checked': 0,
            'findings': 0,
            'by_type': {},
            'vulnerabilities': []
        }
        
        print(f"[CUSTOM] Running custom checks on {len(urls)} URLs...")
        
        with ThreadPoolExecutor(max_workers=5) as ex:
            for findings in ex.map(self.scan_url, urls):
                results['urls_checked'] += 1
                for f in findings:
                    results['vulnerabilities'].append(f)
                    results['findings'] += 1
                    t = f['type']
                    results['by_type'][t] = results['by_type'].get(t, 0) + 1
        
        # Check GraphQL on unique hosts
        hosts = list(set([urlparse(u).netloc for u in urls]))[:20]
        for host in hosts:
            for finding in self.check_graphql_introspection(f"https://{host}"):
                results['vulnerabilities'].append(finding)
                results['findings'] += 1
        
        with open(f"{self.output_dir}/custom_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[CUSTOM] Found {results['findings']} issues")
        return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: custom.py <urls_file> [output_dir]")
        sys.exit(1)
    import urllib3; urllib3.disable_warnings()
    CustomVulnChecker(sys.argv[2] if len(sys.argv) > 2 else ".").run(sys.argv[1])

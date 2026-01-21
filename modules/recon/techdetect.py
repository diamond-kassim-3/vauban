#!/usr/bin/env python3
"""
LostFuzzer v2.0 - Technology Detection Module
==============================================
Fingerprint technologies, frameworks, and WAFs on targets.
"""

import subprocess
import json
import re
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TechDetector:
    """Detect technologies and frameworks on web targets."""
    
    # Common technology signatures
    TECH_SIGNATURES = {
        'frameworks': {
            'express': ['x-powered-by: express', 'express'],
            'django': ['csrftoken', 'django', 'x-frame-options: deny'],
            'flask': ['werkzeug', 'flask'],
            'rails': ['x-runtime', 'x-request-id', 'ruby'],
            'laravel': ['laravel_session', 'xsrf-token'],
            'spring': ['x-application-context', 'spring'],
            'fastapi': ['fastapi', 'starlette'],
            'nextjs': ['x-nextjs', '__next'],
            'nuxt': ['nuxt', '__nuxt'],
        },
        'servers': {
            'nginx': ['nginx', 'server: nginx'],
            'apache': ['apache', 'server: apache'],
            'iis': ['server: microsoft-iis', 'x-aspnet'],
            'cloudflare': ['cf-ray', 'cf-cache-status'],
            'aws': ['x-amz-', 'amazons3', 'awselb'],
        },
        'cms': {
            'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
            'drupal': ['drupal', 'x-drupal-cache'],
            'joomla': ['joomla', '/administrator'],
        },
        'api': {
            'graphql': ['/graphql', 'graphiql', 'apollo'],
            'swagger': ['swagger', 'openapi', '/api-docs'],
            'rest': ['/api/v', '/rest/', 'application/json'],
        },
        'waf': {
            'cloudflare': ['cf-ray', '__cfduid'],
            'akamai': ['akamai', 'x-akamai'],
            'aws_waf': ['x-amzn-waf'],
            'imperva': ['incap_ses', 'visid_incap'],
            'sucuri': ['sucuri', 'x-sucuri'],
            'modsecurity': ['mod_security', 'modsecurity'],
        }
    }
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.results = {}
    
    def detect_with_httpx(self, targets_file: str) -> Dict:
        """Use httpx for technology detection."""
        output_file = f"{self.output_dir}/tech_httpx.json"
        
        try:
            cmd = f"httpx -l {targets_file} -silent -json -tech-detect -status-code -title -web-server -o {output_file}"
            subprocess.run(cmd, shell=True, capture_output=True, timeout=600)
            
            results = []
            if Path(output_file).exists():
                with open(output_file, 'r') as f:
                    for line in f:
                        try:
                            results.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            return {'httpx': results}
        except Exception as e:
            print(f"[TECH] httpx detection failed: {e}")
            return {}
    
    def analyze_headers(self, url: str, headers: Dict) -> Dict:
        """Analyze HTTP headers for technology signatures."""
        detected = {
            'frameworks': [],
            'servers': [],
            'cms': [],
            'api': [],
            'waf': []
        }
        
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        headers_str = json.dumps(headers_lower)
        
        for category, signatures in self.TECH_SIGNATURES.items():
            for tech, patterns in signatures.items():
                for pattern in patterns:
                    if pattern.lower() in headers_str:
                        if tech not in detected[category]:
                            detected[category].append(tech)
                        break
        
        return detected
    
    def detect_api_docs(self, targets: List[str]) -> List[Dict]:
        """Check for exposed API documentation endpoints."""
        api_doc_paths = [
            '/swagger.json',
            '/swagger.yaml',
            '/swagger-ui.html',
            '/swagger-ui/',
            '/openapi.json',
            '/openapi.yaml',
            '/api-docs',
            '/api-docs.json',
            '/v1/swagger.json',
            '/v2/swagger.json',
            '/v3/swagger.json',
            '/docs',
            '/redoc',
            '/graphql',
            '/graphiql',
            '/playground',
            '/.well-known/openapi.json',
        ]
        
        found_docs = []
        
        for target in targets:
            target = target.rstrip('/')
            urls_to_check = [f"{target}{path}" for path in api_doc_paths]
            
            # Create temp file with URLs
            temp_file = f"{self.output_dir}/api_doc_urls.txt"
            with open(temp_file, 'w') as f:
                for url in urls_to_check:
                    f.write(f"{url}\n")
            
            try:
                cmd = f"httpx -l {temp_file} -silent -mc 200 -o {self.output_dir}/found_api_docs.txt"
                subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
                
                if Path(f"{self.output_dir}/found_api_docs.txt").exists():
                    with open(f"{self.output_dir}/found_api_docs.txt", 'r') as f:
                        for line in f:
                            url = line.strip()
                            if url:
                                found_docs.append({
                                    'target': target,
                                    'url': url,
                                    'type': self._identify_doc_type(url)
                                })
            except Exception as e:
                print(f"[TECH] API doc detection failed for {target}: {e}")
        
        return found_docs
    
    def _identify_doc_type(self, url: str) -> str:
        """Identify the type of API documentation."""
        url_lower = url.lower()
        
        if 'swagger' in url_lower:
            return 'swagger'
        elif 'openapi' in url_lower:
            return 'openapi'
        elif 'graphql' in url_lower or 'graphiql' in url_lower or 'playground' in url_lower:
            return 'graphql'
        elif 'redoc' in url_lower:
            return 'redoc'
        else:
            return 'unknown'
    
    def run(self, targets_file: str) -> Dict:
        """Run full technology detection."""
        print("[TECH] Starting technology detection...")
        
        results = {
            'technologies': [],
            'api_docs': [],
            'summary': {
                'frameworks': {},
                'servers': {},
                'waf_detected': []
            }
        }
        
        # Run httpx tech detection
        httpx_results = self.detect_with_httpx(targets_file)
        
        if 'httpx' in httpx_results:
            for item in httpx_results['httpx']:
                tech_item = {
                    'url': item.get('url', ''),
                    'status': item.get('status_code', 0),
                    'title': item.get('title', ''),
                    'server': item.get('webserver', ''),
                    'technologies': item.get('tech', []),
                }
                results['technologies'].append(tech_item)
                
                # Update summary
                for tech in item.get('tech', []):
                    tech_lower = tech.lower()
                    for category in ['frameworks', 'servers']:
                        for tech_name in self.TECH_SIGNATURES.get(category, {}).keys():
                            if tech_name in tech_lower:
                                if tech_name not in results['summary'][category]:
                                    results['summary'][category][tech_name] = 0
                                results['summary'][category][tech_name] += 1
        
        # Check for API documentation
        targets = []
        with open(targets_file, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
        
        if targets:
            results['api_docs'] = self.detect_api_docs(targets[:50])  # Limit to 50 for speed
        
        print(f"[TECH] Detected {len(results['technologies'])} hosts with technology info")
        print(f"[TECH] Found {len(results['api_docs'])} exposed API documentation endpoints")
        
        # Save results
        output_file = f"{self.output_dir}/tech_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: techdetect.py <targets_file> [output_dir]")
        sys.exit(1)
    
    targets_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    detector = TechDetector(output_dir)
    results = detector.run(targets_file)
    
    print(f"\n[TECH] Results saved to: {output_dir}/tech_results.json")


if __name__ == "__main__":
    main()

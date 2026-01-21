#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║  ██╗   ██╗ █████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗                        ║
║  ██║   ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗████╗  ██║                        ║
║  ██║   ██║███████║██║   ██║██████╔╝███████║██╔██╗ ██║                        ║
║  ╚██╗ ██╔╝██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║                        ║
║   ╚████╔╝ ██║  ██║╚██████╔╝██████╔╝██║  ██║██║ ╚████║                        ║
║    ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝                        ║
║                                                                               ║
║                    ━━━ The Scientific Breacher ━━━                           ║
║                                                                               ║
║  "A fortress besieged by Vauban is a fortress taken"                         ║
║                                                                               ║
║  Created by: Kassim Muhammad Atiku                                           ║
║  Credentials: CC, CEH, CSI, CISSP, CISO, ECCS                               ║
║  Known as: R00TQU35T                                                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Vauban - Advanced Bug Hunting Automation System
================================================

Named after Sébastien Le Prestre de Vauban (1633-1707), the legendary French 
military engineer who revolutionized siege warfare. Like its namesake who 
never lost a siege, Vauban systematically identifies and breaches security 
fortifications with mathematical precision.

Usage:
    python3 vauban.py --input domains.txt --mode full
    python3 vauban.py --input api_endpoints.txt --mode api
    python3 vauban.py --input target.com --mode quick
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.utils import (
    load_config, create_output_dir, read_file_lines, write_file_lines,
    merge_files, check_tool_installed, get_missing_tools, count_file_lines
)
from lib.logger import Logger, log
from lib.notifier import Notifier


class Vauban:
    """
    Vauban - The Scientific Breacher
    
    Main orchestrator for the bug hunting system.
    Like the legendary siege engineer, systematically breaches security fortifications.
    """
    
    REQUIRED_TOOLS = ['httpx', 'nuclei']
    OPTIONAL_TOOLS = ['subfinder', 'gau', 'katana', 'ffuf', 'arjun', 'dnsx']
    
    def __init__(self, args):
        self.args = args
        self.config = load_config('config/settings.yaml') if os.path.exists('config/settings.yaml') else {}
        self.logger = Logger(verbose=args.verbose)
        self.output_dir = None
        self.stats = {
            'target': args.input,
            'subdomains': 0,
            'live_hosts': 0,
            'urls': 0,
            'api_endpoints': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'secrets': 0,
            'report_path': ''
        }
    
    def check_requirements(self) -> bool:
        """Check if required tools are installed."""
        missing = get_missing_tools(self.REQUIRED_TOOLS)
        if missing:
            self.logger.error(f"Missing required tools: {', '.join(missing)}")
            return False
        
        optional_missing = get_missing_tools(self.OPTIONAL_TOOLS)
        if optional_missing:
            self.logger.warning(f"Optional tools not found: {', '.join(optional_missing)}")
        
        return True
    
    def setup_output(self) -> str:
        """Create output directory structure."""
        target_name = self.args.input.replace('https://', '').replace('http://', '').replace('/', '_')
        self.output_dir = create_output_dir(self.args.output, target_name)
        self.logger.info(f"Siege output: {self.output_dir}")
        return self.output_dir
    
    def run_module(self, script: str, *args, timeout: int = 600) -> tuple:
        """Run a shell module script."""
        script_path = os.path.join(os.path.dirname(__file__), script)
        
        if not os.path.exists(script_path):
            self.logger.warning(f"Module not found: {script}")
            return "", "", 1
        
        cmd = f"bash {script_path} {' '.join(str(a) for a in args)}"
        
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                timeout=timeout, cwd=os.path.dirname(__file__)
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Module timed out: {script}")
            return "", "Timeout", -1
        except Exception as e:
            return "", str(e), -1
    
    def run_python_module(self, script: str, *args) -> bool:
        """Run a Python module."""
        script_path = os.path.join(os.path.dirname(__file__), script)
        
        if not os.path.exists(script_path):
            self.logger.warning(f"Module not found: {script}")
            return False
        
        cmd = f"python3 {script_path} {' '.join(str(a) for a in args)}"
        
        try:
            subprocess.run(cmd, shell=True, timeout=600, cwd=os.path.dirname(__file__))
            return True
        except Exception as e:
            self.logger.warning(f"Module error: {e}")
            return False
    
    def prepare_input(self) -> str:
        """Prepare input file for processing."""
        input_path = self.args.input
        targets_file = os.path.join(self.output_dir, 'targets.txt')
        
        if os.path.isfile(input_path):
            shutil.copy(input_path, targets_file)
        else:
            with open(targets_file, 'w') as f:
                f.write(f"{input_path}\n")
        
        return targets_file
    
    def phase_recon(self, targets_file: str) -> str:
        """Phase 1: Reconnaissance - Mapping the fortress."""
        self.logger.section("PHASE 1: RECONNAISSANCE ◈ Mapping the Fortress")
        
        subdomains_file = os.path.join(self.output_dir, 'recon', 'subdomains.txt')
        resolved_file = os.path.join(self.output_dir, 'recon', 'resolved.txt')
        live_file = os.path.join(self.output_dir, 'recon', 'live_hosts.txt')
        
        targets = read_file_lines(targets_file)
        
        if self.args.mode in ['full', 'recon']:
            self.logger.info("Enumerating subdomains (outer fortifications)...")
            for target in targets:
                domain = target.replace('https://', '').replace('http://', '').split('/')[0]
                self.run_module('modules/recon/subdomain.sh', domain, subdomains_file)
            
            self.stats['subdomains'] = count_file_lines(subdomains_file)
            self.logger.success(f"Mapped {self.stats['subdomains']} subdomains")
            
            if count_file_lines(subdomains_file) > 0:
                self.logger.info("Resolving DNS (identifying active bastions)...")
                self.run_module('modules/recon/dns.sh', subdomains_file, resolved_file)
        else:
            shutil.copy(targets_file, subdomains_file)
        
        self.logger.info("Probing for live hosts (active defenses)...")
        input_for_probe = resolved_file if os.path.exists(resolved_file) else subdomains_file
        if not os.path.exists(input_for_probe):
            input_for_probe = targets_file
        
        cmd = f"httpx -l {input_for_probe} -silent -t 50 -o {live_file}"
        subprocess.run(cmd, shell=True, capture_output=True)
        
        self.stats['live_hosts'] = count_file_lines(live_file)
        self.logger.success(f"Identified {self.stats['live_hosts']} live hosts")
        
        if self.args.mode == 'full' and count_file_lines(live_file) > 0:
            self.logger.info("Fingerprinting technologies (analyzing defenses)...")
            self.run_python_module('modules/recon/techdetect.py', live_file, os.path.join(self.output_dir, 'recon'))
        
        return live_file
    
    def phase_url_discovery(self, live_file: str) -> str:
        """Phase 2: URL Discovery - Digging the parallels."""
        self.logger.section("PHASE 2: URL DISCOVERY ◈ Digging the Parallels")
        
        passive_file = os.path.join(self.output_dir, 'urls', 'passive_urls.txt')
        crawled_file = os.path.join(self.output_dir, 'urls', 'crawled_urls.txt')
        js_file = os.path.join(self.output_dir, 'urls', 'js_files.txt')
        all_urls_file = os.path.join(self.output_dir, 'urls', 'all_urls.txt')
        
        if count_file_lines(live_file) == 0:
            self.logger.warning("No live hosts - fortress appears abandoned")
            return all_urls_file
        
        self.logger.info("Collecting passive URLs (historical intelligence)...")
        self.run_module('modules/urls/passive.sh', live_file, passive_file, timeout=900)
        
        if self.args.mode == 'full':
            self.logger.info("Active crawling (scouting the perimeter)...")
            self.run_module('modules/urls/crawler.sh', live_file, crawled_file, '3', timeout=900)
        
        input_files = [f for f in [passive_file, crawled_file] if os.path.exists(f)]
        if input_files:
            merge_files(input_files, all_urls_file, unique=True)
        
        self.stats['urls'] = count_file_lines(all_urls_file)
        self.logger.success(f"Collected {self.stats['urls']} unique URLs")
        
        if os.path.exists(js_file) and count_file_lines(js_file) > 0:
            self.logger.info("Analyzing JavaScript (decrypting communications)...")
            self.run_python_module('modules/urls/jsparser.py', js_file, os.path.join(self.output_dir, 'urls'))
        
        return all_urls_file
    
    def phase_api_discovery(self, live_file: str, urls_file: str) -> str:
        """Phase 3: API Discovery - Finding the weak points."""
        self.logger.section("PHASE 3: API DISCOVERY ◈ Finding Weak Points")
        
        api_endpoints_file = os.path.join(self.output_dir, 'api', 'api_endpoints.txt')
        
        if self.args.mode in ['full', 'api']:
            if count_file_lines(live_file) > 0:
                self.logger.info("Brute-forcing API endpoints (probing the walls)...")
                self.run_module('modules/api/endpoints.sh', live_file, api_endpoints_file, timeout=600)
            
            self.logger.info("Detecting OpenAPI/Swagger (finding blueprints)...")
            self.run_python_module('modules/api/openapi.py', live_file, os.path.join(self.output_dir, 'api'))
            
            if count_file_lines(urls_file) > 0:
                self.logger.info("Discovering hidden parameters (secret passages)...")
                self.run_module('modules/api/params.sh', urls_file, os.path.join(self.output_dir, 'api'), timeout=300)
        
        self.stats['api_endpoints'] = count_file_lines(api_endpoints_file)
        self.logger.success(f"Discovered {self.stats['api_endpoints']} API endpoints")
        
        return api_endpoints_file
    
    def phase_scanning(self, urls_file: str):
        """Phase 4: Vulnerability Scanning - The calculated breach."""
        self.logger.section("PHASE 4: VULNERABILITY SCANNING ◈ The Calculated Breach")
        
        scan_dir = os.path.join(self.output_dir, 'scan')
        
        if count_file_lines(urls_file) == 0:
            self.logger.warning("No targets for breach - fortress impenetrable")
            return
        
        self.logger.info("Running Nuclei DAST (siege artillery)...")
        scan_mode = 'api' if self.args.mode == 'api' else 'full'
        self.run_module('modules/scan/nuclei.sh', urls_file, scan_dir, scan_mode, timeout=1800)
        
        self.logger.info("Scanning for exposed secrets (intercepting couriers)...")
        self.run_python_module('modules/scan/secrets.py', urls_file, scan_dir)
        
        self.logger.info("Running custom checks (specialized sappers)...")
        self.run_python_module('modules/scan/custom.py', urls_file, scan_dir)
        
        self._load_scan_results(scan_dir)
    
    def _load_scan_results(self, scan_dir: str):
        """Load scan results and update stats."""
        import json
        
        secrets_file = os.path.join(scan_dir, 'secrets_results.json')
        if os.path.exists(secrets_file):
            try:
                with open(secrets_file) as f:
                    data = json.load(f)
                    self.stats['secrets'] = data.get('secrets_found', 0)
                    self.stats['critical'] += data.get('by_severity', {}).get('critical', 0)
                    self.stats['high'] += data.get('by_severity', {}).get('high', 0)
            except:
                pass
        
        custom_file = os.path.join(scan_dir, 'custom_results.json')
        if os.path.exists(custom_file):
            try:
                with open(custom_file) as f:
                    data = json.load(f)
                    self.stats['medium'] += data.get('findings', 0)
            except:
                pass
    
    def phase_reporting(self):
        """Phase 5: Generate Reports - Victory documentation."""
        self.logger.section("PHASE 5: REPORTING ◈ Documenting the Victory")
        
        scan_dir = os.path.join(self.output_dir, 'scan')
        for f in os.listdir(scan_dir):
            if f.endswith('.json'):
                shutil.copy(os.path.join(scan_dir, f), self.output_dir)
        
        self.logger.info("Generating siege report...")
        self.run_python_module('modules/report/generator.py', self.output_dir, self.args.input)
        
        self.stats['report_path'] = os.path.join(self.output_dir, 'report.html')
        
        if self.args.notify:
            self._send_notifications()
    
    def _send_notifications(self):
        """Send scan completion notifications."""
        try:
            notifier = Notifier(self.config)
            message = f"⚔️ Vauban siege complete for {self.args.input}\n"
            message += f"Breach points: {self.stats['critical']} critical, {self.stats['high']} high"
            notifier.send_all(message)
            self.logger.success("Notifications dispatched")
        except Exception as e:
            self.logger.warning(f"Notification failed: {e}")
    
    def run(self):
        """Execute the full siege operation."""
        self.logger.banner()
        
        if not self.check_requirements():
            sys.exit(1)
        
        self.setup_output()
        targets_file = self.prepare_input()
        
        try:
            # Phase 1: Reconnaissance
            live_file = self.phase_recon(targets_file)
            
            # Phase 2: URL Discovery
            urls_file = self.phase_url_discovery(live_file)
            
            # Phase 3: API Discovery
            api_file = self.phase_api_discovery(live_file, urls_file)
            
            # Merge all discovered URLs
            all_targets = os.path.join(self.output_dir, 'all_targets.txt')
            merge_files([urls_file, api_file], all_targets, unique=True)
            
            # Phase 4: Scanning
            self.phase_scanning(all_targets)
            
            # Phase 5: Reporting
            self.phase_reporting()
            
            # Final summary
            self.logger.summary(self.stats)
            
        except KeyboardInterrupt:
            self.logger.warning("Siege aborted by commander")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Siege failed: {e}")
            if self.args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


def check_tools():
    """Check if all required and optional tools are installed."""
    from lib.logger import Logger
    from lib.utils import check_tool_installed
    
    logger = Logger(verbose=True)
    logger.banner()
    
    print()
    logger.section("TOOL VERIFICATION ◈ Checking Arsenal")
    
    # Required tools
    required = {
        'httpx': 'HTTP probing and technology detection',
        'nuclei': 'Vulnerability scanning with templates',
    }
    
    # Optional tools with descriptions
    optional = {
        'subfinder': 'Subdomain enumeration',
        'assetfinder': 'Additional subdomain sources',
        'amass': 'Advanced subdomain enumeration',
        'dnsx': 'DNS resolution and wildcard detection',
        'gau': 'Fetch URLs from AlienVault, Wayback, CommonCrawl',
        'waybackurls': 'Fetch URLs from Wayback Machine',
        'katana': 'Next-gen web crawler',
        'hakrawler': 'Fast web crawler',
        'gospider': 'Web spider with various features',
        'ffuf': 'Fast fuzzer for directories, parameters',
        'arjun': 'Hidden HTTP parameter discovery',
        'uro': 'URL deduplication and filtering',
    }
    
    all_ok = True
    missing_required = []
    missing_optional = []
    
    print()
    print("[REQUIRED TOOLS]")
    print("-" * 50)
    for tool, desc in required.items():
        if check_tool_installed(tool):
            print(f"  ✓ {tool:15} │ {desc}")
        else:
            print(f"  ✗ {tool:15} │ {desc} [MISSING]")
            missing_required.append(tool)
            all_ok = False
    
    print()
    print("[OPTIONAL TOOLS]")
    print("-" * 50)
    for tool, desc in optional.items():
        if check_tool_installed(tool):
            print(f"  ✓ {tool:15} │ {desc}")
        else:
            print(f"  ○ {tool:15} │ {desc} [NOT FOUND]")
            missing_optional.append(tool)
    
    print()
    print("-" * 50)
    
    if missing_required:
        print()
        print("⚠️  CRITICAL: Missing required tools!")
        print("   Install with: ./install_tools.sh")
        print()
        print("   Or manually install:")
        for tool in missing_required:
            if tool == 'httpx':
                print(f"     go install github.com/projectdiscovery/httpx/cmd/httpx@latest")
            elif tool == 'nuclei':
                print(f"     go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
        return False
    
    if missing_optional:
        print()
        print("ℹ️  Some optional tools are missing.")
        print("   Vauban will still work but with reduced functionality.")
        print("   Install missing tools with: ./install_tools.sh")
    else:
        print()
        print("✓ All tools are installed and ready!")
    
    print()
    print("━" * 50)
    print(f"Required: {len(required) - len(missing_required)}/{len(required)} installed")
    print(f"Optional: {len(optional) - len(missing_optional)}/{len(optional)} installed")
    print("━" * 50)
    
    return all_ok


def main():
    parser = argparse.ArgumentParser(
        description="Vauban - The Scientific Breacher | Advanced Bug Hunting Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔═══════════════════════════════════════════════════════════════╗
║  "A fortress besieged by Vauban is a fortress taken"         ║
║                                                               ║
║  Created by: Kassim Muhammad Atiku (R00TQU35T)               ║
║  Credentials: CC, CEH, CSI, CISSP, CISO, ECCS                ║
║  Organization: NHT Corporations                              ║
║  GitHub: https://github.com/diamond-kassim-3/vauban          ║
╚═══════════════════════════════════════════════════════════════╝

Examples:
  python3 vauban.py --check                     # Verify tool installation
  python3 vauban.py --input domains.txt --mode full
  python3 vauban.py --input https://example.com --mode quick
  python3 vauban.py --input api_endpoints.txt --mode api --notify
        """
    )
    
    parser.add_argument('--check', action='store_true',
                        help='Verify all required and optional tools are installed')
    parser.add_argument('-i', '--input',
                        help='Target domain, URL, or file containing targets')
    parser.add_argument('-m', '--mode', choices=['full', 'quick', 'api', 'recon'],
                        default='full', help='Siege mode (default: full)')
    parser.add_argument('-o', '--output', default='./output',
                        help='Output directory (default: ./output)')
    parser.add_argument('-t', '--threads', type=int, default=10,
                        help='Number of threads (default: 10)')
    parser.add_argument('--notify', action='store_true',
                        help='Send notifications on completion')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Handle --check command
    if args.check:
        success = check_tools()
        sys.exit(0 if success else 1)
    
    # Require input for normal operation
    if not args.input:
        parser.error("--input is required unless using --check")
    
    vauban = Vauban(args)
    vauban.run()


if __name__ == "__main__":
    main()


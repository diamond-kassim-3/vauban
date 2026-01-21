#!/usr/bin/env python3
"""
Vauban - Report Generator
==========================
Generate HTML reports with Vauban color theme.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ReportGenerator:
    """Generate comprehensive siege reports with Vauban styling."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.data = {}
    
    def load_results(self) -> Dict:
        """Load all result files from output directory."""
        results = {
            'nuclei': [],
            'secrets': [],
            'custom': [],
            'tech': {},
            'openapi': {},
            'js_analysis': {},
            'stats': {}
        }
        
        files = {
            'nuclei_results.json': 'nuclei',
            'secrets_results.json': 'secrets',
            'custom_results.json': 'custom',
            'tech_results.json': 'tech',
            'openapi_results.json': 'openapi',
            'js_analysis.json': 'js_analysis'
        }
        
        for filename, key in files.items():
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath) as f:
                        results[key] = json.load(f)
                except:
                    pass
        
        return results
    
    def generate_html(self, target: str, results: Dict) -> str:
        """Generate HTML report with Vauban styling."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nuclei_count = len(results.get('nuclei', []))
        secrets_count = results.get('secrets', {}).get('secrets_found', 0)
        custom_count = results.get('custom', {}).get('findings', 0)
        total = nuclei_count + secrets_count + custom_count
        
        critical = results.get('secrets', {}).get('by_severity', {}).get('critical', 0)
        high = results.get('secrets', {}).get('by_severity', {}).get('high', 0)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vauban Siege Report - {target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Consolas', 'Monaco', monospace; 
            background: #0C0C0C; 
            color: #B0B0B0; 
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        /* Header */
        .header {{ 
            background: linear-gradient(135deg, #0C0C0C, #1A1A1A); 
            border: 1px solid #00FFFF; 
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            text-align: center;
        }}
        .header h1 {{ 
            color: #00FFFF; 
            font-size: 2.5em; 
            text-shadow: 0 0 10px #00FFFF;
            margin-bottom: 10px;
        }}
        .header .subtitle {{ color: #FF00FF; font-size: 1.2em; }}
        .header .meta {{ color: #666; margin-top: 15px; font-size: 0.9em; }}
        .header .quote {{ 
            color: #FFD700; 
            font-style: italic; 
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        /* Stats Grid */
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; 
            margin-bottom: 20px; 
        }}
        .stat-card {{ 
            background: #1A1A1A; 
            border: 1px solid #333;
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            transition: all 0.3s;
        }}
        .stat-card:hover {{
            border-color: #00FFFF;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
        }}
        .stat-card .number {{ font-size: 2.5em; font-weight: bold; }}
        .stat-card .label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .stat-card.critical .number {{ color: #FF0000; text-shadow: 0 0 10px #FF0000; }}
        .stat-card.high .number {{ color: #FF6600; }}
        .stat-card.medium .number {{ color: #FFCC00; }}
        .stat-card.total .number {{ color: #00FFFF; }}
        .stat-card.secrets .number {{ color: #FF00FF; }}
        
        /* Sections */
        .section {{ 
            background: #1A1A1A; 
            border: 1px solid #333;
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px; 
        }}
        .section h2 {{ 
            color: #00FFFF; 
            margin-bottom: 20px; 
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section h2::before {{
            content: "◈";
            color: #FF00FF;
        }}
        
        /* Findings */
        .finding {{ 
            background: #0C0C0C; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 10px; 
            border-left: 4px solid #00FFFF;
            transition: all 0.3s;
        }}
        .finding:hover {{
            background: #151515;
        }}
        .finding.critical {{ border-left-color: #FF0000; }}
        .finding.high {{ border-left-color: #FF6600; }}
        .finding.medium {{ border-left-color: #FFCC00; }}
        .finding.low {{ border-left-color: #00FF41; }}
        .finding h3 {{ color: #FFFFFF; margin-bottom: 8px; font-size: 1em; }}
        .finding .url {{ color: #666; word-break: break-all; font-size: 0.85em; }}
        .finding .details {{ color: #888; margin-top: 5px; font-size: 0.9em; }}
        
        /* Severity Badges */
        .severity {{ 
            padding: 4px 12px; 
            border-radius: 4px; 
            font-size: 0.75em; 
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 10px;
        }}
        .severity.critical {{ background: #FF0000; color: #FFF; }}
        .severity.high {{ background: #FF6600; color: #FFF; }}
        .severity.medium {{ background: #FFCC00; color: #000; }}
        .severity.low {{ background: #00FF41; color: #000; }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid #333;
            margin-top: 40px;
        }}
        .footer .brand {{ color: #00FFFF; font-size: 1.2em; margin-bottom: 10px; }}
        .footer .author {{ color: #FF00FF; }}
        
        /* No findings */
        .no-findings {{ 
            color: #666; 
            text-align: center; 
            padding: 40px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚔️ VAUBAN SIEGE REPORT</h1>
            <div class="subtitle">━━━ The Scientific Breacher ━━━</div>
            <div class="meta">Target: {target} | Siege completed: {timestamp}</div>
            <div class="quote">"A fortress besieged by Vauban is a fortress taken"</div>
        </div>
        
        <div class="stats">
            <div class="stat-card total">
                <div class="number">{total}</div>
                <div class="label">Total Findings</div>
            </div>
            <div class="stat-card critical">
                <div class="number">{critical}</div>
                <div class="label">Critical</div>
            </div>
            <div class="stat-card high">
                <div class="number">{high}</div>
                <div class="label">High</div>
            </div>
            <div class="stat-card medium">
                <div class="number">{custom_count}</div>
                <div class="label">Medium</div>
            </div>
            <div class="stat-card secrets">
                <div class="number">{secrets_count}</div>
                <div class="label">Secrets</div>
            </div>
        </div>
'''
        
        # Secrets Section
        secrets = results.get('secrets', {}).get('secrets', [])
        if secrets:
            html += '''
        <div class="section">
            <h2>Exposed Secrets</h2>
'''
            for s in secrets[:20]:
                sev = s.get('severity', 'medium')
                html += f'''
            <div class="finding {sev}">
                <h3><span class="severity {sev}">{sev}</span> {s.get('type', 'Unknown')}</h3>
                <div class="url">{s.get('url', '')}</div>
                <div class="details">Value: <code>{s.get('value', '')}</code></div>
            </div>
'''
            html += '</div>'
        
        # Custom Findings
        custom = results.get('custom', {}).get('vulnerabilities', [])
        if custom:
            html += '''
        <div class="section">
            <h2>Vulnerability Findings</h2>
'''
            for c in custom[:20]:
                sev = c.get('severity', 'medium')
                html += f'''
            <div class="finding {sev}">
                <h3><span class="severity {sev}">{sev}</span> {c.get('type', 'Unknown')}</h3>
                <div class="url">{c.get('url', '')}</div>
                <div class="details">{c.get('details', '')}</div>
            </div>
'''
            html += '</div>'
        
        # Footer
        html += '''
        <div class="footer">
            <div class="brand">VAUBAN - The Scientific Breacher</div>
            <div class="author">Created by Kassim Muhammad Atiku (R00TQU35T)</div>
            <div>CC, CEH, CSI, CISSP, CISO, ECCS</div>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def generate(self, target: str) -> Dict:
        """Generate all report formats."""
        results = self.load_results()
        
        html = self.generate_html(target, results)
        html_path = os.path.join(self.output_dir, 'report.html')
        with open(html_path, 'w') as f:
            f.write(html)
        
        summary = {
            'tool': 'Vauban',
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'author': 'Kassim Muhammad Atiku (R00TQU35T)',
            'findings': {
                'total': 0,
                'critical': results.get('secrets', {}).get('by_severity', {}).get('critical', 0),
                'high': results.get('secrets', {}).get('by_severity', {}).get('high', 0)
            }
        }
        
        json_path = os.path.join(self.output_dir, 'report_summary.json')
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"[REPORT] HTML siege report: {html_path}")
        print(f"[REPORT] JSON summary: {json_path}")
        
        return {'html': html_path, 'json': json_path}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generator.py <output_dir> <target>")
        sys.exit(1)
    
    ReportGenerator(sys.argv[1]).generate(sys.argv[2])

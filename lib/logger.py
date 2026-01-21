"""
Vauban - Logging System with Vauban Color Palette
==================================================
Rich console logging with hacker aesthetic colors.
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.style import Style
from rich.theme import Theme
from datetime import datetime
import sys

# Vauban Color Palette
VAUBAN_THEME = Theme({
    "info": "cyan",
    "success": "#00FF41",       # Matrix Green
    "warning": "#FFD700",       # Gold
    "error": "#FF3131",         # Neon Red
    "critical": "bold #FF0000", # Bright Red
    "high": "#FF6600",          # Orange
    "medium": "#FFCC00",        # Yellow
    "low": "#00FF41",           # Green
    "header": "bold #00FFFF",   # Cyan
    "accent": "#FF00FF",        # Magenta
    "dim": "#666666",
    "breach": "bold #FF0000",   # For findings
})


class Logger:
    """Rich console logger for Vauban - The Scientific Breacher."""
    
    def __init__(self, verbose: bool = False):
        self.console = Console(theme=VAUBAN_THEME)
        self.verbose = verbose
        self.start_time = datetime.now()
    
    def banner(self):
        """Print the Vauban ASCII art banner."""
        banner_text = """[bold #00FFFF]
██╗   ██╗ █████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗
██║   ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗████╗  ██║
██║   ██║███████║██║   ██║██████╔╝███████║██╔██╗ ██║
╚██╗ ██╔╝██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║
 ╚████╔╝ ██║  ██║╚██████╔╝██████╔╝██║  ██║██║ ╚████║
  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝[/]
[bold #FF00FF]          ━━━ The Scientific Breacher ━━━[/]
[dim #B0B0B0]    "A fortress besieged by Vauban is a fortress taken"[/]
"""
        self.console.print(Panel(
            banner_text,
            border_style="#00FFFF",
            subtitle="[bold #FF00FF]by R00TQU35T[/bold #FF00FF]"
        ))
        self.console.print("[dim]Created by Kassim Muhammad Atiku | CC, CEH, CSI, CISSP, CISO, ECCS[/dim]")
        self.console.print()
    
    def info(self, message: str):
        """Print info message."""
        self.console.print(f"[cyan]◈[/cyan] [info]{message}[/info]")
    
    def success(self, message: str):
        """Print success message."""
        self.console.print(f"[#00FF41]◉[/#00FF41] [success]{message}[/success]")
    
    def warning(self, message: str):
        """Print warning message."""
        self.console.print(f"[#FFD700]⚠[/#FFD700] [warning]{message}[/warning]")
    
    def error(self, message: str):
        """Print error message."""
        self.console.print(f"[#FF3131]✗[/#FF3131] [error]{message}[/error]")
    
    def critical(self, message: str):
        """Print critical finding."""
        self.console.print(f"[bold #FF0000]◆ CRITICAL[/bold #FF0000] {message}")
    
    def high(self, message: str):
        """Print high severity finding."""
        self.console.print(f"[#FF6600]◆ HIGH[/#FF6600] {message}")
    
    def medium(self, message: str):
        """Print medium severity finding."""
        self.console.print(f"[#FFCC00]◆ MEDIUM[/#FFCC00] {message}")
    
    def low(self, message: str):
        """Print low severity finding."""
        self.console.print(f"[#00FF41]◆ LOW[/#00FF41] {message}")
    
    def debug(self, message: str):
        """Print debug message if verbose mode."""
        if self.verbose:
            self.console.print(f"[dim][DEBUG] {message}[/dim]")
    
    def step(self, step_num: int, total: int, message: str):
        """Print step progress."""
        self.console.print(f"[bold #00FFFF]⟦{step_num}/{total}⟧[/bold #00FFFF] {message}")
    
    def section(self, title: str):
        """Print section header."""
        self.console.print()
        self.console.print(f"[bold #FF00FF]{'━' * 60}[/bold #FF00FF]")
        self.console.print(f"[bold #00FFFF]  ◈ {title}[/bold #00FFFF]")
        self.console.print(f"[bold #FF00FF]{'━' * 60}[/bold #FF00FF]")
        self.console.print()
    
    def stats_table(self, title: str, data: dict):
        """Print statistics table."""
        table = Table(title=title, border_style="#00FFFF", header_style="bold #FF00FF")
        table.add_column("Metric", style="#00FFFF")
        table.add_column("Value", style="#00FF41")
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        self.console.print(table)
    
    def findings_table(self, findings: list):
        """Print vulnerability findings table."""
        if not findings:
            self.info("No vulnerabilities found")
            return
        
        table = Table(title="[bold #FF0000]⚡ BREACH POINTS DETECTED[/bold #FF0000]", 
                     border_style="#FF0000", header_style="bold #FF00FF")
        table.add_column("Severity", style="bold")
        table.add_column("Type", style="#00FFFF")
        table.add_column("Target", style="#B0B0B0")
        table.add_column("Details", style="dim")
        
        severity_styles = {
            'critical': '[bold #FF0000]◆ CRITICAL[/bold #FF0000]',
            'high': '[#FF6600]◆ HIGH[/#FF6600]',
            'medium': '[#FFCC00]◆ MEDIUM[/#FFCC00]',
            'low': '[#00FF41]◆ LOW[/#00FF41]',
            'info': '[#00FFFF]◆ INFO[/#00FFFF]'
        }
        
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            table.add_row(
                severity_styles.get(severity, severity),
                finding.get('type', 'Unknown'),
                finding.get('target', '')[:50],
                finding.get('details', '')[:40]
            )
        
        self.console.print(table)
    
    def summary(self, stats: dict):
        """Print final scan summary."""
        duration = datetime.now() - self.start_time
        
        summary_panel = f"""
[bold #00FFFF]Target:[/bold #00FFFF] {stats.get('target', 'N/A')}
[bold #00FFFF]Duration:[/bold #00FFFF] {str(duration).split('.')[0]}

[bold #00FF41]◈ Reconnaissance:[/bold #00FF41]
  • Subdomains: {stats.get('subdomains', 0):,}
  • Live Hosts: {stats.get('live_hosts', 0):,}
  • URLs: {stats.get('urls', 0):,}
  • API Endpoints: {stats.get('api_endpoints', 0):,}

[bold #FF0000]◈ Breach Points:[/bold #FF0000]
  • [bold #FF0000]Critical: {stats.get('critical', 0)}[/bold #FF0000]
  • [#FF6600]High: {stats.get('high', 0)}[/#FF6600]
  • [#FFCC00]Medium: {stats.get('medium', 0)}[/#FFCC00]
  • [#00FF41]Low: {stats.get('low', 0)}[/#00FF41]

[bold #FFD700]◈ Secrets Exposed:[/bold #FFD700] {stats.get('secrets', 0)}

[bold #FF00FF]◈ Report:[/bold #FF00FF] {stats.get('report_path', 'N/A')}
        """
        
        self.console.print(Panel(
            summary_panel,
            title="[bold #00FF41]◉ SIEGE COMPLETE[/bold #00FF41]",
            border_style="#00FF41",
            subtitle="[dim]A fortress besieged by Vauban is a fortress taken[/dim]"
        ))
    
    def progress(self, description: str = "Processing"):
        """Create and return a progress context manager."""
        return Progress(
            SpinnerColumn(style="#00FFFF"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="#00FF41", finished_style="#00FF41"),
            TaskProgressColumn(),
            console=self.console
        )


# Global logger instance
log = Logger()

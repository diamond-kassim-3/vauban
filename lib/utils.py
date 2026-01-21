"""
LostFuzzer v2.0 - Utility Functions
====================================
Shared utilities for file operations, command execution, and data processing.
"""

import os
import subprocess
import shutil
import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import hashlib


def load_config(config_path: str = "config/settings.yaml") -> Dict:
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_json(data: Dict, filepath: str) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(filepath: str) -> Dict:
    """Load data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def read_file_lines(filepath: str) -> List[str]:
    """Read file and return non-empty lines."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def write_file_lines(filepath: str, lines: List[str], mode: str = 'w') -> None:
    """Write lines to file."""
    with open(filepath, mode) as f:
        for line in lines:
            f.write(f"{line}\n")


def append_to_file(filepath: str, content: str) -> None:
    """Append content to file."""
    with open(filepath, 'a') as f:
        f.write(f"{content}\n")


def dedupe_lines(filepath: str) -> int:
    """Remove duplicate lines from file, return count of unique lines."""
    lines = read_file_lines(filepath)
    unique = list(dict.fromkeys(lines))
    write_file_lines(filepath, unique)
    return len(unique)


def merge_files(input_files: List[str], output_file: str, unique: bool = True) -> int:
    """Merge multiple files into one, optionally removing duplicates."""
    all_lines: Set[str] = set() if unique else []
    
    for filepath in input_files:
        lines = read_file_lines(filepath)
        if unique:
            all_lines.update(lines)
        else:
            all_lines.extend(lines)
    
    final_lines = list(all_lines) if unique else all_lines
    write_file_lines(output_file, final_lines)
    return len(final_lines)


def run_command(cmd: str, cwd: Optional[str] = None, timeout: int = 300) -> tuple:
    """
    Execute shell command and return (stdout, stderr, returncode).
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", -1
    except Exception as e:
        return "", str(e), -1


def run_command_async(cmd: str, output_file: str, cwd: Optional[str] = None) -> subprocess.Popen:
    """
    Execute shell command asynchronously, piping output to file.
    Returns Popen object for monitoring.
    """
    with open(output_file, 'w') as f:
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            stdout=f,
            stderr=subprocess.STDOUT
        )
    return process


def check_tool_installed(tool_name: str) -> bool:
    """Check if a tool is installed and accessible."""
    return shutil.which(tool_name) is not None


def get_missing_tools(tools: List[str]) -> List[str]:
    """Return list of tools that are not installed."""
    return [tool for tool in tools if not check_tool_installed(tool)]


def create_output_dir(base_dir: str, target: str) -> str:
    """Create timestamped output directory for target."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = sanitize_filename(target)
    output_dir = os.path.join(base_dir, f"{safe_target}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories
    for subdir in ['recon', 'urls', 'api', 'scan', 'report']:
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
    
    return output_dir


def sanitize_filename(name: str) -> str:
    """Sanitize string for use as filename."""
    # Remove protocol
    name = name.replace("https://", "").replace("http://", "")
    # Replace unsafe characters
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']:
        name = name.replace(char, '_')
    return name


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    url = url.replace("https://", "").replace("http://", "")
    return url.split('/')[0].split(':')[0]


def filter_urls_with_params(urls: List[str]) -> List[str]:
    """Filter URLs that contain query parameters."""
    return [url for url in urls if '?' in url and '=' in url]


def get_unique_domains(urls: List[str]) -> List[str]:
    """Extract unique domains from list of URLs."""
    domains = set()
    for url in urls:
        domain = extract_domain(url)
        if domain:
            domains.add(domain)
    return list(domains)


def hash_string(s: str) -> str:
    """Generate MD5 hash of string."""
    return hashlib.md5(s.encode()).hexdigest()


def count_file_lines(filepath: str) -> int:
    """Count lines in file."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r') as f:
        return sum(1 for _ in f)


def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    if not os.path.exists(filepath):
        return 0
    return os.path.getsize(filepath)


def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"


def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_severity_score(findings: List[Dict]) -> Dict:
    """Calculate severity breakdown from findings."""
    severity_count = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'info': 0
    }
    
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity in severity_count:
            severity_count[severity] += 1
    
    return severity_count

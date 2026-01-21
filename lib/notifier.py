"""
LostFuzzer v2.0 - Notification System
======================================
Send alerts to Slack, Discord, and Telegram.
"""

import json
import requests
from typing import Dict, List, Optional
from datetime import datetime


class Notifier:
    """Multi-platform notification sender."""
    
    def __init__(self, config: Dict):
        self.config = config.get('notifications', {})
    
    def send_slack(self, message: str, findings: Optional[List[Dict]] = None) -> bool:
        """Send notification to Slack."""
        slack_config = self.config.get('slack', {})
        
        if not slack_config.get('enabled') or not slack_config.get('webhook_url'):
            return False
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔥 LostFuzzer Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
            
            if findings:
                findings_text = self._format_findings_slack(findings)
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": findings_text
                    }
                })
            
            payload = {
                "channel": slack_config.get('channel', '#security-alerts'),
                "blocks": blocks,
                "text": message
            }
            
            response = requests.post(
                slack_config['webhook_url'],
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False
    
    def send_discord(self, message: str, findings: Optional[List[Dict]] = None) -> bool:
        """Send notification to Discord."""
        discord_config = self.config.get('discord', {})
        
        if not discord_config.get('enabled') or not discord_config.get('webhook_url'):
            return False
        
        try:
            embeds = [{
                "title": "🔥 LostFuzzer Alert",
                "description": message,
                "color": 16711680,  # Red
                "timestamp": datetime.utcnow().isoformat()
            }]
            
            if findings:
                findings_text = self._format_findings_discord(findings[:10])
                embeds[0]["fields"] = [{
                    "name": "Findings",
                    "value": findings_text,
                    "inline": False
                }]
            
            payload = {"embeds": embeds}
            
            response = requests.post(
                discord_config['webhook_url'],
                json=payload,
                timeout=10
            )
            
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Discord notification failed: {e}")
            return False
    
    def send_telegram(self, message: str, findings: Optional[List[Dict]] = None) -> bool:
        """Send notification to Telegram."""
        telegram_config = self.config.get('telegram', {})
        
        if not telegram_config.get('enabled') or not telegram_config.get('bot_token'):
            return False
        
        try:
            full_message = f"🔥 *LostFuzzer Alert*\n\n{message}"
            
            if findings:
                full_message += "\n\n" + self._format_findings_telegram(findings[:5])
            
            url = f"https://api.telegram.org/bot{telegram_config['bot_token']}/sendMessage"
            payload = {
                "chat_id": telegram_config['chat_id'],
                "text": full_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram notification failed: {e}")
            return False
    
    def send_all(self, message: str, findings: Optional[List[Dict]] = None) -> Dict[str, bool]:
        """Send notification to all enabled platforms."""
        results = {
            'slack': self.send_slack(message, findings),
            'discord': self.send_discord(message, findings),
            'telegram': self.send_telegram(message, findings)
        }
        return results
    
    def _format_findings_slack(self, findings: List[Dict]) -> str:
        """Format findings for Slack."""
        lines = []
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'info': 'ℹ️'
        }
        
        for finding in findings[:10]:
            severity = finding.get('severity', 'info').lower()
            emoji = severity_emoji.get(severity, '•')
            lines.append(f"{emoji} *{severity.upper()}*: {finding.get('type', 'Unknown')} - `{finding.get('target', '')[:50]}`")
        
        if len(findings) > 10:
            lines.append(f"\n_...and {len(findings) - 10} more_")
        
        return "\n".join(lines)
    
    def _format_findings_discord(self, findings: List[Dict]) -> str:
        """Format findings for Discord."""
        lines = []
        
        for finding in findings:
            severity = finding.get('severity', 'info').upper()
            lines.append(f"**{severity}**: {finding.get('type', 'Unknown')}")
        
        return "\n".join(lines) if lines else "No critical findings"
    
    def _format_findings_telegram(self, findings: List[Dict]) -> str:
        """Format findings for Telegram."""
        lines = ["*Top Findings:*"]
        
        for finding in findings:
            severity = finding.get('severity', 'info').upper()
            lines.append(f"• *{severity}*: {finding.get('type', 'Unknown')}")
        
        return "\n".join(lines)

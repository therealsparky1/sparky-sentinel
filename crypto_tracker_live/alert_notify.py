#!/usr/bin/env python3
"""
Alert-Sentry-01: Notification System
Part of 5-agent crypto tracker swarm
"""

import json
import time
from typing import Dict, List


class AlertNotifier:
    """Send alerts via Discord/Telegram/Console"""
    
    def __init__(self, discord_webhook: str = None, telegram_config: Dict = None):
        """
        Initialize notifier
        
        Args:
            discord_webhook: Discord webhook URL (optional)
            telegram_config: {'bot_token': ..., 'chat_id': ...} (optional)
        """
        self.discord_webhook = discord_webhook
        self.telegram_config = telegram_config
        self.sent_alerts = []
    
    def process_alerts(self, alerts: List[Dict]) -> Dict:
        """
        Process and route alerts by severity
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Delivery status
        """
        high_alerts = [a for a in alerts if a['severity'] == 'high']
        medium_alerts = [a for a in alerts if a['severity'] == 'medium']
        low_alerts = [a for a in alerts if a['severity'] == 'low']
        
        delivery_status = {
            'total_alerts': len(alerts),
            'high': len(high_alerts),
            'medium': len(medium_alerts),
            'low': len(low_alerts),
            'sent': []
        }
        
        # High severity: Send to both channels
        for alert in high_alerts:
            self._send_to_console(alert, priority='HIGH')
            
            if self.discord_webhook:
                self._send_to_discord(alert)
                delivery_status['sent'].append(('discord', alert['alert_id']))
            
            if self.telegram_config:
                self._send_to_telegram(alert)
                delivery_status['sent'].append(('telegram', alert['alert_id']))
        
        # Medium severity: Console + Discord
        for alert in medium_alerts:
            self._send_to_console(alert, priority='MEDIUM')
            
            if self.discord_webhook:
                self._send_to_discord(alert)
                delivery_status['sent'].append(('discord', alert['alert_id']))
        
        # Low severity: Console only (log)
        for alert in low_alerts:
            self._send_to_console(alert, priority='LOW')
        
        return delivery_status
    
    def _send_to_console(self, alert: Dict, priority: str = 'INFO'):
        """Print alert to console (always works)"""
        icons = {
            'arbitrage': '💰',
            'spike': '🚀',
            'drop': '📉',
            'volume_anomaly': '📊'
        }
        
        severity_icons = {'low': '🟡', 'medium': '🟠', 'high': '🔴'}
        
        icon = icons.get(alert['type'], '⚠️')
        severity_icon = severity_icons.get(alert['severity'], '⚪')
        
        print(f"[{priority}] {icon} {alert['type'].upper()} - {alert['coin']} {severity_icon}")
        print(f"        {alert['recommendation']}")
        
        if alert['severity'] == 'high':
            for key, value in alert['details'].items():
                if isinstance(value, float):
                    print(f"        {key}: {value:.2f}")
                elif key != 'sources':
                    print(f"        {key}: {value}")
        
        print()
        
        self.sent_alerts.append({
            'channel': 'console',
            'alert_id': alert['alert_id'],
            'timestamp': time.time()
        })
    
    def _send_to_discord(self, alert: Dict):
        """Send alert to Discord (placeholder - would use webhook)"""
        # In production: requests.post(self.discord_webhook, json=embed)
        
        # For demo: just log
        print(f"[DISCORD] Would send {alert['alert_id']} to Discord")
        
        self.sent_alerts.append({
            'channel': 'discord',
            'alert_id': alert['alert_id'],
            'timestamp': time.time()
        })
    
    def _send_to_telegram(self, alert: Dict):
        """Send alert to Telegram (placeholder - would use bot API)"""
        # In production: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", ...)
        
        # For demo: just log
        print(f"[TELEGRAM] Would send {alert['alert_id']} to Telegram")
        
        self.sent_alerts.append({
            'channel': 'telegram',
            'alert_id': alert['alert_id'],
            'timestamp': time.time()
        })
    
    def format_discord_embed(self, alert: Dict) -> Dict:
        """Format alert as Discord embed"""
        color_map = {
            'high': 16711680,    # Red
            'medium': 16753920,  # Orange
            'low': 16776960      # Yellow
        }
        
        embed = {
            'embeds': [{
                'title': f"{alert['type'].upper()} - {alert['coin']}",
                'color': color_map.get(alert['severity'], 0),
                'description': alert['recommendation'],
                'fields': [],
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(alert['timestamp']))
            }]
        }
        
        # Add detail fields
        for key, value in alert['details'].items():
            if key != 'sources':
                if isinstance(value, float):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)
                
                embed['embeds'][0]['fields'].append({
                    'name': key.replace('_', ' ').title(),
                    'value': value_str,
                    'inline': True
                })
        
        # Add confidence
        embed['embeds'][0]['fields'].append({
            'name': 'Confidence',
            'value': f"{alert['confidence']*100:.0f}%",
            'inline': True
        })
        
        return embed


def main():
    """Demo/test function"""
    print("="*70)
    print("ALERT-SENTRY-01: Notification System")
    print("="*70)
    print()
    
    # Load alerts
    try:
        with open('alerts.json', 'r') as f:
            data = json.load(f)
        
        alerts = data['alerts']
        print(f"✅ Loaded {len(alerts)} alerts for notification")
        print()
        
    except FileNotFoundError:
        print("❌ Missing alerts.json. Run analyze_anomalies.py first.")
        return None
    
    # Initialize notifier
    # In production: would pass real webhook URLs and tokens
    notifier = AlertNotifier(
        discord_webhook=None,  # "https://discord.com/api/webhooks/..."
        telegram_config=None   # {'bot_token': '...', 'chat_id': '...'}
    )
    
    # Process alerts
    print("[1/2] Routing alerts by severity...")
    delivery_status = notifier.process_alerts(alerts)
    
    print()
    print("="*70)
    print("NOTIFICATION SUMMARY")
    print("="*70)
    print(f"Total Alerts:   {delivery_status['total_alerts']}")
    print(f"  🔴 High:      {delivery_status['high']} (Console + Discord + Telegram)")
    print(f"  🟠 Medium:    {delivery_status['medium']} (Console + Discord)")
    print(f"  🟡 Low:       {delivery_status['low']} (Console only)")
    print()
    print(f"Deliveries:     {len(delivery_status['sent'])}")
    
    # Count by channel
    discord_count = sum(1 for c, _ in delivery_status['sent'] if c == 'discord')
    telegram_count = sum(1 for c, _ in delivery_status['sent'] if c == 'telegram')
    
    if discord_count:
        print(f"  Discord:      {discord_count}")
    if telegram_count:
        print(f"  Telegram:     {telegram_count}")
    
    print()
    print("="*70)
    print(f"✅ ALERT-SENTRY-01 COMPLETE")
    print("="*70)
    
    # Save delivery log
    output = {
        'timestamp': time.time(),
        'delivery_status': delivery_status,
        'sent_alerts': notifier.sent_alerts
    }
    
    with open('sent_alerts.log', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Delivery log saved to sent_alerts.log")
    
    return output


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Analyze-Sentry-01: Anomaly & Opportunity Detector
Part of 5-agent crypto tracker swarm
"""

import json
import time
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    timestamp: float
    alert_type: str  # 'arbitrage', 'spike', 'drop', 'volume_anomaly'
    severity: str  # 'low', 'medium', 'high'
    coin: str
    details: Dict
    recommendation: str
    confidence: float


class AnomalyAnalyzer:
    """Detect price anomalies and trading opportunities"""
    
    # Thresholds
    ARBITRAGE_MIN_SPREAD = 1.0  # 1% minimum spread
    SPIKE_THRESHOLD = 5.0  # 5% sudden change
    VOLUME_MULTIPLIER = 3.0  # 3x average volume
    
    def __init__(self):
        self.alerts = []
    
    def analyze(self, aggregated_data: Dict) -> List[Alert]:
        """
        Run all analysis types
        
        Args:
            aggregated_data: Dict of {coin_id: aggregated_data}
            
        Returns:
            List of alerts
        """
        self.alerts = []
        
        for coin, data in aggregated_data.items():
            # 1. Check for arbitrage opportunities
            self._check_arbitrage(coin, data)
            
            # 2. Check for sudden price spikes
            self._check_spike(coin, data)
            
            # 3. Check for sudden price drops
            self._check_drop(coin, data)
            
            # 4. Check for volume anomalies
            self._check_volume(coin, data)
        
        return self.alerts
    
    def _check_arbitrage(self, coin: str, data: Dict):
        """Detect arbitrage opportunities (price spread between sources)"""
        spread = data.get('price_spread', 0)
        
        if spread >= self.ARBITRAGE_MIN_SPREAD and len(data.get('prices', [])) >= 2:
            min_price = data.get('min_price', 0)
            max_price = data.get('max_price', 0)
            avg_price = data.get('avg_price', 0)
            
            # Calculate potential profit
            profit_per_unit = max_price - min_price
            profit_percent = spread
            
            # Severity based on spread
            if spread >= 3.0:
                severity = 'high'
            elif spread >= 2.0:
                severity = 'medium'
            else:
                severity = 'low'
            
            alert = Alert(
                alert_id=f"arb-{coin}-{int(time.time())}",
                timestamp=time.time(),
                alert_type='arbitrage',
                severity=severity,
                coin=coin,
                details={
                    'spread_percent': spread,
                    'min_price': min_price,
                    'max_price': max_price,
                    'avg_price': avg_price,
                    'profit_per_unit': profit_per_unit,
                    'sources': data.get('sources', [])
                },
                recommendation=f"Buy at ${min_price:.2f}, sell at ${max_price:.2f} "
                              f"for ${profit_per_unit:.2f} profit per unit",
                confidence=0.90 if len(data.get('sources', [])) >= 2 else 0.70
            )
            
            self.alerts.append(alert)
    
    def _check_spike(self, coin: str, data: Dict):
        """Detect sudden price spikes (>5% in 24h)"""
        change = data.get('avg_change_24h', 0)
        
        if change >= self.SPIKE_THRESHOLD:
            # Severity based on magnitude
            if change >= 15.0:
                severity = 'high'
            elif change >= 10.0:
                severity = 'medium'
            else:
                severity = 'low'
            
            alert = Alert(
                alert_id=f"spike-{coin}-{int(time.time())}",
                timestamp=time.time(),
                alert_type='spike',
                severity=severity,
                coin=coin,
                details={
                    'change_24h_percent': change,
                    'current_price': data.get('avg_price', 0),
                    'sources': data.get('sources', [])
                },
                recommendation=f"Monitor for trend continuation or reversal",
                confidence=0.85
            )
            
            self.alerts.append(alert)
    
    def _check_drop(self, coin: str, data: Dict):
        """Detect sudden price drops (<-5% in 24h)"""
        change = data.get('avg_change_24h', 0)
        
        if change <= -self.SPIKE_THRESHOLD:
            # Severity based on magnitude
            if change <= -15.0:
                severity = 'high'
            elif change <= -10.0:
                severity = 'medium'
            else:
                severity = 'low'
            
            alert = Alert(
                alert_id=f"drop-{coin}-{int(time.time())}",
                timestamp=time.time(),
                alert_type='drop',
                severity=severity,
                coin=coin,
                details={
                    'change_24h_percent': change,
                    'current_price': data.get('avg_price', 0),
                    'sources': data.get('sources', [])
                },
                recommendation=f"Potential buying opportunity if fundamentals strong",
                confidence=0.80
            )
            
            self.alerts.append(alert)
    
    def _check_volume(self, coin: str, data: Dict):
        """Detect volume anomalies (placeholder - needs historical data)"""
        # Would compare current volume to historical average
        # For demo: flag any volume > $1B as noteworthy
        
        volume = data.get('total_volume_24h', 0)
        
        if volume > 1_000_000_000:  # $1B
            alert = Alert(
                alert_id=f"vol-{coin}-{int(time.time())}",
                timestamp=time.time(),
                alert_type='volume_anomaly',
                severity='medium',
                coin=coin,
                details={
                    'volume_24h': volume,
                    'sources': data.get('sources', [])
                },
                recommendation="High trading activity detected - monitor for volatility",
                confidence=0.75
            )
            
            self.alerts.append(alert)
    
    def get_high_severity_alerts(self) -> List[Alert]:
        """Filter to only high severity alerts"""
        return [a for a in self.alerts if a.severity == 'high']
    
    def format_alert(self, alert: Alert) -> str:
        """Format alert for display"""
        icons = {
            'arbitrage': '💰',
            'spike': '🚀',
            'drop': '📉',
            'volume_anomaly': '📊'
        }
        
        icon = icons.get(alert.alert_type, '⚠️')
        severity_icon = {'low': '🟡', 'medium': '🟠', 'high': '🔴'}[alert.severity]
        
        return f"{icon} {alert.alert_type.upper()} - {alert.coin} {severity_icon}\n" \
               f"   {alert.recommendation}"


def main():
    """Demo/test function"""
    print("="*70)
    print("ANALYZE-SENTRY-01: Anomaly & Opportunity Detector")
    print("="*70)
    print()
    
    # Load normalized data
    try:
        with open('normalized_prices.json', 'r') as f:
            data = json.load(f)
        
        aggregated = data['aggregated']
        print(f"✅ Loaded {len(aggregated)} coins for analysis")
        print()
        
    except FileNotFoundError:
        print("❌ Missing normalized_prices.json. Run parse_normalize.py first.")
        return None
    
    # Analyze
    analyzer = AnomalyAnalyzer()
    
    print("[1/4] Checking for arbitrage opportunities...")
    print("[2/4] Detecting price spikes...")
    print("[3/4] Detecting price drops...")
    print("[4/4] Analyzing volume...")
    print()
    
    alerts = analyzer.analyze(aggregated)
    
    print("="*70)
    print(f"ANALYSIS COMPLETE - {len(alerts)} ALERTS GENERATED")
    print("="*70)
    print()
    
    if alerts:
        # Group by severity
        high = [a for a in alerts if a.severity == 'high']
        medium = [a for a in alerts if a.severity == 'medium']
        low = [a for a in alerts if a.severity == 'low']
        
        print(f"🔴 High:   {len(high)}")
        print(f"🟠 Medium: {len(medium)}")
        print(f"🟡 Low:    {len(low)}")
        print()
        
        # Display all alerts
        for alert in sorted(alerts, key=lambda a: ('high', 'medium', 'low').index(a.severity)):
            print(analyzer.format_alert(alert))
            
            # Show details for high severity
            if alert.severity == 'high':
                for key, value in alert.details.items():
                    if isinstance(value, float):
                        print(f"     {key}: {value:.2f}")
                    else:
                        print(f"     {key}: {value}")
                print()
    else:
        print("✅ No anomalies detected - all markets stable")
    
    print("="*70)
    print(f"✅ ANALYZE-SENTRY-01 COMPLETE")
    print("="*70)
    
    # Save alerts
    output = {
        'timestamp': time.time(),
        'total_alerts': len(alerts),
        'alerts': [
            {
                'alert_id': a.alert_id,
                'timestamp': a.timestamp,
                'type': a.alert_type,
                'severity': a.severity,
                'coin': a.coin,
                'details': a.details,
                'recommendation': a.recommendation,
                'confidence': a.confidence
            }
            for a in alerts
        ]
    }
    
    with open('alerts.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Alerts saved to alerts.json")
    
    return output


if __name__ == "__main__":
    main()

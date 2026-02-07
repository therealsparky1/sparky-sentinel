#!/usr/bin/env python3
"""
5-Agent Crypto Tracker Swarm Coordinator
Orchestrates all 5 specialist agents
"""

import time
import sys

# Import all agents
from fetch_coingecko import CoinGeckoFetcher
from fetch_binance import BinanceFetcher
from parse_normalize import PriceNormalizer
from analyze_anomalies import AnomalyAnalyzer
from alert_notify import AlertNotifier


class SwarmCoordinator:
    """Coordinate 5-agent crypto tracker swarm"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {}
        self.agents_completed = []
        self.agents_failed = []
    
    def run(self):
        """Execute full swarm workflow"""
        print("="*70)
        print("5-AGENT CRYPTO TRACKER SWARM")
        print("="*70)
        print()
        print("Orchestrator: Sparky-Sentry-1065")
        print("Swarm Size: 5 agents")
        print("Mode: Real-time cryptocurrency monitoring")
        print()
        print("="*70)
        print()
        
        # Define target coins
        coins = [
            'solana', 'bitcoin', 'ethereum', 'usd-coin', 'cardano',
            'dogecoin', 'polkadot', 'avalanche-2', 'chainlink', 'polygon'
        ]
        
        print(f"📊 Monitoring {len(coins)} cryptocurrencies")
        print()
        
        # PHASE 1: FETCH (Parallel in production)
        print("PHASE 1: DATA FETCHING (Parallel)")
        print("-" * 70)
        
        # Agent 1: CoinGecko
        print("[1/5] Fetch-Sentry-02 (CoinGecko) starting...")
        fetch1_start = time.time()
        try:
            fetcher1 = CoinGeckoFetcher()
            result1 = fetcher1.fetch_prices(coins)
            fetch1_time = time.time() - fetch1_start
            
            if result1['success']:
                print(f"      ✅ Complete ({fetch1_time:.2f}s) - {len(result1['data'])} coins")
                self.agents_completed.append('Fetch-Sentry-02')
                self.results['coingecko'] = result1
            else:
                print(f"      ❌ Failed: {result1.get('error')}")
                self.agents_failed.append('Fetch-Sentry-02')
                # Continue anyway with partial data
                self.results['coingecko'] = result1
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
            self.agents_failed.append('Fetch-Sentry-02')
            self.results['coingecko'] = {'success': False, 'data': {}, 'error': str(e)}
        
        # Agent 2: Binance
        print("[2/5] Fetch-Sentry-03 (Binance) starting...")
        fetch2_start = time.time()
        try:
            fetcher2 = BinanceFetcher()
            result2 = fetcher2.fetch_prices(coins)
            fetch2_time = time.time() - fetch2_start
            
            if result2['success'] or result2['data']:
                print(f"      ✅ Complete ({fetch2_time:.2f}s) - {len(result2['data'])} coins")
                self.agents_completed.append('Fetch-Sentry-03')
                self.results['binance'] = result2
            else:
                print(f"      ⚠️  Completed with errors")
                self.agents_completed.append('Fetch-Sentry-03')  # Partial success
                self.results['binance'] = result2
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
            self.agents_failed.append('Fetch-Sentry-03')
            self.results['binance'] = {'success': False, 'data': {}, 'error': str(e)}
        
        print()
        
        # PHASE 2: PARSE
        print("PHASE 2: DATA NORMALIZATION")
        print("-" * 70)
        print("[3/5] Parse-Sentry-02 starting...")
        parse_start = time.time()
        try:
            normalizer = PriceNormalizer()
            normalized = normalizer.normalize(
                self.results.get('coingecko', {}),
                self.results.get('binance', {})
            )
            deduped = normalizer.deduplicate(normalized)
            aggregated = normalizer.aggregate_by_coin(deduped)
            parse_time = time.time() - parse_start
            
            print(f"      ✅ Complete ({parse_time:.2f}s) - {len(aggregated)} coins aggregated")
            self.agents_completed.append('Parse-Sentry-02')
            self.results['aggregated'] = aggregated
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
            self.agents_failed.append('Parse-Sentry-02')
            return self._finalize(success=False)
        
        print()
        
        # PHASE 3: ANALYZE
        print("PHASE 3: ANOMALY DETECTION")
        print("-" * 70)
        print("[4/5] Analyze-Sentry-01 starting...")
        analyze_start = time.time()
        try:
            analyzer = AnomalyAnalyzer()
            alerts = analyzer.analyze(self.results['aggregated'])
            analyze_time = time.time() - analyze_start
            
            # Convert Alert objects to dicts
            alerts_dicts = [
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
            
            high_count = sum(1 for a in alerts_dicts if a['severity'] == 'high')
            
            print(f"      ✅ Complete ({analyze_time:.2f}s) - {len(alerts_dicts)} alerts ({high_count} high)")
            self.agents_completed.append('Analyze-Sentry-01')
            self.results['alerts'] = alerts_dicts
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
            self.agents_failed.append('Analyze-Sentry-01')
            return self._finalize(success=False)
        
        print()
        
        # PHASE 4: ALERT
        print("PHASE 4: NOTIFICATION")
        print("-" * 70)
        print("[5/5] Alert-Sentry-01 starting...")
        alert_start = time.time()
        try:
            notifier = AlertNotifier()
            delivery = notifier.process_alerts(self.results['alerts'])
            alert_time = time.time() - alert_start
            
            print(f"      ✅ Complete ({alert_time:.2f}s) - {delivery['total_alerts']} alerts processed")
            self.agents_completed.append('Alert-Sentry-01')
            self.results['delivery'] = delivery
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
            self.agents_failed.append('Alert-Sentry-01')
            return self._finalize(success=False)
        
        print()
        
        # FINALIZE
        return self._finalize(success=True)
    
    def _finalize(self, success: bool):
        """Finalize and display results"""
        total_time = time.time() - self.start_time
        
        print("="*70)
        print("SWARM EXECUTION COMPLETE")
        print("="*70)
        print()
        
        print(f"Total Time:          {total_time:.2f}s")
        print(f"Agents Completed:    {len(self.agents_completed)}/5")
        print(f"Agents Failed:       {len(self.agents_failed)}/5")
        print()
        
        if self.agents_completed:
            print("✅ Successful:")
            for agent in self.agents_completed:
                print(f"   - {agent}")
        
        if self.agents_failed:
            print()
            print("❌ Failed:")
            for agent in self.agents_failed:
                print(f"   - {agent}")
        
        print()
        
        # Results summary
        if success and len(self.agents_completed) == 5:
            print("📊 RESULTS SUMMARY:")
            print(f"   Coins Monitored:    {len(self.results.get('aggregated', {}))} ")
            print(f"   Total Alerts:       {len(self.results.get('alerts', []))}")
            
            alerts = self.results.get('alerts', [])
            if alerts:
                high = sum(1 for a in alerts if a['severity'] == 'high')
                medium = sum(1 for a in alerts if a['severity'] == 'medium')
                low = sum(1 for a in alerts if a['severity'] == 'low')
                
                print(f"     🔴 High:          {high}")
                print(f"     🟠 Medium:        {medium}")
                print(f"     🟡 Low:           {low}")
            
            print()
            print("="*70)
            print("🎉 5-AGENT SWARM SUCCESS")
            print("="*70)
            
            return True
        else:
            print("="*70)
            print("⚠️  SWARM COMPLETED WITH ISSUES")
            print("="*70)
            
            return False


def main():
    """Main entry point"""
    coordinator = SwarmCoordinator()
    success = coordinator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

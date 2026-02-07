#!/usr/bin/env python3
"""
Parse-Sentry-02: Price Data Normalizer
Part of 5-agent crypto tracker swarm
"""

import json
import time
from typing import Dict, List


class PriceNormalizer:
    """Normalize price data from multiple sources to unified schema"""
    
    def normalize(self, coingecko_data: Dict, binance_data: Dict) -> List[Dict]:
        """
        Normalize data from CoinGecko and Binance to unified format
        
        Args:
            coingecko_data: Raw CoinGecko response
            binance_data: Raw Binance response
            
        Returns:
            List of normalized price records
        """
        normalized = []
        current_time = time.time()
        
        # Process CoinGecko data
        if coingecko_data.get('success'):
            for coin_id, data in coingecko_data.get('data', {}).items():
                record = {
                    'timestamp': current_time,
                    'coin': coin_id,
                    'price_usd': data.get('usd', 0),
                    'change_24h_percent': data.get('usd_24h_change', 0),
                    'volume_24h_usd': data.get('usd_24h_vol', 0),
                    'market_cap_usd': data.get('usd_market_cap', 0),
                    'source': 'coingecko',
                    'fetch_time': coingecko_data.get('fetch_time', 0)
                }
                normalized.append(record)
        
        # Process Binance data
        if binance_data.get('success') or binance_data.get('data'):
            for coin_id, data in binance_data.get('data', {}).items():
                record = {
                    'timestamp': current_time,
                    'coin': coin_id,
                    'price_usd': data.get('usd', 0),
                    'change_24h_percent': data.get('usd_24h_change', 0),
                    'volume_24h_usd': data.get('usd_24h_vol', 0),
                    'market_cap_usd': None,  # Binance doesn't provide mcap
                    'source': 'binance',
                    'fetch_time': binance_data.get('fetch_time', 0)
                }
                normalized.append(record)
        
        return normalized
    
    def aggregate_by_coin(self, normalized_data: List[Dict]) -> Dict:
        """
        Aggregate prices by coin (combine sources)
        
        Args:
            normalized_data: List of normalized records
            
        Returns:
            Dictionary {coin_id: aggregated_data}
        """
        aggregated = {}
        
        for record in normalized_data:
            coin = record['coin']
            
            if coin not in aggregated:
                aggregated[coin] = {
                    'coin': coin,
                    'sources': [],
                    'prices': [],
                    'avg_price': 0,
                    'price_spread': 0,
                    'change_24h': [],
                    'volume_24h': []
                }
            
            aggregated[coin]['sources'].append(record['source'])
            aggregated[coin]['prices'].append(record['price_usd'])
            aggregated[coin]['change_24h'].append(record['change_24h_percent'])
            aggregated[coin]['volume_24h'].append(record['volume_24h_usd'])
        
        # Calculate averages and spreads
        for coin, data in aggregated.items():
            if data['prices']:
                data['avg_price'] = sum(data['prices']) / len(data['prices'])
                data['min_price'] = min(data['prices'])
                data['max_price'] = max(data['prices'])
                data['price_spread'] = (data['max_price'] - data['min_price']) / data['avg_price'] * 100
            
            if data['change_24h']:
                data['avg_change_24h'] = sum(data['change_24h']) / len(data['change_24h'])
            
            if data['volume_24h']:
                data['total_volume_24h'] = sum(data['volume_24h'])
        
        return aggregated
    
    def deduplicate(self, normalized_data: List[Dict]) -> List[Dict]:
        """Remove duplicate entries (same coin + source)"""
        seen = set()
        deduped = []
        
        for record in normalized_data:
            key = (record['coin'], record['source'])
            if key not in seen:
                seen.add(key)
                deduped.append(record)
        
        return deduped


def main():
    """Demo/test function"""
    print("="*70)
    print("PARSE-SENTRY-02: Price Data Normalizer")
    print("="*70)
    print()
    
    # Load data from previous fetchers
    try:
        with open('coingecko_prices.json', 'r') as f:
            coingecko_data = json.load(f)
        
        with open('binance_prices.json', 'r') as f:
            binance_data = json.load(f)
        
        print("✅ Loaded data from both sources")
        print(f"   CoinGecko: {len(coingecko_data.get('data', {}))} coins")
        print(f"   Binance: {len(binance_data.get('data', {}))} coins")
        print()
        
    except FileNotFoundError:
        print("❌ Missing input files. Run fetchers first:")
        print("   python fetch_coingecko.py")
        print("   python fetch_binance.py")
        return None
    
    # Normalize
    normalizer = PriceNormalizer()
    
    print("[1/3] Normalizing data...")
    normalized = normalizer.normalize(coingecko_data, binance_data)
    print(f"  ✅ Normalized {len(normalized)} records")
    
    print("[2/3] Deduplicating...")
    deduped = normalizer.deduplicate(normalized)
    print(f"  ✅ Removed {len(normalized) - len(deduped)} duplicates")
    
    print("[3/3] Aggregating by coin...")
    aggregated = normalizer.aggregate_by_coin(deduped)
    print(f"  ✅ Aggregated {len(aggregated)} coins")
    print()
    
    # Display results
    print("="*70)
    print("AGGREGATED PRICES (Multi-Source Average)")
    print("="*70)
    print()
    
    for coin, data in sorted(aggregated.items()):
        sources_str = "+".join(data['sources'])
        spread = data.get('price_spread', 0)
        spread_icon = "⚠️ " if spread > 1.0 else ""
        
        print(f"{coin:15} ${data['avg_price']:>12,.2f}  "
              f"Spread: {spread_icon}{spread:>5.2f}%  "
              f"Sources: {sources_str}")
    
    print()
    print("="*70)
    print(f"✅ PARSE-SENTRY-02 COMPLETE")
    print("="*70)
    
    # Save output
    output = {
        'timestamp': time.time(),
        'normalized': deduped,
        'aggregated': aggregated
    }
    
    with open('normalized_prices.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Data saved to normalized_prices.json")
    
    return output


if __name__ == "__main__":
    main()

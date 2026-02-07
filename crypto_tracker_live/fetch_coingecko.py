#!/usr/bin/env python3
"""
Fetch-Sentry-02: CoinGecko Price Fetcher
Part of 5-agent crypto tracker swarm
"""

import requests
import time
import json
from typing import Dict, List


class CoinGeckoFetcher:
    """Fetch cryptocurrency prices from CoinGecko API"""
    
    API_BASE = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sparky-Crypto-Tracker/1.0'
        })
    
    def fetch_prices(self, coins: List[str], vs_currency: str = "usd") -> Dict:
        """
        Fetch prices for multiple coins
        
        Args:
            coins: List of coin IDs (e.g., ['solana', 'bitcoin'])
            vs_currency: Quote currency (default: usd)
            
        Returns:
            Price data dictionary
        """
        start_time = time.time()
        
        # Build query
        ids = ",".join(coins)
        params = {
            'ids': ids,
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        try:
            # Make request
            response = self.session.get(
                f"{self.API_BASE}/simple/price",
                params=params,
                timeout=5
            )
            
            response.raise_for_status()
            data = response.json()
            
            fetch_time = time.time() - start_time
            
            # Format response
            result = {
                'source': 'coingecko',
                'timestamp': time.time(),
                'fetch_time': fetch_time,
                'data': data,
                'success': True,
                'error': None
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            fetch_time = time.time() - start_time
            
            return {
                'source': 'coingecko',
                'timestamp': time.time(),
                'fetch_time': fetch_time,
                'data': {},
                'success': False,
                'error': str(e)
            }
    
    def get_coin_info(self, coin_id: str) -> Dict:
        """Get detailed info for a single coin"""
        try:
            response = self.session.get(
                f"{self.API_BASE}/coins/{coin_id}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}


def main():
    """Demo/test function"""
    print("="*70)
    print("FETCH-SENTRY-02: CoinGecko Price Fetcher")
    print("="*70)
    print()
    
    fetcher = CoinGeckoFetcher()
    
    # Fetch prices for major coins
    coins = [
        'solana',
        'bitcoin',
        'ethereum',
        'usd-coin',
        'cardano',
        'dogecoin',
        'polkadot',
        'avalanche-2',
        'chainlink',
        'polygon'
    ]
    
    print(f"Fetching prices for {len(coins)} coins...")
    result = fetcher.fetch_prices(coins)
    
    if result['success']:
        print(f"✅ Fetch successful ({result['fetch_time']:.2f}s)")
        print()
        
        for coin_id, price_data in result['data'].items():
            price = price_data.get('usd', 0)
            change = price_data.get('usd_24h_change', 0)
            mcap = price_data.get('usd_market_cap', 0)
            
            change_icon = "📈" if change > 0 else "📉"
            
            print(f"{coin_id:15} ${price:>12,.2f}  {change_icon} {change:>6.2f}%  "
                  f"MCap: ${mcap:>15,.0f}")
        
        print()
        print("="*70)
        print(f"✅ FETCH-SENTRY-02 COMPLETE")
        print("="*70)
        
        # Save to file
        with open('coingecko_prices.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 Data saved to coingecko_prices.json")
        
    else:
        print(f"❌ Fetch failed: {result['error']}")
    
    return result


if __name__ == "__main__":
    main()

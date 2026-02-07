#!/usr/bin/env python3
"""
Fetch-Sentry-03: Binance Price Fetcher
Part of 5-agent crypto tracker swarm
"""

import requests
import time
import json
from typing import Dict, List


class BinanceFetcher:
    """Fetch cryptocurrency prices from Binance API"""
    
    API_BASE = "https://api.binance.com/api/v3"
    
    # Mapping: CoinGecko ID -> Binance symbol
    SYMBOL_MAP = {
        'solana': 'SOLUSDT',
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'cardano': 'ADAUSDT',
        'dogecoin': 'DOGEUSDT',
        'polkadot': 'DOTUSDT',
        'avalanche-2': 'AVAXUSDT',
        'chainlink': 'LINKUSDT',
        'polygon': 'MATICUSDT'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sparky-Crypto-Tracker/1.0'
        })
    
    def fetch_prices(self, coins: List[str]) -> Dict:
        """
        Fetch prices for multiple coins
        
        Args:
            coins: List of coin IDs (CoinGecko format)
            
        Returns:
            Price data dictionary
        """
        start_time = time.time()
        
        results = {}
        errors = []
        
        for coin_id in coins:
            symbol = self.SYMBOL_MAP.get(coin_id)
            
            if not symbol:
                # Skip coins not available on Binance
                continue
            
            try:
                # Get 24h ticker
                response = self.session.get(
                    f"{self.API_BASE}/ticker/24hr",
                    params={'symbol': symbol},
                    timeout=5
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Format as CoinGecko-compatible structure
                results[coin_id] = {
                    'usd': float(data['lastPrice']),
                    'usd_24h_change': float(data['priceChangePercent']),
                    'usd_24h_vol': float(data['volume']) * float(data['lastPrice']),
                    'binance_symbol': symbol
                }
                
            except requests.exceptions.RequestException as e:
                errors.append(f"{coin_id}: {str(e)}")
        
        fetch_time = time.time() - start_time
        
        result = {
            'source': 'binance',
            'timestamp': time.time(),
            'fetch_time': fetch_time,
            'data': results,
            'success': len(errors) == 0,
            'errors': errors if errors else None
        }
        
        return result
    
    def get_orderbook(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book depth"""
        try:
            response = self.session.get(
                f"{self.API_BASE}/depth",
                params={'symbol': symbol, 'limit': limit},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}


def main():
    """Demo/test function"""
    print("="*70)
    print("FETCH-SENTRY-03: Binance Price Fetcher")
    print("="*70)
    print()
    
    fetcher = BinanceFetcher()
    
    # Fetch prices for available coins
    coins = list(fetcher.SYMBOL_MAP.keys())
    
    print(f"Fetching prices for {len(coins)} coins from Binance...")
    result = fetcher.fetch_prices(coins)
    
    if result['success']:
        print(f"✅ Fetch successful ({result['fetch_time']:.2f}s)")
        print()
        
        for coin_id, price_data in result['data'].items():
            price = price_data.get('usd', 0)
            change = price_data.get('usd_24h_change', 0)
            vol = price_data.get('usd_24h_vol', 0)
            symbol = price_data.get('binance_symbol', '')
            
            change_icon = "📈" if change > 0 else "📉"
            
            print(f"{coin_id:15} ${price:>12,.2f}  {change_icon} {change:>6.2f}%  "
                  f"Vol: ${vol:>15,.0f}  ({symbol})")
        
        print()
        print("="*70)
        print(f"✅ FETCH-SENTRY-03 COMPLETE")
        print("="*70)
        
        # Save to file
        with open('binance_prices.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 Data saved to binance_prices.json")
        
    else:
        print(f"⚠️  Fetch completed with errors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    return result


if __name__ == "__main__":
    main()

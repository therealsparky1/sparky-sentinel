#!/usr/bin/env python3
"""
Web Scraper Integration Demo
Combines Fetch-Sentry, Parse-Sentry, and Store-Sentry modules
Demonstrates end-to-end scraping workflow
"""

import sys
import time
from html_fetcher import fetch_html
from html_parser import HTMLParser, extract_text, extract_links
from data_storage import DataStorage
from bs4 import BeautifulSoup

def demo_single_url():
    """Demo: Scrape single URL end-to-end"""
    print("=" * 60)
    print("WEB SCRAPER DEMO - Single URL")
    print("=" * 60)
    
    url = "https://example.com"
    
    # Step 1: Fetch (using Fetch-Sentry module)
    print(f"\n[1/3] Fetching: {url}")
    result = fetch_html(url)
    
    if result['error']:
        print(f"❌ Fetch failed: {result['error']}")
        return
    
    print(f"✅ Fetched {len(result['html'])} bytes")
    print(f"   Status: {result['status_code']}")
    print(f"   Time: {result['fetch_time']:.2f}s")
    
    # Step 2: Parse (using Parse-Sentry module)
    print(f"\n[2/3] Parsing HTML...")
    soup = BeautifulSoup(result['html'], 'html.parser')
    
    # Extract various elements
    title = soup.title.string if soup.title else "No title"
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')][:5]  # First 5
    
    data = {
        'url': url,
        'title': title,
        'links_count': len(links),
        'headings_count': len(headings),
        'paragraphs_count': len(paragraphs),
        'fetch_time': result['fetch_time'],
        'status_code': result['status_code']
    }
    
    print(f"✅ Extracted:")
    print(f"  - Title: {title}")
    print(f"  - Links: {len(links)}")
    print(f"  - Headings: {len(headings)}")
    print(f"  - Paragraphs: {len(paragraphs)}")
    
    # Step 3: Store (using Store-Sentry module)
    print(f"\n[3/3] Storing to database...")
    storage = DataStorage()
    
    storage.store_data(
        data=data,
        table_name="web_scrapes"
    )
    print(f"✅ Stored to SQLite (table: web_scrapes)")
    
    # Verify retrieval
    print(f"\n[VERIFY] Retrieving from database...")
    retrieved = storage.fetch_data(
        table_name="web_scrapes",
        filters={'url': url}
    )
    
    if retrieved:
        record = retrieved[0]
        print(f"✅ Retrieved successfully:")
        print(f"  - URL: {record['url']}")
        print(f"  - Title: {record['title']}")
        print(f"  - Links: {record['links_count']}")
        print(f"  - Status: {record['status_code']}")
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE - All 3 modules working")
    print("=" * 60)

def demo_multiple_urls():
    """Demo: Scrape multiple URLs"""
    print("\n" + "=" * 60)
    print("WEB SCRAPER DEMO - Multiple URLs")
    print("=" * 60)
    
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    storage = DataStorage()
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        try:
            # Fetch
            result = fetch_html(url)
            if result['error']:
                raise Exception(result['error'])
            
            print(f"  ✅ Fetched {len(result['html'])} bytes ({result['fetch_time']:.2f}s)")
            
            # Parse
            soup = BeautifulSoup(result['html'], 'html.parser')
            title = soup.title.string if soup.title else "No title"
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            print(f"  ✅ Parsed: {title}")
            
            # Store
            data = {
                'url': url,
                'title': title,
                'links_count': len(links),
                'status_code': result['status_code'],
                'fetch_time': result['fetch_time']
            }
            
            storage.store_data(data=data, table_name="web_scrapes")
            print(f"  ✅ Stored")
            
            results.append({'url': url, 'success': True})
            time.sleep(1.0)  # Rate limiting
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({'url': url, 'success': False, 'error': str(e)})
    
    # Summary
    print("\n" + "=" * 60)
    print("SCRAPING SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r['success'])
    print(f"Success: {successful}/{len(urls)}")
    
    # Show all stored URLs
    print("\nStored URLs in database:")
    all_records = storage.fetch_data(table_name="web_scrapes")
    for record in all_records[-10:]:  # Last 10
        print(f"  - {record['url']} (status: {record['status_code']})")
    
    print("\n✅ DEMO COMPLETE")

def demo_statistics():
    """Demo: Show database statistics"""
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    storage = DataStorage()
    
    # Get all records
    all_records = storage.fetch_data(table_name="web_scrapes")
    
    if all_records:
        print(f"\nTotal URLs scraped: {len(all_records)}")
        print(f"\nRecent scrapes:")
        for record in all_records[-5:]:  # Last 5
            print(f"  - {record['url']}")
            print(f"    Title: {record['title']}")
            print(f"    Links: {record['links_count']}")
            print(f"    Status: {record['status_code']}")
    else:
        print("\nNo records found. Run 'single' or 'multiple' demo first.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            demo_single_url()
        elif sys.argv[1] == "multiple":
            demo_multiple_urls()
        elif sys.argv[1] == "stats":
            demo_statistics()
        else:
            print("Usage: python web_scraper_demo.py [single|multiple|stats]")
    else:
        # Default: Run all demos
        demo_single_url()
        demo_multiple_urls()
        demo_statistics()

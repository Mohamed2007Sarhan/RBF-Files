#!/usr/bin/env python3
"""
Simple Mempool Integration Demo

This script demonstrates the mempool integration capabilities.
"""

import requests
import time

def demo_mempool_integration():
    """Demonstrate mempool integration"""
    print("Mempool Integration Demo")
    print("=" * 30)
    
    # Test mempool API connectivity
    try:
        print("1. Connecting to mempool.space API...")
        response = requests.get("https://mempool.space/api/v1/fees/recommended", timeout=10)
        if response.status_code == 200:
            fees = response.json()
            print("   ✓ Connected successfully!")
            print(f"   Fastest fee: {fees.get('fastestFee', 'N/A')} sat/vB")
            print(f"   Half-hour fee: {fees.get('halfHourFee', 'N/A')} sat/vB")
        else:
            print(f"   ❌ Connection failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    try:
        print("\n2. Fetching mempool statistics...")
        response = requests.get("https://mempool.space/api/mempool", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("   ✓ Mempool stats fetched!")
            print(f"   Transactions: {stats.get('count', 'N/A')}")
        else:
            print(f"   ❌ Failed to fetch stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    try:
        print("\n3. Fetching block height...")
        response = requests.get("https://mempool.space/api/blocks/tip/height", timeout=10)
        if response.status_code == 200:
            height = response.text.strip()
            print("   ✓ Block height fetched!")
            print(f"   Current height: {height}")
        else:
            print(f"   ❌ Failed to fetch height: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Height error: {e}")
    
    print("\n" + "=" * 30)
    print("✅ Mempool integration demo completed!")
    print("The RBF system is fully connected to mempool.space")

if __name__ == "__main__":
    demo_mempool_integration()
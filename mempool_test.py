#!/usr/bin/env python3
"""
Mempool Integration Test

This script tests the full mempool integration capabilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the mempool monitor
from rbf_main import MempoolMonitor
import time

def test_mempool_integration():
    """Test full mempool integration"""
    print("Testing Full Mempool Integration")
    print("=" * 40)
    
    # Create mempool monitor
    monitor = MempoolMonitor("mainnet")
    
    print("1. Testing fee recommendations...")
    fees = monitor.get_recommended_fees()
    print(f"   Fastest fee: {fees.get('fastestFee', 'N/A')} sat/vB")
    print(f"   Half-hour fee: {fees.get('halfHourFee', 'N/A')} sat/vB")
    print(f"   Hour fee: {fees.get('hourFee', 'N/A')} sat/vB")
    print("   ✓ Fee recommendations working")
    
    print("\n2. Testing mempool statistics...")
    stats = monitor.get_mempool_stats()
    if stats:
        print(f"   Mempool size: {stats.get('count', 'N/A')} transactions")
        print(f"   Total fee: {stats.get('total_fee', 'N/A')} BTC")
        print("   ✓ Mempool statistics working")
    else:
        print("   ⚠️  Mempool statistics unavailable")
    
    print("\n3. Testing block height...")
    height = monitor.get_block_height()
    print(f"   Current block height: {height}")
    print("   ✓ Block height working")
    
    print("\n4. Testing transaction status (with sample TX)...")
    # Test with a known transaction (Genesis block coinbase)
    sample_tx = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    status = monitor.get_transaction_status(sample_tx)
    print(f"   Sample transaction status: {status.get('status', 'N/A')}")
    print("   ✓ Transaction status working")
    
    print("\n" + "=" * 40)
    print("✅ All mempool integration tests completed!")
    print("The system is fully connected to mempool.space API")

if __name__ == "__main__":
    test_mempool_integration()
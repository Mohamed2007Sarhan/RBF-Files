#!/usr/bin/env python3
"""
Demo Runner for RBF System

This script runs the RBF system with predefined inputs for demonstration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rbf_main import BitcoinRBFSystem
import time

def run_demo():
    """Run the RBF system demo with predefined inputs"""
    print("=" * 60)
    print("BITCOIN RBF SYSTEM DEMO")
    print("=" * 60)
    print("Running with predefined inputs for demonstration...\n")
    
    # Create and initialize the RBF system
    rbf_system = BitcoinRBFSystem()
    
    # Set predefined inputs for demonstration
    rbf_system.network = "mainnet"
    rbf_system.wallet_address = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
    rbf_system.private_key = "5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS"
    rbf_system.cancellation_address = "bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3"
    rbf_system.amount = 0.001
    rbf_system.initial_fee_rate = 5
    rbf_system.target_fee_rate = 20
    rbf_system.utxo = {
        "txid": "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "vout": 1,
        "amount": 0.002
    }
    
    print("INPUTS:")
    print(f"  Network: {rbf_system.network.upper()}")
    print(f"  Wallet Address: {rbf_system.wallet_address}")
    print(f"  Cancellation Address: {rbf_system.cancellation_address}")
    print(f"  Amount: {rbf_system.amount} BTC")
    print(f"  Initial Fee Rate: {rbf_system.initial_fee_rate} sat/vB")
    print(f"  Target Fee Rate: {rbf_system.target_fee_rate} sat/vB")
    print()
    
    try:
        # Start RBF operation
        print("Starting RBF operation...")
        rbf_system.start_rbf_operation()
        
        # Simulate monitoring for a few seconds
        print("\nMonitoring for 10 seconds...")
        time.sleep(5)
        
        # Stop the operation
        print("\nStopping RBF operation...")
        rbf_system.stop_rbf_operation()
        
        # Show final status
        print("\n" + "=" * 40)
        print("FINAL STATUS")
        print("=" * 40)
        status = rbf_system.get_status()
        print(f"System running: {status['running']}")
        if status['original_transaction']:
            print(f"Original transaction: {status['original_transaction']['txid'][:16]}...")
            print(f"  Status: {status['original_transaction']['status']}")
        if status['rbf_transaction']:
            print(f"RBF transaction: {status['rbf_transaction']['txid'][:16]}...")
            print(f"  Status: {status['rbf_transaction']['status']}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    run_demo()
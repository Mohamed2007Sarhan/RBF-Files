#!/usr/bin/env python3
"""
Test script for RBF system - shows how to use with YOUR inputs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the RBF system
from rbf_main import BitcoinRBFSystem
import time

def demo_with_your_inputs():
    """Demo showing how to use the system with YOUR inputs"""
    print("BITCOIN RBF SYSTEM - YOUR INPUTS DEMO")
    print("=" * 50)
    print("This demo shows how the system works with YOUR inputs")
    print("In real usage, you would enter your own values\n")
    
    # Create the RBF system
    rbf_system = BitcoinRBFSystem()
    
    # Show what inputs you need to provide
    print("YOU NEED TO PROVIDE THE FOLLOWING INFORMATION:")
    print("1. Network (mainnet/testnet)")
    print("2. Your wallet address (sender)")
    print("3. Your private key (WIF format)")
    print("4. Wrong recipient address")
    print("5. Your cancellation address (to get funds back)")
    print("6. Amount to send (BTC)")
    print("7. Initial fee rate (sat/vB)")
    print("8. Target fee rate (sat/vB)")
    print("9. UTXO transaction ID")
    print("10. UTXO output index (vout)")
    print()
    
    print("Example of what you would enter:")
    print("- Network: 1 (for mainnet)")
    print("- Wallet Address: bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq")
    print("- Private Key: 5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS")
    print("- Wrong Recipient: bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4")
    print("- Cancellation Address: bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3")
    print("- Amount: 0.001")
    print("- Initial Fee Rate: 5")
    print("- Target Fee Rate: 20")
    print("- UTXO TXID: a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890")
    print("- UTXO Vout: 1")
    print()
    
    print("To run the system with your own inputs:")
    print("  python rbf_main.py")
    print()
    print("The system will then prompt you to enter all the above information.")
    print("It will NOT use any predefined keys or addresses.")
    print()
    print("✅ System is ready to accept YOUR inputs!")

if __name__ == "__main__":
    demo_with_your_inputs()
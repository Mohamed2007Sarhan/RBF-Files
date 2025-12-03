#!/usr/bin/env python3
"""
Example RBF (Replace-By-Fee) Transaction Script

This script shows a complete example of how to use RBF to cancel a Bitcoin transaction.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rbf_transaction import RBFSender

def example_rbf_transaction():
    """
    Example showing how to create an RBF transaction to cancel a previous one
    """
    print("=== RBF Transaction Example ===\n")
    
    # Initialize RBF sender (using testnet for safety)
    rbf_sender = RBFSender('testnet')
    
    # Example wallet information
    # Wallet 1: Original sender (you control this)
    wallet1_address = "mfi1N3DRmV5J51zhrMBmFRDpKn5tt66JKk"  # Example testnet address
    wallet1_private_key = "cV4tV2SHDr4FCp5GvTzaZkKQVfsEFXTYi68RS1r8Wzpp2tbHbpUd"  # Example WIF
    
    # Wallet 3: Your own wallet (recipient for cancellation)
    wallet3_address = "mxnhtSmJS3EhEtA3UF1u1kB9trE5ZebpBr"  # Example testnet address
    
    # UTXO information for the original transaction
    utxo_txid = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"  # Example TXID
    utxo_vout = 0  # Output index
    utxo_script_pubkey = "76a914a914a914a914a914a914a914a914a914a914a91488ac"  # Example scriptPubKey
    
    try:
        print("Step 1: Creating original transaction...")
        
        # Create original transaction with lower fee
        original_amount = 0.001  # BTC
        original_fee = 0.0001    # BTC
        original_tx_hex, original_tx = rbf_sender.create_raw_transaction(
            wallet1_address, 
            "some_recipient_address",  # Original intended recipient
            original_amount, 
            original_fee, 
            utxo_txid, 
            utxo_vout
        )
        
        print(f"✓ Original transaction created")
        print(f"  Transaction ID: {original_tx.GetTxid()}") 
        
        # Sign the original transaction
        signed_original_tx_hex = rbf_sender.sign_transaction(
            original_tx_hex, 
            wallet1_private_key, 
            utxo_script_pubkey
        )
        print("✓ Original transaction signed")
        
        print("\nStep 2: Creating RBF transaction with higher fee...")
        
        # Create RBF transaction with higher fee to cancel the original
        higher_fee = 0.0005  # Higher fee to incentivize miners to pick this instead
        rbf_tx_hex, rbf_tx = rbf_sender.create_rbf_transaction(
            wallet1_address,
            wallet3_address,  # Send to your own wallet to effectively cancel
            original_amount,
            higher_fee,
            utxo_txid,
            utxo_vout
        )
        
        print(f"✓ RBF transaction created")
        print(f"  Transaction ID: {rbf_tx.GetTxid()}")
        print(f"  Fee: {higher_fee} BTC (higher than original fee of {original_fee} BTC)")
        
        # Sign the RBF transaction
        signed_rbf_tx_hex = rbf_sender.sign_transaction(
            rbf_tx_hex, 
            wallet1_private_key, 
            utxo_script_pubkey
        )
        print("✓ RBF transaction signed")
        
        print("\n=== RBF Process Complete ===")
        print("To execute this RBF transaction:")
        print("1. Broadcast the original transaction (if not already done)")
        print("2. Broadcast the signed RBF transaction below")
        print("3. Miners should include the RBF transaction due to higher fees\n")
        
        print("Signed RBF transaction (ready for broadcast):")
        print(signed_rbf_tx_hex)
        
        return signed_rbf_tx_hex
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def demonstrate_rbf_concept():
    """
    Demonstrate the concept of RBF transactions
    """
    print("\n=== RBF Concept Explanation ===")
    print("""
    Replace-By-Fee (RBF) is a Bitcoin feature that allows users to increase the fee of 
    an unconfirmed transaction by replacing it with a new one that has a higher fee.
    
    How it works:
    1. Create an original transaction with a low fee
    2. Before the original confirms, create a replacement transaction that:
       - Spends the same UTXO(s)
       - Has a higher fee
       - Is typically sent back to yourself (cancellation)
    3. Broadcast the replacement transaction
    4. Miners will likely pick the higher-fee transaction
    
    Requirements for RBF:
    - Original transaction must signal RBF (opt-in)
    - Replacement must pay a higher fee
    - Both transactions must spend the same UTXOs
    """)
    
if __name__ == "__main__":
    # Show concept explanation
    demonstrate_rbf_concept()
    
    # Run example
    example_rbf_transaction()
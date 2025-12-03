#!/usr/bin/env python3
"""
Advanced RBF (Replace-By-Fee) Transaction Script for Bitcoin Wallets

This script demonstrates how to create and replace Bitcoin transactions using 
the Replace-By-Fee mechanism to cancel previous unconfirmed transactions.
It includes command-line arguments for easier usage.
"""

import argparse
import sys
import bitcoin
from bitcoin import SelectParams
from bitcoin.core import COIN, COutPoint, CTransaction, CTxIn, CTxOut, lx, b2x
from bitcoin.core.script import CScript, SignatureHash, SIGHASH_ALL
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
import binascii

class RBFSender:
    def __init__(self, network='testnet'):
        """Initialize the RBF sender with network parameters"""
        self.setup_network(network)
        
    def setup_network(self, network='testnet'):
        """Setup the Bitcoin network parameters"""
        if network == 'mainnet':
            SelectParams('mainnet')
            self.network = 'mainnet'
        else:
            SelectParams('testnet')
            self.network = 'testnet'
            
    def create_raw_transaction(self, from_address, to_address, amount_btc, fee_btc, utxo_txid, utxo_vout):
        """
        Create a raw Bitcoin transaction
        
        Args:
            from_address (str): Source Bitcoin address
            to_address (str): Destination Bitcoin address
            amount_btc (float): Amount to send in BTC
            fee_btc (float): Transaction fee in BTC
            utxo_txid (str): Transaction ID of the UTXO to spend
            utxo_vout (int): Output index of the UTXO to spend
        
        Returns:
            tuple: (raw_transaction_hex, tx_object)
        """
        try:
            # Convert addresses
            from_addr = CBitcoinAddress(from_address)
            to_addr = CBitcoinAddress(to_address)
            
            # Calculate amounts
            amount_sat = int(amount_btc * COIN)
            fee_sat = int(fee_btc * COIN)
            
            # Validate that fee is less than amount
            if fee_sat >= amount_sat:
                raise ValueError("Fee must be less than the amount being sent")
                
            # Calculate change (amount sent to recipient)
            send_amount_sat = amount_sat - fee_sat
            
            # Create transaction inputs
            txin = CTxIn(COutPoint(lx(utxo_txid), utxo_vout))
            
            # Create transaction outputs
            txout = CTxOut(send_amount_sat, to_addr.to_scriptPubKey())
            
            # Create the transaction
            tx = CTransaction([txin], [txout])
            
            return b2x(tx.serialize()), tx
        except Exception as e:
            raise Exception(f"Error creating transaction: {str(e)}")
            
    def sign_transaction(self, raw_tx_hex, private_key_wif, utxo_script_pubkey):
        """
        Sign a raw transaction with a private key
        
        Args:
            raw_tx_hex (str): Hexadecimal representation of the raw transaction
            private_key_wif (str): Private key in WIF format
            utxo_script_pubkey (str): ScriptPubKey of the UTXO being spent
        
        Returns:
            str: Signed transaction hex
        """
        try:
            # Deserialize the transaction
            tx = CTransaction.deserialize(lx(raw_tx_hex))
            
            # Import the private key
            key = CBitcoinSecret(private_key_wif)
            
            # Create the scriptSig
            script_pubkey = CScript(binascii.unhexlify(utxo_script_pubkey))
            
            # Sign the transaction
            sighash = SignatureHash(script_pubkey, tx, 0, SIGHASH_ALL)
            sig = key.sign(sighash) + bytes([SIGHASH_ALL])
            
            # Create the unlocking script
            script_sig = CScript([sig, key.pub])
            
            # Apply the signature to the transaction
            tx.vin[0].scriptSig = script_sig
            
            return b2x(tx.serialize())
        except Exception as e:
            raise Exception(f"Error signing transaction: {str(e)}")
            
    def create_rbf_transaction(self, from_address, to_address, amount_btc, higher_fee_btc, utxo_txid, utxo_vout):
        """
        Create a replacement transaction with higher fees (RBF)
        
        Args:
            from_address (str): Source Bitcoin address
            to_address (str): Destination Bitcoin address (typically back to self for cancellation)
            amount_btc (float): Amount to send in BTC
            higher_fee_btc (float): Higher fee for RBF transaction
            utxo_txid (str): Transaction ID of the UTXO to spend
            utxo_vout (int): Output index of the UTXO to spend
        
        Returns:
            tuple: (rbf_transaction_hex, tx_object)
        """
        try:
            # Create the replacement transaction
            rbf_tx_hex, rbf_tx = self.create_raw_transaction(
                from_address, to_address, amount_btc, higher_fee_btc, utxo_txid, utxo_vout
            )
            
            return rbf_tx_hex, rbf_tx
        except Exception as e:
            raise Exception(f"Error creating RBF transaction: {str(e)}")

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(description="Create RBF Bitcoin transactions")
    parser.add_argument("--network", choices=['mainnet', 'testnet'], default='testnet',
                        help="Bitcoin network to use (default: testnet)")
    parser.add_argument("--from-address", required=True,
                        help="Source Bitcoin address")
    parser.add_argument("--to-address", required=True,
                        help="Destination Bitcoin address")
    parser.add_argument("--cancel-address",
                        help="Address to send funds to cancel transaction (usually your own)")
    parser.add_argument("--private-key", required=True,
                        help="Private key in WIF format")
    parser.add_argument("--amount", type=float, required=True,
                        help="Amount to send in BTC")
    parser.add_argument("--original-fee", type=float, default=0.0001,
                        help="Original transaction fee in BTC (default: 0.0001)")
    parser.add_argument("--rbf-fee", type=float, required=True,
                        help="RBF transaction fee in BTC (must be higher than original)")
    parser.add_argument("--utxo-txid", required=True,
                        help="UTXO transaction ID")
    parser.add_argument("--utxo-vout", type=int, required=True,
                        help="UTXO output index")
    parser.add_argument("--utxo-script-pubkey", required=True,
                        help="UTXO scriptPubKey")
    
    args = parser.parse_args()
    
    # Validate fees
    if args.rbf_fee <= args.original_fee:
        print("Error: RBF fee must be higher than original fee")
        sys.exit(1)
    
    try:
        # Initialize RBF sender
        rbf_sender = RBFSender(args.network)
        
        print(f"Using {args.network} network")
        print(f"Creating original transaction...")
        
        # Create original transaction
        original_tx_hex, original_tx = rbf_sender.create_raw_transaction(
            args.from_address,
            args.to_address,
            args.amount,
            args.original_fee,
            args.utxo_txid,
            args.utxo_vout
        )
        
        print(f"Original transaction created: {original_tx_hex[:64]}...")
        
        # Sign original transaction
        signed_original_tx_hex = rbf_sender.sign_transaction(
            original_tx_hex,
            args.private_key,
            args.utxo_script_pubkey
        )
        
        print(f"Original transaction signed: {signed_original_tx_hex[:64]}...")
        
        # Determine cancellation address
        cancel_address = args.cancel_address if args.cancel_address else args.from_address
        
        print(f"\nCreating RBF transaction with higher fee ({args.rbf_fee} BTC)...")
        
        # Create RBF transaction
        rbf_tx_hex, rbf_tx = rbf_sender.create_rbf_transaction(
            args.from_address,
            cancel_address,
            args.amount,
            args.rbf_fee,
            args.utxo_txid,
            args.utxo_vout
        )
        
        print(f"RBF transaction created: {rbf_tx_hex[:64]}...")
        
        # Sign RBF transaction
        signed_rbf_tx_hex = rbf_sender.sign_transaction(
            rbf_tx_hex,
            args.private_key,
            args.utxo_script_pubkey
        )
        
        print(f"RBF transaction signed: {signed_rbf_tx_hex[:64]}...")
        
        print("\n=== RBF Process Complete ===")
        print("To cancel the original transaction:")
        print("1. Broadcast the original transaction first (if not already done)")
        print("2. Broadcast the RBF transaction to replace it")
        print("3. The higher fee should incentivize miners to include the new transaction")
        print("\nSigned RBF transaction hex (ready for broadcast):")
        print(signed_rbf_tx_hex)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
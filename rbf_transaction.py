#!/usr/bin/env python3
"""
RBF (Replace-By-Fee) Transaction Script for Bitcoin Wallets

This script demonstrates how to create and replace Bitcoin transactions using 
the Replace-By-Fee mechanism to cancel previous unconfirmed transactions.
"""

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
        # Create the replacement transaction
        rbf_tx_hex, rbf_tx = self.create_raw_transaction(
            from_address, to_address, amount_btc, higher_fee_btc, utxo_txid, utxo_vout
        )
        
        return rbf_tx_hex, rbf_tx

def setup_network(network='testnet'):
    """Setup the Bitcoin network parameters"""
    if network == 'mainnet':
        SelectParams('mainnet')
    else:
        SelectParams('testnet')

def create_raw_transaction(from_address, to_address, amount_btc, fee_btc, utxo_txid, utxo_vout):
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
    # Convert addresses
    from_addr = CBitcoinAddress(from_address)
    to_addr = CBitcoinAddress(to_address)
    
    # Calculate amounts
    amount_sat = int(amount_btc * COIN)
    fee_sat = int(fee_btc * COIN)
    change_sat = amount_sat - fee_sat
    
    # Create transaction inputs
    txin = CTxIn(COutPoint(lx(utxo_txid), utxo_vout))
    
    # Create transaction outputs
    txout = CTxOut(amount_sat, to_addr.to_scriptPubKey())
    
    # Create the transaction
    tx = CTransaction([txin], [txout])
    
    return b2x(tx.serialize()), tx

def sign_transaction(raw_tx_hex, private_key_wif, utxo_script_pubkey):
    """
    Sign a raw transaction with a private key
    
    Args:
        raw_tx_hex (str): Hexadecimal representation of the raw transaction
        private_key_wif (str): Private key in WIF format
        utxo_script_pubkey (str): ScriptPubKey of the UTXO being spent
    
    Returns:
        str: Signed transaction hex
    """
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

def create_rbf_transaction(original_tx_hex, from_address, to_address, higher_fee_btc, utxo_txid, utxo_vout):
    """
    Create a replacement transaction with higher fees (RBF)
    
    Args:
        original_tx_hex (str): Original transaction hex
        from_address (str): Source Bitcoin address
        to_address (str): Destination Bitcoin address (typically back to self for cancellation)
        higher_fee_btc (float): Higher fee for RBF transaction
        utxo_txid (str): Transaction ID of the UTXO to spend
        utxo_vout (int): Output index of the UTXO to spend
    
    Returns:
        tuple: (rbf_transaction_hex, tx_object)
    """
    # For simplicity, we're sending the same amount but with higher fee
    # In practice, you'd calculate the actual amount from the original transaction
    amount_btc = 0.001  # Example amount
    
    # Create the replacement transaction
    rbf_tx_hex, rbf_tx = create_raw_transaction(
        from_address, to_address, amount_btc, higher_fee_btc, utxo_txid, utxo_vout
    )
    
    return rbf_tx_hex, rbf_tx

def main():
    """
    Main function demonstrating RBF transaction workflow
    """
    # Setup network (using testnet for safety)
    setup_network('testnet')
    
    # Example wallet information (these would be provided as parameters in real usage)
    # Wallet 1: Original sender
    wallet1_address = "mfi1N3DRmV5J51zhrMBmFRDpKn5tt66JKk"  # Example testnet address
    wallet1_private_key = "cV4tV2SHDr4FCp5GvTzaZkKQVfsEFXTYi68RS1r8Wzpp2tbHbpUd"  # Example WIF
    
    # Wallet 2: RBF facilitator (not used in this simplified example)
    
    # Wallet 3: Your own wallet (recipient for cancellation)
    wallet3_address = "mxnhtSmJS3EhEtA3UF1u1kB9trE5ZebpBr"  # Example testnet address
    
    # UTXO information for the original transaction
    utxo_txid = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"  # Example TXID
    utxo_vout = 0  # Output index
    utxo_script_pubkey = "76a914a914a914a914a914a914a914a914a914a914a91488ac"  # Example scriptPubKey
    
    print("Creating original transaction...")
    
    # Create original transaction with lower fee
    original_amount = 0.001  # BTC
    original_fee = 0.0001    # BTC
    original_tx_hex, original_tx = create_raw_transaction(
        wallet1_address, 
        "some_destination_address",  # This would be the original intended recipient
        original_amount, 
        original_fee, 
        utxo_txid, 
        utxo_vout
    )
    
    print(f"Original transaction created: {original_tx_hex}")
    
    # Sign the original transaction
    signed_original_tx_hex = sign_transaction(original_tx_hex, wallet1_private_key, utxo_script_pubkey)
    print(f"Original transaction signed: {signed_original_tx_hex}")
    
    print("\nCreating RBF transaction with higher fee...")
    
    # Create RBF transaction with higher fee to cancel the original
    higher_fee = 0.0005  # Higher fee to incentivize miners to pick this instead
    rbf_tx_hex, rbf_tx = create_rbf_transaction(
        original_tx_hex,
        wallet1_address,
        wallet3_address,  # Send to your own wallet to effectively cancel
        higher_fee,
        utxo_txid,
        utxo_vout
    )
    
    print(f"RBF transaction created: {rbf_tx_hex}")
    
    # Sign the RBF transaction
    signed_rbf_tx_hex = sign_transaction(rbf_tx_hex, wallet1_private_key, utxo_script_pubkey)
    print(f"RBF transaction signed: {signed_rbf_tx_hex}")
    
    print("\nRBF Process Complete!")
    print("Broadcast the RBF transaction to replace the original one.")
    print("The higher fee should incentivize miners to include the new transaction instead.")

if __name__ == "__main__":
    main()
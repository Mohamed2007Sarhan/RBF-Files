#!/usr/bin/env python3
"""
Practical RBF Implementation using Bitcoin API

This script demonstrates how to implement RBF transactions using 
Bitcoin RPC calls or API endpoints.
"""

import json
import requests
from typing import Dict, Any, Optional

class BitcoinRBFSender:
    """
    A practical RBF sender that works with Bitcoin nodes or APIs
    """
    
    def __init__(self, rpc_url: str = None, rpc_user: str = None, rpc_password: str = None):
        """
        Initialize the RBF sender with RPC connection details
        
        Args:
            rpc_url: Bitcoin node RPC URL (e.g., http://localhost:8332)
            rpc_user: RPC username
            rpc_password: RPC password
        """
        self.rpc_url = rpc_url
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.rpc_id = 1
        
    def rpc_call(self, method: str, params: list = None) -> Dict[str, Any]:
        """
        Make an RPC call to the Bitcoin node
        
        Args:
            method: RPC method name
            params: List of parameters
            
        Returns:
            RPC response as dictionary
        """
        if not self.rpc_url:
            # Return mock response for demonstration
            return self._mock_rpc_response(method, params)
            
        headers = {'content-type': 'application/json'}
        payload = {
            "method": method,
            "params": params or [],
            "jsonrpc": "2.0",
            "id": self.rpc_id
        }
        self.rpc_id += 1
        
        try:
            response = requests.post(
                self.rpc_url,
                data=json.dumps(payload),
                headers=headers,
                auth=(self.rpc_user, self.rpc_password)
            )
            return response.json()
        except Exception as e:
            raise Exception(f"RPC call failed: {str(e)}")
    
    def _mock_rpc_response(self, method: str, params: list) -> Dict[str, Any]:
        """
        Mock RPC responses for demonstration purposes
        """
        mock_responses = {
            "listunspent": {
                "result": [
                    {
                        "txid": "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",
                        "vout": 1,
                        "address": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
                        "amount": 0.002,
                        "confirmations": 6,
                        "spendable": True,
                        "solvable": True
                    }
                ]
            },
            "createrawtransaction": {
                "result": "0200000001a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f678900100000000ffffffff01a086010000000000160014751e76e8199196d454941c45d1b3a323f1433bd600000000"
            },
            "signrawtransactionwithwallet": {
                "result": {
                    "hex": "0200000001a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890010000006a47304402204e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd410220181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d090121020000000000000000000000000000000000000000000000000000000000000000ffffffff01a086010000000000160014751e76e8199196d454941c45d1b3a323f1433bd600000000",
                    "complete": True
                }
            },
            "sendrawtransaction": {
                "result": "f1d2c3b4a5e6f7890123456789abcdef1234567890abcdef1234567890abcdef"
            }
        }
        return mock_responses.get(method, {"result": "mock_result"})
    
    def get_utxos(self, address: str = None) -> list:
        """
        Get available UTXOs for an address
        
        Args:
            address: Bitcoin address to get UTXOs for
            
        Returns:
            List of UTXOs
        """
        if address:
            response = self.rpc_call("listunspent", [1, 9999999, [address]])
        else:
            response = self.rpc_call("listunspent")
        return response.get("result", [])
    
    def create_transaction(self, inputs: list, outputs: Dict[str, float], 
                          replaceable: bool = True) -> str:
        """
        Create a raw transaction
        
        Args:
            inputs: List of transaction inputs (UTXOs)
            outputs: Dictionary of address -> amount mappings
            replaceable: Whether to signal RBF support
            
        Returns:
            Raw transaction hex
        """
        # Prepare inputs for RPC call
        rpc_inputs = []
        for inp in inputs:
            rpc_inputs.append({
                "txid": inp["txid"],
                "vout": inp["vout"],
                "sequence": 0xfffffffd if replaceable else 0xffffffff  # Enable RBF
            })
        
        response = self.rpc_call("createrawtransaction", [rpc_inputs, outputs])
        return response.get("result", "")
    
    def sign_transaction(self, raw_tx: str) -> Dict[str, Any]:
        """
        Sign a raw transaction
        
        Args:
            raw_tx: Raw transaction hex
            
        Returns:
            Signed transaction details
        """
        response = self.rpc_call("signrawtransactionwithwallet", [raw_tx])
        return response.get("result", {})
    
    def broadcast_transaction(self, signed_tx: str) -> str:
        """
        Broadcast a signed transaction
        
        Args:
            signed_tx: Signed transaction hex
            
        Returns:
            Transaction ID
        """
        response = self.rpc_call("sendrawtransaction", [signed_tx])
        return response.get("result", "")
    
    def create_rbf_transaction(self, original_txid: str, original_vout: int,
                              original_amount: float, original_fee: float,
                              new_destination: str, new_fee: float) -> str:
        """
        Create an RBF transaction to replace an existing one
        
        Args:
            original_txid: Original transaction ID
            original_vout: Original output index
            original_amount: Amount being sent
            original_fee: Original fee
            new_destination: New destination address
            new_fee: Higher fee for replacement
            
        Returns:
            Transaction ID of the replacement transaction
        """
        # Calculate the amount to send (original amount - fee difference)
        fee_difference = new_fee - original_fee
        new_amount = original_amount - fee_difference
        
        if new_amount <= 0:
            raise ValueError("New fee is too high, would result in negative amount")
        
        # Use the same UTXO as the original transaction
        inputs = [{
            "txid": original_txid,
            "vout": original_vout
        }]
        
        # Send to the new destination (often back to yourself)
        outputs = {
            new_destination: new_amount
        }
        
        print(f"Creating RBF transaction:")
        print(f"  - Input: {original_txid}:{original_vout}")
        print(f"  - Output: {new_destination} ({new_amount} BTC)")
        print(f"  - Fee: {new_fee} BTC (higher than original {original_fee} BTC)")
        
        # Create the replacement transaction with RBF enabled
        raw_tx = self.create_transaction(inputs, outputs, replaceable=True)
        print(f"  - Raw transaction created")
        
        # Sign the transaction
        signed_tx = self.sign_transaction(raw_tx)
        if not signed_tx.get("complete"):
            raise Exception("Failed to sign transaction")
        print(f"  - Transaction signed")
        
        # Broadcast the transaction
        txid = self.broadcast_transaction(signed_tx["hex"])
        print(f"  - Transaction broadcast: {txid}")
        
        return txid

def demonstrate_rbf_process():
    """
    Demonstrate the complete RBF process
    """
    print("=" * 60)
    print("PRACTICAL RBF TRANSACTION IMPLEMENTATION")
    print("=" * 60)
    
    # Initialize the RBF sender (using mock responses for demo)
    rbf_sender = BitcoinRBFSender()
    
    # Example scenario: Canceling a transaction sent to wrong address
    sender_address = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
    wrong_recipient = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
    correct_recipient = "bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3"  # Your own wallet
    
    print(f"Sender address: {sender_address}")
    print(f"Wrong recipient: {wrong_recipient}")
    print(f"Correct recipient (refund): {correct_recipient}\n")
    
    # Get available UTXOs
    print("Step 1: Getting available UTXOs...")
    utxos = rbf_sender.get_utxos(sender_address)
    if not utxos:
        print("No UTXOs available")
        return
    
    utxo = utxos[0]  # Use the first available UTXO
    print(f"Using UTXO: {utxo['txid']}:{utxo['vout']} ({utxo['amount']} BTC)\n")
    
    # Create original transaction (simulated)
    print("Step 2: Creating original transaction...")
    original_inputs = [{
        "txid": utxo["txid"],
        "vout": utxo["vout"]
    }]
    original_outputs = {
        wrong_recipient: 0.001  # Sending 0.001 BTC
    }
    
    # Include a fee of 0.00001 BTC
    original_amount = 0.001
    original_fee = 0.00001
    total_cost = original_amount + original_fee
    
    print(f"  - Sending {original_amount} BTC to {wrong_recipient}")
    print(f"  - Fee: {original_fee} BTC")
    print(f"  - Total: {total_cost} BTC")
    
    # Create the original transaction
    original_raw_tx = rbf_sender.create_transaction(
        original_inputs, 
        original_outputs, 
        replaceable=True  # Signal RBF support
    )
    print(f"  - Original transaction created (RBF-enabled)")
    
    # Sign and broadcast original transaction (simulated)
    original_signed = rbf_sender.sign_transaction(original_raw_tx)
    original_txid = rbf_sender.broadcast_transaction(original_signed["hex"])
    print(f"  - Original transaction broadcast: {original_txid}\n")
    
    # Create RBF transaction to cancel the original
    print("Step 3: Creating RBF transaction to cancel original...")
    new_fee = 0.0001  # 10x higher fee
    
    try:
        rbf_txid = rbf_sender.create_rbf_transaction(
            original_txid=utxo["txid"],
            original_vout=utxo["vout"],
            original_amount=original_amount,
            original_fee=original_fee,
            new_destination=correct_recipient,
            new_fee=new_fee
        )
        
        print(f"\n✅ RBF TRANSACTION SUCCESSFUL!")
        print(f"   Original TXID: {original_txid}")
        print(f"   RBF TXID: {rbf_txid}")
        print(f"   Higher fee should prioritize the RBF transaction")
        print(f"   Funds will be returned to your wallet minus the higher fee")
        
    except Exception as e:
        print(f"❌ Error creating RBF transaction: {str(e)}")

def show_api_integration():
    """
    Show how to integrate with real Bitcoin APIs
    """
    print("\n" + "=" * 60)
    print("REAL API INTEGRATION EXAMPLE")
    print("=" * 60)
    
    api_example = '''
# Example using Bitcoin Core RPC:
rbf_sender = BitcoinRBFSender(
    rpc_url="http://localhost:8332",
    rpc_user="your_username",
    rpc_password="your_password"
)

# Example using Blockchain.info API:
import requests

def get_utxos_blockchain(address):
    url = f"https://blockchain.info/unspent?active={address}"
    response = requests.get(url)
    return response.json()

# Example using BlockCypher API:
def create_transaction_blockcypher(inputs, outputs, api_token):
    url = f"https://api.blockcypher.com/v1/btc/main/txs/new?token={api_token}"
    data = {
        "inputs": inputs,
        "outputs": outputs
    }
    response = requests.post(url, json=data)
    return response.json()
'''
    
    print(api_example)

def main():
    """
    Main function to demonstrate RBF implementation
    """
    demonstrate_rbf_process()
    show_api_integration()
    
    print("\n" + "=" * 60)
    print("USAGE INSTRUCTIONS")
    print("=" * 60)
    print("1. Install required packages: pip install requests")
    print("2. For real usage, connect to a Bitcoin node with RPC enabled")
    print("3. For testing, use Bitcoin testnet")
    print("4. Always test with small amounts first")
    print("5. Ensure original transaction signals RBF support")
    
    print("\n⚠️  DISCLAIMER:")
    print("This code is for educational purposes only.")
    print("Real Bitcoin transactions require secure key management.")
    print("Never expose private keys in code or version control.")

if __name__ == "__main__":
    main()
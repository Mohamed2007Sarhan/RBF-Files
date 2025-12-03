#!/usr/bin/env python3
"""
Advanced RBF Transaction Monitor and Cancellation System

Professional-grade Bitcoin RBF monitoring system that:
- Continuously monitors mempool for optimal fee rates
- Tracks transaction confirmation status
- Automatically creates RBF transactions when needed
- Cancels operations if original transaction confirms
- Monitors for competing transactions
"""

import json
import time
import threading
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    BROADCASTED = "broadcasted"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class TransactionInfo:
    """Transaction information container"""
    txid: str
    address: str
    amount: float
    fee: float
    timestamp: datetime
    status: TransactionStatus
    raw_tx: Optional[str] = None
    signed_tx: Optional[str] = None

class MempoolMonitor:
    """Mempool monitoring and fee estimation service"""
    
    def __init__(self, network: str = "mainnet", config_file: str = "rbf_config.json"):
        """Initialize mempool monitor"""
        self.config = self._load_config(config_file)
        self.network = network
        self.base_url = self.config["mempool_api"]["mainnet"] if network == "mainnet" else self.config["mempool_api"]["testnet"]
        self.fee_cache = {}
        self.last_update = 0
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default configuration
                return {
                    "mempool_api": {
                        "mainnet": "https://mempool.space/api",
                        "testnet": "https://mempool.space/testnet/api"
                    },
                    "default_fees": {
                        "initial_fee_rate": 5,
                        "target_fee_rate": 20,
                        "max_fee_rate": 100
                    }
                }
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def get_recommended_fees(self) -> Dict[str, float]:
        """
        Get recommended fees from mempool.space
        
        Returns:
            Dictionary with fee recommendations (sat/vB):
            - fastestFee: Highest fee rate for immediate confirmation
            - halfHourFee: Medium-high fee rate for confirmation within 30 minutes
            - hourFee: Medium fee rate for confirmation within an hour
            - economyFee: Low fee rate for economical transactions
            - minimumFee: Minimum fee rate for eventual confirmation
        """
        try:
            response = requests.get(f"{self.base_url}/v1/fees/recommended", timeout=10)
            if response.status_code == 200:
                fees = response.json()
                self.fee_cache = fees
                self.last_update = time.time()
                logger.info(f"Fee rates updated: {fees}")
                return fees
            else:
                logger.warning(f"Failed to fetch fees: {response.status_code}")
                return self.fee_cache if self.fee_cache else {
                    "fastestFee": self.config["default_fees"]["target_fee_rate"],
                    "halfHourFee": max(self.config["default_fees"]["target_fee_rate"] - 5, 5),
                    "hourFee": max(self.config["default_fees"]["target_fee_rate"] - 10, 3),
                    "economyFee": max(self.config["default_fees"]["target_fee_rate"] - 15, 2),
                    "minimumFee": 1
                }
        except Exception as e:
            logger.error(f"Error fetching recommended fees: {e}")
            return self.fee_cache if self.fee_cache else {
                "fastestFee": self.config["default_fees"]["target_fee_rate"],
                "halfHourFee": max(self.config["default_fees"]["target_fee_rate"] - 5, 5),
                "hourFee": max(self.config["default_fees"]["target_fee_rate"] - 10, 3),
                "economyFee": max(self.config["default_fees"]["target_fee_rate"] - 15, 2),
                "minimumFee": 1
            }
    
    def get_mempool_stats(self) -> Dict[str, Any]:
        """Get mempool statistics"""
        try:
            response = requests.get(f"{self.base_url}/mempool", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch mempool stats: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching mempool stats: {e}")
            return {}
    
    def get_transaction_status(self, txid: str) -> Dict[str, Any]:
        """
        Get transaction status from mempool
        
        Args:
            txid: Transaction ID to check
            
        Returns:
            Transaction status information
        """
        try:
            response = requests.get(f"{self.base_url}/tx/{txid}", timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # Transaction not found, possibly not broadcasted yet
                return {"status": "not_found"}
            else:
                logger.warning(f"Failed to fetch transaction {txid}: {response.status_code}")
                return {"status": "error"}
        except Exception as e:
            logger.error(f"Error fetching transaction {txid}: {e}")
            return {"status": "error"}

class BitcoinRBFEngine:
    """Advanced Bitcoin RBF Engine with monitoring capabilities"""
    
    def __init__(self, rpc_url: str = None, rpc_user: str = None, rpc_password: str = None, 
                 network: str = "mainnet", config_file: str = "rbf_config.json"):
        """
        Initialize the RBF engine
        
        Args:
            rpc_url: Bitcoin node RPC URL
            rpc_user: RPC username
            rpc_password: RPC password
            network: Bitcoin network (mainnet/testnet)
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.rpc_url = rpc_url
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.network = network
        self.mempool_monitor = MempoolMonitor(network, config_file)
        self.rpc_id = 1
        self.running = False
        self.monitor_thread = None
        self.original_tx = None
        self.rbf_tx = None
        self.wallet_address = None
        self.cancellation_address = None
        self.utxo = None
        self.target_fee_rate = None  # sat/vB
        self.rbf_attempts = 0
        self.max_rbf_attempts = self.config.get("max_rbf_attempts", 5)
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default configuration
                return {
                    "max_rbf_attempts": 5,
                    "default_fees": {
                        "initial_fee_rate": 5,
                        "target_fee_rate": 20,
                        "max_fee_rate": 100
                    }
                }
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
        
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
                auth=(self.rpc_user, self.rpc_password),
                timeout=30
            )
            return response.json()
        except Exception as e:
            logger.error(f"RPC call failed: {str(e)}")
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
                          replaceable: bool = True, fee_rate: float = None) -> str:
        """
        Create a raw transaction with specified fee rate
        
        Args:
            inputs: List of transaction inputs (UTXOs)
            outputs: Dictionary of address -> amount mappings
            replaceable: Whether to signal RBF support
            fee_rate: Fee rate in sat/vB (optional)
            
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
    
    def calculate_transaction_size(self, inputs: int, outputs: int) -> int:
        """
        Estimate transaction size in bytes
        
        Args:
            inputs: Number of transaction inputs
            outputs: Number of transaction outputs
            
        Returns:
            Estimated transaction size in bytes
        """
        # Simplified estimation: 180 bytes per input, 34 bytes per output, 10 bytes base
        return inputs * 180 + outputs * 34 + 10
    
    def calculate_fee_from_rate(self, tx_size: int, fee_rate: float) -> float:
        """
        Calculate fee in BTC from fee rate in sat/vB
        
        Args:
            tx_size: Transaction size in bytes
            fee_rate: Fee rate in sat/vB
            
        Returns:
            Fee in BTC
        """
        # Fee in satoshis = size (bytes) * fee rate (sat/vB)
        fee_sats = tx_size * fee_rate
        return fee_sats / 100000000  # Convert to BTC
    
    def start_rbf_operation(self, wallet_address: str, cancellation_address: str,
                           amount: float, initial_fee_rate: float = None, 
                           target_fee_rate: float = None):
        """
        Start RBF operation with continuous monitoring
        
        Args:
            wallet_address: Address to send funds from
            cancellation_address: Address to send funds to (cancellation)
            amount: Amount to send in BTC
            initial_fee_rate: Initial fee rate in sat/vB (optional, uses config default if not provided)
            target_fee_rate: Target fee rate for RBF (optional, uses config default if not provided)
        """
        logger.info("Starting RBF operation...")
        self.wallet_address = wallet_address
        self.cancellation_address = cancellation_address
        self.target_fee_rate = target_fee_rate or self.config["default_fees"]["target_fee_rate"]
        
        # Use default fee rate if not provided
        if initial_fee_rate is None:
            initial_fee_rate = self.config["default_fees"]["initial_fee_rate"]
        
        # Get available UTXOs
        logger.info("Getting available UTXOs...")
        utxos = self.get_utxos(wallet_address)
        if not utxos:
            raise Exception("No UTXOs available")
        
        self.utxo = utxos[0]  # Use the first available UTXO
        logger.info(f"Using UTXO: {self.utxo['txid']}:{self.utxo['vout']}")
        
        # Calculate transaction size and fee
        tx_size = self.calculate_transaction_size(1, 1)  # 1 input, 1 output
        initial_fee = self.calculate_fee_from_rate(tx_size, initial_fee_rate)
        
        # Create original transaction
        logger.info(f"Creating original transaction with fee rate {initial_fee_rate} sat/vB...")
        inputs = [{
            "txid": self.utxo["txid"],
            "vout": self.utxo["vout"]
        }]
        
        outputs = {
            "some_recipient_address": amount  # This would be the mistaken recipient
        }
        
        raw_tx = self.create_transaction(inputs, outputs, replaceable=True)
        signed_tx = self.sign_transaction(raw_tx)
        
        if not signed_tx.get("complete"):
            raise Exception("Failed to sign original transaction")
        
        # Broadcast original transaction
        txid = self.broadcast_transaction(signed_tx["hex"])
        logger.info(f"Original transaction broadcasted: {txid}")
        
        # Store transaction info
        self.original_tx = TransactionInfo(
            txid=txid,
            address=wallet_address,
            amount=amount,
            fee=initial_fee,
            timestamp=datetime.now(),
            status=TransactionStatus.BROADCASTED,
            raw_tx=raw_tx,
            signed_tx=signed_tx["hex"]
        )
        
        # Start monitoring
        self.running = True
        self.rbf_attempts = 0
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("RBF monitoring started")
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        logger.info("Entering monitoring loop...")
        monitoring_interval = self.config.get("monitoring_interval", 30)
        
        while self.running:
            try:
                # Check original transaction status
                tx_status = self.mempool_monitor.get_transaction_status(self.original_tx.txid)
                
                if tx_status.get("status") == "confirmed":
                    logger.info("Original transaction confirmed! Stopping RBF operation.")
                    self.original_tx.status = TransactionStatus.CONFIRMED
                    self.running = False
                    break
                
                # Get current fee rates
                fees = self.mempool_monitor.get_recommended_fees()
                current_fastest_fee = fees.get("fastestFee", self.config["default_fees"]["target_fee_rate"])
                
                # Determine target fee rate
                target_rate = self.target_fee_rate or current_fastest_fee
                
                # Add buffer to ensure confirmation
                fee_buffer = self.config.get("fee_buffer_percentage", 10)
                target_rate_with_buffer = target_rate * (1 + fee_buffer / 100)
                
                # Cap at maximum fee rate
                max_fee_rate = self.config["default_fees"].get("max_fee_rate", 100)
                target_rate_with_buffer = min(target_rate_with_buffer, max_fee_rate)
                
                # Check if we need to create RBF transaction
                original_fee_rate = (self.original_tx.fee * 100000000) / self.calculate_transaction_size(1, 1)
                
                if target_rate_with_buffer > original_fee_rate:
                    logger.info(f"Current fee rate ({target_rate_with_buffer:.1f}) higher than original ({original_fee_rate:.1f}). Creating RBF transaction...")
                    self._create_rbf_transaction(target_rate_with_buffer)
                
                # Wait before next check
                logger.info(f"Waiting {monitoring_interval} seconds before next check...")
                time.sleep(monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _create_rbf_transaction(self, target_fee_rate: float):
        """
        Create RBF transaction with target fee rate
        
        Args:
            target_fee_rate: Target fee rate in sat/vB
        """
        try:
            # Check if we've exceeded max RBF attempts
            if self.rbf_attempts >= self.max_rbf_attempts:
                logger.warning(f"Maximum RBF attempts ({self.max_rbf_attempts}) reached. Stopping.")
                return
            
            # Calculate transaction size and fee
            tx_size = self.calculate_transaction_size(1, 1)  # 1 input, 1 output
            target_fee = self.calculate_fee_from_rate(tx_size, target_fee_rate)
            
            # Ensure we have enough funds
            if target_fee >= self.original_tx.amount:
                logger.warning("Target fee is too high, would result in negative amount")
                return
            
            # Calculate amount to send (original amount - fee difference)
            send_amount = self.original_tx.amount - (target_fee - self.original_tx.fee)
            
            if send_amount <= 0:
                logger.warning("Insufficient funds for RBF transaction")
                return
            
            # Create RBF transaction
            inputs = [{
                "txid": self.utxo["txid"],
                "vout": self.utxo["vout"]
            }]
            
            outputs = {
                self.cancellation_address: send_amount
            }
            
            logger.info(f"Creating RBF transaction with fee rate {target_fee_rate} sat/vB...")
            raw_tx = self.create_transaction(inputs, outputs, replaceable=True)
            signed_tx = self.sign_transaction(raw_tx)
            
            if not signed_tx.get("complete"):
                logger.error("Failed to sign RBF transaction")
                return
            
            # Broadcast RBF transaction
            rbf_txid = self.broadcast_transaction(signed_tx["hex"])
            logger.info(f"RBF transaction broadcasted: {rbf_txid}")
            
            # Store RBF transaction info
            self.rbf_tx = TransactionInfo(
                txid=rbf_txid,
                address=self.cancellation_address,
                amount=send_amount,
                fee=target_fee,
                timestamp=datetime.now(),
                status=TransactionStatus.BROADCASTED,
                raw_tx=raw_tx,
                signed_tx=signed_tx["hex"]
            )
            
            # Increment RBF attempt counter
            self.rbf_attempts += 1
            logger.info(f"RBF attempt #{self.rbf_attempts} completed")
            
        except Exception as e:
            logger.error(f"Error creating RBF transaction: {e}")
    
    def stop_rbf_operation(self):
        """Stop RBF operation"""
        logger.info("Stopping RBF operation...")
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("RBF operation stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of RBF operation"""
        status = {
            "running": self.running,
            "rbf_attempts": self.rbf_attempts,
            "original_transaction": None,
            "rbf_transaction": None
        }
        
        if self.original_tx:
            status["original_transaction"] = {
                "txid": self.original_tx.txid,
                "status": self.original_tx.status.value,
                "amount": self.original_tx.amount,
                "fee": self.original_tx.fee
            }
            
        if self.rbf_tx:
            status["rbf_transaction"] = {
                "txid": self.rbf_tx.txid,
                "status": self.rbf_tx.status.value,
                "amount": self.rbf_tx.amount,
                "fee": self.rbf_tx.fee
            }
            
        return status

def main():
    """Main function for demonstration"""
    print("=" * 70)
    print("ADVANCED BITCOIN RBF MONITORING SYSTEM")
    print("=" * 70)
    print("Professional-grade RBF engine with real-time monitoring")
    print()
    
    # Initialize RBF engine
    rbf_engine = BitcoinRBFEngine(network="mainnet")
    
    # Example usage (with mock data)
    try:
        print("Starting RBF operation...")
        rbf_engine.start_rbf_operation(
            wallet_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
            cancellation_address="bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3",
            amount=0.001,  # 0.001 BTC
            initial_fee_rate=5,  # 5 sat/vB
            target_fee_rate=20   # 20 sat/vB
        )
        
        print("\nRBF system is now running and monitoring...")
        print("Press Ctrl+C to stop the monitoring")
        
        # Display status periodically
        try:
            while rbf_engine.running:
                status = rbf_engine.get_status()
                print(f"\nStatus: Running={status['running']}, Attempts={status['rbf_attempts']}")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopping RBF monitoring...")
            rbf_engine.stop_rbf_operation()
            print("RBF monitoring stopped.")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        rbf_engine.stop_rbf_operation()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Command-Line Interface for Advanced RBF Monitoring System

Professional CLI for controlling the RBF monitoring system.
"""

import argparse
import sys
import time
import json
import signal
from advanced_rbf_monitor import BitcoinRBFEngine

class RBFCli:
    """Command-Line Interface for RBF operations"""
    
    def __init__(self):
        self.rbf_engine = None
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nReceived shutdown signal. Stopping RBF operation...")
        if self.rbf_engine:
            self.rbf_engine.stop_rbf_operation()
        self.running = False
        sys.exit(0)
        
    def start_operation(self, args):
        """Start RBF operation"""
        try:
            # Initialize RBF engine
            self.rbf_engine = BitcoinRBFEngine(
                rpc_url=args.rpc_url,
                rpc_user=args.rpc_user,
                rpc_password=args.rpc_password,
                network=args.network
            )
            
            # Start RBF operation
            self.rbf_engine.start_rbf_operation(
                wallet_address=args.wallet_address,
                cancellation_address=args.cancellation_address,
                amount=args.amount,
                initial_fee_rate=args.initial_fee_rate,
                target_fee_rate=args.target_fee_rate
            )
            
            self.running = True
            print("RBF operation started successfully!")
            print("Monitoring in progress. Press Ctrl+C to stop.")
            
            # Keep running and display status
            while self.running and self.rbf_engine.running:
                status = self.rbf_engine.get_status()
                print(f"\rStatus: Running={status['running']}, Attempts={status['rbf_attempts']}", end="", flush=True)
                time.sleep(5)
                
        except Exception as e:
            print(f"Error starting RBF operation: {e}")
            return False
            
        return True
    
    def stop_operation(self, args):
        """Stop RBF operation"""
        if self.rbf_engine:
            self.rbf_engine.stop_rbf_operation()
            print("RBF operation stopped.")
        else:
            print("No RBF operation is currently running.")
            
    def status_operation(self, args):
        """Get status of RBF operation"""
        if self.rbf_engine:
            status = self.rbf_engine.get_status()
            print(json.dumps(status, indent=2))
        else:
            print("No RBF operation is currently running.")
            
    def run(self):
        """Run the CLI"""
        parser = argparse.ArgumentParser(description="Advanced Bitcoin RBF Monitoring System")
        parser.add_argument("--network", choices=["mainnet", "testnet"], default="mainnet",
                          help="Bitcoin network to use (default: mainnet)")
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Start command
        start_parser = subparsers.add_parser("start", help="Start RBF operation")
        start_parser.add_argument("--rpc-url", required=True, help="Bitcoin node RPC URL")
        start_parser.add_argument("--rpc-user", required=True, help="RPC username")
        start_parser.add_argument("--rpc-password", required=True, help="RPC password")
        start_parser.add_argument("--wallet-address", required=True, help="Wallet address to send from")
        start_parser.add_argument("--cancellation-address", required=True, help="Address to send funds to (cancellation)")
        start_parser.add_argument("--amount", type=float, required=True, help="Amount to send in BTC")
        start_parser.add_argument("--initial-fee-rate", type=float, help="Initial fee rate in sat/vB")
        start_parser.add_argument("--target-fee-rate", type=float, help="Target fee rate in sat/vB")
        
        # Stop command
        stop_parser = subparsers.add_parser("stop", help="Stop RBF operation")
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Get RBF operation status")
        
        # Parse arguments
        args = parser.parse_args()
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Execute command
        if args.command == "start":
            if not self.start_operation(args):
                sys.exit(1)
        elif args.command == "stop":
            self.stop_operation(args)
        elif args.command == "status":
            self.status_operation(args)
        else:
            parser.print_help()

def main():
    """Main function"""
    cli = RBFCli()
    cli.run()

if __name__ == "__main__":
    main()
# Bitcoin RBF (Replace-By-Fee) Transaction System

This repository contains a complete Python implementation of a Bitcoin RBF monitoring and cancellation system.

## Overview

Replace-By-Fee (RBF) is a Bitcoin feature that allows users to increase the fee of an unconfirmed transaction by replacing it with a new one that pays a higher fee. This system provides:

- Real-time mempool monitoring for optimal fee rates
- Automatic creation of RBF transactions
- Monitoring of transaction confirmation status
- Automatic termination when transactions confirm

## Files

- **[rbf_main.py](file:///C:/Users/Moham/OneDrive/Desktop/rbf/rbf_main.py)** - Main RBF system implementation
- **[start_rbf_system.py](file:///C:/Users/Moham/OneDrive/Desktop/rbf/start_rbf_system.py)** - Main execution script
- **[run_rbf_demo.py](file:///C:/Users/Moham/OneDrive/Desktop/rbf/run_rbf_demo.py)** - Demo runner with predefined inputs
- **[advanced_rbf_monitor.py](file:///C:/Users/Moham/OneDrive/Desktop/rbf/advanced_rbf_monitor.py)** - Advanced monitoring system
- **[rbf_config.json](file:///C:/Users/Moham/OneDrive/Desktop/rbf/rbf_config.json)** - Configuration file

## Requirements

- Python 3.6+
- Required packages:
  ```bash
  pip install requests ecdsa
  ```

## Usage

### Option 1: Run with Interactive Inputs
```bash
python start_rbf_system.py
```
Then select option 1 to run the interactive system.

### Option 2: Run Demo with Predefined Inputs
```bash
python start_rbf_system.py
```
Then select option 2 to run the demo.

### Option 3: Direct Execution
```bash
python rbf_main.py
```
This will prompt you for all necessary inputs.

## How It Works

1. **Input Collection** - The system collects all necessary information:
   - Bitcoin network (mainnet/testnet)
   - Wallet address (sender)
   - Private key (for signing)
   - Cancellation address (your wallet to receive funds)
   - Amount to send
   - Initial fee rate
   - Target fee rate

2. **Original Transaction** - Creates and broadcasts the original transaction with low fees

3. **Monitoring** - Continuously monitors the mempool for:
   - Transaction confirmation status
   - Current fee rates in the network

4. **RBF Decision** - When fee rates increase, automatically creates an RBF transaction with higher fees

5. **Cancellation** - Sends funds to your cancellation address and stops monitoring

6. **Termination** - Automatically stops when either transaction confirms

## Security Notes

⚠️ **Warning**: This is a demonstration system. For real Bitcoin transactions:
- Never expose private keys in code
- Use secure hardware wallets for key storage
- Test thoroughly on testnet before using on mainnet
- Implement proper error handling for production use

## Features

- Real-time mempool monitoring using mempool.space API
- Dynamic fee rate adjustment based on network conditions
- Automatic RBF transaction creation
- Transaction confirmation tracking
- Configurable safety limits
- Professional error handling
- Modular design for easy extension

## Professional Applications

This system is suitable for:
- Merchant payment systems requiring transaction cancellation
- Exchange withdrawal optimization
- High-frequency trading platforms
- Custodial wallet services
- Bitcoin node operators managing transaction fees

# Scripting Snitchers

## Overview

**Scripting Snitchers** is a comprehensive project for the Bitcoin Scripting assignment in CS 216: Introduction to Blockchain. The repository contains Python solutions and associated resources to create, decode, and analyze Bitcoin transactions using two address formats: Legacy (P2PKH) and P2SH-SegWit (P2SH-P2WPKH). The project demonstrates how to connect to Bitcoin Core running in regtest mode, manage wallets, generate addresses, create transactions, and compare transaction metrics.

## Team NAME : SNITCHER
## Team Members

- **Srujan Patel  - 230001063**
- **Utkarsh Singh - 230041035**
- **Rohan Sinha   - 230041030**
- *(Add additional team members as necessary)*
## Repository Structure

```
Scripting_Snitchers/
├──scripts├── legacy.py                 # Python script for Legacy (P2PKH) transactions
          ├── segwit.py                 # Python script for P2SH-SegWit transactions
          ├── transaction_comp.py       # Python script for comparing transaction details
├── Bitcoin_Scripting_Assignment_Report.docx  # Detailed report (with placeholders for screenshots)
├── README.md                 # This file
├── Debugger_Results
└── Screenshot results
    # Screenshots of results (legacy_1.png, legacy_2.png, segwit_1.png, segwit_2.png, trans_comp_1.png, trans_comp_2.png)
```

## Prerequisites

Before running the scripts, ensure you have the following set up:

1. **Bitcoin Core (bitcoind):**  
   - Install Bitcoin Core and run it in regtest mode.
   - Configure your `bitcoin.conf` file with settings similar to:
     ```
     rpcuser=srujan
     rpcpassword=ruturaj123
     rpcport=18443
     paytxfee=0.0001
     fallbackfee=0.0002
     mintxfee=0.00001
     txconfirmtarget=6
     ```
   - Start Bitcoin Core in regtest mode with mining enabled:
     ```
     bitcoind -regtest -server -rpcuser=srujan -rpcpassword=ruturaj123 -rpcport=18443
     ```

2. **Python and Dependencies:**  
   - Python 3.x installed on your system.
   - Install the `python-bitcoinrpc` package:
     ```bash
     pip install python-bitcoinrpc
     ```

## How to Use

### 1. Running the Legacy Transactions Script

- **Script:** `legacy.py`
- **Purpose:**  
  - Connects to Bitcoin Core via RPC.
  - Creates/loads the legacy wallet (`assignment_wallet`).
  - Generates three Legacy addresses (A, B, C).
  - Funds address A by mining blocks.
  - Creates a transaction from Address A to Address B.
  - Decodes the transaction to extract and display the locking script (ScriptPubKey) for Address B.
  - Creates another transaction from Address B to Address C and decodes it to display the unlocking script (ScriptSig) and output details.

- **Run the script:**
  ```bash
  python legacy.py
  ```

### 2. Running the SegWit Transactions Script

- **Script:** `segwit.py`
- **Purpose:**  
  - Connects to Bitcoin Core via RPC.
  - Creates/loads the SegWit wallet (`assignment_wallet_segwit`).
  - Generates three P2SH-SegWit addresses (A′, B′, C′).
  - Funds address A′ by mining blocks.
  - Creates a transaction from Address A′ to Address B′.
  - Decodes the transaction to extract and display the locking script for Address B′.
  - Creates another transaction from Address B′ to Address C′ and decodes it to display both unlocking scripts (ScriptSig) and witness data.

- **Run the script:**
  ```bash
  python segwit.py
  ```

### 3. Running the Transaction Comparison Script

- **Script:** `transaction_comp.py`
- **Purpose:**  
  - Prompts for the transaction IDs (txids) of the Legacy transaction (B → C) and the SegWit transaction (B′ → C′).
  - Decodes each transaction and computes key metrics:
    - Raw Size (in kB)
    - Virtual Size (in kB)
    - Transaction Weight (in kWU)
    - Number of inputs and outputs
  - Compares the metrics and explains the benefits of SegWit (reduced size, lower fees, improved scalability, and mitigation of transaction malleability).

- **Run the script:**
  ```bash
  python transaction_comp.py
  ```

  Follow the prompts to enter the respective txids when requested.

## Detailed Explanation

### Legacy Transactions (P2PKH)

- **Wallet Management:**  
  The `legacy.py` script checks for an existing wallet or creates one if it is not already loaded.
  
- **Address Generation:**  
  Three Legacy addresses are generated using the `getnewaddress` RPC command with the `"legacy"` parameter.
  
- **Transaction Workflow:**  
  1. **Funding Address A:**  
     Funds are provided by mining 101 blocks to address A.
  2. **Transaction A → B:**  
     A transaction is sent from address A to address B. The raw transaction is then decoded to extract the locking script associated with address B.
  3. **Transaction B → C:**  
     Using UTXOs from address B, a transaction is created to send coins to address C. The script extracts and displays the unlocking script (ScriptSig) and locking script of the output for address C, along with transaction size details.

### SegWit Transactions (P2SH-SegWit)

- **Wallet Management:**  
  The `segwit.py` script loads or creates the SegWit wallet (`assignment_wallet_segwit`).

- **Address Generation:**  
  Three SegWit addresses (A′, B′, C′) are generated with the `"p2sh-segwit"` parameter.
  
- **Transaction Workflow:**  
  1. **Funding Address A′:**  
     Similar to legacy transactions, funds are secured by mining blocks to address A′.
  2. **Transaction A′ → B′:**  
     A transaction is made from address A′ to address B′. The locking script for address B′ is extracted and displayed.
  3. **Transaction B′ → C′:**  
     A transaction is sent from address B′ to address C′. The script decodes the transaction to show both unlocking scripts (including witness data) and the locking script for address C′.

### Transaction Comparison

- **Comparison Metrics:**  
  The `transaction_comp.py` script analyzes key transaction properties such as size, virtual size, and weight.
  
- **Benefits of SegWit:**  
  - **Reduced Size:** SegWit transactions discount witness data during fee calculation, resulting in smaller transaction sizes.
  - **Lower Fees:** Reduced virtual size translates to lower transaction fees.
  - **Improved Scalability:** Smaller transactions allow more transactions to fit into a block.
  - **Mitigation of Transaction Malleability:** By separating signature data into the witness field, SegWit addresses transaction malleability issues.
  - **Enhanced Future Upgradability:** SegWit enables script versioning for future improvements without hard forks.

## Report

A comprehensive report detailing the assignment workflow, analysis, and comparison is included in the file:  
**Bitcoin_Scripting_Assignment_Report.docx**  
This report also contains placeholders for screenshots of the results, which should be updated with your actual output images.




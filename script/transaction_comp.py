from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
import time

# Configuration
rpc_user = "srujan"
rpc_password = "ruturaj123"
rpc_port = 18443  # Default regtest port
rpc_connection = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}"

def connect_to_rpc():
    """Connect to Bitcoin Core RPC."""
    return AuthServiceProxy(rpc_connection)

def print_separator():
    """Print a separator line."""
    print("\n" + "="*80 + "\n")

def analyze_transaction(rpc, txid, tx_type):
    """Analyze a transaction and return details."""
    raw_tx = rpc.getrawtransaction(txid)
    decoded_tx = rpc.decoderawtransaction(raw_tx)
    
    # Calculate sizes
    raw_size = len(bytes.fromhex(raw_tx)) / 1024  # In kB
    vsize = decoded_tx.get("vsize", 0) / 1024  # Virtual size in kB
    weight = decoded_tx.get("weight", 0) / 1000  # Weight in kWU
    
    print(f"\n{tx_type} Transaction Analysis:")
    print(f"TXID: {txid}")
    print(f"Raw Size: {raw_size:.4f} kB")
    print(f"Virtual Size: {vsize:.4f} kB")
    print(f"Weight: {weight:.4f} kWU")
    
    # Count inputs and outputs
    num_inputs = len(decoded_tx["vin"])
    num_outputs = len(decoded_tx["vout"])
    print(f"Number of inputs: {num_inputs}")
    print(f"Number of outputs: {num_outputs}")
    
    # Analyze scripts
    for i, vin in enumerate(decoded_tx["vin"]):
        print(f"\nInput #{i}:")
        if "scriptSig" in vin:
            scriptsig_size = len(bytes.fromhex(vin["scriptSig"]["hex"])) / 2
            print(f"ScriptSig Size: {scriptsig_size:.0f} bytes")
            print(f"ScriptSig ASM: {vin['scriptSig']['asm']}")
        else:
            print("No ScriptSig (possibly SegWit)")
        
        if "txinwitness" in vin:
            print("Witness data present (SegWit):")
            for item in vin["txinwitness"]:
                print(f"- {item}")
    
    for i, vout in enumerate(decoded_tx["vout"]):
        print(f"\nOutput #{i}:")
        scriptpubkey_size = len(bytes.fromhex(vout["scriptPubKey"]["hex"])) / 2
        print(f"ScriptPubKey Size: {scriptpubkey_size:.0f} bytes")
        print(f"ScriptPubKey ASM: {vout['scriptPubKey']['asm']}")
        print(f"ScriptPubKey Type: {vout['scriptPubKey']['type']}")
        
    return {
        "raw_size": raw_size,
        "vsize": vsize,
        "weight": weight,
        "num_inputs": num_inputs,
        "num_outputs": num_outputs
    }

def main():
    try:
        # Connect to Bitcoin Core RPC
        rpc = connect_to_rpc()
        
        # Get legacy wallet
        rpc_legacy = AuthServiceProxy(f"{rpc_connection}/wallet/assignment_wallet")
        
        # Get SegWit wallet
        rpc_segwit = AuthServiceProxy(f"{rpc_connection}/wallet/assignment_wallet_segwit")
        
        print("Enter the txid for a legacy transaction (B to C):")
        legacy_txid = input().strip()
        
        print("Enter the txid for a SegWit transaction (B' to C'):")
        segwit_txid = input().strip()
        
        # Analyze transactions
        legacy_analysis = analyze_transaction(rpc_legacy, legacy_txid, "Legacy (P2PKH)")
        segwit_analysis = analyze_transaction(rpc_segwit, segwit_txid, "SegWit (P2SH-P2WPKH)")
        
        print_separator()
        print("Transaction Comparison:")
        print(f"Legacy Raw Size: {legacy_analysis['raw_size']:.4f} kB")
        print(f"SegWit Raw Size: {segwit_analysis['raw_size']:.4f} kB")
        print(f"Size Difference: {(legacy_analysis['raw_size'] - segwit_analysis['raw_size']):.4f} kB")
        print(f"Size Reduction: {((legacy_analysis['raw_size'] - segwit_analysis['raw_size']) / legacy_analysis['raw_size'] * 100):.2f}%")
        
        print(f"\nLegacy Virtual Size: {legacy_analysis['vsize']:.4f} kB")
        print(f"SegWit Virtual Size: {segwit_analysis['vsize']:.4f} kB")
        print(f"Virtual Size Difference: {(legacy_analysis['vsize'] - segwit_analysis['vsize']):.4f} kB")
        print(f"Virtual Size Reduction: {((legacy_analysis['vsize'] - segwit_analysis['vsize']) / legacy_analysis['vsize'] * 100):.2f}%")
        
        print(f"\nLegacy Weight: {legacy_analysis['weight']:.4f} kWU")
        print(f"SegWit Weight: {segwit_analysis['weight']:.4f} kWU")
        
        print_separator()
        print("Explanation of SegWit Benefits:")
        print("""
1. Reduced Transaction Size:
   - SegWit moves signature data to the "witness" portion of the transaction
   - This reduces the size of transactions, particularly for complex transactions

2. Lower Fees:
   - Smaller transaction size results in lower fees
   - Fee calculation is based on "virtual size" which gives a discount to witness data

3. Improved Scalability:
   - More transactions can fit into each block due to smaller transaction sizes
   - This increases the overall throughput of the Bitcoin network

4. Fix for Transaction Malleability:
   - SegWit fixes the transaction malleability issue by separating signature data
   - This enables more advanced second-layer solutions like Lightning Network

5. Script Versioning:
   - SegWit introduces a version field for scripts
   - This allows for future script upgrades without needing hard forks
        """)
        
    except JSONRPCException as e:
        print(f"RPC Error: {e.error}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
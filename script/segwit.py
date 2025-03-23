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

def main():
    try:
        # Connect to Bitcoin Core RPC
        rpc = connect_to_rpc()
        
        # Print blockchain info
        info = rpc.getblockchaininfo()
        print(f"Connected to Bitcoin Core (Regtest): {info['chain']}")
        print(f"Current block height: {info['blocks']}")
        
        # Create or load wallet
        try:
            wallet_name = "assignment_wallet_segwit"
            rpc.loadwallet(wallet_name)
            print(f"Loaded existing wallet: {wallet_name}")
        except JSONRPCException:
            rpc.createwallet(wallet_name)
            print(f"Created new wallet: {wallet_name}")
        
        # Reconnect with wallet
        rpc = AuthServiceProxy(f"{rpc_connection}/wallet/{wallet_name}")
        
        # Generate P2SH-SegWit addresses
        address_a_prime = rpc.getnewaddress("", "p2sh-segwit")
        address_b_prime = rpc.getnewaddress("", "p2sh-segwit")
        address_c_prime = rpc.getnewaddress("", "p2sh-segwit")
        
        print(f"Address A' (P2SH-SegWit): {address_a_prime}")
        print(f"Address B' (P2SH-SegWit): {address_b_prime}")
        print(f"Address C' (P2SH-SegWit): {address_c_prime}")
        
        # Fund address A' by generating some blocks
        mining_address = address_a_prime
        blocks = rpc.generatetoaddress(101, mining_address)
        print(f"Generated {len(blocks)} blocks to address A'")
        
        # Check the balance
        balance = rpc.getbalance()
        print(f"Wallet balance: {balance} BTC")
        
        # Get UTXOs for address A'
        utxos = rpc.listunspent(1, 9999999, [address_a_prime])
        if not utxos:
            raise Exception("No UTXOs found for address A'!")
        
        print_separator()
        print("Creating transaction from Address A' to Address B'")
        
        # Create a transaction from A' to B'
        amount_to_send = 10.0
        txid_a_to_b = rpc.sendtoaddress(address_b_prime, amount_to_send)
        print(f"Transaction created: {txid_a_to_b}")
        
        # Generate a block to confirm the transaction
        rpc.generatetoaddress(1, mining_address)
        print("Generated block to confirm transaction")
        
        # Decode and analyze the transaction
        tx_details = rpc.gettransaction(txid_a_to_b)
        raw_tx = rpc.getrawtransaction(txid_a_to_b)
        decoded_tx = rpc.decoderawtransaction(raw_tx)
        
        print("\nTransaction Details:")
        print(f"TXID: {txid_a_to_b}")
        print(f"Amount: {amount_to_send} BTC")
        print(f"Fee: {tx_details['fee']} BTC")
        
        # Find the output to address B' to extract its script
        for vout in decoded_tx["vout"]:
            if "addresses" in vout["scriptPubKey"] and address_b_prime in vout["scriptPubKey"]["addresses"]:
                print("\nLocking Script (ScriptPubKey) for Address B':")
                print(f"ASM: {vout['scriptPubKey']['asm']}")
                print(f"Hex: {vout['scriptPubKey']['hex']}")
                print(f"Type: {vout['scriptPubKey']['type']}")
        
        print_separator()
        print("Creating transaction from Address B' to Address C'")
        
        # Get UTXOs for address B'
        utxos_b = rpc.listunspent(1, 9999999, [address_b_prime])
        if not utxos_b:
            raise Exception("No UTXOs found for address B'!")
            
        print("\nUTXOs for Address B':")
        for utxo in utxos_b:
            print(f"TXID: {utxo['txid']}")
            print(f"Amount: {utxo['amount']} BTC")
            print(f"vout: {utxo['vout']}")
        
        # Send from B' to C'
        amount_to_send_b_to_c = 5.0
        txid_b_to_c = rpc.sendtoaddress(address_c_prime, amount_to_send_b_to_c)
        print(f"\nTransaction created (B' to C'): {txid_b_to_c}")
        
        # Generate a block to confirm the transaction
        rpc.generatetoaddress(1, mining_address)
        print("Generated block to confirm transaction")
        
        # Decode and analyze the transaction
        raw_tx_b_to_c = rpc.getrawtransaction(txid_b_to_c)
        decoded_tx_b_to_c = rpc.decoderawtransaction(raw_tx_b_to_c)
        
        print("\nTransaction Details (B' to C'):")
        print(f"TXID: {txid_b_to_c}")
        
        # Extract input script (ScriptSig)
        for vin in decoded_tx_b_to_c["vin"]:
            if "txid" in vin and vin["txid"] == txid_a_to_b:
                print("\nUnlocking Script (ScriptSig):")
                if "scriptSig" in vin:
                    print(f"ASM: {vin['scriptSig']['asm']}")
                    print(f"Hex: {vin['scriptSig']['hex']}")
                # Check for witness data (SegWit specific)
                if "txinwitness" in vin:
                    print("\nWitness Data:")
                    for item in vin["txinwitness"]:
                        print(f"Witness item: {item}")
        
        # Extract output script for C'
        for vout in decoded_tx_b_to_c["vout"]:
            if "addresses" in vout["scriptPubKey"] and address_c_prime in vout["scriptPubKey"]["addresses"]:
                print("\nLocking Script (ScriptPubKey) for Address C':")
                print(f"ASM: {vout['scriptPubKey']['asm']}")
                print(f"Hex: {vout['scriptPubKey']['hex']}")
                print(f"Type: {vout['scriptPubKey']['type']}")
        
        # Calculate transaction size
        tx_size = len(bytes.fromhex(raw_tx_b_to_c)) / 1024
        print(f"\nTransaction Size (B' to C'): {tx_size:.4f} kB")
        
        print_separator()
        print("SegWit Address Transactions Completed Successfully")
        
    except JSONRPCException as e:
        print(f"RPC Error: {e.error}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
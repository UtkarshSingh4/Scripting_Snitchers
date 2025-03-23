from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
import time
import sys

# Configuration
rpc_user = "srujan"
rpc_password = "ruturaj123"
rpc_port = 18443  # Default regtest port
rpc_connection = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}"

def connect_to_rpc(wallet_path=None):
    """Connect to Bitcoin Core RPC with better error handling."""
    connection_string = rpc_connection
    if wallet_path:
        connection_string = f"{rpc_connection}/wallet/{wallet_path}"
    
    try:
        # Set a timeout to avoid hanging indefinitely
        rpc = AuthServiceProxy(connection_string, timeout=120)
        # Test connection with a simple command
        rpc.getblockcount()
        return rpc
    except ConnectionRefusedError:
        print("Connection refused. Make sure Bitcoin Core is running in regtest mode.")
        print(f"Attempted to connect to: {connection_string.replace(rpc_password, '******')}")
        print("Start bitcoind with: bitcoind -regtest -server -rpcuser=srujan -rpcpassword=ruturaj123 -rpcport=18443")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to Bitcoin Core RPC: {str(e)}")
        sys.exit(1)

def print_separator():
    """Print a separator line."""
    print("\n" + "="*80 + "\n")

def main():
    try:
        # Connect to Bitcoin Core RPC
        print("Connecting to Bitcoin Core...")
        rpc = connect_to_rpc()
        
        # Print blockchain info
        info = rpc.getblockchaininfo()
        print(f"Connected to Bitcoin Core (Regtest): {info['chain']}")
        print(f"Current block height: {info['blocks']}")
        
        # Create or load wallet with proper error handling
        wallet_name = "assignment_wallet"
        try:
            # First try listing wallets to see what's available
            wallets = rpc.listwallets()
            print(f"Available wallets: {wallets}")
            
            if wallet_name in wallets:
                print(f"Wallet '{wallet_name}' is already loaded")
            else:
                # Try to create the wallet, which is the safer approach
                try:
                    result = rpc.createwallet(wallet_name, False, False)
                    print(f"Created new wallet: {wallet_name}")
                    print(f"Creation result: {result}")
                except JSONRPCException as e:
                    if "already exists" in str(e):
                        print(f"Wallet '{wallet_name}' already exists but is not loaded.")
                        result = rpc.loadwallet(wallet_name)
                        print(f"Loaded existing wallet: {wallet_name}")
                        print(f"Load result: {result}")
                    else:
                        raise
        except JSONRPCException as e:
            print(f"Wallet error: {str(e)}")
            print("Attempting to create wallet with explicit path...")
            
            # If conventional approach fails, try with explicit path
            try:
                # On Windows, we might need to use descriptor wallets
                result = rpc.createwallet(
                    wallet_name=wallet_name,
                    disable_private_keys=False,
                    blank=False,
                    passphrase="",
                    avoid_reuse=False,
                    descriptors=True,
                    load_on_startup=True
                )
                print(f"Created descriptor wallet: {result}")
            except JSONRPCException as e2:
                print(f"Failed to create wallet: {str(e2)}")
                print("Trying one last method...")
                
                # One last attempt with minimal parameters
                try:
                    result = rpc.createwallet(wallet_name)
                    print(f"Created wallet with minimal parameters: {result}")
                except Exception as e3:
                    print(f"All wallet creation methods failed: {str(e3)}")
                    print("Please check Bitcoin Core documentation for your specific version")
                    sys.exit(1)
        
        # Reconnect with wallet - add delay to ensure wallet is ready
        print(f"Waiting for wallet to be ready...")
        time.sleep(2)
        print(f"Connecting to wallet: {wallet_name}")
        rpc = connect_to_rpc(wallet_name)
        
        # Generate legacy addresses
        print("Generating addresses...")
        address_a = rpc.getnewaddress("", "legacy")
        address_b = rpc.getnewaddress("", "legacy")
        address_c = rpc.getnewaddress("", "legacy")
        
        print(f"Address A (Legacy): {address_a}")
        print(f"Address B (Legacy): {address_b}")
        print(f"Address C (Legacy): {address_c}")
        
        # Fund address A by generating some blocks
        print("\nMining blocks to fund address A...")
        mining_address = address_a
        try:
            blocks = rpc.generatetoaddress(101, mining_address)
            print(f"Generated {len(blocks)} blocks to address A")
        except JSONRPCException as e:
            print(f"Mining failed: {str(e)}")
            print("Make sure Bitcoin Core is running in regtest mode with mining support.")
            return
        
        # Check the balance
        balance = rpc.getbalance()
        print(f"Wallet balance: {balance} BTC")
        
        # Get UTXOs for address A
        utxos = rpc.listunspent(1, 9999999, [address_a])
        if not utxos:
            print("No UTXOs found for address A! Mining might not have completed properly.")
            return
        
        print_separator()
        print("Creating transaction from Address A to Address B")
        
        # Create a transaction from A to B
        amount_to_send = 10.0
        txid_a_to_b = rpc.sendtoaddress(address_b, amount_to_send)
        print(f"Transaction created: {txid_a_to_b}")
        
        # Generate a block to confirm the transaction
        print("Generating block to confirm transaction...")
        rpc.generatetoaddress(1, mining_address)
        
        # Wait a moment for block propagation
        time.sleep(1)
        
        # Decode and analyze the transaction
        print("\nFetching transaction details...")
        tx_details = rpc.gettransaction(txid_a_to_b)
        raw_tx = rpc.getrawtransaction(txid_a_to_b)
        decoded_tx = rpc.decoderawtransaction(raw_tx)
        
        print("\nTransaction Details:")
        print(f"TXID: {txid_a_to_b}")
        print(f"Amount: {amount_to_send} BTC")
        print(f"Fee: {tx_details['fee']} BTC")
        
        # Find the output to address B to extract its script
        script_found = False
        for vout in decoded_tx["vout"]:
            if "scriptPubKey" in vout:
                scriptPubKey = vout["scriptPubKey"]
                # Handle different Bitcoin Core versions
                if "addresses" in scriptPubKey and address_b in scriptPubKey["addresses"]:
                    print("\nLocking Script (ScriptPubKey) for Address B:")
                    print(f"ASM: {scriptPubKey['asm']}")
                    print(f"Hex: {scriptPubKey['hex']}")
                    print(f"Type: {scriptPubKey['type']}")
                    script_found = True
                    break
                elif "address" in scriptPubKey and scriptPubKey["address"] == address_b:
                    print("\nLocking Script (ScriptPubKey) for Address B:")
                    print(f"ASM: {scriptPubKey['asm']}")
                    print(f"Hex: {scriptPubKey['hex']}")
                    print(f"Type: {scriptPubKey['type']}")
                    script_found = True
                    break
        
        if not script_found:
            print("Warning: Could not find output for address B in transaction.")
        
        print_separator()
        print("Creating transaction from Address B to Address C")
        
        # Get UTXOs for address B
        print("Checking UTXOs for Address B...")
        utxos_b = rpc.listunspent(1, 9999999, [address_b])
        if not utxos_b:
            print("No UTXOs found for address B! Transaction might not have confirmed properly.")
            return
            
        print("\nUTXOs for Address B:")
        for utxo in utxos_b:
            print(f"TXID: {utxo['txid']}")
            print(f"Amount: {utxo['amount']} BTC")
            print(f"vout: {utxo['vout']}")
        
        # Send from B to C
        print("\nSending from B to C...")
        amount_to_send_b_to_c = 5.0
        txid_b_to_c = rpc.sendtoaddress(address_c, amount_to_send_b_to_c)
        print(f"Transaction created (B to C): {txid_b_to_c}")
        
        # Generate a block to confirm the transaction
        print("Generating block to confirm transaction...")
        rpc.generatetoaddress(1, mining_address)
        
        # Wait a moment for block propagation
        time.sleep(1)
        
        # Decode and analyze the transaction
        print("\nFetching transaction details...")
        raw_tx_b_to_c = rpc.getrawtransaction(txid_b_to_c)
        decoded_tx_b_to_c = rpc.decoderawtransaction(raw_tx_b_to_c)
        
        print("\nTransaction Details (B to C):")
        print(f"TXID: {txid_b_to_c}")
        
        # Extract input script (ScriptSig)
        script_found = False
        for vin in decoded_tx_b_to_c["vin"]:
            input_txid = vin.get("txid", "")
            if input_txid == txid_a_to_b:
                print("\nUnlocking Script (ScriptSig):")
                if "scriptSig" in vin:
                    print(f"ASM: {vin['scriptSig']['asm']}")
                    print(f"Hex: {vin['scriptSig']['hex']}")
                else:
                    print("No scriptSig found in this input (possibly segwit)")
                script_found = True
                break
        
        if not script_found:
            print("Warning: Could not find input from transaction A->B in the B->C transaction.")
        
        # Extract output script for C
        script_found = False
        for vout in decoded_tx_b_to_c["vout"]:
            if "scriptPubKey" in vout:
                scriptPubKey = vout["scriptPubKey"]
                # Handle different Bitcoin Core versions
                if "addresses" in scriptPubKey and address_c in scriptPubKey["addresses"]:
                    print("\nLocking Script (ScriptPubKey) for Address C:")
                    print(f"ASM: {scriptPubKey['asm']}")
                    print(f"Hex: {scriptPubKey['hex']}")
                    print(f"Type: {scriptPubKey['type']}")
                    script_found = True
                    break
                elif "address" in scriptPubKey and scriptPubKey["address"] == address_c:
                    print("\nLocking Script (ScriptPubKey) for Address C:")
                    print(f"ASM: {scriptPubKey['asm']}")
                    print(f"Hex: {scriptPubKey['hex']}")
                    print(f"Type: {scriptPubKey['type']}")
                    script_found = True
                    break
        
        if not script_found:
            print("Warning: Could not find output for address C in transaction.")
        
        # Calculate transaction size
        tx_size = len(bytes.fromhex(raw_tx_b_to_c)) / 1024
        print(f"\nTransaction Size (B to C): {tx_size:.4f} kB")
        
        print_separator()
        print("Legacy Address Transactions Completed Successfully")
        
    except JSONRPCException as e:
        print(f"RPC Error: {e.error}")
        print("Make sure Bitcoin Core is running in regtest mode with the correct settings.")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
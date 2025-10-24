import click
import bitcoinlib
import requests
import os
import time
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import Key, Address

# Configuration
BLOCKCYPHER_API_TOKEN = os.getenv("BLOCKCYPHER_API_TOKEN")
if not BLOCKCYPHER_API_TOKEN:
    raise ValueError(
        "BLOCKCYPHER_API_TOKEN environment variable not set. Get a token from https://accounts.blockcypher.com/")
BLOCKCYPHER_API_URL = "https://api.blockcypher.com/v1/btc/test3"


class WalletModule:
    def __init__(self):
        self.wallet = None

    def generate_wallet(self) -> dict:
        """Generate a new Bitcoin testnet wallet."""
        mnemonic_obj = Mnemonic()
        mnemonic = mnemonic_obj.generate()
        # Use a unique temporary name to avoid conflicts
        wallet_name = f"temp_wallet_{int(time.time())}"
        try:
            self.wallet = bitcoinlib.wallets.Wallet.create(
                name=wallet_name,
                network="testnet",
                witness_type="segwit",
                keys=mnemonic,
                db_cache_uri=None  # Disable persistent database
            )
            key = self.wallet.key_for_path("m/84'/1'/0'/0/0")
            address = key.address
            # Convert HDKey private key to WIF format
            key_obj = Key(key.key_private, network="testnet",
                          is_private=True, compressed=True)
            private_key = key_obj.wif()  # Call the method to get the WIF key
            return {"address": address, "mnemonic": mnemonic, "private_key": private_key}
        except Exception as e:
            raise ValueError(f"Failed to generate wallet: {str(e)}")

    def load_wallet_from_privatekey(self, private_key: str) -> dict:
        """Load address from WIF private key."""
        try:
            if private_key.startswith(('xprv', 'tprv', 'vprv')):
                raise ValueError(
                    "Extended private keys (xprv/tprv/vprv) are not supported. Use WIF private key (starts with 'c' for testnet).")
            key_obj = Key(private_key, network="testnet",
                          is_private=True, compressed=True)
            address_obj = Address(key_obj.public_hex,
                                  network="testnet", script_type="p2wpkh")
            address = address_obj.address
            return {"address": address}
        except Exception as e:
            raise Exception(
                f"Failed to load address from private key: {str(e)}")


class BlockchainModule:
    def get_balance(self, address: str) -> float:
        """Fetch balance for an address from Blockcypher."""
        # Contruct the API URL
        url = f"{BLOCKCYPHER_API_URL}/addrs/{address}/balance?token={BLOCKCYPHER_API_TOKEN}"
        for attempt in range(5):
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                # Convert the balance from satoshis to BTC
                return data["final_balance"] / 100000000
            except requests.RequestException as e:
                if attempt < 4:
                    time.sleep(2)
                    continue
                raise Exception(
                    f"Error fetching balance after retries: {str(e)}")

    def get_utxos(self, address: str) -> list:
        """Fetch UTXOs for an address from Blockcypher."""
        # Construct the API URL to get unspent outputs at the given address
        url = f"{BLOCKCYPHER_API_URL}/addrs/{address}?unspentOnly=true&token={BLOCKCYPHER_API_TOKEN}"
        for attempt in range(5):
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                utxos = data.get("txrefs", [])  # Get the list of UTXOs
                unconfirmed_balance = data.get("unconfirmed_balance", 0)
                if not utxos:
                    if unconfirmed_balance > 0:
                        raise Exception(
                            f"No confirmed UTXOs. Unconfirmed balance: {unconfirmed_balance / 100000000:.8f} BTC. Wait for confirmation (10-60 minutes).")
                    else:
                        raise Exception(
                            "No UTXOs available. Fund the wallet on testnet and wait for confirmation.")
                return utxos
            except requests.RequestException as e:
                if attempt < 4:
                    time.sleep(2)
                    continue
                raise Exception(
                    f"Error fetching UTXOs after retries: {str(e)}")


class TransactionModule:
    def __init__(self, blockchain: BlockchainModule):
        self.blockchain = blockchain

    def send_transaction(self, private_key: str, recipient: str, amount: float) -> str:
        """Construct, sign, and broadcast a transaction using a WIF private key."""
        try:
            key_obj = Key(private_key, network="testnet",
                          is_private=True, compressed=True)
            address_obj = Address(key_obj.public_hex,
                                  network="testnet", script_type="p2wpkh")
            address = address_obj.address
        except Exception as e:
            raise ValueError(f"Invalid private key: {str(e)}")

        utxos = self.blockchain.get_utxos(address)
        if not utxos:
            raise Exception(
                "No UTXOs available. Fund the wallet on testnet and wait for confirmation.")

        fee = 500  # 0.000005 BTC
        amount_satoshi = int(amount * 100000000)
        total_input = sum(utxo["value"] for utxo in utxos)

        if total_input < amount_satoshi + fee:
            raise Exception(
                f"Insufficient funds: Balance {total_input / 100000000:.8f} BTC < {amount} + fee {fee / 100000000:.8f} BTC. Lower amount or fee.")

        try:
            tx = bitcoinlib.transactions.Transaction(
                network="testnet", witness_type="segwit")
            for utxo in utxos:
                tx.add_input(
                    prev_txid=utxo["tx_hash"],
                    output_n=utxo["tx_output_n"],
                    value=utxo["value"],
                    address=address,
                    public_hash=key_obj.hash160  # Add public key hash for P2WPKH
                )
            tx.add_output(value=amount_satoshi, address=recipient)
            if total_input > amount_satoshi + fee:
                tx.add_output(value=total_input -
                              amount_satoshi - fee, address=address)

            tx.sign(keys=key_obj)

            raw_tx = tx.raw_hex()

            # Broadcast transaction
            url = f"{BLOCKCYPHER_API_URL}/txs/push?token={BLOCKCYPHER_API_TOKEN}"
            response = requests.post(url, json={"tx": raw_tx}, timeout=15)
            response.raise_for_status()
            return response.json()["tx"]["hash"]
        except Exception as e:
            raise Exception(
                f"Transaction creation/signing/broadcast failed: {str(e)}")


@click.group()
def cli():
    """Non-Custodial Bitcoin Wallet Demo (Testnet)"""
    pass


@cli.command()
def generate_wallet():
    """Generate a new Bitcoin testnet wallet."""
    try:
        wallet_module = WalletModule()
        result = wallet_module.generate_wallet()
        click.echo(
            f"Wallet Generated!\nAddress: {result['address']}\nMnemonic: {result['mnemonic']}\nPrivate Key (WIF): {result['private_key']}")
        click.echo(
            "WARNING: Save your mnemonic and private key securely! The WIF key controls the displayed address.")
    except Exception as e:
        click.echo(
            f"Error: {str(e) or 'Unknown error during wallet generation'}")


@cli.command()
@click.argument("address")
def check_balance(address):
    """Check the balance of a Bitcoin testnet address."""
    try:
        blockchain = BlockchainModule()
        balance = blockchain.get_balance(address)
        click.echo(f"Address: {address}\nBalance: {balance:.8f} BTC (Testnet)")
    except Exception as e:
        click.echo(f"Error: {str(e) or 'Unknown error during balance check'}")


@cli.command()
@click.option("--privatekey", prompt=True, hide_input=True, help="Private key (WIF) of the sender wallet")
@click.argument("receiver")
@click.argument("amount", type=float)
def send_transaction(privatekey, receiver, amount):
    """Send a Bitcoin testnet transaction."""
    try:
        blockchain = BlockchainModule()
        transaction = TransactionModule(blockchain)
        wallet_module = WalletModule()
        wallet_info = wallet_module.load_wallet_from_privatekey(privatekey)
        click.echo(f"Sending from address: {wallet_info['address']}")
        txid = transaction.send_transaction(privatekey, receiver, amount)
        click.echo(f"Transaction sent! TxID: {txid}")
    except Exception as e:
        click.echo(f"Error: {str(e) or 'Unknown error during transaction'}")


if __name__ == "__main__":
    cli()

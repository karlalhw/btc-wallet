# Bitcoin Wallet Simulator (Testnet)

A non-custodial Bitcoin testnet wallet built with Python, using a modular architecture for secure key generation, balance checking, and transaction sending via the Blockcypher API. Ideal for learning Bitcoin wallet mechanics and fintech applications.

## Setup

1. **Install Dependencies**:
   - Install required libraries: `pip install -r requirements.txt`
   - Ensure Python 3.8+ is installed.

2. **Set Blockcypher API Token**:
   - Sign up at https://accounts.blockcypher.com/ to get a free testnet API token.
   - Set the token as an environment variable:
     - **Linux/macOS**: `export BLOCKCYPHER_API_TOKEN="your_token"`
     - **Windows (Git Bash)**: `export BLOCKCYPHER_API_TOKEN="your_token"`
     - **Windows (Command Prompt)**: `set BLOCKCYPHER_API_TOKEN=your_token`
     - **Windows (PowerShell)**: `$env:BLOCKCYPHER_API_TOKEN="your_token"`

3. **Run the Wallet**:
   - Check available commands: `python btc_wallet.py --help`

## Commands

- **Generate Wallet**:
  - Command: `python btc_wallet.py generate_wallet`
  - Output: Testnet SegWit address (starts with `tb1q`), WIF key (starts with `c`), mnemonic phrase.
  - Example: `Address: tb1q7zqrz..., WIF: c..., Mnemonic: apple banana ...`

- **Check Balance**:
  - Command: `python btc_wallet.py check_balance <address>`
  - Output: Balance in BTC.
  - Example: `Balance: 0.00002500 BTC`

- **Send Transaction**:
  - Command: `python btc_wallet.py send-transaction --wif <wif_key> <receiver> <amount>`
  - Output: Transaction ID (TxID).
  - Example: `TxID: 5c61f8fc...` (sends to `tb1qf3qfrm...`)

## Technical Details

- **Wallet**: Generates P2WPKH (SegWit) addresses using BIP-84 derivation path `m/84'/1'/0'/0/0` for testnet (`tb1q`). Uses BIP-39 for mnemonic phrases and BIP-32 for key derivation.
- **Transactions**: Creates P2WPKH transactions with witness data (sig_pubkey: signature and public key) for secure, low-fee transfers.
- **Dependencies**:
  - `bitcoinlib`: For key generation and transaction signing.
  - `click`: For CLI interface.
  - `requests`: For Blockcypher API queries.
- **Fee**: Minimum 0.000005 BTC (500 satoshis); ensure amount + fee ≤ balance.
- **UTXO Confirmation**: Transactions require confirmed UTXOs (10-60 minutes on testnet).

## Troubleshooting

- **API Timeouts**: Set a valid `BLOCKCYPHER_API_TOKEN`, check network, or retry later.
- **Invalid SegWit Transaction (HTTP 400 Bad Request)**:
  - **Cause**: Invalid witness data (e.g., incorrect sig_pubkey due to wrong WIF key or UTXOs).
  - **Solution**: Verify WIF key matches sending address, ensure valid UTXOs via Blockcypher API, check `bitcoinlib` configuration (`network="testnet", witness_type="segwit"`).
- **Rate Limits**: ~2000 requests/day, 6/sec with token. Contact Blockcypher if needed.

## Security

- **Mnemonic**: Save your mnemonic phrase offline securely. It’s required to recover your wallet.
- **WIF Key**: Controls one address; keep it private.
- **Testnet**: Uses testnet Bitcoin (no real value), safe for testing.

**WARNING**: Never share your mnemonic or WIF key. Use only on testnet.
# Bitcoin Wallet Simulator (Testnet)

A non-custodial Bitcoin testnet wallet CLI built with Python. It demonstrates secure key generation, balance checking, and transaction sending using the Blockcypher API. Modular architecture with separate modules for wallet, blockchain, and transaction logic.

Ideal for learning Bitcoin mechanics, fintech development, and Web3 concepts.

## Features

- Generate new SegWit testnet wallets (BIP-84 derivation)
- Check real-time balance via Blockcypher
- Send signed transactions with proper witness data
- Interactive web demo via Streamlit (browser-based CLI)

## Quick Start

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/btc-wallet.git
cd btc-wallet
```

2. **Set up virtual environment**

```bash
python -m venv env
env\Scripts\activate   # Windows
# or source env/bin/activate   # macOS/Linux
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set Blockcypher API token**
   Create a `.env` file:

```bash
BLOCKCYPHER_API_TOKEN=your_token_here
```

(Get free testnet token at https://accounts.blockcypher.com/)

5. **Run the CLI**

```bash
python btc_wallet.py --help
```

Example commands:

```bash
python btc_wallet.py generate_wallet
python btc_wallet.py check_balance tb1q...
python btc_wallet.py send-transaction --privatekey c... tb1q... 0.0001
```

6. **Run the Web Demo**

```bash
streamlit run app.py
```

Open http://localhost:8501

## Commands

| Command                   | Description                      | Example                                                                  |
| ------------------------- | -------------------------------- | ------------------------------------------------------------------------ |
| `generate_wallet`         | Create new testnet SegWit wallet | `python btc_wallet.py generate_wallet`                                   |
| `check_balance <address>` | Show balance in BTC              | `python btc_wallet.py check_balance tb1q...`                             |
| `send-transaction`        | Send BTC with WIF private key    | `python btc_wallet.py send-transaction --privatekey c... tb1q... 0.0001` |

**Warning**: Always save mnemonic and WIF key securely — they control funds on testnet.

## Technical Stack

- **bitcoinlib**: Key generation, signing, BIP-32/39/84
- **click**: CLI interface
- **requests**: Blockcypher API calls
- **streamlit**: Interactive web demo
- **dotenv**: Environment variable loading

## Security & Warnings

- Testnet only — no real value at risk
- Never share mnemonic or WIF key
- Use only with testnet addresses (tb1q...)
- API rate limit: ~2000 req/day with token

## Live Demo

Coming soon: [https://karlalhw.com/btc-wallet-demo](https://karla.com/btc-wallet-demo)

(Updates automatically via GitHub Actions when code is pushed)

## Troubleshooting

- **ModuleNotFoundError**: Run pip install -r requirements.txt
- **Invalid transaction (HTTP 400)**: Check WIF key, UTXO confirmation (10–60 min), and witness type (segwit)
- **API errors**: Verify token, check Blockcypher status, or retry later

Contributions, issues, and suggestions welcome!

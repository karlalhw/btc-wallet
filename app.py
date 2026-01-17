import streamlit as st
from dotenv import load_dotenv
import os
import subprocess
import sys
from pathlib import Path

# Try to find venv python relative to current file
project_root = Path(__file__).parent
venv_python = project_root / "env" / "Scripts" / "python.exe"

if not venv_python.exists():
    venv_python = sys.executable  # fallback to current Python

# Load environment variables (BLOCKCYPHER_TOKEN)
load_dotenv()

# Title and description
st.title("BTC Wallet CLI Demo (Testnet)")
st.markdown("""
This is a web interface for my Bitcoin testnet CLI wallet.  
Enter commands like:
- `generate-wallet`
- `check-balance <address>`
- `send-transaction <privatekey> <receiver> <amount>`
""")

# Input field for the command
command_input = st.text_input(
    "Enter CLI command", placeholder="e.g. generate-wallet or check-balance 2N...")

if st.button("Run Command"):
    if not command_input.strip():
        st.warning("Please enter a command.")
    else:
        # Get the Blockcypher token from env
        token = os.getenv("BLOCKCYPHER_API_TOKEN")
        if not token:
            st.error("BLOCKCYPHER_API_TOKEN not found in environment variables.")
        else:
            try:
                # Run your CLI script with the command as argument
                result = subprocess.run(
                    [str(venv_python), "btc_wallet.py"] +
                    command_input.split(),
                    capture_output=True,
                    text=True,
                    env={**os.environ, "BLOCKCYPHER_API_TOKEN": token}
                )

                if result.returncode == 0:
                    st.success("Command executed successfully!")
                    st.code(result.stdout.strip())
                else:
                    st.error("Command failed!")
                    st.code(result.stderr.strip())

            except Exception as e:
                st.error(f"Error running command: {str(e)}")

import time
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.types import TxOpts

# Konfigurasi Wallet & Endpoint
PRIVATE_KEY = bytes.fromhex("3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB")
WALLET = Keypair.from_secret_key(PRIVATE_KEY)
SOLANA_URL = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_URL)

# Konfigurasi Bot
BUY_AMOUNT_SOL = 0.01
BUYER_COUNT_LIMIT = 20
TRAILING_STOP_PERCENT = 0.05
token_history = {}

# Fungsi Beli Token
def buy_token(token_address):
    print(f"🚀 Membeli token: {token_address}")
    token_history[token_address] = {
        "bought_price": get_price(token_address),
        "highest_price": get_price(token_address)
    }

# Fungsi Harga Token (Dummy)
def get_price(token_address):
    return 1.0  # Simulasi harga awal

# Fungsi Cek Trailing Stop
def check_trailing_stop(token_address):
    current_price = get_price(token_address)
    if current_price > token_history[token_address]["highest_price"]:
        token_history[token_address]["highest_price"] = current_price
    drop = (token_history[token_address]["highest_price"] - current_price) / token_history[token_address]["highest_price"]
    if drop >= TRAILING_STOP_PERCENT:
        print(f"🔻 Menjual {token_address} - harga turun {drop*100:.2f}% dari puncak")
        sell_token(token_address)

# Fungsi Jual Token (Dummy)
def sell_token(token_address):
    print(f"💰 Token dijual: {token_address}")
    del token_history[token_address]

# Fungsi Dapatkan Token Baru (Dummy)
def get_new_tokens():
    return [
        {"address": "TokenA1", "buyerCount": 12},
        {"address": "TokenB2", "buyerCount": 5},
        {"address": "TokenC3", "buyerCount": 18}
    ]

# Bot Utama
def run_bot():
    print("🤖 Bot dijalankan...")
    while True:
        tokens = get_new_tokens()
        for token in tokens:
            if 10 < token["buyerCount"] <= BUYER_COUNT_LIMIT:
                if token["address"] not in token_history:
                    buy_token(token["address"])
        for token_address in list(token_history.keys()):
            check_trailing_stop(token_address)
        time.sleep(5)

# Jalankan
run_bot()

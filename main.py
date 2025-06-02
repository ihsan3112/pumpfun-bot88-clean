import time
import requests
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.config import RpcSendTransactionConfig
from solders.transaction import VersionedTransaction
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

# Konfigurasi
BUY_AMOUNT_SOL = 0.01
TRAILING_STOP_PERCENT = 0.05  # 5%
BUYER_COUNT_MIN = 11
PRIVATE_KEY = Keypair.from_base58_string("3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB")
solana_client = Client("https://api.mainnet-beta.solana.com")

bought_tokens = {}

def get_new_tokens():
    try:
        response = requests.get("https://pump.fun/api/recent")
        return response.json()
    except Exception as e:
        print("Error fetch token:", e)
        return []

def get_token_info(token_address):
    try:
        url = f"https://pump.fun/{token_address}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return ""
    except Exception:
        return ""

def buy_token(token_address):
    print(f"Membeli token {token_address} sebanyak {BUY_AMOUNT_SOL} SOL...")
    bought_tokens[token_address] = {
        "buy_price": get_token_price(token_address),
        "highest_price": get_token_price(token_address)
    }

def get_token_price(token_address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
        data = requests.get(url).json()
        return float(data['pair']['priceUsd'])
    except:
        return 0.0

def sell_token(token_address):
    print(f"Menjual token {token_address} karena turun lebih dari {TRAILING_STOP_PERCENT*100}% dari harga tertinggi")

def monitor_tokens():
    while True:
        tokens = get_new_tokens()
        for token in tokens:
            token_address = token.get("tokenAddress")
            buyer_count = token.get("buyerCount", 0)

            if token_address and buyer_count >= BUYER_COUNT_MIN and token_address not in bought_tokens:
                buy_token(token_address)

        # Trailing stop check
        for token_address, data in list(bought_tokens.items()):
            current_price = get_token_price(token_address)
            if current_price > data["highest_price"]:
                bought_tokens[token_address]["highest_price"] = current_price

            threshold_price = data["highest_price"] * (1 - TRAILING_STOP_PERCENT)
            if current_price < threshold_price:
                sell_token(token_address)
                del bought_tokens[token_address]

        time.sleep(10)

if __name__ == "__main__":
    print("Memulai bot Pump.fun - Memory 2")
    monitor_tokens()

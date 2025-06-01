import requests
import time
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solders.signature import Signature

# --- Konfigurasi utama ---
PRIVATE_KEY = "3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB"
BUY_AMOUNT_SOL = 0.01
MAX_BUYER_COUNT = 10
TRAILING_STOP_PERCENT = 0.20

# --- Setup Solana client dan keypair ---
client = Client("https://api.mainnet-beta.solana.com")
keypair = Keypair.from_base58_string(PRIVATE_KEY)
wallet_address = str(keypair.pubkey())

def get_trending_tokens():
    try:
        res = requests.get("https://pump.fun/api/trending")
        tokens = res.json()
        return tokens
    except Exception as e:
        print(f"Error get tokens: {e}")
        return []

def buy_token(token):
    # Fungsi pembelian dummy - disesuaikan dgn smart contract Pump.fun kalau mau aktif
    print(f"[BUY] Token: {token['mint']} | Buyer count: {token['buyerCount']}")

def monitor_trailing_stop(token):
    mint = token['mint']
    max_price = 0
    while True:
        try:
            res = requests.get(f"https://pump.fun/api/price/{mint}")
            price = float(res.json().get("price", 0))
            if price > max_price:
                max_price = price
            if price < max_price * (1 - TRAILING_STOP_PERCENT):
                print(f"[SELL] Trailing Stop triggered: Price dropped from {max_price} to {price}")
                # Tambahkan logika sell di sini jika mau real transaction
                break
            time.sleep(10)
        except Exception as e:
            print(f"Error monitoring stop: {e}")
            break

def main():
    while True:
        tokens = get_trending_tokens()
        for token in tokens:
            buyer_count = token.get("buyerCount", 0)
            if buyer_count <= MAX_BUYER_COUNT:
                print(f"Found Token: {token['mint']} | Buyers: {buyer_count}")
                buy_token(token)
                monitor_trailing_stop(token)
                time.sleep(3)  # Jeda antar pembelian
        time.sleep(30)  # Delay polling API utama

if __name__ == "__main__":
    main()

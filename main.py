print("⛔ Bot Memory 3 dihentikan sementara. Tidak ada eksekusi auto-buy saat ini.")
# Memory 3 - Pump.fun Bot
# Logika: 
# - Beli token hanya jika buyer count >= 20
# - Pastikan token masih bertahan setidaknya 2 menit
# - Tambahkan proteksi agar buyer count tidak drop drastis
# - Trailing stop 5%
# - Jumlah beli 0.01 SOL

import requests
import time
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

PRIVATE_KEY = Keypair.from_base58_string("3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB")
WALLET_ADDRESS = str(PRIVATE_KEY.pubkey())
client = Client("https://api.mainnet-beta.solana.com")

checked_tokens = {}
buy_amount = 0.01  # in SOL
minimum_buyers = 20
trailing_stop_percentage = 0.05

print("[BOT] Memory 3 aktif. Menunggu token valid...")

def get_new_tokens():
    try:
        res = requests.get("https://pump.fun/api/token/list?sort=recent")
        data = res.json()
        return data
    except:
        return []

def get_token_details(token):
    try:
        res = requests.get(f"https://pump.fun/api/token/{token}")
        return res.json()
    except:
        return {}

def buy_token(token):
    print(f"[BELI] Eksekusi beli token: {token}")
    # Placeholder transaksi pembelian token
    # Tambahkan logika pembelian SPL token di sini
    pass

def check_trailing_stop(token, buy_price):
    high_price = buy_price
    while True:
        data = get_token_details(token)
        current_price = data.get("price", buy_price)

        if current_price > high_price:
            high_price = current_price

        drop_trigger = high_price * (1 - trailing_stop_percentage)
        if current_price < drop_trigger:
            print(f"[JUAL] Trailing stop triggered! Harga turun ke {current_price:.6f}")
            # Placeholder logika jual
            return

        time.sleep(15)

while True:
    tokens = get_new_tokens()
    for token in tokens:
        token_id = token.get("id")
        if token_id in checked_tokens:
            continue

        detail = get_token_details(token_id)
        buyers = detail.get("buyerCount", 0)
        time_live = detail.get("launchedAt", 0)

        if buyers >= minimum_buyers:
            now = int(time.time())
            if now - time_live >= 120:  # 2 menit
                print(f"[VALID] Token lolos filter: {token_id} dengan {buyers} buyers")
                buy_token(token_id)
                price = detail.get("price", 0.00001)
                check_trailing_stop(token_id, price)

        checked_tokens[token_id] = True

    time.sleep(10)

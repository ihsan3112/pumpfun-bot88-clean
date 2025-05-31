import requests
import time
import threading
from flask import Flask, request
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import transfer, TransferParams
from solana.rpc.types import TxOpts
import base58
import os

# === Konfigurasi ===
PRIVATE_KEY = "3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB"
RPC_URL = "https://rpc.ankr.com/solana"
BUY_AMOUNT_SOL = 0.03
BUYER_THRESHOLD = 10
MAX_ACTIVE_TRADES = 5
ACCESS_KEY = "sansha99"

# === Inisialisasi ===
client = Client(RPC_URL)
app = Flask(__name__)
robot_ready = False
active_trades = []
known_tokens = set()

# === Load Keypair ===
keypair = Keypair.from_secret_key(base58.b58decode(PRIVATE_KEY))
wallet_address = keypair.public_key

# === Fungsi Pantau Token Baru ===
def fetch_new_tokens():
    try:
        response = requests.get("https://client-api-2-74b6e9733e6d.herokuapp.com/tokens")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# === Fungsi Beli Token ===
def buy_token(token_address):
    print(f"[BELI] Token: {token_address}")
    to_pubkey = PublicKey(token_address)
    lamports = int(BUY_AMOUNT_SOL * 1_000_000_000)
    tx = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=wallet_address,
                to_pubkey=to_pubkey,
                lamports=lamports
            )
        )
    )
    try:
        result = client.send_transaction(tx, keypair, opts=TxOpts(skip_preflight=True))
        print(f"[SUKSES BELI] Tx Hash: {result['result']}")
    except Exception as e:
        print(f"[GAGAL BELI] {e}")

# === Fungsi Dummy Harga Token ===
def get_token_price(token_address):
    return 1.0 + (time.time() % 10) / 100  # Simulasi harga naik turun

# === Fungsi Jual Token ===
def sell_token(token_address):
    print(f"[JUAL] Token: {token_address} — dijual karena turun 20% dari puncak")
    if token_address in active_trades:
        active_trades.remove(token_address)

# === Pantau Harga dan Jual ===
def monitor_price_and_sell(token_address, buy_price):
    highest = buy_price
    while True:
        try:
            price = get_token_price(token_address)
            if price > highest:
                highest = price
            drop = (highest - price) / highest
            if drop >= 0.2:
                sell_token(token_address)
                break
        except:
            break
        time.sleep(3)

# === Fungsi Utama Beli Token ===
def start_robot():
    tokens = fetch_new_tokens()
    for token in tokens:
        address = token.get("address")
        buyers = token.get("buyers")
        if not address or not buyers or address in known_tokens:
            continue
        if buyers >= BUYER_THRESHOLD and len(active_trades) < MAX_ACTIVE_TRADES:
            known_tokens.add(address)
            active_trades.append(address)
            buy_token(address)
            buy_price = get_token_price(address)
            threading.Thread(target=monitor_price_and_sell, args=(address, buy_price)).start()
        time.sleep(2)

# === Endpoint Web ===
@app.route('/resume')
def resume():
    global robot_ready
    key = request.args.get("key", "")
    if key != ACCESS_KEY:
        return "❌ Kunci salah", 403
    robot_ready = True
    return "✅ Bot dilanjutkan!"

@app.route('/pause')
def pause():
    global robot_ready
    key = request.args.get("key", "")
    if key != ACCESS_KEY:
        return "❌ Kunci salah", 403
    robot_ready = False
    return "⏸️ Bot dijeda."

# === Thread Utama ===
def main_loop():
    last_state = False
    while True:
        if robot_ready and not last_state:
            threading.Thread(target=start_robot).start()
            last_state = True
        elif not robot_ready:
            last_state = False
        time.sleep(1)

# === Jalankan Flask dan Bot Bersamaan ===
if __name__ == '__main__':
    threading.Thread(target=main_loop).start()
    app.run(host='0.0.0.0', port=80)

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
wallet_address = str(keypair.public_key)

# === Fungsi Fetch Token ===
def fetch_new_tokens():
    try:
        res = requests.get("https://pump.fun/api/tokens")
        data = res.json()
        return data
    except Exception as e:
        print("Gagal fetch token:", e)
        return []

# === Fungsi Harga Token ===
def get_token_price(address):
    try:
        res = requests.get(f"https://pump.fun/api/token/{address}")
        return res.json().get("price", 0)
    except:
        return 0

# === Fungsi Auto-Buy Token ===
def buy_token(address):
    print("🟢 Membeli token:", address)
    tx = Transaction()
    tx.add(
        transfer(
            TransferParams(
                from_pubkey=keypair.public_key,
                to_pubkey=PublicKey(address),
                lamports=int(BUY_AMOUNT_SOL * 1_000_000_000),
            )
        )
    )
    try:
        response = client.send_transaction(tx, keypair, opts=TxOpts(skip_preflight=True))
        print("✅ Transaksi:", response)
    except Exception as e:
        print("❌ Gagal transaksi:", e)

# === Fungsi Penjualan Token (dummy) ===
def sell_token(address):
    print("🔴 Menjual token:", address)
    # Placeholder jual, bisa isi metode DEX di sini
    pass

# === Fungsi Pantau Harga ===
def monitor_price_and_sell(address, buy_price):
    peak_price = buy_price
    stop_loss_triggered = False
    while True:
        try:
            current_price = get_token_price(address)
            if current_price > peak_price:
                peak_price = current_price
            elif current_price < peak_price * 0.8:
                print("📉 Trailing stop triggered, menjual:", address)
                sell_token(address)
                break
        except:
            pass
        time.sleep(3)

# === Fungsi Utama Bot ===
def start_robot():
    global active_trades
    tokens = fetch_new_tokens()
    for token in tokens:
        address = token.get("address")
        buyer_count = token.get("buyerCount", 0)
        if not address or address in known_tokens or buyer_count < BUYER_THRESHOLD:
            continue
        if len(active_trades) >= MAX_ACTIVE_TRADES:
            continue
        known_tokens.add(address)
        active_trades.append(address)
        buy_token(address)
        buy_price = get_token_price(address)
        threading.Thread(target=monitor_price_and_sell, args=(address, buy_price)).start()
        time.sleep(2)

# === Endpoint Flask ===
@app.route('/start')
def trigger():
    global robot_ready
    if request.args.get("key") != ACCESS_KEY:
        return "Unauthorized", 403
    robot_ready = True
    return "✅ Bot aktif!"

@app.route('/pause')
def pause():
    global robot_ready
    if request.args.get("key") != ACCESS_KEY:
        return "Unauthorized", 403
    robot_ready = False
    return "⏸️ Bot dijeda"

# === Thread utama ===
def background_loop():
    while True:
        if robot_ready:
            start_robot()
        time.sleep(1)

# === Start Bot Otomatis Saat App Jalan ===
threading.Thread(target=background_loop, daemon=True).start()

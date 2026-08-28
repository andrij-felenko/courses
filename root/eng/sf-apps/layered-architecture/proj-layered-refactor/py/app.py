# app.py — усе в одному обробнику: HTTP + правило + SQL
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/orders")
def place_order():
    body = request.get_json()
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()

    total = 0.0
    for line in body["items"]:
        row = cur.execute(
            "SELECT price, stock FROM products WHERE sku = ?",
            (line["sku"],)).fetchone()
        if row is None:
            return jsonify(error=f"немає товару {line['sku']}"), 404
        price, stock = row
        if stock < line["qty"]:
            return jsonify(error=f"замало {line['sku']}"), 409
        total += price * line["qty"]

    # знижка за промокодом — правило бізнесу, вписане просто тут
    code = body.get("promo")
    if code == "SPRING":
        total *= 0.9
    elif code == "VIP":
        total *= 0.8

    order_id = cur.execute(
        "INSERT INTO orders(total) VALUES (?)", (total,)).lastrowid
    for line in body["items"]:
        cur.execute("UPDATE products SET stock = stock - ? WHERE sku = ?",
                    (line["qty"], line["sku"]))
    conn.commit()
    return jsonify(order_id=order_id, total=total), 201

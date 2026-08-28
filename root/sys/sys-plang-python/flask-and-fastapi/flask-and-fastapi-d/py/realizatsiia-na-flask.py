import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, g

app = Flask(__name__)
DATABASE_PATH = os.getenv("DB_PATH", "telemetry_flask.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                pressure_hpa REAL NOT NULL,
                battery_mv INTEGER NOT NULL
            )
        """)

@app.route("/api/v1/telemetry", methods=["POST"])
def ingest_telemetry():
    # 1. Перевірка заголовка авторизації
    token = request.headers.get("X-Sensor-Token")
    if token != "secret-station-token":
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Отримання та парсинг JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON format"}), 400

    # 3. Ручна валідація полів
    required_fields = ["device_id", "timestamp", "temperature", "humidity", "pressure_hpa", "battery_mv"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 422

    device_id = str(data["device_id"])
    try:
        ts = datetime.fromisoformat(data["timestamp"])
        temp = float(data["temperature"])
        hum = float(data["humidity"])
        press = float(data["pressure_hpa"])
        batt = int(data["battery_mv"])
    except (ValueError, TypeError) as exc:
        return jsonify({"error": "Data type validation failed", "details": str(exc)}), 422

    if not (-50.0 <= temp <= 85.0) or not (0.0 <= hum <= 100.0) or not (300.0 <= press <= 1200.0):
        return jsonify({"error": "Sensor value out of physical bounds"}), 422

    # 4. Запис у базу даних
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO telemetry (device_id, timestamp, temperature, humidity, pressure_hpa, battery_mv)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (device_id, ts.isoformat(), temp, hum, press, batt))
    db.commit()

    return jsonify({"status": "success", "id": cursor.lastrowid}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)

import time
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/v1/telemetry", methods=["POST"])
def ingest_telemetry():
    # 1. Перевірка заголовка автентифікації
    token = request.headers.get("X-Sensor-Token")
    if token != "secret-station-token":
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Отримання та валідація JSON-пакета
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    device_id = data.get("device_id")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    battery_mv = data.get("battery_mv")

    if not isinstance(device_id, str) or not (3 <= len(device_id) <= 32):
        return jsonify({"error": "Invalid device_id"}), 422
    if not isinstance(temperature, (int, float)) or not (-50.0 <= temperature <= 150.0):
        return jsonify({"error": "Invalid temperature"}), 422
    if not isinstance(humidity, (int, float)) or not (0.0 <= humidity <= 100.0):
        return jsonify({"error": "Invalid humidity"}), 422
    if not isinstance(battery_mv, int) or not (0 <= battery_mv <= 5000):
        return jsonify({"error": "Invalid battery_mv"}), 422

    # 3. Емуляція блокувального запису в БД (15 мс)
    time.sleep(0.015)

    return jsonify({"status": "stored", "device_id": device_id}), 200

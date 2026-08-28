# Підхід Flask з ручною валідацією або Marshmallow
@app.route("/api/v1/telemetry", methods=["POST"])
def ingest():
    data = request.get_json()
    if not data or "device_id" not in data or "temperature" not in data:
        return jsonify({"error": "Bad Request", "details": "Missing fields"}), 400
    
    # Ручна перевірка типів та меж значень
    try:
        temp = float(data["temperature"])
        if not (-50.0 <= temp <= 150.0):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Validation Error", "field": "temperature"}), 422

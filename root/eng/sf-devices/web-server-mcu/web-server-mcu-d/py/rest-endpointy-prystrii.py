# POST /led з тілом {"on":true} — прочитати тіло й перемкнути світло.
from flask import request, jsonify, abort

@app.route("/led", methods=["POST"])
def led_post():
    if request.content_length and request.content_length >= 64:
        abort(400, "тіло завелике")             # захист від завеликого тіла
    data = request.get_json(silent=True) or {}  # нормальний розбір JSON
    on = bool(data.get("on"))
    set_led(on)
    return jsonify(led=on)                       # Content-Type виставиться сам

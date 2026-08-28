# Хендлери на Flask: гілка /static/* і параметр запиту /led?state=on.
from flask import request

@app.route("/static/<path:name>")           # <path:...> ловить усю гілку
def static_get(name):                        # name = "app.js" — уже без префікса
    return send_file_from_fs(name)           # читаємо файл і віддаємо (нижче)

@app.route("/led")                           # /led?state=on
def led_get():
    state = request.args.get("state")        # окремий ключ query string
    if state is not None:
        set_led(state == "on")               # вмикаємо/вимикаємо
    return "ok"

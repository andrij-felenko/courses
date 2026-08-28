import hmac, hashlib, json, os
from flask import Flask, request, abort

app = Flask(__name__)
SECRET = os.environ["WEBHOOK_SECRET"].encode()

@app.post("/webhooks")
def receive():
    raw = request.get_data()                       # сирі байти, доки їх не чіпав розбір
    if not verify(raw, request.headers.get("X-Signature", "")):
        abort(401)                                 # підпис не збігся — геть

    try:
        event = json.loads(raw)                    # розбір ЛИШЕ після перевірки
    except ValueError:
        abort(400)                                 # криве тіло — не наша подія

    try:
        if inbox_insert(event["id"], event["type"], raw):   # нова — False, якщо дубль
            enqueue(event["id"])                   # роботу знімемо з гарячого шляху
        return "", 200                             # 200 і новій, і дублю
    except Exception:
        abort(500)                                 # не зберегли — хай ПОВТОРЯТЬ, не 200!

def verify(raw: bytes, sig: str) -> bool:
    expected = hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)      # сталий час

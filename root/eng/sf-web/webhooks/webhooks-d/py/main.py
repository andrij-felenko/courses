import hmac, hashlib, os
from flask import Flask, request, abort

app = Flask(__name__)
SECRET = os.environ["WEBHOOK_SECRET"].encode()
seen = set()                              # насправді — стійке сховище, не пам'ять

@app.post("/webhooks")
def receive():
    raw = request.get_data()              # сирі байти тіла, не розібраний JSON
    expected = hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    sig = request.headers.get("X-Signature", "")
    if not hmac.compare_digest(sig, expected):   # порівняння сталого часу
        abort(401)

    event = request.get_json()
    if event["id"] in seen:               # вже бачили — тихо
        return "", 200
    seen.add(event["id"])

    queue.put(event)                      # зняти роботу з гарячого шляху
    return "", 200                        # підтвердити ОДРАЗУ

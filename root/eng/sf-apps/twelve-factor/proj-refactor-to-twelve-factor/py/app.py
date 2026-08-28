# app.py — застосунок «до». Працює на одній машині й тільки на ній.
from flask import Flask, request, session, send_file

app = Flask(__name__)

# ── прив'язка №1: конфіг зашитий у код ──
app.secret_key = "super-secret-please-change"        # ключ підпису сесій
DATABASE_URL = "postgresql://localhost:5432/photos"  # адреса бази — «localhost»
UPLOAD_DIR = "/var/app/uploads"                       # тека на ЦЬОМУ диску

# ── прив'язка №2: сесія живе в пам'яті ЦЬОГО процесу ──
# (Flask за замовчуванням кладе сесію в підписану cookie, але щойно
#  ми починаємо тримати «залогінених» у власному dict — стан осідає в процесі)
logged_in_users = {}   # session_id -> user_id, у пам'яті процесу

@app.post("/login")
def login():
    user_id = check_password(request.form["user"], request.form["pass"])
    session["sid"] = new_session_id()
    logged_in_users[session["sid"]] = user_id   # ← стан у пам'яті
    return {"ok": True}

@app.post("/upload")
def upload():
    user_id = logged_in_users[session["sid"]]         # хто вантажить
    photo = request.files["photo"]
    path = f"{UPLOAD_DIR}/{user_id}/{photo.filename}"  # ← файл на локальний диск
    photo.save(path)
    return {"stored": path}

@app.get("/photo/<user_id>/<name>")
def get_photo(user_id, name):
    return send_file(f"{UPLOAD_DIR}/{user_id}/{name}")  # ← читаємо з ЦЬОГО диска

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)   # ← порт зашитий у код

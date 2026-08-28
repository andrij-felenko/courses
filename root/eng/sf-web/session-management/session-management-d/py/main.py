import secrets, time

sessions: dict[str, dict] = {}          # правда живе на сервері

def login(response, user_id: str) -> None:
    sid = secrets.token_hex(16)         # 128 біт із CSPRNG
    sessions[sid] = {"user_id": user_id, "created_at": time.time()}
    response.set_cookie("sid", sid, httponly=True, secure=True, samesite="Lax")

def who_am_i(request) -> str | None:
    sid = request.cookies.get("sid")
    session = sessions.get(sid) if sid else None
    return session["user_id"] if session else None     # немає запису → анонім

def logout(sid: str) -> None:
    sessions.pop(sid, None)       # знищуємо ПРАВДУ на сервері, не лише cookie

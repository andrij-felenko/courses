from dataclasses import dataclass
from fastapi import FastAPI, Depends, HTTPException, Request

app = FastAPI()

# ── Домен ────────────────────────────────────────────────
@dataclass(frozen=True)
class Subject:
    id: str

@dataclass(frozen=True)
class Home:
    id: str
    owner_id: str

Role   = str   # "guest" | "family" | "founder"
Action = str   # "read"  | "write"  | "manage"

# Автентифікація — на краю, залежністю: токен → суб'єкт
def current_subject(request: Request) -> Subject:
    subject = verify_token(request.headers.get("authorization"))
    if subject is None:                              # немає / хибний / протух
        raise HTTPException(401, headers={"WWW-Authenticate": "Bearer"})
    return subject

# ⛔ БАГ: спитано лише «хто», не «що саме йому можна»
@app.get("/homes/{home_id}/thermostat")
def get_thermostat(home_id: str, subject: Subject = Depends(current_subject)):
    home = homes.get(home_id)                        # home_id — рядок від клієнта
    if home is None:
        raise HTTPException(404)
    return read_thermostat(home)                     # ← другої брами немає

@app.get("/homes/{home_id}/thermostat")
def thermostat(home_id: str, req: Request):
    # Питання 1 — автентифікація: хто на іншому кінці?
    subject = authenticate(req)                  # токен → суб'єкт, або None
    if subject is None:
        raise HTTPException(401)                 # «не знаю тебе» → 401

    # Питання 2 — авторизація: чи можна САМЕ ЦЬОМУ суб'єктові саме ЦЕ?
    home = homes.get(home_id)                    # ← об'єкт, якого двері ще не бачили
    if not can_read(subject, home):
        raise HTTPException(403)                 # «знаю — але ні» → 403

    return read_thermostat(home)                 # обидві межі пройдено

# ── Брама 2: тонка ОБ'ЄКТНА авторизація ──
async def unlock_door(req, door_id: str):
    subject = attested_subject(req)                      # хто — із ЗАСВІДЧЕННЯ, не з токена
    door = await devices.load(door_id)                   # об'єкт У РУКАХ: у ньому home_id
    if door is None:
        raise Http(404)
    if not await authz.can(subject, "unlock", door):     # «цей замок — у ТВОЄМУ домі?» ключ = door.home_id
        raise Http(403)                                  # чужий дім → 403, IDOR закрито
    await door.unlock()                                  # обидві брами пройдено → сигнал на хаб
    return {"ok": True}

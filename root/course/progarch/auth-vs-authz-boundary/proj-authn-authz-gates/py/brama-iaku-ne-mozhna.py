# Фабрика брами: залежність, що вантажить дім і пускає лише з правом.
# Обробник ОДЕРЖУЄ вже авторизований дім параметром — інакше його просто нема.
def authorized_home(action: Action):
    def dep(home_id: str, subject: Subject = Depends(current_subject)) -> Home:
        home = homes.get(home_id)
        if home is None:
            raise HTTPException(404)
        if not can(subject, action, home):
            raise HTTPException(403)
        return home
    return dep

@app.get("/homes/{home_id}/thermostat")
def get_thermostat(home: Home = Depends(authorized_home("read"))):
    return read_thermostat(home)                     # дім тут ⇒ право вже перевірено

@app.put("/homes/{home_id}/thermostat")
def put_thermostat(target: float, home: Home = Depends(authorized_home("write"))):
    set_thermostat(home, target)
    return {"ok": True}                              # сюди Гриць-гість не дійде

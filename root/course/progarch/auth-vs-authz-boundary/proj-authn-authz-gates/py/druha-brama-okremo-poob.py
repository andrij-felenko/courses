def can_read(subject: Subject, home: Home) -> bool:
    return home.owner_id == subject.id               # поки що — тільки власник

@app.get("/homes/{home_id}/thermostat")
def get_thermostat(home_id: str, subject: Subject = Depends(current_subject)):
    home = homes.get(home_id)
    if home is None:
        raise HTTPException(404)
    if not can_read(subject, home):                  # ← друга брама, ПІСЛЯ завантаження
        raise HTTPException(403)
    return read_thermostat(home)

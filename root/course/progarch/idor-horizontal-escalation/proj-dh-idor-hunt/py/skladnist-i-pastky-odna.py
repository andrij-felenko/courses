@app.get("/api/homes/{home_id}/devices/{device_id}")
def get_device(home_id: str, device_id: str, user: User = Depends(current_user)):
    home = homes.by_id(home_id)
    if home is None or not home.belongs_to(user.id):
        raise HTTPException(404)
    device = devices.by_id(device_id)
    # пристрій мусить належати саме цьому дому, а не будь-якому нашому
    if device is None or device.home_id != home.id:
        raise HTTPException(404)
    return device

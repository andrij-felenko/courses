# Точка входу 1: HTTP-контролер із вшитою перевіркою правила
@app.post("/api/heating/start")
def start_heating_web(payload: dict):
    room_id = payload["room_id"]
    target_temperature = payload["target_temperature"]

    # Доменне правило зашите безпосередньо в обробник запиту
    open_windows = db.query(
        "SELECT id FROM windows WHERE room_id = %s AND is_open = true",
        (room_id,)
    )
    if open_windows:
        return {"error": "Неможливо увімкнути опалення: вікна відчинені"}, 422

    db.query(
        "UPDATE climate SET target_temperature = %s, is_heating = true WHERE room_id = %s",
        (target_temperature, room_id)
    )
    return {"status": "ok"}, 200

# Точка входу 2: консольна утиліта монтажника (CLI)
def run_cli(args: list[str]):
    room_id = args[0]
    target_temperature = float(args[1])

    # Перевірку вікон пропущено: прямий запис у спільну базу даних
    db.query(
        "UPDATE climate SET target_temperature = %s, is_heating = true WHERE room_id = %s",
        (target_temperature, room_id)
    )
    print(f"Опалення кімнати {room_id} увімкнено на {target_temperature}°C")

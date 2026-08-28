# Хаб і хмара котяться нарізно. Тому читач ТЕРПЛЯЧИЙ:
# невідомі поля ігнорує, відсутні — підставляє за замовчуванням.
def from_wire(raw: dict) -> CloudDevice:
    return CloudDevice(
        raw["id"],
        raw.get("type", "unknown"),
        raw.get("room", "?"),
        raw.get("state", "unknown"),
        raw.get("brightness", 0),
        raw.get("last_seen", 0),
        # raw.get("signal") (нове поле v2) старий читач просто не чіпає — і не падає
    )

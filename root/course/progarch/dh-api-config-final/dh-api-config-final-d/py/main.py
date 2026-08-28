# Публічна поверхня v1: тільки ДОДАЄМО, ніколи не переінакшуємо.
# Одне джерело правди — доменний Device; старе виводимо з нового.
def to_dto(d: Device) -> dict:
    dto = {
        "id": d.id,                                       # формат опублікований — заморожений
        "temperature": {"value": d.temperature.value,
                        "unit": d.temperature.unit},      # канон — єдина правда
        "tempC": to_celsius(d.temperature),               # legacy: ПОХІДНЕ від канону
        "at": d.last_reading_at,
    }
    if d.power is not None:                               # НОВЕ поле — суто адитивно
        dto["power"] = {"watts": d.power.watts, "at": d.power.at}
    return dto

# Стабільний конверт помилки: машинний код + людський текст, і НІЧОГО зсередини.
def to_api_error(e: DomainError) -> dict:
    return {"error": {"code": e.code, "message": e.public_message}}
    # ані stack, ані SQL, ані шляху файлу — нутрощі лишаються неопублікованими

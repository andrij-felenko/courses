# honest.py — контракт межі, витягнутий у фабрику
from home import Reading

SENSOR_MIN, SENSOR_MAX = -40.0, 85.0        # паспортний діапазон давача

def reading(celsius: float, ok: bool = True) -> Reading:
    """Той самий контракт, що й драйвер: правдиве число ⇒ у паспортних межах."""
    if ok and not (SENSOR_MIN <= celsius <= SENSOR_MAX):
        raise ValueError(f"{celsius} °C поза −40…85: справжній давач такого з ok=True не дасть")
    return Reading(celsius, ok)

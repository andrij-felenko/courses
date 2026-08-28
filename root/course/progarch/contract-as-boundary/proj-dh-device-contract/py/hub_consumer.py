# hub_consumer.py — споживач, що спирається ЛИШЕ на I-1..I-6.
import time
from device_driver import DeviceDriver, Ok, Err

MIN_PERIOD_S = 1.0                                # I-5: не частіше 1/с — наш борг

def render(r) -> str:
    match r:                                      # I-3: множина закрита → розбір вичерпний
        case Err(reason="offline"): return "пристрій офлайн"
        case Err(reason="timeout"): return "пристрій не встиг"
        case Ok(temp_c=t):
            # I-1+I-2: t — °C у [−40,85]. Формат НАШ, на межі (I-6 мовчить про точність).
            return f"{t:.1f} °C"
        case _:
            raise AssertionError("нечинний Reading — контракт зламано")

def run(driver: DeviceDriver, show) -> None:
    while True:
        show(render(driver.read()))               # read не кине — обробляємо значення
        time.sleep(MIN_PERIOD_S)                  # розклад від СВОГО годинника, не з at

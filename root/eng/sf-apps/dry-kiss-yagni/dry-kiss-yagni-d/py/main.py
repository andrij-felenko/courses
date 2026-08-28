# Спекулятивно: гнучкість "на виріст", якої ніхто не просив.
# Реєстр драйверів, вибір протоколу, конфіг — усе заради ОДНОГО давача.
_drivers: dict[str, Callable[[], float]] = {}   # місце під те, чого нема

def sensor_register(name: str, read: Callable[[], float]) -> None:
    _drivers[name] = read                        # ...+ вибір протоколу, конфіг...

def sensor_read_by_name(name: str) -> float:
    return _drivers[name]()                       # ...пошук у реєстрі...

# Те саме, чесно за потребою: рівно те, що просили.
def read_temperature() -> float:
    return bmp280_read_celsius()                  # один давач — один виклик

# SensorUtils: звалище. Що спільного? Слово "sensor" у назві файлу — і все.
class SensorUtils:
    @staticmethod
    def celsius_from_raw(raw: int) -> float: ...      # математика перетворення
    @staticmethod
    def crc8(data: bytes) -> int: ...                 # контрольна сума I²C
    @staticmethod
    def log_reading(t: float) -> None: ...            # запис у кільцевий буфер
    @staticmethod
    def is_plausible(t: float) -> bool: ...           # перевірка діапазону
    @staticmethod
    def millis_since_boot() -> int: ...               # обгортка над таймером
    @staticmethod
    def blink_error(code: int) -> None: ...           # блимання світлодіодом
    # …ще п'ять таких самих різнорідних

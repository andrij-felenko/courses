# Дім для знання про конкретний давач — правиться при зміні давача
class Tmp117:
    @staticmethod
    def celsius(raw: int) -> float:
        return raw * 0.0078125          # 7.8125 м°C/LSB
    @staticmethod
    def plausible(c: float) -> bool:
        return -40.0 < c < 125.0

# Дім для знання про шину — правиться при зміні протоколу
class I2cFrame:
    @staticmethod
    def crc8(data: bytes) -> int: ...   # поліном 0x07, як у SMBus

# Дім для логу — правиться при зміні формату/носія
class ReadingLog:
    def append(self, celsius: float) -> None: ...

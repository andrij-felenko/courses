class TelemetrySink(Protocol):        # ВІДКЛАДЕНИЙ ШОВ на місці майбутнього розлому
    def append(self, device_id: str, ts: float, value: float) -> None: ...

class SqliteTelemetrySink:            # реалізація ЗАРАЗ: та сама реляційна база, послаблена тривкість
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn             # відкрито з synchronous=NORMAL (див. точку збірки)
    def append(self, device_id: str, ts: float, value: float) -> None:
        self._conn.execute("INSERT INTO measurement(device_id, ts, value) VALUES(?,?,?)",
                           (device_id, ts, value))     # autocommit: один короткий долив

# коли масштаб телеметрії справді зросте, СЮДИ стане інша реалізація — за ТИМ САМИМ портом:
# class LsmTelemetrySink:  def append(self, ...): ...   # окреме сховище, реєстру не чіпає

class StatusView:
    """Похідний погляд на пристрої для застосунку. Записати можна лише З ПРИСТРОЮ."""
    def __init__(self):
        self._by_id = {}

    def refresh(self, d):                       # ЄДИНИЙ шлях запису — завжди з пристрою
        self._by_id[d.id] = {"temp": d.temp, "online": d.online, "ts": now()}

    def get(self, device_id):                   # усі інші лише читають
        row = self._by_id.get(device_id)
        if row and now() - row["ts"] > TIMEOUT_S:
            return {**row, "stale": True}        # свіжість позначена, а не прихована
        return row

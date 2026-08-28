import json, os, threading

class FileDeviceRepository:                        # за портом DeviceRepository з v2
    def __init__(self, path: str = "dh-devices.json"):
        self._path = path
        self._lock = threading.Lock()              # черга писарів — про неї нижче
        self._devices: dict[str, Device] = self._load()

    def _load(self) -> dict[str, Device]:
        try:
            with open(self._path, encoding="utf-8") as f:
                rows = json.load(f)
        except FileNotFoundError:
            return {}                              # перший запуск — дім порожній
        return {r["id"]: Device.from_dict(r) for r in rows}

    def save(self, d: Device) -> None:
        with self._lock:                           # один писар за раз
            self._devices[d.id] = d                # онови памʼять…
            self._flush()                          # …і відразу поклади ВЕСЬ реєстр на диск

    def get(self, id: str) -> Device | None:
        return self._devices.get(id)

    def all(self) -> list[Device]:
        return list(self._devices.values())

    def _flush(self) -> None:                      # атомарний тривкий запис — серце класу
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([d.to_dict() for d in self._devices.values()], f, ensure_ascii=False)
            f.flush()                              # з буфера мови → в кеш ОС (ще летюче!)
            os.fsync(f.fileno())                   # кеш ОС → на носій, з підтвердженням
        os.replace(tmp, self._path)                # атомарна заміна: старий XOR новий

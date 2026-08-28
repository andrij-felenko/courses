# --- adapter_a.py: єдине місце, що знає SDK вендора A ---
import vendora  # тип вендора живе ЛИШЕ в цьому файлі

class VendorAStore(ObjectStore):
    def __init__(self, bucket: str) -> None:
        self._cli = vendora.Client(bucket)

    def put(self, key: str, data: bytes) -> None:
        st = self._cli.write(key, data)
        if st != vendora.OK:
            raise StoreError("vendorA put: " + vendora.str_status(st))

    def get(self, key: str) -> bytes | None:
        buf, st = self._cli.read(key)
        if st == vendora.NOT_FOUND:
            return None                       # не помилка!
        if st != vendora.OK:
            raise StoreError("vendorA get: " + vendora.str_status(st))
        return buf

    def list(self, prefix: str) -> list[str]:
        return [obj.key for obj in self._cli.enumerate(prefix)]  # SDK гортає сам

# --- adapter_b.py: єдине місце, що знає SDK вендора B ---
import vendorb  # тип вендора живе ЛИШЕ в цьому файлі

class VendorBStore(ObjectStore):
    def __init__(self, container: str) -> None:
        self._svc = vendorb.connect(container)

    def put(self, key: str, data: bytes) -> None:
        try:
            self._svc.upload(key, data)              # кидає при збої
        except vendorb.Error as e:
            raise StoreError(f"vendorB put: {e}") from e

    def get(self, key: str) -> bytes | None:
        try:
            blob = self._svc.download(key)
            return blob.as_bytes()
        except vendorb.NotFound:
            return None                             # приводимо до нашого правила
        except vendorb.Error as e:
            raise StoreError(f"vendorB get: {e}") from e

    def list(self, prefix: str) -> list[str]:
        return list(self._svc.list_blobs(prefix))

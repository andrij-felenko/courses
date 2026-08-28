from enum import Enum

class Vendor(Enum):
    A = "a"
    B = "b"

# Єдине місце, що знає обидва адаптери. Уся решта коду бачить лише
# ObjectStore. Переїзд на іншого вендора = змінити конфіг, а не логіку.
def make_store(v: Vendor, target: str) -> ObjectStore:
    if v is Vendor.A:
        return VendorAStore(target)
    if v is Vendor.B:
        return VendorBStore(target)
    raise StoreError("unknown vendor")

def main() -> None:
    store = make_store(Vendor.A, "orders-bucket")  # ← лише тут
    # Переїзд на B: make_store(Vendor.B, "orders-container").
    # save_receipt / load_last_order не змінюються ВЗАГАЛІ.
    save_receipt(store, some_order)

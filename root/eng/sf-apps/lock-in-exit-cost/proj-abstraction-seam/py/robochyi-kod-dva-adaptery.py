# --- логіка домену: жодної згадки про вендора, лише порт ---
def save_receipt(store: ObjectStore, o: Order) -> None:
    store.put(f"orders/{o.id}/receipt.json", render_receipt(o))

def load_last_order(store: ObjectStore, customer: str) -> Order | None:
    keys = store.list(f"orders/{customer}/")
    if not keys:
        return None
    keys.sort()                          # ключі впорядкуємо самі
    data = store.get(keys[-1])
    return parse_order(data) if data is not None else None

import hashlib

class PercentFlags:
    def __init__(self, percent_by_key: dict[str, int]):
        self._percent_by_key = percent_by_key

    def sampled(self, key: str, id: str) -> bool:
        pct = self._percent_by_key.get(key, 0)     # 0 → вимкнено; 1, 10, 100 — щаблі
        if pct >= 100:
            return True
        if pct <= 0:
            return False
        # Хеш стабільного id → рівномірне число 0..99; те саме id → та сама відповідь
        digest = hashlib.sha256(f"{key}:{id}".encode()).digest()
        bucket = int.from_bytes(digest[:4], "big") % 100
        return bucket < pct

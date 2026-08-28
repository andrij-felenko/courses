from dataclasses import dataclass
import re

# Опис одного маршруту. Це і є той конфіг, який змінюють при переїзді.
# Жодного рішення не зашито в код — усе тут, і все оборотне правкою полів.
@dataclass
class RouteRule:
    pattern: re.Pattern   # які шляхи стосуються цієї можливості
    target: str           # "legacy" | "service" — куди основний потік
    percent: int          # 0..100 — яку частку пускати в нове (canary)
    shadow: bool          # тіньово звіряти нове зі старим, не показуючи клієнту
    service_url: str      # база нового сервісу


def bucket_of(key: str) -> int:
    """Детермінований хеш ключа в діапазон 0..99. Той самий ключ — той самий
    бакет ЗАВЖДИ, тож клієнт не стрибає між старим і новим від запиту до запиту."""
    # FNV-1a — простий, швидкий, добре розсіює; криптостійкість тут не потрібна.
    h = 0x811c9dc5
    for ch in key.encode("utf-8"):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF   # множення за модулем 2³²
    return h % 100


def goes_to_service(rule: RouteRule, user_key: str) -> bool:
    """Чи веде цей запит у НОВИЙ сервіс? = напрям × відсоток × стабільний бакет."""
    if rule.target != "service":
        return False                       # напрям ще на старе
    if rule.percent >= 100:
        return True                        # усі
    if rule.percent <= 0:
        return False                       # ніхто
    return bucket_of(user_key) < rule.percent   # стабільна частка

# Тригер LRM: не «коли встигнемо», а конкретний вимірюваний поріг.
# Поки в межах — тримаємо пошук усередині моноліта (рішення відкрите).
from dataclasses import dataclass

@dataclass
class SearchMetrics:
    search_load_fraction: float  # частка запитів на пошук, 0..1
    search_p99_ms: float         # 99-й перцентиль латентності пошуку

def search_extraction_due(m: SearchMetrics) -> bool:
    # Пороги — заздалегідь домовлений момент, а не відчуття "вже пора".
    LOAD_TRIGGER = 0.30   # пошук з'їдає ≥30% навантаження
    P99_TRIGGER = 200.0   # або деградує до >200 мс на p99
    return (m.search_load_fraction >= LOAD_TRIGGER
            or m.search_p99_ms >= P99_TRIGGER)

# У періодичній перевірці метрик:
if search_extraction_due(metrics):
    raise_decision_alert("Пошук: настав LRM для виділення в окремий сервіс")

// Тригер LRM: не «коли встигнемо», а конкретний вимірюваний поріг.
// Поки в межах — тримаємо пошук усередині моноліта (рішення відкрите).
typedef struct {
    double search_load_fraction;  // частка запитів на пошук, 0..1
    double search_p99_ms;         // 99-й перцентиль латентності пошуку
} SearchMetrics;

int search_extraction_due(const SearchMetrics *m) {
    // Пороги — заздалегідь домовлений момент, а не відчуття "вже пора".
    const double LOAD_TRIGGER = 0.30;   // пошук з'їдає ≥30% навантаження
    const double P99_TRIGGER  = 200.0;  // або деградує до >200 мс на p99
    return (m->search_load_fraction >= LOAD_TRIGGER)
        || (m->search_p99_ms       >= P99_TRIGGER);
}

// У періодичній перевірці метрик:
if (search_extraction_due(&metrics)) {
    raise_decision_alert("Пошук: настав LRM для виділення в окремий сервіс");
}

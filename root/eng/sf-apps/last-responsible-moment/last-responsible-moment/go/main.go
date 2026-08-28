// Тригер LRM: не «коли встигнемо», а конкретний вимірюваний поріг.
// Поки в межах — тримаємо пошук усередині моноліта (рішення відкрите).
type SearchMetrics struct {
	SearchLoadFraction float64 // частка запитів на пошук, 0..1
	SearchP99Ms        float64 // 99-й перцентиль латентності пошуку
}

func searchExtractionDue(m SearchMetrics) bool {
	// Пороги — заздалегідь домовлений момент, а не відчуття "вже пора".
	const (
		loadTrigger = 0.30  // пошук з'їдає ≥30% навантаження
		p99Trigger  = 200.0 // або деградує до >200 мс на p99
	)
	return m.SearchLoadFraction >= loadTrigger ||
		m.SearchP99Ms >= p99Trigger
}

// У періодичній перевірці метрик:
if searchExtractionDue(metrics) {
	raiseDecisionAlert("Пошук: настав LRM для виділення в окремий сервіс")
}

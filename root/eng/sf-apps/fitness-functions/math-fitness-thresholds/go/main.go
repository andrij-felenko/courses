const (
	budget  = 0.001   // 1 − SLO (99.9%)
	periodH = 30 * 24 // 720 годин
)

func burnRate(errRate float64) float64 {
	// у скільки разів швидше за «рівно вичерпати за період»
	return errRate / budget
}

func budgetBurned(errRate, windowH float64) float64 {
	// частка 30-денного бюджету, з'їдена за вікно
	return burnRate(errRate) * windowH / periodH
}

// пейдж лише коли ОБИДВА вікна згодні: і година, і 5 хв горять 14.4×
func page(err1h, err5m float64) bool {
	longFast := burnRate(err1h) >= 14.4  // тривке?
	shortFast := burnRate(err5m) >= 14.4 // ще триває?
	return longFast && shortFast
}

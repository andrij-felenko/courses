// Прогнати варіант у двох крайнощах: оптимістичній (усі p × 0.6)
// і песимістичній (усі p × 1.4, але не вище 1.0). Дає ВИЛКУ експозиції.
func exposureRange(v Variant) (lo, hi float64) {
	for _, r := range v.Risks {
		pLo := r.P * 0.6
		pHi := r.P * 1.4
		if pHi > 1.0 {
			pHi = 1.0 // ймовірність не буває > 1
		}
		lo += pLo * r.Loss
		hi += pHi * r.Loss
	}
	return lo, hi
}

// Чи стійкий вирок? Вирок надійний ЛИШЕ якщо вилки не перекриваються:
// найгірший випадок переможця все одно кращий за найкращий випадок суперника.
func verdictRobust(a, b Variant) {
	aLo, aHi := exposureRange(a)
	bLo, bHi := exposureRange(b)
	fmt.Printf("%s: %.1f .. %.1f\n", a.Name, aLo, aHi)
	fmt.Printf("%s: %.1f .. %.1f\n", b.Name, bLo, bHi)
	switch {
	case aHi < bLo:
		fmt.Printf("Вирок СТІЙКИЙ: %s кращий навіть у найгіршому для себе разі.\n", a.Name)
	case bHi < aLo:
		fmt.Printf("Вирок СТІЙКИЙ: %s кращий навіть у найгіршому для себе разі.\n", b.Name)
	default:
		fmt.Print("Вирок ХИТКИЙ: вилки перекриваються — цифри не вирішують, " +
			"потрібні інші аргументи або точніші оцінки.\n")
	}
}

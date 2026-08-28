type Risk struct {
	Name  string
	P     float64
	Loss  float64
	Group int // 0 = незалежний; однакове ненульове = зчеплені між собою
}

// Експозиція варіанта з урахуванням зчеплення.
// Незалежні ризики додаємо як є. Кожну групу зчеплених згортаємо в ОДИН
// доданок: ймовірність «спрацював хоч один» = 1 − Π(1 − p_i),
// а втрата — найбільша в групі (спільна скеля коштує стільки, скільки
// коштує найгірший її прояв, а не сума проявів того самого лиха).
func totalExposureGrouped(v Variant) float64 {
	sum := 0.0
	// спочатку незалежні
	for _, r := range v.Risks {
		if r.Group == 0 {
			sum += exposure(r)
		}
	}

	// тепер групи: акумулюємо по номеру групи
	pNone := map[int]float64{}
	maxLoss := map[int]float64{}
	for _, r := range v.Risks {
		if r.Group == 0 {
			continue
		}
		if _, ok := pNone[r.Group]; !ok {
			pNone[r.Group] = 1.0
		}
		pNone[r.Group] *= (1.0 - r.P) // ймовірність, що ЖОДЕН не спрацював
		if r.Loss > maxLoss[r.Group] {
			maxLoss[r.Group] = r.Loss // найбільша втрата в групі
		}
	}
	for g, pn := range pNone {
		pAny := 1.0 - pn // об'єднання, не сума
		sum += pAny * maxLoss[g]
	}
	return sum
}

package tia

import "math"

const twoPi = 2.0 * math.Pi

type Tia struct {
	Rf    float64 // резистор перетворення, Ом
	Cin   float64 // повна вхідна ємність (діод + ОП + монтаж), Ф
	Cf    float64 // конденсатор компенсації, Ф
	Fgbw  float64 // добуток підсилення на смугу ОП, Гц
}

// Частоти зламів коефіцієнта зворотного зв'язку
func fzOf(t Tia) float64 { // нуль 1/β від вхідної ємності
	return 1.0 / (twoPi * t.Rf * (t.Cin + t.Cf))
}
func fpOf(t Tia) float64 { // полюс 1/β від Cf = смуга −3 дБ
	return 1.0 / (twoPi * t.Rf * t.Cf)
}

// |A|·β = 1: ОП з одним домінантним полюсом має |A(f)| ≈ Fgbw / f.
// 1/β(f) на полиці прямує до (Cin+Cf)/Cf; точну криву беремо з полюса й нуля.
func crossoverHz(t Tia) float64 {
	fz, fp := fzOf(t), fpOf(t)
	// |A(f)| = Fgbw/f;  |1/β(f)| = sqrt(1+(f/fz)^2) / sqrt(1+(f/fp)^2)
	// шукаємо f, де Fgbw/f = |1/β|, простим діленням навпіл по логарифму
	lo, hi := fp*0.05, t.Fgbw // перетин гарантовано в цьому вікні
	for i := 0; i < 60; i++ {
		f := math.Sqrt(lo * hi) // середина в лог-масштабі
		A := t.Fgbw / f
		ib := math.Sqrt(1.0+(f/fz)*(f/fz)) / math.Sqrt(1.0+(f/fp)*(f/fp))
		if A > ib { // |A| ще вище за 1/β → перетин правіше
			lo = f
		} else {
			hi = f
		}
	}
	return math.Sqrt(lo * hi)
}

// Запас фази (градуси) при поточному Cf
func phaseMarginDeg(t Tia) float64 {
	fz, fp, fc := fzOf(t), fpOf(t), crossoverHz(t)
	deg := 180.0 / math.Pi
	// фаза петлі: −90° (полюс ОП) − atan(fc/fz) (нуль 1/β) + atan(fc/fp) (полюс 1/β)
	phase := -90.0 - math.Atan(fc/fz)*deg + math.Atan(fc/fp)*deg
	return 180.0 + phase // запас до −180°
}

// Cf-орієнтир максимально плоского відгуку (полюс у геом. середині fz та Fgbw)
func cfButterworth(Rf, Cin, Fgbw float64) float64 {
	return math.Sqrt(Cin / (twoPi * Rf * Fgbw))
}

// Приклад: Rf = 1 МОм, Cin = 60 пФ, Fgbw = 10 МГц
func checkExample() {
	t := Tia{Rf: 1.0e6, Cin: 60.0e-12, Fgbw: 10.0e6}
	t.Cf = cfButterworth(t.Rf, t.Cin, t.Fgbw) // ≈ 0.98 пФ
	pm := phaseMarginDeg(t)                    // ≈ 45° — мінімально безпечно
	bw := fpOf(t)                              // смуга −3 дБ ≈ 162 кГц
	if pm < 45.0 {
		// запас замалий: побільшити Cf (нижчий полюс, тихіше) або взяти швидший ОП
	}
	_, _ = pm, bw
}

// Стеля частоти в мегагерцах. Затримки — у наносекундах.
// Синхронний: критичний шлях НЕ залежить від n (перенос паралельний).
func FmaxSyncMHz(tPd, tCarry, tSetup float64) float64 {
	pathNs := tPd + tCarry + tSetup // n тут не бере участі
	return 1000.0 / pathNs          // 1/нс = ГГц → ×1000 = МГц
}

// Ланцюговий: затримки складаються вздовж усіх n розрядів (естафета).
func FmaxRippleMHz(tPd float64, n uint32) float64 {
	pathNs := float64(n) * tPd // ось воно, N біля затримки
	return 1000.0 / pathNs
}

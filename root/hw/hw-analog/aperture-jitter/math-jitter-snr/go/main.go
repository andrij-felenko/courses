package jitter

import "math"

// Максимально допустимий RMS-джиттер такту (с),
// щоб на частоті fHz отримати задану кількість ефективних розрядів.
func MaxJitterForBits(fHz, bits float64) float64 {
	snrDB := 6.02*bits + 1.76             // цільовий SNR
	ratio := math.Pow(10, snrDB/20)       // SNR у разах (амплітудно)
	return 1 / (2 * math.Pi * fHz * ratio)
}

// приклад: MaxJitterForBits(10e6, 14) ≈ 0.79e-12 с (з урахуванням 1.76 дБ)

package jitter

import "math"

// Стеля SNR (дБ) від апертурного джиттера
// fHz   — частота вхідного сигналу, Гц
// tjSec — RMS-джиттер такту, с
func SNRdB(fHz, tjSec float64) float64 {
	x := 2.0 * math.Pi * fHz * tjSec
	return -20.0 * math.Log10(x)
}

// Скільки ефективних розрядів (ENOB) лишає ця стеля
func ENOB(fHz, tjSec float64) float64 {
	snr := SNRdB(fHz, tjSec)
	return (snr - 1.76) / 6.02 // SNR ≈ 6.02·ENOB + 1.76
}

// приклад: SNRdB(10e6, 1e-12) ≈ 84.0;  ENOB(...) ≈ 13.7

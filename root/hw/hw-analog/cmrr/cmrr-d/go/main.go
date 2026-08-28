package main

import "math"

// Похибка на вході (В) від синфазної завади vcm (В)
// за паспортного cmrrDB (дБ).
func cmErrorInput(vcm, cmrrDB float64) float64 {
	ratio := math.Pow(10, cmrrDB/20) // дБ → у разах
	return vcm / ratio               // зведена до входу завада
}

// Приклад: 1 В синфазного, CMRR = 100 дБ
// cmErrorInput(1.0, 100.0) -> 1e-05 В = 10 мкВ

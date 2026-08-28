package main

import (
	"fmt"
	"math"
)

const cSound = 343.0 // швидкість звуку при 20 °C, м/с

// portLengthM — довжина круглого порту (метри) під настройку fb.
// vLitres — об'єм коробки; dM — діаметр порту в метрах.
func portLengthM(fb, vLitres, dM float64) float64 {
	V := vLitres * 1e-3   // літри → м³
	r := dM * 0.5
	A := math.Pi * r * r  // площа перерізу, м²
	w := 2.0 * math.Pi * fb // кутова частота

	lEff := cSound * cSound * A / (w * w * V) // ефективна довжина
	lEnd := 2.0 * 0.85 * r                    // поправка: ~0.85·d, обидва кінці
	lPhys := lEff - lEnd                      // стільки різати трубу
	return lPhys
}

func main() {
	fb, V, d := 35.0, 30.0, 0.05
	L := portLengthM(fb, V, d)
	fmt.Printf("Фізична довжина порту = %.1f см\n", L*100.0)
}

// Параметри реального конденсатора → точки галочки |Z(f)|.
// f0 — дно (резонанс), |Z|min = ESR, плюс DF і Q на заданій частоті.
package main

import (
	"fmt"
	"math"
)

// модуль повного опору в одній точці частоти: |Z| = sqrt(ESR^2 + (wL - 1/wC)^2)
func zMag(f, C, L, esr float64) float64 {
	w := 2.0 * math.Pi * f
	X := w*L - 1.0/(w*C) // чиста реактивність: індуктивна − ємнісна
	return math.Sqrt(esr*esr + X*X)
}

func main() {
	C := 100e-9      // 100 нФ
	L := 2e-9        // 2 нГ паразитної індуктивності
	esr := 0.03      // 0.03 Ом
	fWork := 100e3   // робоча частота 100 кГц

	f0 := 1.0 / (2.0 * math.Pi * math.Sqrt(L*C)) // дно галочки
	Xc := 1.0 / (2.0 * math.Pi * fWork * C)      // ємнісний опір на 100 кГц
	DF := esr / Xc                                // коефіцієнт втрат
	Q := Xc / esr                                 // добротність = 1/DF

	fmt.Printf("f0      = %.2f MHz\n", f0/1e6)
	fmt.Printf("|Z|@f0  = %.3f Ohm  (= ESR)\n", zMag(f0, C, L, esr))
	fmt.Printf("|Z|@100kHz = %.2f Ohm\n", zMag(fWork, C, L, esr))
	fmt.Printf("DF      = %.5f\n", DF)
	fmt.Printf("Q       = %.0f\n", Q)
}

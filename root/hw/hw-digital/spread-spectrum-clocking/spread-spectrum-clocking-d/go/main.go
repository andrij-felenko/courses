package main

import (
	"fmt"
	"math"
)

func main() {
	f0 := 100e6      // такт, Гц
	harmonic := 5    // проблемна гармоніка
	spread := 0.005  // 0.5 %  розмаз униз
	rbw := 120e3     // вікно приймача CISPR, Гц

	fHarm := float64(harmonic) * f0     // 500 МГц — де стоїть спиця
	df := spread * fHarm                // абсолютний обшир розмазу на цій гармоніці
	gainDB := 10.0 * math.Log10(df/rbw) // наближене падіння піку

	fmt.Printf("гармоніка : %.0f МГц\n", fHarm/1e6)
	fmt.Printf("розмаз Δf  : %.2f МГц (%.1f %% від гармоніки)\n", df/1e6, spread*100)
	fmt.Printf("вікно RBW  : %.0f кГц\n", rbw/1e3)
	fmt.Printf("падіння піку ~ %.1f дБ\n", gainDB)

	marginBefore := -6.0 // було: на 6 дБ ВИЩЕ межі
	marginAfter := marginBefore + gainDB
	verdict := "(усе ще завалено)"
	if marginAfter > 0 {
		verdict = "(проходить)"
	}
	fmt.Printf("запас до межі: %.1f дБ → %.1f дБ  %s\n",
		marginBefore, marginAfter, verdict)
}

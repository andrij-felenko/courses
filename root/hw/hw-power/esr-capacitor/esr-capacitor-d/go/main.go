// Скільки тепла народжує пульсівний струм на ESR конденсатора.
// iRms — діюче значення пульсації, А; esr — еквівалентний послідовний опір, Ом.
package main

import "fmt"

func rippleHeat(iRms, esr float64) float64 {
	return iRms * iRms * esr // P = I² · ESR, Вт
}

func main() {
	i := 2.0                                                     // пульсівний струм 2 А (rms)
	fmt.Printf("ESR=0.50: P = %.2f W\n", rippleHeat(i, 0.50)) // звичайний електроліт
	fmt.Printf("ESR=0.02: P = %.2f W\n", rippleHeat(i, 0.02)) // low-ESR
}

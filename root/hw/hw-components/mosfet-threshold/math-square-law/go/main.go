// Квадратичний закон у насиченні: Id = 0.5 * k * (Vgs - Vth)^2
package main

import "fmt"

func idSat(vgs, vth, k float64) float64 {
	vov := vgs - vth        // перевищення порогу
	if vov <= 0 {           // нижче порога — канал закрито
		return 0
	}
	return 0.5 * k * vov * vov // квадрат перевищення
}

func main() {
	vth, k := 1.0, 0.5
	for _, vgs := range []float64{1.5, 2.0, 3.0} {
		vov := vgs - vth
		fmt.Printf("Vgs=%.1f V  Vov=%.1f V  Id=%.3f A\n",
			vgs, vov, idSat(vgs, vth, k))
	}
}

package main

import (
	"fmt"
	"math"
	"gonum.org/v1/gonum/mathext"
)

const EulerMascheroni = 0.57721566490153286060

func ComputeHarmonic(x float64) (float64, error) {
	if x < 0 {
		return 0, fmt.Errorf("invalid argument x = %g", x)
	}
	if x == 0 {
		return 0, nil
	}
	// H[x] = Digamma(x + 1) + EulerMascheroni
	dig := mathext.Digamma(x + 1.0)
	return dig + EulerMascheroni, nil
}

func main() {
	val, err := ComputeHarmonic(10.0)
	if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Printf("H[10] = %.15f\n", val)
	}
}

package main

import "math"

// Підбір емітерного резистора джерела Відлара під заданий малий вихідний струм.
// Усе у вольтах і амперах; повертає опір в омах.
func widlarEmitterResistor(iRef, iOut float64) float64 {
    const V_T = 0.026                              // термічний потенціал при ~27 °C
    return (V_T * math.Log(iRef/iOut)) / iOut      // R_E = V_T·ln(I_REF/I_OUT)/I_OUT
}
// widlarEmitterResistor(1.0e-3, 10.0e-6) -> ~12 кОм

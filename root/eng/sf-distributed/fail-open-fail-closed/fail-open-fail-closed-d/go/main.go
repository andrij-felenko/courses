package main

import "fmt"

type CostEvaluation struct {
	Alpha        float64 // Частка шкідливого трафіку
	CostDowntime float64 // Втрати від блокування легітимного запиту ($)
	CostBreach   float64 // Втрати від пропуску зловмисного запиту ($)
}

func (c CostEvaluation) CriticalAlpha() float64 {
	return c.CostDowntime / (c.CostDowntime + c.CostBreach)
}

func (c CostEvaluation) ShouldFailOpen() bool {
	return c.Alpha < c.CriticalAlpha()
}

func main() {
	blog := CostEvaluation{Alpha: 0.01, CostDowntime: 0.05, CostBreach: 0.10}
	banking := CostEvaluation{Alpha: 0.001, CostDowntime: 2.00, CostBreach: 5000.00}

	fmt.Printf("Блог: поріг alpha = %.5f -> Режим: %s\n", 
		blog.CriticalAlpha(), map[bool]string{true: "FAIL-OPEN", false: "FAIL-CLOSED"}[blog.ShouldFailOpen()])
	fmt.Printf("Банк: поріг alpha = %.5f -> Режим: %s\n", 
		banking.CriticalAlpha(), map[bool]string{true: "FAIL-OPEN", false: "FAIL-CLOSED"}[banking.ShouldFailOpen()])
}

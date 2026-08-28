package main

import "fmt"

// Число пар (комунікаційних шляхів) у групі з n людей: n·(n−1)/2.
// Порядок множення (n−1) перед діленням гарантує, що n·(n−1) — завжди
// парне (два послідовні цілі), тож ділення на 2 точне, без утрати дробу.
func paths(n int64) int64 {
	return n * (n - 1) / 2
}

// Незалежна перевірка через лему про рукостискання:
// у повному графі кожна з n вершин має степінь (n−1);
// сума степенів = подвоєне число ребер, тож ребер = сума/2.
func pathsViaHandshake(n int64) int64 {
	var sumOfDegrees int64 = 0
	for v := int64(0); v < n; v++ {
		sumOfDegrees += (n - 1) // степінь кожної вершини у Kₙ
	}
	return sumOfDegrees / 2 // ребро лічиться з обох кінців
}

func main() {
	// 1) Дві формули мають дати те саме число — це наша страховка.
	for _, n := range []int64{3, 5, 10, 20, 50} {
		a := paths(n)
		b := pathsViaHandshake(n)
		status := "збіг"
		if a != b {
			status = "РОЗБІЖНІСТЬ!"
		}
		fmt.Printf("n=%2d:  формула=%d  лема=%d  %s\n", n, a, b, status)
	}
	fmt.Printf("\n")

	// 2) Моноліт із 12 у купі проти трьох автономних команд по 4.
	mono := paths(12)

	teams := []int64{4, 4, 4}
	var inside int64 = 0
	for _, t := range teams { // густо всередині кожної
		inside += paths(t)
	}
	between := int64(len(teams) - 1) // тонкі контракти між ними

	fmt.Printf("Моноліт (12 разом):        %d шляхів\n", mono)
	fmt.Printf("3 команди — усередині:     %d шляхів\n", inside)
	fmt.Printf("3 команди — між командами: %d контракти\n", between)
	fmt.Printf("Разом при розбитті:        %d проти %d\n",
		inside+between, mono)
}

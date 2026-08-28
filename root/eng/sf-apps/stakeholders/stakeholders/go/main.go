package main

import "fmt"

// Якісний атрибут, про який дбає стейкхолдер.
type Attribute int

const (
	Availability Attribute = iota
	Modifiability
	Performance
	Security
	Cost
)

var attrName = map[Attribute]string{
	Availability:  "доступність",
	Modifiability: "змінюваність",
	Performance:   "швидкодія",
	Security:      "безпека",
	Cost:          "вартість",
}

type Stakeholder struct {
	name    string
	power   int       // 1..5 — наскільки може впливати на рішення
	concern Attribute // головна турбота цієї людини
}

func main() {
	reg := []Stakeholder{
		{"Замовник", 5, Cost},
		{"Оператор", 2, Availability}, // тихий, але з великою ставкою
		{"Супровід", 3, Modifiability},
		{"Аудитор", 4, Security},
		{"Користувач", 3, Performance},
	}

	// Атрибути, які архітектура вже свідомо закрила рішеннями.
	covered := map[Attribute]bool{
		Cost: true, Modifiability: true, Performance: true,
	}

	// Знаходимо турботи без відповіді — саме тут ховаються майбутні провали.
	for _, s := range reg {
		if !covered[s.concern] {
			fmt.Printf("НЕ ЗАКРИТО: %-10s (вплив %d) дбає про %s\n",
				s.name, s.power, attrName[s.concern])
		}
	}
}

type Risk struct {
	Name         string
	P            float64
	Loss         float64
	Group        int
	Catastrophic bool // true = «хвіст»: рідкісна, але руйнівна подія
}

// Поріг, за яким втрата вважається такою, що її не можна усереднювати:
// подія цього масштабу не «дорога», вона ЕКЗИСТЕНЦІЙНА для проєкту.
const RuinThreshold = 100.0 // людино-днів

// Замість того, щоб мовчки додати хвіст до середнього, виносимо його окремо.
func reportWithTail(v Variant) {
	routine := 0.0 // сума експозицій буденних ризиків
	fmt.Printf("=== %s ===\n", v.Name)
	for _, r := range v.Risks {
		tail := r.Catastrophic || r.Loss >= RuinThreshold
		if tail {
			// хвіст НЕ вливаємо в середнє — показуємо як окремий стоп-сигнал
			fmt.Printf("  [ХВІСТ] %-38s p=%.3f, втрата=%.0f  <-- окреме рішення!\n",
				r.Name, r.P, r.Loss)
		} else {
			routine += exposure(r)
		}
	}
	fmt.Printf("  Буденна експозиція (усереднена): %.1f люд.-днів\n", routine)
	fmt.Print("  Хвостові ризики середнім НЕ вимірюються — їх або усувають " +
		"(резервні копії, реплікація), або свідомо приймають ОКРЕМИМ рішенням.\n")
}

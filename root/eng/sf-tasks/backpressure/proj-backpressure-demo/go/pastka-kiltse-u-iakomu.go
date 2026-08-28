forward := make(chan Job, 4) // A → B
back := make(chan Job, 4)    // B → A: те, що треба переробити

// Етап A: бере з поворотної черги, віддає в пряму.
go func() {
	for j := range back {
		forward <- rework(j) // ← застрягне тут, коли forward повний
	}
}()

// Етап B: бере з прямої, частину повертає назад.
go func() {
	for j := range forward {
		if needsRework(j) {
			back <- j // ← застрягне тут, коли back повний
		}
	}
}()

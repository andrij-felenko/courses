// PathLengthDeadband — шлях із порогом мінімального кроку eps.
func PathLengthDeadband(pts []Pt, eps float64) float64 {
	if len(pts) == 0 {
		return 0
	}
	total := 0.0
	anchor := pts[0] // остання збережена точка
	for _, p := range pts[1:] {
		step := math.Hypot(p.X-anchor.X, p.Y-anchor.Y)
		if step >= eps {
			total += step
			anchor = p // якір рухаємо ЛИШЕ на зарахованому кроці
		}
	}
	return total
}

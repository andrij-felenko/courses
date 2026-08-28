package odometry

import "math"

type Pt struct{ X, Y float64 } // метри

// NetDisplacement — вектор rₙ − r₀ та його модуль.
func NetDisplacement(pts []Pt) (Pt, float64) {
	if len(pts) < 2 {
		return Pt{}, 0
	}
	first, last := pts[0], pts[len(pts)-1]
	d := Pt{last.X - first.X, last.Y - first.Y}
	return d, math.Hypot(d.X, d.Y)
}

// PathLength — сума довжин відрізків між сусідніми відліками.
func PathLength(pts []Pt) float64 {
	total := 0.0
	for i := 1; i < len(pts); i++ {
		total += math.Hypot(pts[i].X-pts[i-1].X, pts[i].Y-pts[i-1].Y)
	}
	return total
}

// MovingAverage згладжує відліки вікном ±w по обох осях.
func MovingAverage(pts []Pt, w int) []Pt {
	n := len(pts)
	out := make([]Pt, n)
	for i := range pts {
		lo, hi := i-w, i+w+1
		if lo < 0 {
			lo = 0
		}
		if hi > n {
			hi = n
		}
		var sx, sy float64
		for _, p := range pts[lo:hi] {
			sx += p.X
			sy += p.Y
		}
		cnt := float64(hi - lo)
		out[i] = Pt{sx / cnt, sy / cnt}
	}
	return out
}

// ужиток: PathLength(MovingAverage(pts, 2))

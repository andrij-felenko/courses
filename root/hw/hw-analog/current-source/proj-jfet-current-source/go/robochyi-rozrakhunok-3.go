func BiasCurrent(q Jfet, rs float64) float64 {
	if rs <= 0.0 {
		return q.Idss
	}

	i := q.Idss * 0.5 // старт із середини діапазону
	for n := 0; n < 60; n++ {
		ugs := -i * rs
		if ugs <= q.Vp {
			ugs = q.Vp
		}
		t := 1.0 - ugs/q.Vp
		iNew := q.Idss * t * t
		i = 0.5 * (i + iNew) // демпфування — гасить гойдання
	}
	return i
}

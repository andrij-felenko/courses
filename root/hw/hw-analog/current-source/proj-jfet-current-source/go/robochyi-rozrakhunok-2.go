// BiasCurrent — струм self-bias-джерела при заданому резисторі витоку.
// Простою ітерацією петлі U_GS = −I·R_S → I(U_GS) за квадратичним законом.
// Петля стискальна, тож збігається за кілька кроків.
func BiasCurrent(q Jfet, rs float64) float64 {
	if rs <= 0.0 {
		return q.Idss // закорочений затвор
	}

	i := q.Idss // старт зверху, з I_DSS
	for n := 0; n < 40; n++ {
		ugs := -i * rs // напруга, яку дає резистор
		if ugs <= q.Vp {
			ugs = q.Vp // глибше відсічки не буває
		}
		t := 1.0 - ugs/q.Vp // = (1 − U_GS/U_P)
		i = q.Idss * t * t  // струм за квадратичним законом
	}
	return i
}

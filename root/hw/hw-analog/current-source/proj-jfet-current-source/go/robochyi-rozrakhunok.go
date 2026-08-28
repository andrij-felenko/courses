package current

import "math"

// Jfet — параметри конкретного JFET (виміряні або з даташита).
type Jfet struct {
	Idss float64 // струм насичення витоку, А (U_GS = 0)
	Vp   float64 // напруга відсічки, В — ВІД'ЄМНА (напр. −3.0)
}

// SourceResistor повертає опір резистора витоку для бажаного струму
// self-bias-джерела в омах, або −1, якщо струм недосяжний для цього JFET.
// iTarget — бажаний струм, А (має бути 0 < iTarget ≤ Idss).
func SourceResistor(q Jfet, iTarget float64) float64 {
	// Нижче за I_DSS опустити можна, вище — ні: за U_GS=0 уже тече
	// рівно I_DSS, а додатну U_GS на керівний перехід подавати не можна.
	if iTarget <= 0.0 || iTarget > q.Idss {
		return -1.0
	}

	// Точно I_DSS — це закорочений затвор: R_S = 0.
	if iTarget == q.Idss {
		return 0.0
	}

	// Потрібна напруга затвор-витік за квадратичним законом:
	//   U_GS = U_P · (1 − sqrt(I_target / I_DSS))            (В, від'ємна)
	ugs := q.Vp * (1.0 - math.Sqrt(iTarget/q.Idss))

	// Резистор створює цю напругу падінням від струму:
	//   R_S = −U_GS / I_target                                (Ом)
	return -ugs / iTarget
}

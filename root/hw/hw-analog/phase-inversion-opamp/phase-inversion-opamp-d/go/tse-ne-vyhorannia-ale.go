// Чи безпечний синфазний рівень для ОП на одному живленні 0..5 В?
// Вікно з довідника: [v_cm_min .. v_cm_max]. Сигнал може мати викид.
package sensor

const (
	vCmMin = 0.0  // нижня межа синфазного вікна, В
	vCmMax = 3.5  // верхня межа: V+ − 1.5 В
	margin = 0.20 // запас на дрейф/температуру, В
)

func cmLevelSafe(vSignalPeak float64) bool {
	lo := vCmMin + margin // 0.20 В
	hi := vCmMax - margin // 3.30 В
	return vSignalPeak >= lo && vSignalPeak <= hi
}

// приклад: давач інколи викидає до 3.8 В
//   cmLevelSafe(3.8) → 3.8 > 3.30 → false → переворот можливий!

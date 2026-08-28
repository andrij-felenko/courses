// Спайк: одноразова проба ОДНІЄЇ небезпеки — пропускної здатності.
// Мета не «код у прод», а факт: витримує чи ні. Після заміру — викинути.

type SpikeResult struct {
	TargetRate   uint32  // цільовий потік, повідомлень/с
	ObservedRate uint32  // що показав замір під навантаженням
	ObservedP99  float64 // 99-й перцентиль затримки, мс
}

// Пороги — з бюджету якісних атрибутів, а не «на око».
const (
	RateBudget uint32  = 10000 // менше — гіпотеза провалена
	P99Budget  float64 = 50.0  // більше — теж провал
)

func hypothesisHolds(r SpikeResult) bool {
	return r.ObservedRate >= RateBudget &&
		r.ObservedP99 <= P99Budget
}

// Рішення керує не думка, а результат спайка:
func decideBroker(r SpikeResult) {
	if hypothesisHolds(r) {
		commitBroker() // факт підтвердив — будуємо на ньому
	} else {
		rejectAndTryNext(r) // факт спростував — гілка закрита за день
	}
}

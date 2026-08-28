// Виявити «застряглий» вихід ОП (ознака перевороту/защіпки) і скинути вузол.
// Якщо АЦП довго стоїть у крайньому коді — фізичний сигнал так не поводиться.
package analog

const (
	adcMax     = 4095 // 12-бітний АЦП
	railGuard  = 20   // «крайня» зона: ≤20 або ≥4075
	stuckLimit = 50   // стільки поспіль вибірок у рейці = підозра
)

var stuckCount uint16

func powerCycleAnalog() // зняти/подати живлення аналогового вузла

func opampLatched(adc uint16) bool {
	atRail := adc <= railGuard || adc >= adcMax-railGuard
	if atRail {
		stuckCount++
	} else {
		stuckCount = 0
	}

	if stuckCount >= stuckLimit {
		powerCycleAnalog() // струсонути тракт — вибити защіпку
		stuckCount = 0
		return true        // повідомити верхньому рівню: був збій
	}
	return false
}

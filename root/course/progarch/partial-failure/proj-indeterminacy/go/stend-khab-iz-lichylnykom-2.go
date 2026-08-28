type Fault int

const (
	None    Fault = iota
	DropReq       // (1) запит зник дорогою ТУДИ — хаб команди не бачив
	DropAck       // (2) хаб виконав, підтвердження зникло НАЗАД
	SlowReq       // (3) запит повзе — дійде, та вже після терпіння клієнта
)

// Link — ненадійний канал. faults[i] — який збій станеться на i-ту спробу
// (далі канал чистий). work() виконує ефект на боці хаба й повертає підтвердження.
type Link struct {
	faults  []Fault
	slow    time.Duration
	attempt int
}

func (l *Link) send(work func() string) <-chan string {
	fault := None
	if l.attempt < len(l.faults) {
		fault = l.faults[l.attempt]
	}
	l.attempt++

	reply := make(chan string, 1) // буфер 1: горутина не зависне, коли клієнт уже пішов
	go func() {
		switch fault {
		case DropReq:
			return // хаб work() не викликав — ні ефекту, ні відповіді
		case DropAck:
			work() // ефект СТАВСЯ…
			return // …а підтвердження зникло: клієнту тиша
		case SlowReq:
			time.Sleep(l.slow) // повзе довше за терпіння клієнта
			work()             // зрештою виконає — але клієнт уже не слухає
			reply <- "пізно"   // відповідь прийде в порожнечу
		default:
			reply <- work() // ідеальний прохід: виконали й підтвердили
		}
	}()
	return reply
}

// ── типи повідомлень (як у кістяку, плюс Command) ──
type Msg interface{}
type Tick struct{}
type SetThreshold struct{ C float64 }
type Command struct{ Action string }         // "force_on" | "force_off"
type Query struct{ Reply chan Snapshot }      // зворотний канал — у самому повідомленні
type Snapshot struct {
	On        bool
	Threshold float64
}

// ── ЧИСТЕ ЯДРО: той самий гістерезис із мертвою зоною ±0.5 ──
func decide(reading, threshold float64, on bool) bool {
	switch {
	case reading < threshold-0.5:
		return true // холодно — гріти
	case reading > threshold+0.5:
		return false // тепло — не гріти
	default:
		return on // у мертвій зоні — тримати як було
	}
}

type Device struct {
	id     string
	sensor func() float64 // може панікувати — «отруєний» давач
}

// ── тіло актора: приватний стан = локальні змінні, одне повідомлення за раз ──
func runActor(d Device, box <-chan Msg) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("panic: %v", r) // впіймали паніку ЦІЄЇ горутини
		}
	}()
	on, threshold := false, 20.0     // ніхто інший цього не бачить → замок не потрібен
	for msg := range box {           // ← одне повідомлення за раз
		switch m := msg.(type) {
		case Tick:
			reading := d.sensor()    // отруєний давач панікує тут
			on = decide(reading, threshold, on)
			actuate(d.id, on)
		case SetThreshold:
			threshold = m.C
		case Command:
			on = m.Action == "force_on"
		case Query:
			m.Reply <- Snapshot{On: on, Threshold: threshold} // відповідь — каналом
		}
	}
	return nil // канал закрито — штатний вихід
}

// ── наглядач: перезапуск із чистого стану + межа інтенсивності ВРУЧНУ ──
func supervise(d Device, box chan Msg) {
	fails, since := 0, time.Now()
	for {
		if runActor(d, box) == nil {
			return // штатне завершення
		}
		if time.Since(since) > 5*time.Second { // вікно скинулось
			fails, since = 0, time.Now()
		}
		fails++
		if fails > 3 { // ← інакше отрута дасть ВІЧНИЙ цикл рестарту
			log.Printf("[sup] %s: 3 падіння за 5 с — КАРАНТИН", d.id)
			return
		}
		log.Printf("[sup] %s впав — рестарт #%d з чистого стану", d.id, fails)
	}
}

const MailboxCap = 64

func startDevice(d Device) chan<- Msg {
	box := make(chan Msg, MailboxCap) // ← ОБМЕЖЕНА скринька: у каналу є ємність
	go supervise(d, box)
	return box
}

// політика переповнення: відкинути надлишок (не блокувати джерело)
func offer(box chan<- Msg, m Msg) bool {
	select {
	case box <- m:
		return true
	default:
		return false // повна — свідомо кидаємо
	}
	// backpressure-варіант: просто `box <- m` — заблокує джерело, поки не звільниться
}

// ── доказ ізоляції ──
ok := startDevice(Device{id: "therm_ok", sensor: func() float64 { return 18.5 }})
bad := startDevice(Device{id: "therm_bad", sensor: func() float64 { panic("давач замкнуло") }})

offer(ok, Tick{})  // гріє
offer(bad, Tick{}) // впаде; supervise перезапустить ЛИШЕ цю горутину

reply := make(chan Snapshot)
offer(ok, Query{Reply: reply})
fmt.Println(<-reply) // {true 20} ← паніка сусіда його не зачепила

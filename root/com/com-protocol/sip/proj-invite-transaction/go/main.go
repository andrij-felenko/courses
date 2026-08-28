const (
	T1      = 500 * time.Millisecond
	timerB  = 64 * T1              // 32 с — стеля мовчання
	timerD  = 32 * time.Second     // поглинання дублів
	ringing = 3 * time.Minute      // власна межа для Proceeding (див. пастку 1)
)

type response struct {
	status int
	raw    []byte
}

type txn struct {
	key  string             // branch + метод CSeq
	req  []byte             // серіалізований INVITE
	in   chan response      // сюди демультиплексор кладе відповіді
	tu   TU
	send func([]byte)
	drop func(string)       // зняти запис із покажчика транзакцій
}

func (t *txn) run() {
	defer t.drop(t.key)     // хоч як вийдемо — запис зникне

	t.send(t.req)
	a := time.NewTimer(T1)      // таймер A: повтор
	b := time.NewTimer(timerB)  // таймер B: здача
	defer a.Stop()
	defer b.Stop()
	step := T1

	for { // Calling і Proceeding
		select {
		case <-a.C:
			t.send(t.req)          // повтор байт-у-байт
			step *= 2              // 0.5 → 1 → 2 → 4 … без стелі T2
			a.Reset(step)

		case <-b.C:
			t.tu.Timeout(t.key)    // здача; ACK на це НЕ шлемо
			return

		case r := <-t.in:
			switch {
			case r.status < 200: // 1xx
				if a.Stop() {
					step = 0       // повтори більше не потрібні
				}
				b.Reset(ringing)   // і межа очікування тепер інша
				t.tu.Provisional(t.key, r.raw)

			case r.status < 300: // 2xx
				t.tu.Success(t.key, r.raw) // ACK зробить TU, окремою транзакцією
				return

			default: // 300–699
				t.sendACK(r)               // ACK наш, із тим самим branch
				t.tu.Failure(t.key, r.raw) // доповідаємо РІВНО раз
				t.completed()
				return
			}
		}
	}
}

// Completed: транзакція вже все сказала TU. Її єдина робота — повторювати ACK
// на дублі відповіді, щоб ті не піднялися нагору вдруге.
func (t *txn) completed() {
	d := time.NewTimer(timerD)
	defer d.Stop()
	for {
		select {
		case <-d.C:
			return
		case r := <-t.in:
			if r.status >= 300 {
				t.sendACK(r) // мовчки: TU про дубль знати не треба
			}
		}
	}
}

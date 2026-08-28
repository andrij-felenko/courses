// ── Вимірювання. Кожне число відповідає на своє питання.
type meters struct {
	mu      sync.Mutex
	done    int           // скільки оброблено від старту
	service time.Duration // тривалість САМОЇ обробки останнього елемента
	sojourn time.Duration // повне життя останнього елемента: від born до кінця обробки
	blocked time.Duration // сумарний час, який виробник простояв усередині put
}

func (m *meters) record(service, sojourn time.Duration) {
	m.mu.Lock()
	m.done++
	m.service, m.sojourn = service, sojourn
	m.mu.Unlock()
}

func (m *meters) addBlocked(d time.Duration) {
	m.mu.Lock()
	m.blocked += d
	m.mu.Unlock()
}

func (m *meters) snapshot() (done int, service, sojourn, blocked time.Duration) {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.done, m.service, m.sojourn, m.blocked
}

// Виробник нічого не знає про споживача й не має способу його спитати.
// Єдине, що здатне його вгамувати, — put, який не повертається.
func producer(q queue, m *meters, stop <-chan struct{}) {
	defer q.close() // він єдиний, хто пише в чергу, тож закриває її він
	for id := 0; ; id++ {
		select {
		case <-stop:
			return
		default:
		}
		time.Sleep(produceEvery) // тримає темп: не частіше ніж раз на 2 мс

		j := Job{id: id, born: time.Now(), payload: make([]byte, payloadSize)}

		t0 := time.Now()
		q.put(j) // ← увесь протитиск світу відбувається саме в цьому рядку
		m.addBlocked(time.Since(t0))
	}
}

// Споживач — вузьке місце. Його темп і є темпом усього конвеєра.
func consumer(q queue, m *meters, wg *sync.WaitGroup) {
	defer wg.Done()
	for {
		j, ok := q.take()
		if !ok {
			return
		}
		t0 := time.Now()
		handle(j)
		m.record(time.Since(t0), time.Since(j.born)) // два різні числа — у цьому вся сіль
	}
}

// handle — повільна ланка: запис у базу, виклик по мережі, кодування кадру.
// В обох прогонах вона однакова до останньої наносекунди. Змінюємо тільки чергу.
func handle(j Job) { time.Sleep(handleCost) }

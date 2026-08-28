type Event struct {
	at  uint64 // віртуальний час спрацювання
	seq uint64 // номер народження — детермінований розрив нічиїх
	fn  func()
}

type queue []*Event

func (q queue) Len() int { return len(q) }
func (q queue) Less(i, j int) bool {
	if q[i].at != q[j].at {
		return q[i].at < q[j].at
	}
	return q[i].seq < q[j].seq // однаковий час → вирішує seq, а не випадковість
}
func (q queue) Swap(i, j int) { q[i], q[j] = q[j], q[i] }
func (q *queue) Push(x any)   { *q = append(*q, x.(*Event)) }
func (q *queue) Pop() any {
	old := *q
	e := old[len(old)-1]
	*q = old[:len(old)-1]
	return e
}

type Sim struct {
	now uint64
	seq uint64
	rng *Rand
	q   queue
}

func NewSim(seed uint64) *Sim { return &Sim{rng: NewRand(seed)} }

// after — запланувати fn через delay одиниць віртуального часу.
func (s *Sim) after(delay uint64, fn func()) {
	s.seq++
	heap.Push(&s.q, &Event{at: s.now + delay, seq: s.seq, fn: fn})
}

// run — головний цикл: доки є події, брати найранішу, посувати годинник, виконувати.
func (s *Sim) run() {
	for s.q.Len() > 0 {
		e := heap.Pop(&s.q).(*Event)
		s.now = e.at // годинник СТРИБАЄ прямо на час події — жодного реального очікування
		e.fn()
	}
}

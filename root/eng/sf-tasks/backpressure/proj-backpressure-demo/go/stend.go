// ── Черга зі стелею: канал скінченної місткості.
// Протитиску тут не написано жодного рядка — він вбудований у сам факт стелі.
// Усередині каналу — кільцевий буфер: рухаються два індекси, елементи не їздять.
type boundedQueue struct{ ch chan Job }

func newBounded(capacity int) *boundedQueue { return &boundedQueue{make(chan Job, capacity)} }

// put у ПОВНИЙ канал присипляє горутину, доки споживач не звільнить місце. O(1).
func (q *boundedQueue) put(j Job) { q.ch <- j }

// take з ПОРОЖНЬОГО каналу присипляє споживача, доки не з'явиться робота. O(1).
func (q *boundedQueue) take() (Job, bool) { j, ok := <-q.ch; return j, ok }

func (q *boundedQueue) length() int { return len(q.ch) }
func (q *boundedQueue) close()      { close(q.ch) }

// ── Черга без стелі: у Go її немає, тож доводиться зібрати руками.
// Уже це мало б насторожити — мову спроєктували так, що небезпечне
// не дається задарма. (Канал на мільйон стелю має: це не «без стелі»,
// це «стеля на мільйон», і Go виділяє під неї весь масив одразу.)
type unboundedQueue struct {
	mu       sync.Mutex
	notEmpty *sync.Cond
	items    []Job
	closed   bool
}

func newUnbounded() *unboundedQueue {
	q := &unboundedQueue{}
	q.notEmpty = sync.NewCond(&q.mu)
	return q
}

// put НІКОЛИ не чекає: стану «повна» тут просто не існує.
// Амортизовано O(1) — append час від часу подвоює масив і копіює вміст.
func (q *unboundedQueue) put(j Job) {
	q.mu.Lock()
	q.items = append(q.items, j)
	q.mu.Unlock()
	q.notEmpty.Signal()
}

// take чекає лише на ПОРОЖНІЙ черзі. O(1): голову зсуваємо, хвіст не копіюємо.
func (q *unboundedQueue) take() (Job, bool) {
	q.mu.Lock()
	defer q.mu.Unlock()
	for len(q.items) == 0 && !q.closed {
		q.notEmpty.Wait()
	}
	if len(q.items) == 0 {
		return Job{}, false
	}
	j := q.items[0]
	q.items[0] = Job{}    // обнулити ОБОВ'ЯЗКОВО: інакше масив триматиме вантаж
	q.items = q.items[1:] // мертвого елемента, і збирач сміття його не забере
	return j, true
}

func (q *unboundedQueue) length() int {
	q.mu.Lock()
	defer q.mu.Unlock()
	return len(q.items)
}

func (q *unboundedQueue) close() {
	q.mu.Lock()
	q.closed = true
	q.mu.Unlock()
	q.notEmpty.Broadcast()
}

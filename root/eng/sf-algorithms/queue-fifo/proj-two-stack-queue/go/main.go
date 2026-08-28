type Queue[T any] struct {
    in  []T // сюди пхаємо (Enqueue)
    out []T // звідси знімаємо (Dequeue / Peek)
}

func (q *Queue[T]) Enqueue(x T) {
    q.in = append(q.in, x) // просто на вершину вхідного
}

func (q *Queue[T]) transfer() {
    if len(q.out) == 0 { // переливаємо ЛИШЕ коли вихідний порожній
        for len(q.in) > 0 {
            top := q.in[len(q.in)-1]
            q.in = q.in[:len(q.in)-1]
            q.out = append(q.out, top) // друге перевертання
        }
    }
}

// Dequeue за звичаєм Go повертає (значення, ok): ok=false на порожній черзі.
func (q *Queue[T]) Dequeue() (T, bool) {
    q.transfer()
    var zero T
    if len(q.out) == 0 {
        return zero, false
    }
    top := q.out[len(q.out)-1]
    q.out = q.out[:len(q.out)-1]
    return top, true
}

func (q *Queue[T]) Peek() (T, bool) {
    q.transfer() // Peek теж змушує переливання
    var zero T
    if len(q.out) == 0 {
        return zero, false
    }
    return q.out[len(q.out)-1], true
}

func (q *Queue[T]) Len() int { return len(q.in) + len(q.out) }

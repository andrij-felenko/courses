const (
	rbSize = 256 // степінь двійки → швидка маска
	rbMask = rbSize - 1
)

type Ring struct {
	buf   [rbSize]byte
	head  uint16 // writer index
	tail  uint16 // reader index
	count uint16 // зайнято байтів
}

// writer: true = записано, false = повно (політика «відкинути новий»)
func (r *Ring) Push(b byte) bool {
	if r.count == rbSize { // повно
		return false
	}
	r.buf[r.head] = b            // 1) дані
	r.head = (r.head + 1) & rbMask // 2) посунути голову
	r.count++
	return true
}

// reader: повертає (байт, true) або (0, false), якщо порожньо
func (r *Ring) Pop() (byte, bool) {
	if r.count == 0 { // порожньо
		return 0, false
	}
	b := r.buf[r.tail]
	r.tail = (r.tail + 1) & rbMask
	r.count--
	return b, true
}

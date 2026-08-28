// забрати до n байтів суцільним блоком; повертає скільки реально віддав
func (r *Ring) PopBlock(dst []byte, n int) int {
	if n > int(r.count) { // не більше, ніж є
		n = int(r.count)
	}
	first := rbSize - int(r.tail) // до фізичного краю масиву
	if first > n {
		first = n
	}
	copy(dst[:first], r.buf[r.tail:])       // частина 1: tail..край
	copy(dst[first:n], r.buf[0:n-first])    // частина 2: з початку
	r.tail = (r.tail + uint16(n)) & rbMask
	r.count -= uint16(n)
	return n
}

func VarintEncodeU64(value uint64, buf []byte) int {
	i := 0
	for value >= 0x80 {
		if i >= len(buf) {
			return 0
		}
		buf[i] = byte(value) | 0x80
		i++
		value >>= 7
	}
	if i >= len(buf) {
		return 0
	}
	buf[i] = byte(value)
	i++
	return i
}

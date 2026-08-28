func VarintDecodeU64(buf []byte) (value uint64, n int, ok bool) {
	var result uint64
	shift := 0
	for i := 0; i < len(buf); i++ {
		b := buf[i]
		result |= uint64(b&0x7F) << shift
		if b&0x80 == 0 {
			return result, i + 1, true
		}
		shift += 7
		if shift >= 64 {
			return 0, 0, false
		}
	}
	return 0, 0, false
}

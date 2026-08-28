// Повертає (значення, число зчитаних байтів); ok=false при помилці.
func VarintDecodeU32(buf []byte) (value uint32, n int, ok bool) {
	var result uint32
	shift := 0
	for i := 0; i < len(buf); i++ {
		b := buf[i]
		// Наростити результат: молодші 7 бітів цього байта на позицію shift.
		result |= uint32(b&0x7F) << shift
		if b&0x80 == 0 { // старший біт 0 → це останній байт числа
			return result, i + 1, true // успіх
		}
		shift += 7
		if shift >= 32 { // задовгий varint для 32 бітів → потік зіпсовано
			return 0, 0, false
		}
	}
	return 0, 0, false // прапорець ще «далі є», а буфер скінчився → обірвано
}

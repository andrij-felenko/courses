// Мінімальний CRC-16/CCITT (поліном 0x1021) — для прикладу побайтово.
// У прошивці частіше беруть табличний варіант заради швидкості.
func crc16CCITT(p []byte) uint16 {
    crc := uint16(0xFFFF)
    for _, b := range p {
        crc ^= uint16(b) << 8
        for k := 0; k < 8; k++ {
            if crc&0x8000 != 0 {
                crc = (crc << 1) ^ 0x1021
            } else {
                crc <<= 1
            }
        }
    }
    return crc
}

// сюди приймач кладе те, що робити з валідним кадром
func handleFrame(data []byte) { /* ... */ }

// метод FrameRx з попередньої вкладки
func (rx *FrameRx) complete() {
    if len(rx.buf) < 3 { // кадр коротший за 1 байт даних + 2 CRC — брак
        return
    }

    body := len(rx.buf) - 2 // тіло без двох байтів CRC
    got := uint16(rx.buf[body])<<8 | uint16(rx.buf[body+1]) // CRC із кадру (big-endian)
    calc := crc16CCITT(rx.buf[:body])                       // рахуємо самі

    if got == calc { // сума зійшлася — кадр цілий
        handleFrame(rx.buf[:body]) // віддаємо тіло логіці
    }
    // не зійшлася — тихо відкидаємо: приймач уже в WAIT, чекає наступного FLAG
}

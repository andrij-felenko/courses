// Мінімальний CRC-16/CCITT (поліном 0x1021) — для прикладу побайтово.
// У прошивці частіше беруть табличний варіант заради швидкості.
function crc16Ccitt(data) {
  let crc = 0xFFFF;
  for (const byte of data) {
    crc ^= byte << 8;
    for (let k = 0; k < 8; k++) {
      crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
      crc &= 0xFFFF;                  // тримаємо 16 біт
    }
  }
  return crc;
}

// сюди приймач кладе те, що робити з валідним кадром
function handleFrame(data) { /* ... */ }

// метод класу FrameRx з попередньої вкладки
_complete() {
  if (this.buf.length < 3)             // кадр коротший за 1 байт даних + 2 CRC — брак
    return;

  const body = this.buf.length - 2;    // тіло без двох байтів CRC
  const got  = (this.buf[body] << 8) | this.buf[body + 1];  // CRC із кадру (big-endian)
  const calc = crc16Ccitt(this.buf.slice(0, body));         // рахуємо самі

  if (got === calc)                    // сума зійшлася — кадр цілий
    handleFrame(this.buf.slice(0, body));  // віддаємо тіло логіці
  // не зійшлася — тихо відкидаємо: приймач уже в WAIT, чекає наступного FLAG
}

// Записати ОДИН біт у давач.
void ow_write_bit(uint8_t bit) {
  if (bit) {
    ow_low();
    delayMicroseconds(6);             // «1»: коротко притиснути (<15 мкс)…
    ow_release();
    delayMicroseconds(64);            // …і відпустити на решту слота (усього ~70 мкс)
  } else {
    ow_low();
    delayMicroseconds(60);            // «0»: тримати притиснутою майже весь слот
    ow_release();
    delayMicroseconds(10);            // коротка пауза між слотами
  }
}

// Прочитати ОДИН біт із давача.
uint8_t ow_read_bit() {
  ow_low();
  delayMicroseconds(3);               // самі смикнули лінію (≥1 мкс) — старт слота
  ow_release();
  delayMicroseconds(10);              // дали лінії/давачу усталитись у вікні <15 мкс
  uint8_t bit = ow_read();            // САМЕ ТУТ читаємо: 0 = давач тримає, 1 = відпустив
  delayMicroseconds(50);             // добути слот до ~60 мкс
  return bit;
}

// Повертає true, якщо на шині відгукнувся хоча б один давач.
bool ow_reset() {
  ow_low();
  delayMicroseconds(480);             // тримаємо низько ≥480 мкс — це «скидання»
  ow_release();
  delayMicroseconds(70);              // чекаємо, поки давач видасть presence
  uint8_t present = (ow_read() == 0); // давач притиснув лінію → present == true
  delayMicroseconds(410);             // добути слот скидання до кінця (усього ~960 мкс)
  return present;
}

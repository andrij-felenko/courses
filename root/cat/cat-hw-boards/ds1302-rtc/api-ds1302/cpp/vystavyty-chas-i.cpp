struct Clock {
  uint8_t sec, min, hour;      // 0..59, 0..59, 0..23
  uint8_t date, month;         // 1..31, 1..12
  uint8_t dow;                 // день тижня 1..7 (виставляєте самі!)
  uint8_t year;                // 00..99 (додаєте 2000 у своєму коді)
};

void ds_set_time(const Clock& c) {
  ds_write_protect_off();                       // 1) WP off — інакше все марно

  // 2) Секунди пишемо з ГАРАНТОВАНО скинутим CH (біт7=0), щоб пустити годинник.
  ds_write(REG_SECONDS, dec_to_bcd(c.sec) & 0x7F);
  ds_write(REG_MINUTES, dec_to_bcd(c.min));
  ds_write(REG_HOURS,   dec_to_bcd(c.hour));     // біт7=0 → 24-годинний режим
  ds_write(REG_DATE,    dec_to_bcd(c.date));
  ds_write(REG_MONTH,   dec_to_bcd(c.month));
  ds_write(REG_DOW,     dec_to_bcd(c.dow));
  ds_write(REG_YEAR,    dec_to_bcd(c.year));

  ds_write(REG_WP, 0x80);                        // 3) знову захистити — від збоїв на шині
}

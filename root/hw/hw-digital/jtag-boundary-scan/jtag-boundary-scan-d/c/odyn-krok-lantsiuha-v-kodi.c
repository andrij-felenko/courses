// Порт TAP «ногами» мікроконтролера (bit-banging).
// Такт низький у спокої; крокуємо один такт зсуву.
static uint8_t tap_clock(uint8_t tms, uint8_t tdi) {
    gpio_write(PIN_TMS, tms);      // 1) готуємо керування й дані
    gpio_write(PIN_TDI, tdi);      //    ДО фронту такту
    gpio_write(PIN_TCK, 1);        // 2) висхідний фронт TCK:
    uint8_t tdo = gpio_read(PIN_TDO); //   ведений засуває біт — ловимо TDO
    gpio_write(PIN_TCK, 0);        // 3) спадний фронт — крок завершено
    return tdo;                    //    повертаємо висунутий біт
}

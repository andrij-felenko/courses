// повертає 1, якщо на шині озвався хоч один пристрій, інакше 0
uint8_t ow_reset(void) {
    uint8_t sreg = SREG;
    ow_release();             // хай лінія спокійно висока
    cli();
    ow_drive_low();
    _delay_us(OW_H);          // 480 мкс низько — «усім скинутись»
    ow_release();
    _delay_us(OW_I);          // 70 мкс — і дивимось на імпульс присутності
    uint8_t present = (ow_sample() == 0);  // 0 на лінії = хтось притиснув = є пристрій
    SREG = sreg;
    _delay_us(OW_J);          // добиваємо вікно скидання
    return present;
}

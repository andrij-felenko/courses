uint8_t ow_read_bit(void) {
    uint8_t sreg = SREG;
    cli();
    ow_drive_low();
    _delay_us(OW_A);          // стартовий спад — 6 мкс
    ow_release();             // відпускаємо: далі говорить ведений
    _delay_us(OW_E);          // чекаємо до вікна вибірки (разом 15 мкс від спаду)
    uint8_t bit = ow_sample();// знімаємо рівень: висока = «1», низька = «0»
    SREG = sreg;
    _delay_us(OW_F);          // добиваємо слот
    return bit;
}

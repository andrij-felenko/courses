void ow_write_bit(uint8_t bit) {
    uint8_t sreg = SREG;      // 1) запам'ятати стан переривань
    cli();                    // 2) критична ділянка — нас не можна спиняти
    if (bit) {                //    запис «1»: короткий провал
        ow_drive_low();
        _delay_us(OW_A);      //    6 мкс низько
        ow_release();
        SREG = sreg;          // 3) відновити переривання
        _delay_us(OW_B);      //    відновлення — тут переривання вже не завадять
    } else {                  //    запис «0»: тримаємо майже весь слот
        ow_drive_low();
        _delay_us(OW_C);      //    60 мкс низько
        ow_release();
        SREG = sreg;
        _delay_us(OW_D);
    }
}

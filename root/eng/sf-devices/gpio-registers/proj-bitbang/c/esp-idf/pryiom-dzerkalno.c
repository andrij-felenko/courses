uint8_t recv_byte(void) {
    uint8_t b = 0;
    for (int i = 7; i >= 0; i--) {
        GPIO.out_w1ts = M_CLK;                 // підняли такт
        uint32_t bit = (GPIO.in >> PIN_DATA) & 1u;  // читаємо рівень DATA
        b |= (uint8_t)(bit << i);              // вкладаємо біт на своє місце
        GPIO.out_w1tc = M_CLK;                 // опустили такт
    }
    return b;
}

const uint32_t M_DATA = (1u << PIN_DATA);
const uint32_t M_CLK  = (1u << PIN_CLK);

void send_byte_fast(uint8_t b) {        // старший біт першим
    for (int i = 7; i >= 0; i--) {
        if ((b >> i) & 1) GPIO.out_w1ts = M_DATA;   // біт = 1 → set
        else              GPIO.out_w1tc = M_DATA;   // біт = 0 → clear
        GPIO.out_w1ts = M_CLK;          // фронт такту вгору
        GPIO.out_w1tc = M_CLK;          // і вниз
    }
}

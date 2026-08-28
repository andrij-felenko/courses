volatile uint8_t count_lo;
volatile uint8_t count_hi;
volatile uint8_t overflow_flag;

void tick(void) {
    count_lo++;
    if (count_lo == 0) {          // молодший байт перекотився
        count_hi++;
        if (count_hi == 0)        // і старший теж
            overflow_flag = 1;
    }
}

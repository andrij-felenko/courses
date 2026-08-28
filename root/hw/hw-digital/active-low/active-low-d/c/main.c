#define CS_PORT   GPIOB
#define CS_PIN    12          // CS̅ — active-low

// вибрати чип: активний рівень = НУЛЬ
static inline void chip_select(void)   { CS_PORT->BSRR = (1u << (CS_PIN + 16)); } // скинути в 0
// відпустити чип: пасивний рівень = ОДИНИЦЯ
static inline void chip_release(void)  { CS_PORT->BSRR = (1u <<  CS_PIN);       } // поставити 1

void read_sensor(void) {
    chip_select();            // 0 → чип слухає нас
    spi_transfer(0x80);       // ... обмін ...
    chip_release();           // 1 → чип відпущено
}

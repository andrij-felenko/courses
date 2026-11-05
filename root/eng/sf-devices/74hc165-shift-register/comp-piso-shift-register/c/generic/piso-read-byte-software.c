#include <stdint.h>
#include <stdbool.h>

extern void set_pl_pin(bool state);
extern void set_clk_pin(bool state);
extern bool get_q_pin(void);
extern void delay_us(uint32_t us);

uint8_t piso_read_byte_software(void) {
    uint8_t data = 0;

    set_pl_pin(false);
    delay_us(1);
    set_pl_pin(true);
    delay_us(1);

    for (int i = 0; i < 8; i++) {
        if (get_q_pin()) {
            data |= (1 << (7 - i));
        }
        
        set_clk_pin(true);
        delay_us(1);
        set_clk_pin(false);
        delay_us(1);
    }

    return data;
}

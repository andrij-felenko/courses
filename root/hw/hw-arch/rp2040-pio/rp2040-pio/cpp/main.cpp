#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h"          // згенеровано pioasm із програми вище

#define WS2812_PIN 16
#define SM         0

void ws2812_init(void) {
    uint off = pio_add_program(pio0, &ws2812_program);          // залити програму
    pio_sm_config c = ws2812_program_get_default_config(off);
    sm_config_set_sideset_pins(&c, WS2812_PIN);                 // ніжка DATA
    float div = (float)clock_get_hz(clk_sys) / (800000.f * 25.f);
    sm_config_set_clkdiv(&c, div);                              // автомат на 20 МГц
    sm_config_set_out_shift(&c, false, true, 24);              // autopull 24 біти (GRB)
    pio_gpio_init(pio0, WS2812_PIN);
    pio_sm_set_consecutive_pindirs(pio0, SM, WS2812_PIN, 1, true);
    pio_sm_init(pio0, SM, off, &c);
    pio_sm_set_enabled(pio0, SM, true);                         // пуск
}

void ws2812_send(const uint32_t *pixels, uint n) {
    for (uint i = 0; i < n; i++)
        pio_sm_put_blocking(pio0, SM, pixels[i] << 8u);        // ядро лише годує FIFO
}

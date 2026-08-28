#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h"    // згенеровано pioasm

#define WS2812_PIN 16
#define PIO_INST   pio0
#define SM         0

void ws2812_init(void) {
    uint offset = pio_add_program(PIO_INST, &ws2812_program);   // 1. залити програму
    pio_sm_config cfg = ws2812_program_get_default_config(offset);

    sm_config_set_sideset_pins(&cfg, WS2812_PIN);               // 2. ніжка DATA
    float div = (float)clock_get_hz(clk_sys) / (800000.f * 25.f);
    sm_config_set_clkdiv(&cfg, div);                            // 3. 20 МГц автомата
    sm_config_set_out_shift(&cfg, false, true, 24);             // 4. autopull 24 біти (GRB)

    pio_gpio_init(PIO_INST, WS2812_PIN);                        // 5. GPIO → PIO
    pio_sm_set_consecutive_pindirs(PIO_INST, SM, WS2812_PIN, 1, true);

    pio_sm_init(PIO_INST, SM, offset, &cfg);
    pio_sm_set_enabled(PIO_INST, SM, true);                     // 6. пуск
}

void ws2812_send_grb(uint32_t *pixels, uint n) {
    // Ядро лише висипає пікселі у FIFO — далі автомат жене протокол сам
    for (uint i = 0; i < n; i++)
        pio_sm_put_blocking(PIO_INST, SM, pixels[i] << 8u);
}

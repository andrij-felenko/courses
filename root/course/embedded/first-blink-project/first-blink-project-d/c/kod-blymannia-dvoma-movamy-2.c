#include <stdint.h>

// адреси регістрів GPIO у класичного ESP32 (з даташита)
#define GPIO_ENABLE_W1TS (*(volatile uint32_t *)0x3FF44024)  // увімкнути вихід
#define GPIO_OUT_W1TS    (*(volatile uint32_t *)0x3FF44008)  // поставити біт у 1
#define GPIO_OUT_W1TC    (*(volatile uint32_t *)0x3FF4400C)  // скинути біт у 0

#define LED_BIT (1u << 2)                 // GPIO2 — це біт 2

void app_main(void) {
    GPIO_ENABLE_W1TS = LED_BIT;           // ніжка 2 — на вихід (один раз)
    while (1) {
        GPIO_OUT_W1TS = LED_BIT;          // увімкнути: біт 2 = 1
        for (volatile int i = 0; i < 4000000; i++) { }   // груба пауза
        GPIO_OUT_W1TC = LED_BIT;          // вимкнути: біт 2 = 0
        for (volatile int i = 0; i < 4000000; i++) { }   // груба пауза
    }
}

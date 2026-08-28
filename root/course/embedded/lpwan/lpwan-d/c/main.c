#include <stdint.h>
#include <stdbool.h>

#define DUTY_PERMILLE   10        // дозволено 1% = 10 проміле
#define WINDOW_MS       3600000UL // вікно усереднення: 1 година

static uint32_t air_used_ms = 0;  // скільки мс ефіру вже витрачено у вікні
static uint32_t window_start_ms;

// Чи можна зараз зайняти ефір на air_ms мілісекунд?
bool duty_can_transmit(uint32_t now_ms, uint32_t air_ms) {
    // нове вікно — обнуляємо лічильник
    if (now_ms - window_start_ms >= WINDOW_MS) {
        window_start_ms = now_ms;
        air_used_ms = 0;
    }
    uint32_t budget_ms = (uint32_t)((uint64_t)WINDOW_MS * DUTY_PERMILLE / 1000);
    return (air_used_ms + air_ms) <= budget_ms;   // влізе в 1%?
}

// Викликати ОДРАЗУ після успішної передачі, передавши її time-on-air.
void duty_account(uint32_t air_ms) {
    air_used_ms += air_ms;
}

#include <stdint.h>
#include <stdbool.h>

// повертає true рівно раз на кожні period_ms, не блокуючи цикл
static bool every(uint32_t *last, uint32_t period_ms) {
    uint32_t now = millis();
    if (now - *last >= period_ms) {   // різниця переживає перекіт лічильника
        *last += period_ms;           // += period, а не = now — без дрейфу фази
        return true;
    }
    return false;
}

void loop(void) {
    static uint32_t t_blink = 0;
    static uint32_t t_sensor = 0;

    if (every(&t_blink, 500u))   toggle_led();        // блимати двічі на секунду
    if (every(&t_sensor, 100u))  read_sensor();       // опитувати давач 10 Гц

    // ... тут крутиться решта роботи, ніщо не заблоковане ...
}

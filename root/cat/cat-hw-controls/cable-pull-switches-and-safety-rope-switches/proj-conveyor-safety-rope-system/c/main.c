#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "safety_rope_switch.h"

// Симуляція зчитування фізичних GPIO-пінів мікроконтролера
static bool mcu_read_gpio_nc1(void) {
    static int cycle = 0;
    cycle++;
    // Здебільшого контакт замкнений (true), на 10–15 циклах розімкнений (false)
    if (cycle >= 10 && cycle <= 15) return false;
    return true;
}

static bool mcu_read_gpio_nc2(void) {
    static int cycle = 0;
    cycle++;
    if (cycle >= 10 && cycle <= 15) return false;
    return true;
}

int main(void) {
    printf("--- Ініціалізація модуля тросового вимикача аварійного зупинення (IEC 60947-5-5) ---
");

    safety_rope_switch_t rope_switch;
    // Максимальний розсинхрон 40 мс, дебаунс 5 мс
    safety_rope_switch_init(&rope_switch, 40, 5);

    const uint16_t SYSTEM_TICK_MS = 10;
    printf("Початковий стан виходу безпеки: %s
", safety_rope_switch_is_safe(&rope_switch) ? "ДОЗВОЛЕНО" : "ЗАБЛОКОВАНО");

    // Симуляція циклу обробки мікроконтролера протягом 200 мс
    for (int step = 0; step < 20; step++) {
        bool pin_nc1 = mcu_read_gpio_nc1();
        bool pin_nc2 = mcu_read_gpio_nc2();

        safety_rope_switch_update(&rope_switch, pin_nc1, pin_nc2, SYSTEM_TICK_MS);

        printf("Крок %2d (%3d мс) | NC1: %d, NC2: %d | FSM: %d | Вихід: %s
",
               step, step * SYSTEM_TICK_MS,
               pin_nc1, pin_nc2,
               rope_switch.state,
               safety_rope_switch_is_safe(&rope_switch) ? "ОК" : "АВАРІЯ");
    }

    // Симуляція підтвердженого ручного скидання після повернення троса в робоче вікно
    if (safety_rope_switch_reset(&rope_switch)) {
        printf("Ручне скидання успішне. Контур відновлено: %s
",
               safety_rope_switch_is_safe(&rope_switch) ? "ДОЗВОЛЕНО" : "ЗАБЛОКОВАНО");
    } else {
        printf("Ручне скидання відхилено: контакти не в нормі!
");
    }

    return 0;
}

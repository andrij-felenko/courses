// Перевірка гекс-інвертора 74×04 з боку мікроконтролера.
// PIN_A керує входом 1A чипа, PIN_Y читає його вихід 1Y.
// Живлення чипа й МК — від однієї напруги (напр. обидва 3.3 В),
// інакше рівні можуть не збігтися (див. вибір сімейства HC/HCT/LVC).

#include <stdbool.h>

static bool inverter_ok(void) {
    bool all_good = true;

    gpio_write(PIN_A, 0);          // на вхід чипа — «0»
    delay_us(1);                   // дати виходу усталитися
    if (gpio_read(PIN_Y) != 1)     // очікуємо «1» на виході
        all_good = false;

    gpio_write(PIN_A, 1);          // на вхід чипа — «1»
    delay_us(1);
    if (gpio_read(PIN_Y) != 0)     // очікуємо «0» на виході
        all_good = false;

    return all_good;               // true → інвертор працює як слід
}

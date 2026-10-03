// Приклад прямого атомарного керування MMIO-регістрами GPIO у C (ESP8266 SDK)
#include "c_types.h"
#include "eagle_soc.h"

void fast_gpio_toggle_demo(void) {
    // 1. Атомарне налаштування виводу GPIO4 на вихід через регістр GPIO_ENABLE_W1TS
    WRITE_PERI_REG(PERIPHS_GPIO_BASEADDR + 0x10, (1 << 4));

    // 2. Атомарне встановлення високого рівня (HIGH) на GPIO4 через GPIO_OUT_W1TS
    WRITE_PERI_REG(PERIPHS_GPIO_BASEADDR + 0x04, (1 << 4));

    // 3. Атомарне скидання у низький рівень (LOW) на GPIO4 через GPIO_OUT_W1TC
    WRITE_PERI_REG(PERIPHS_GPIO_BASEADDR + 0x08, (1 << 4));

    // 4. Зчитування прямого стану вхідних ліній з регістру GPIO_IN
    uint32_t inputs = READ_PERI_REG(PERIPHS_GPIO_BASEADDR + 0x18);
    (void)inputs;
}

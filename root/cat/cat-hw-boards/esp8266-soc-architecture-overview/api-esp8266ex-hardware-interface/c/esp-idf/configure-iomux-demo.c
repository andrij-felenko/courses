// Приклад налаштування мультиплексора IOMUX та підтяжки у C (ESP8266 SDK)
#include "c_types.h"
#include "eagle_soc.h"
#include "gpio.h"

void configure_iomux_demo(void) {
    // 1. Призначення виводу GPIO5 функцією звичайного цифрового вводу-виводу (FUNC_GPIO5)
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_GPIO5_U, FUNC_GPIO5);

    // 2. Увімкнення внутрішнього підтягувального резистора Pull-Up на GPIO5
    PIN_PULLUP_EN(PERIPHS_IO_MUX_GPIO5_U);

    // 3. Переналаштування виводів UART0 RX/TX у режим цифрових GPIO (GPIO3 та GPIO1)
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_U0RXD_U, FUNC_GPIO3);
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_U0TXD_U, FUNC_GPIO1);

    // 4. Вимкнення підтяжки на GPIO3
    PIN_PULLUP_DIS(PERIPHS_IO_MUX_U0RXD_U);
}

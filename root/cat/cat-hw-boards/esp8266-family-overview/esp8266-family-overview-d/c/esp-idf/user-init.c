// Низькорівнева конфігурація периферійних виводів у Non-OS SDK
#include "ets_sys.h"
#include "osapi.h"
#include "user_config.h"
#include "gpio.h"

void ICACHE_FLASH_ATTR user_init(void) {
    // Ініціалізація підсистеми GPIO
    gpio_init();
    
    // Перемикання функції виводу GPIO4 у режим звичайного цифрового виводу
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_GPIO4_U, FUNC_GPIO4);
    // Встановлення напрямку виводу GPIO4 як вихід
    gpio_output_set(BIT4, 0, BIT4, 0);
    
    // Налаштування GPIO0 як вхід з увімкненням внутрішньої підтяжки
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_GPIO0_U, FUNC_GPIO0);
    PIN_PULLUP_EN(PERIPHS_IO_MUX_GPIO0_U);
}

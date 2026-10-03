#include "esp8266/gpio_struct.h"
#include "esp8266/pin_mux_register.h"
#include "driver/gpio.h"
#include "user_interface.h"

#define BLINK_GPIO 2

void setup_hardware_peripherals(void) {
    // Налаштування функціонального режиму IOMUX для GPIO2
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_GPIO2_U, FUNC_GPIO2);
    
    // Атомарне ввімкнення режиму виходу через MMIO-регістр W1TS
    GPIO_REG_WRITE(GPIO_ENABLE_W1TS_ADDRESS, (1 << BLINK_GPIO));
}

void atomic_toggle_pin(bool state) {
    if (state) {
        // Атомарне встановлення високого рівня (3.3 В) без читання-модифікації
        GPIO_REG_WRITE(GPIO_OUT_W1TS_ADDRESS, (1 << BLINK_GPIO));
    } else {
        // Атомарне скидання логічного рівня в 0 В
        GPIO_REG_WRITE(GPIO_OUT_W1TC_ADDRESS, (1 << BLINK_GPIO));
    }
}

void execute_software_crypto_chunked(const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; i += 64) {
        // Виконання порції програмного шифрування AES/RSA
        // ... обчислення блоку ...
        
        // Скинути сторожовий таймер WDT для запобігання перезавантаженню
        system_soft_wdt_feed();
    }
}

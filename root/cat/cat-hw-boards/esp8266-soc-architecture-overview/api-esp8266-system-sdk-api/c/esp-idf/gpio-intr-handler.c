// Приклад розділення коду між IRAM та Flash у C (Non-OS SDK)
#include "c_types.h"
#include "osapi.h"
#include "user_interface.h"

// 1. Обробник переривання (ISR): БЕЗ макроса ICACHE_FLASH_ATTR!
// Код розміщується в IRAM для швидкого та безпечного виконання.
void gpio_intr_handler(void *arg) {
    uint32 gpio_status = GPIO_REG_READ(GPIO_STATUS_ADDRESS);
    // Очищення прапорця переривання
    GPIO_REG_WRITE(GPIO_STATUS_W1TC_ADDRESS, gpio_status);
}

// 2. Звичайна фонова функція: З макросом ICACHE_FLASH_ATTR!
// Код зберігається у SPI Flash та економить IRAM.
void ICACHE_FLASH_ATTR format_http_response(char *buf, uint16_t max_len) {
    os_sprintf(buf, "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello ESP8266!");
}

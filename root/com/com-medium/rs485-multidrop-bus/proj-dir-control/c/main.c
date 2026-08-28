// ============================================================================
// Мова C: Низькорівневий драйвер RS-485 з перериванням Transmission Complete
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Абстракція низькорівневого HAL мікроконтролера
extern void gpio_set_de_high(void);
extern void gpio_set_de_low(void);
extern void uart_hardware_send_byte(uint8_t byte);
extern bool uart_is_tx_complete(void);

typedef struct {
    const uint8_t *tx_buffer;
    size_t         tx_size;
    volatile size_t tx_index;
    volatile bool   is_busy;
} rs485_driver_t;

static rs485_driver_t g_rs485 = {0};

// Запуск асинхронної відправки блоку даних по RS-485
bool rs485_send_async(rs485_driver_t *drv, const uint8_t *data, size_t len) {
    if (drv->is_busy || len == 0 || data == NULL) {
        return false; // Передача вже триває або невірні параметри
    }

    drv->tx_buffer = data;
    drv->tx_size   = len;
    drv->tx_index  = 0;
    drv->is_busy   = true;

    // Крок 1: Захоплюємо шину — піднімаємо пін DE у HIGH
    gpio_set_de_high();

    // Крок 2: Відправляємо перший байт у зсувний регістр UART
    uart_hardware_send_byte(drv->tx_buffer[drv->tx_index++]);

    // Подальша передача продовжується у функціях переривання UART
    return true;
}

// Обробник переривання спорожнення буфера передачі та повного кадру (TC)
void USART_IRQHandler(void) {
    // Якщо буфер вільний і є ще байти у черзі
    if (g_rs485.is_busy && (g_rs485.tx_index < g_rs485.tx_size)) {
        uart_hardware_send_byte(g_rs485.tx_buffer[g_rs485.tx_index++]);
    } 
    // Якщо всі байти записані й апаратура підтвердила прапорець TC
    else if (g_rs485.is_busy && uart_is_tx_complete()) {
        // Крок 3: Останній стоп-біт вийшов у дріт — відпускаємо шину
        gpio_set_de_low();
        g_rs485.is_busy = false;
    }
}

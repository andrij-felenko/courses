/* dmx_transmitter.c - Генератор пакетів DMX512 з прецизійним Break */
#include <stdint.h>
#include <stdbool.h>

#define DMX_CHANNELS 512
#define DMX_BREAK_US 100    /* Стандарт ANSI E1.11: >= 88 мкс */
#define DMX_MAB_US   12     /* Mark After Break: >= 8 мкс */

/* Низькорівневі апаратні примітиви платформи */
extern void hw_delay_us(uint32_t us);
extern void uart_tx_pin_set_gpio_low(void);
extern void uart_tx_pin_set_gpio_high(void);
extern void uart_tx_pin_restore_peripheral(void);
extern void uart_send_byte_blocking(uint8_t byte);

typedef struct {
    uint8_t start_code;
    uint8_t channels[DMX_CHANNELS];
} dmx_packet_t;

void dmx_send_packet(const dmx_packet_t *packet) {
    /* Крок 1: Формування Break (утримання лінії в 0V) */
    uart_tx_pin_set_gpio_low();
    hw_delay_us(DMX_BREAK_US);

    /* Крок 2: Формування Mark After Break (повернення в 1) */
    uart_tx_pin_set_gpio_high();
    hw_delay_us(DMX_MAB_US);

    /* Крок 3: Повернення піна під контроль апаратного UART */
    uart_tx_pin_restore_peripheral();

    /* Крок 4: Передача стартового коду (0x00 для димерів) */
    uart_send_byte_blocking(packet->start_code);

    /* Крок 5: Послідовна відправка всіх 512 каналів даних */
    for (uint32_t i = 0; i < DMX_CHANNELS; ++i) {
        uart_send_byte_blocking(packet->channels[i]);
    }
}

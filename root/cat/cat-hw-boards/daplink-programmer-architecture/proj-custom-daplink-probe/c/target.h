#ifndef TARGET_H
#define TARGET_H

#include <stdint.h>
#include <stdbool.h>

/* Визначення виводів апаратного інтерфейсу SWD для STM32F103C8T6 */
#define SWCLK_PORT          GPIOA
#define SWCLK_PIN           (1U << 5)   /* PA5: Тактовий сигнал SWCLK */

#define SWDIO_PORT          GPIOA
#define SWDIO_PIN           (1U << 6)   /* PA6: Двонаправлена лінія даних SWDIO */

#define TARGET_RESET_PORT   GPIOB
#define TARGET_RESET_PIN    (1U << 0)   /* PB0: Сигнал скидання цільового МК nRESET */

#define TARGET_PWR_PORT     GPIOB
#define TARGET_PWR_PIN      (1U << 1)   /* PB1: Керування живленням цілі (Target VCC) */

/* Визначення виводів послідовного порту CDC UART (USART1) */
#define UART_PORT           GPIOA
#define UART_TX_PIN         (1U << 9)   /* PA9: Передача USART1 TX */
#define UART_RX_PIN         (1U << 10)  /* PA10: Прийом USART1 RX */

/* Визначення виводів світлодіодних індикаторів станів DAPLink */
#define LED_PORT            GPIOC
#define LED_CONNECTED_PIN   (1U << 13)  /* PC13: Індикатор підключення USB-сесії */
#define LED_RUNNING_PIN     (1U << 14)  /* PC14: Індикатор активного зневадження */
#define LED_ACTIVITY_PIN    (1U << 15)  /* PC15: Індикатор передачі даних SWD/UART */

/* Типи світлодіодних індикаторів */
typedef enum {
    LED_CONNECTED = 0,
    LED_RUNNING,
    LED_ACTIVITY
} daplink_led_t;

/* Прототипи функцій апаратного рівня абстракції (HAL) */
void target_init(void);
void target_power_on(void);
void target_power_off(void);
void target_reset_assert(void);
void target_reset_deassert(void);
void target_swdio_set_input(void);
void target_swdio_set_output(void);
void target_set_led(daplink_led_t led, bool state);
void target_usart1_init(uint32_t baudrate);

#endif /* TARGET_H */

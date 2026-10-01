#ifndef TARGET_BOARD_H
#define TARGET_BOARD_H

#include <stdint.h>
#include <stdbool.h>

/*
 * Апаратне мапування виводів (Pinout) програматора DAPLink (на базі STM32F103C8T6).
 * Заголовочний файл визначає конфігурацію GPIO для зневадження SWD, послідовного порту UART,
 * сигналу системного скидання nRESET та світлодіодів індикації стану.
 */

// Сигнальні лінії зневадження SWD (Serial Wire Debug)
#define SWCLK_PIN_PORT          GPIOA
#define SWCLK_PIN               (1 << 5)   // PA5 - Тактування SWCLK
#define SWDIO_PIN_PORT          GPIOA
#define SWDIO_PIN               (1 << 6)   // PA6 - Двонапрямлена лінія даних SWDIO
#define SWO_PIN_PORT            GPIOA
#define SWO_PIN                 (1 << 7)   // PA7 - Вхід трасування SWO / ITM

// Сигнал керування скиданням цільового МК
#define RESET_PIN_PORT          GPIOB
#define RESET_PIN               (1 << 0)   // PB0 - nRESET (Конфігурація Open-Drain)

// Послідовний порт UART (Virtual COM Port / CDC)
#define UART_TX_PORT            GPIOA
#define UART_TX_PIN             (1 << 9)   // PA9 - TXD (Вихід до цільового МК)
#define UART_RX_PORT            GPIOA
#define UART_RX_PIN             (1 << 10)  // PA10 - RXD (Вхід від цільового МК)

// Світлодіодні індикатори режиму роботи програматора
#define LED_CONNECTED_PORT      GPIOB
#define LED_CONNECTED_PIN       (1 << 12)  // PB12 - Світлодіод утримання з'єднання з ПК
#define LED_RUNNING_PORT        GPIOB
#define LED_RUNNING_PIN         (1 << 13)  // PB13 - Світлодіод активності зневадження (SWD)

// Макроси швидкої маніпуляції станами сигнальних ліній
#define PIN_SWCLK_SET()         (SWCLK_PIN_PORT->BSRR = SWCLK_PIN)
#define PIN_SWCLK_CLR()         (SWCLK_PIN_PORT->BRR  = SWCLK_PIN)

#define PIN_SWDIO_SET()         (SWDIO_PIN_PORT->BSRR = SWDIO_PIN)
#define PIN_SWDIO_CLR()         (SWDIO_PIN_PORT->BRR  = SWDIO_PIN)
#define PIN_SWDIO_GET()         ((SWDIO_PIN_PORT->IDR & SWDIO_PIN) != 0)

#define PIN_RESET_ASSERT()      (RESET_PIN_PORT->BRR  = RESET_PIN)  // nRESET в 0 (Open-Drain активний)
#define PIN_RESET_DEASSERT()    (RESET_PIN_PORT->BSRR = RESET_PIN)  // nRESET в 1 (Підтяжка до VCC)

// Прототипи функцій ініціалізації шару плати (Board Layer)
void board_init(void);
void board_set_swd_dir(bool output);
void board_set_led_state(uint16_t led_pin, bool active);

#endif // TARGET_BOARD_H

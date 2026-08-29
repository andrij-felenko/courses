/* pins.h — план виводів плати на час сну й операції над ним.
 *
 * Плата: STM32L4 на CR2032, датчик температури й Flash сидять на комутованій
 * шині 3V3_SW, яку вмикає високобоковий P-MOSFET (затвор PB12: LOW — увімкнено).
 */
#ifndef PINS_H
#define PINS_H

#include <stdbool.h>
#include <stdint.h>
#include "regs.h"

/* Роль виводу у сні. Усе, чого немає в плані, отримує аналоговий режим. */
typedef enum {
    PIN_ROLE_ANALOG,     /* цифровий буфер від'єднати — наскрізного струму немає */
    PIN_ROLE_PARK_LOW,   /* притиснути до 0 В ДО розмикання ключа: анти-фантом */
    PIN_ROLE_KEEP_HIGH,  /* лишається виходом у стані 1 (затвор ключа) */
    PIN_ROLE_WAKEUP,     /* вивід пробудження, зміщений зовнішнім резистором */
    PIN_ROLE_SENSE       /* вимірювальний вхід, вмикається на мікросекунди */
} pin_role_t;

typedef struct {
    gpio_t     *port;
    uint8_t     pin;
    pin_role_t  role;
    const char *note;
} pin_plan_t;

/* Вивід керування ключем комутованої шини. */
#define RAIL_GATE_PORT GPIOB
#define RAIL_GATE_PIN  12u

void board_clocks_init(void);
void board_pins_init(void);

void board_rail_on(void);
void board_rail_off(void);
/* Чи справді просіла комутована шина після розмикання ключа.
 * Ненульове показання при вимкненому ключі = паразитне живлення через ESD-діод. */
bool board_rail_is_discharged(void);

/* Паркування сигнальних ліній комутованого домену в 0 В (ключ ще замкнений). */
void board_park_switched_domain(void);
/* Переведення всього, що не має ролі, в аналоговий режим без підтяжок. */
void board_pins_to_analog(void);
/* Підтяжки, які діють у Standby (там GPIO знеструмлено, керує PWR_PUCRx/PDCRx). */
void board_apply_standby_pulls(void);

/* Самоаудит: скільки виводів лишилося цифровими входами без підтяжки.
 * Саме такий вивід ловить наводку на VDD/2 і відкриває обидва транзистори буфера.
 * mask_a/b/c — побітові карти знайдених порушників (можна покласти в BKP-регістр). */
unsigned board_audit_floating(uint32_t *mask_a, uint32_t *mask_b, uint32_t *mask_c);

void board_led(bool on);
void board_delay_ms(uint32_t ms);

/* Низькорівневі помічники — потрібні й модулю I2C. */
void pin_mode(gpio_t *port, uint8_t pin, uint32_t mode);
void pin_pull(gpio_t *port, uint8_t pin, uint32_t pull);
void pin_af(gpio_t *port, uint8_t pin, uint32_t af);
void pin_write(gpio_t *port, uint8_t pin, bool level);
bool pin_read(gpio_t *port, uint8_t pin);

#endif /* PINS_H */

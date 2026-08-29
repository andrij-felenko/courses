/* Активне очікування апаратного прапорця: де воно вбиває систему
 * і як виглядає та сама дія, зроблена правильно. */
#ifndef BUSY_WAIT_TRAP_H
#define BUSY_WAIT_TRAP_H

#include <stdint.h>

typedef enum {
    I2C_OK = 0,
    I2C_TIMEOUT,   /* пристрій не відпустив шину за відведений час */
    I2C_BUS_ERROR  /* залізо підняло BERR/AF: колізія або NACK */
} i2c_status_t;

/* Запускає завдання-ретранслятор, яке переливає прийняті байти в I2C. */
void i2c_relay_start(void);

/* Верхня половина UART, зроблена правильно: без жодного очікування. */
void usart2_relay_isr(void);

/* Скільки байтів довелося викинути й скільки транзакцій зірвалося.
 * Без цих лічильників «іноді датчик мовчить» не діагностується взагалі. */
uint32_t i2c_relay_dropped(void);
uint32_t i2c_relay_failures(void);

#endif /* BUSY_WAIT_TRAP_H */

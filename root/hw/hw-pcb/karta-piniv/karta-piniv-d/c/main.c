/* Валідатор карти пінів мікроконтролера на чистому C (C99).
   Перевіряє апаратні конфлікти ліній EXTI та несумісність частот ШІМ таймерів. */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#define MAX_PINS 64
#define EXTI_LINES_COUNT 16
#define TIMERS_COUNT 8

typedef enum {
    PORT_A = 0, PORT_B = 1, PORT_C = 2, PORT_D = 3, PORT_NONE = 255
} mcu_port_t;

typedef enum {
    FUNC_GPIO_IN = 0,
    FUNC_GPIO_OUT,
    FUNC_ANALOG,
    FUNC_EXTI_INTERRUPT,
    FUNC_TIMER_PWM,
    FUNC_SPI,
    FUNC_I2C,
    FUNC_UART
} pin_function_t;

typedef struct {
    mcu_port_t     port;
    uint8_t        pin_index;      /* 0 .. 15 */
    pin_function_t function;
    uint8_t        timer_id;       /* 1 .. 8 (якщо FUNC_TIMER_PWM) */
    uint32_t       pwm_frequency;  /* Бажана частота ШІМ у Гц */
    const char    *net_name;
} pin_assignment_t;

typedef struct {
    bool has_conflict;
    char error_message[256];
} validation_result_t;

/* Перевірка таблиці призначень пінів на апаратні колізії */
validation_result_t validate_pinout(const pin_assignment_t *pins, size_t count)
{
    validation_result_t res = { .has_conflict = false, .error_message = "" };
    
    /* Масив для відстеження зайнятості ліній EXTI: зберігає порт, що зайняв лінію */
    int8_t exti_owner[EXTI_LINES_COUNT];
    for (int i = 0; i < EXTI_LINES_COUNT; ++i) exti_owner[i] = -1;

    /* Масив для відстеження частот таймерів: 0 означає, що таймер ще не використовується */
    uint32_t timer_frequencies[TIMERS_COUNT + 1] = { 0 };

    for (size_t i = 0; i < count; ++i) {
        const pin_assignment_t *p = &pins[i];
        if (p->port == PORT_NONE) continue;

        /* 1. Перевірка колізій ліній переривань EXTI */
        if (p->function == FUNC_EXTI_INTERRUPT) {
            if (p->pin_index >= EXTI_LINES_COUNT) {
                res.has_conflict = true;
                snprintf(res.error_message, sizeof(res.error_message),
                         "Пін %d поза межами ліній EXTI (0..15) для сигналу %s",
                         p->pin_index, p->net_name);
                return res;
            }
            if (exti_owner[p->pin_index] != -1 && exti_owner[p->pin_index] != p->port) {
                res.has_conflict = true;
                snprintf(res.error_message, sizeof(res.error_message),
                         "Колізія EXTI%d: сигнал '%s' (Port %c) конфліктує з Port %c",
                         p->pin_index, p->net_name, 'A' + p->port, 'A' + exti_owner[p->pin_index]);
                return res;
            }
            exti_owner[p->pin_index] = (int8_t)p->port;
        }

        /* 2. Перевірка узгодженості базових частот таймерів ШІМ */
        if (p->function == FUNC_TIMER_PWM) {
            if (p->timer_id == 0 || p->timer_id > TIMERS_COUNT) {
                res.has_conflict = true;
                snprintf(res.error_message, sizeof(res.error_message),
                         "Некоректний ID таймера TIM%d для сигналу %s", p->timer_id, p->net_name);
                return res;
            }
            if (timer_frequencies[p->timer_id] == 0) {
                timer_frequencies[p->timer_id] = p->pwm_frequency;
            } else if (timer_frequencies[p->timer_id] != p->pwm_frequency) {
                res.has_conflict = true;
                snprintf(res.error_message, sizeof(res.error_message),
                         "Конфлікт частоти TIM%d: сигнал '%s' вимагає %u Гц, а таймер налаштовано на %u Гц",
                         p->timer_id, p->net_name, p->pwm_frequency, timer_frequencies[p->timer_id]);
                return res;
            }
        }
    }

    return res;
}

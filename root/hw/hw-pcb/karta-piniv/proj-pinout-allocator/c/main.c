/* ============================================================================
   proj-pinout-allocator: Модуль валідації карти пінів мікроконтролера (C99).
   Перевіряє апаратні конфлікти AF, EXTI, DMA, PWM таймерів та сусідства падів.
   ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define MAX_PINS_PER_PORT      16
#define TOTAL_PORTS            8   /* Порти A, B, C, D, E, F, G, H */
#define TOTAL_EXTI_LINES       16
#define MAX_TIMERS             16
#define MAX_DMA_CONTROLLERS    2
#define MAX_DMA_STREAMS        8
#define MAX_ASSIGNMENTS        128
#define ERROR_BUFFER_SIZE      2048

typedef enum {
    PORT_A = 0, PORT_B, PORT_C, PORT_D,
    PORT_E,     PORT_F, PORT_G, PORT_H,
    PORT_INVALID = 255
} port_id_t;

typedef enum {
    PIN_TYPE_UNUSED = 0,
    PIN_TYPE_GPIO_IN,
    PIN_TYPE_GPIO_OUT,
    PIN_TYPE_EXTI,
    PIN_TYPE_ANALOG_IN,
    PIN_TYPE_TIMER_PWM,
    PIN_TYPE_SPI,
    PIN_TYPE_I2C,
    PIN_TYPE_UART,
    PIN_TYPE_HIGH_SPEED_BUS
} pin_type_t;

/* Опис одного призначення фізичного виводу */
typedef struct {
    port_id_t   port;
    uint8_t     pin_index;        /* 0 .. 15 */
    uint16_t    package_pin_num;  /* Фізичний номер ніжки на корпусі (1..144) */
    pin_type_t  type;
    uint8_t     af_code;          /* Код альтернативної функції (0..15) */
    
    /* Параметри таймера (якщо type == PIN_TYPE_TIMER_PWM) */
    uint8_t     timer_id;         /* 1 .. MAX_TIMERS */
    uint32_t    pwm_frequency_hz; /* Бажана частота ШІМ */

    /* Параметри DMA (якщо задіяно прямий доступ) */
    bool        uses_dma;
    uint8_t     dma_controller;   /* 1 або 2 */
    uint8_t     dma_stream;       /* 0 .. 7 */
    uint8_t     dma_channel;      /* 0 .. 7 */

    const char *signal_name;      /* Назва сигналу на схемі */
} pin_descriptor_t;

/* Результат валідації */
typedef struct {
    bool is_valid;
    uint32_t error_count;
    uint32_t warning_count;
    char report[ERROR_BUFFER_SIZE];
} validation_report_t;

static void report_error(validation_report_t *rep, const char *msg)
{
    rep->is_valid = false;
    rep->error_count++;
    size_t len = strlen(rep->report);
    if (len + strlen(msg) + 32 < ERROR_BUFFER_SIZE) {
        snprintf(rep->report + len, ERROR_BUFFER_SIZE - len, "  [ПОМИЛКА] %s\n", msg);
    }
}

static void report_warning(validation_report_t *rep, const char *msg)
{
    rep->warning_count++;
    size_t len = strlen(rep->report);
    if (len + strlen(msg) + 32 < ERROR_BUFFER_SIZE) {
        snprintf(rep->report + len, ERROR_BUFFER_SIZE - len, "  [ПОПЕРЕДЖЕННЯ] %s\n", msg);
    }
}

/* Головна функція верифікації конфігурації */
validation_report_t validate_mcu_pinout(const pin_descriptor_t *pins, size_t count)
{
    validation_report_t rep;
    rep.is_valid = true;
    rep.error_count = 0;
    rep.warning_count = 0;
    rep.report[0] = '\0';

    /* Масиви для відстеження стану апаратних ресурсів */
    int8_t exti_port_owner[TOTAL_EXTI_LINES];
    for (int i = 0; i < TOTAL_EXTI_LINES; ++i) exti_port_owner[i] = -1;

    uint32_t timer_frequencies[MAX_TIMERS + 1] = { 0 };
    int8_t   dma_stream_owner[MAX_DMA_CONTROLLERS][MAX_DMA_STREAMS];
    for (int c = 0; c < MAX_DMA_CONTROLLERS; ++c) {
        for (int s = 0; s < MAX_DMA_STREAMS; ++s) dma_stream_owner[c][s] = -1;
    }

    bool pad_allocated[TOTAL_PORTS][MAX_PINS_PER_PORT] = { { false } };
    char err_buf[256];

    for (size_t i = 0; i < count; ++i) {
        const pin_descriptor_t *p = &pins[i];
        if (p->port >= TOTAL_PORTS || p->pin_index >= MAX_PINS_PER_PORT) {
            snprintf(err_buf, sizeof(err_buf), "Некоректний порт/пін для сигналу '%s'", p->signal_name);
            report_error(&rep, err_buf);
            continue;
        }

        /* 1. Перевірка дублювання призначення фізичного паду */
        if (pad_allocated[p->port][p->pin_index]) {
            snprintf(err_buf, sizeof(err_buf), "Фізичний пін P%c%d призначено двічі (сигнал '%s')",
                     'A' + p->port, p->pin_index, p->signal_name);
            report_error(&rep, err_buf);
        }
        pad_allocated[p->port][p->pin_index] = true;

        /* 2. Перевірка ліній зовнішніх переривань EXTI */
        if (p->type == PIN_TYPE_EXTI) {
            uint8_t line = p->pin_index;
            if (exti_port_owner[line] != -1 && exti_port_owner[line] != p->port) {
                snprintf(err_buf, sizeof(err_buf),
                         "Колізія EXTI%d: сигнал '%s' (P%c%d) блокує лінію переривання порту P%c",
                         line, p->signal_name, 'A' + p->port, line, 'A' + exti_port_owner[line]);
                report_error(&rep, err_buf);
            }
            exti_port_owner[line] = (int8_t)p->port;
        }

        /* 3. Перевірка узгодженості частот каналів таймерів ШІМ */
        if (p->type == PIN_TYPE_TIMER_PWM) {
            if (p->timer_id == 0 || p->timer_id > MAX_TIMERS) {
                snprintf(err_buf, sizeof(err_buf), "Некоректний таймер TIM%d для сигналу '%s'",
                         p->timer_id, p->signal_name);
                report_error(&rep, err_buf);
            } else {
                if (timer_frequencies[p->timer_id] == 0) {
                    timer_frequencies[p->timer_id] = p->pwm_frequency_hz;
                } else if (timer_frequencies[p->timer_id] != p->pwm_frequency_hz) {
                    snprintf(err_buf, sizeof(err_buf),
                             "Конфлікт частоти TIM%d: сигнал '%s' вимагає %u Гц, але таймер вже працює на %u Гц",
                             p->timer_id, p->signal_name, p->pwm_frequency_hz, timer_frequencies[p->timer_id]);
                    report_error(&rep, err_buf);
                }
            }
        }

        /* 4. Перевірка колізій потоків контролера DMA */
        if (p->uses_dma) {
            if (p->dma_controller < 1 || p->dma_controller > MAX_DMA_CONTROLLERS ||
                p->dma_stream >= MAX_DMA_STREAMS) {
                snprintf(err_buf, sizeof(err_buf), "Некоректна адресація DMA%d_Stream%d для '%s'",
                         p->dma_controller, p->dma_stream, p->signal_name);
                report_error(&rep, err_buf);
            } else {
                uint8_t c_idx = p->dma_controller - 1;
                uint8_t s_idx = p->dma_stream;
                if (dma_stream_owner[c_idx][s_idx] != -1 && dma_stream_owner[c_idx][s_idx] != (int8_t)i) {
                    const pin_descriptor_t *other = &pins[dma_stream_owner[c_idx][s_idx]];
                    snprintf(err_buf, sizeof(err_buf),
                             "Колізія DMA%d_Stream%d: одночасний запит від '%s' та '%s'",
                             p->dma_controller, p->dma_stream, p->signal_name, other->signal_name);
                    report_error(&rep, err_buf);
                }
                dma_stream_owner[c_idx][s_idx] = (int8_t)i;
            }
        }
    }

    /* 5. Топологічна перевірка фізичної близькості (Analog vs High-Speed Digital) */
    for (size_t i = 0; i < count; ++i) {
        for (size_t j = i + 1; j < count; ++j) {
            const pin_descriptor_t *p1 = &pins[i];
            const pin_descriptor_t *p2 = &pins[j];

            if (p1->package_pin_num == 0 || p2->package_pin_num == 0) continue;

            int diff = (int)p1->package_pin_num - (int)p2->package_pin_num;
            if (diff == 1 || diff == -1) {
                /* Сусідні фізичні ніжки */
                bool is_p1_noisy = (p1->type == PIN_TYPE_HIGH_SPEED_BUS || p1->type == PIN_TYPE_SPI);
                bool is_p2_analog = (p2->type == PIN_TYPE_ANALOG_IN);

                bool is_p2_noisy = (p2->type == PIN_TYPE_HIGH_SPEED_BUS || p2->type == PIN_TYPE_SPI);
                bool is_p1_analog = (p1->type == PIN_TYPE_ANALOG_IN);

                if ((is_p1_noisy && is_p2_analog) || (is_p2_noisy && is_p1_analog)) {
                    snprintf(err_buf, sizeof(err_buf),
                             "Топологічний ризик завад: швидкісний цифровий сигнал '%s' (ніжка %d) "
                             "розташований безпосередньо поруч із чутливим аналоговим '%s' (ніжка %d)",
                             is_p1_noisy ? p1->signal_name : p2->signal_name,
                             is_p1_noisy ? p1->package_pin_num : p2->package_pin_num,
                             is_p1_analog ? p1->signal_name : p2->signal_name,
                             is_p1_analog ? p1->package_pin_num : p2->package_pin_num);
                    report_warning(&rep, err_buf);
                }
            }
        }
    }

    return rep;
}

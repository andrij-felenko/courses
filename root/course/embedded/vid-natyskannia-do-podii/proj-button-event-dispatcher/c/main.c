/* Стенд: те саме розділення контекстів, що й у прошивці, але замість
   переривання таймера — цикл по модельному часу, а замість GPIO — сценарій
   натискань із брязкотом. Так автомат можна ганяти на ПК, не маючи плати. */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "button.h"
#include "encoder.h"

#define TICK_MS         5u
#define RUN_MS       6000u
#define BOUNCE_MS       8u   /* скільки брязкотить контакт кнопки */
#define ENC_BOUNCE_MS   4u   /* скільки брязкотить фаза енкодера */

static uint32_t g_now_ms = 0;

/* --- Модель кнопки: коли контакт мав би бути замкнений --- */

typedef struct {
    uint32_t down_ms;
    uint32_t up_ms;
} press_span_t;

static const press_span_t k_presses[] = {
    {  100,  180 },  /* короткий клік */
    {  600,  680 },  /* перше натискання пари */
    {  780,  860 },  /* друге — має дати DOUBLE_CLICK */
    { 1500, 5200 },  /* довге утримання: START, HOLD і автоповтор із розгоном */
};

/* Псевдовипадковий біт для брязкоту. Свій LCG, а не rand(): прогін мусить
   бути повторюваним, інакше «воно іноді ламається» не відтвориш. */
static uint32_t g_rnd = 12345u;

static uint8_t noisy_bit(void) {
    g_rnd = g_rnd * 1103515245u + 12345u;
    return (uint8_t)((g_rnd >> 20) & 1u);
}

/* Active-low: 0 — контакт замкнено. Протягом BOUNCE_MS після кожного фронту
   віддаємо випадковий рівень — це і є брязкіт, через який наївний
   лічильник у перериванні наростає на 7 за одне натискання. */
static uint8_t read_button_pin(void) {
    for (size_t i = 0; i < sizeof k_presses / sizeof k_presses[0]; ++i) {
        const press_span_t p = k_presses[i];
        if (g_now_ms >= p.down_ms && g_now_ms < p.up_ms) {
            return (g_now_ms < p.down_ms + BOUNCE_MS) ? noisy_bit() : 0u;
        }
        if (g_now_ms >= p.up_ms && g_now_ms < p.up_ms + BOUNCE_MS) {
            return noisy_bit();
        }
    }
    return 1u;
}

/* --- Модель енкодера: чверть періоду за 10 мс --- */

static int32_t encoder_position(uint32_t t_ms) {
    int32_t pos = 0;
    if (t_ms > 2400u) {  /* за годинниковою */
        pos += (int32_t)(((t_ms < 3200u ? t_ms : 3200u) - 2400u) / 10u);
    }
    if (t_ms > 4000u) {  /* назад */
        pos -= (int32_t)(((t_ms < 4400u ? t_ms : 4400u) - 4000u) / 10u);
    }
    return pos;
}

/* Код Грея на двох бітах: 00 → 01 → 11 → 10 → 00 при русі вперед.
   Зсув 4096 (кратний чотирьом) прибирає від'ємний аргумент маски. */
static uint8_t encoder_gray_at(uint32_t t_ms) {
    const uint32_t n = (uint32_t)(encoder_position(t_ms) + 4096) & 3u;
    return (uint8_t)(n ^ (n >> 1));
}

static uint8_t phase_bit_at(uint32_t t_ms, uint8_t which) {
    const uint8_t gray = encoder_gray_at(t_ms);
    return (which == 0u) ? (uint8_t)((gray >> 1) & 1u) : (uint8_t)(gray & 1u);
}

/* Брязкотить лише та фаза, що саме перемикається: механічно друга в цей
   момент розімкнена намертво. Тому заборонених переходів стенд не породжує —
   вони бувають на живому валу, і лічильник glitches чекає саме на них. */
static uint8_t read_phase(uint8_t which) {
    const uint32_t back = (g_now_ms >= ENC_BOUNCE_MS) ? (g_now_ms - ENC_BOUNCE_MS) : 0u;
    const uint8_t now_bit = phase_bit_at(g_now_ms, which);
    const uint8_t old_bit = phase_bit_at(back, which);
    return (now_bit != old_bit) ? noisy_bit() : now_bit;
}

static uint8_t read_phase_a(void) { return read_phase(0u); }
static uint8_t read_phase_b(void) { return read_phase(1u); }

/* --- Головний цикл --- */

static const char *event_name(event_type_t type) {
    switch (type) {
    case EVENT_BUTTON_PRESS:            return "PRESS";
    case EVENT_BUTTON_RELEASE:          return "RELEASE";
    case EVENT_BUTTON_SHORT_CLICK:      return "SHORT_CLICK";
    case EVENT_BUTTON_DOUBLE_CLICK:     return "DOUBLE_CLICK";
    case EVENT_BUTTON_LONG_PRESS_START: return "LONG_PRESS_START";
    case EVENT_BUTTON_LONG_PRESS_HOLD:  return "LONG_PRESS_HOLD";
    case EVENT_BUTTON_REPEAT:           return "REPEAT";
    case EVENT_ENCODER_CW:              return "ENCODER_CW";
    case EVENT_ENCODER_CCW:             return "ENCODER_CCW";
    case EVENT_NONE:                    break;
    }
    return "NONE";
}

int main(void) {
    /* Уся пам'ять статична: ні malloc, ні фрагментації, ні сюрпризів на
       мікроконтролері з двома кілобайтами SRAM. */
    static event_queue_t queue;
    static button_t button;
    static encoder_t encoder;

    queue_init(&queue);
    if (!button_init(&button, 1u, read_button_pin) ||
        !encoder_init(&encoder, 2u, read_phase_a, read_phase_b)) {
        fprintf(stderr, "органи введення не налаштовано: порожній покажчик\n");
        return 1;
    }

    for (g_now_ms = 0; g_now_ms <= RUN_MS; g_now_ms += TICK_MS) {
        /* Контекст переривання таймера: лише вибірка, автомат і черга.
           Жодного printf, жодного запису у flash. */
        button_process_tick(&button, (uint16_t)TICK_MS, &queue);
        encoder_process_tick(&encoder, &queue);

        /* Контекст головного циклу: тут уже можна працювати повільно. */
        if (g_now_ms == 1000u) {
            printf("%6lu мс  зміна екрана: відкидаємо %u подій\n",
                   (unsigned long)g_now_ms, (unsigned)queue_size(&queue));
            queue_clear(&queue);
            continue;
        }

        input_event_t evt;
        while (queue_pop(&queue, &evt)) {
            printf("%6lu мс  id=%u  %-16s  %u мс\n",
                   (unsigned long)g_now_ms, (unsigned)evt.id,
                   event_name(evt.type), (unsigned)evt.duration_ms);
        }
    }

    const uint16_t dropped = queue_dropped(&queue);
    if (dropped != 0u) {
        printf("черга переповнювалася: втрачено %u подій\n", (unsigned)dropped);
    }
    printf("заборонених переходів енкодера: %u\n", (unsigned)encoder_glitches(&encoder));
    return 0;
}

#ifndef TELEMETRY_QUEUE_H
#define TELEMETRY_QUEUE_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Офлайн-буфер телеметрії кінцевого вузла.
 * Статична пам'ять, жодного malloc: 32 звіти по 12 байтів — 384 байти SRAM.
 * Коли канал зник, виміри лягають сюди; коли повернувся — їдуть у хмару.
 */
#define TELEMETRY_QUEUE_CAPACITY 32u

/* Прапорці, що їдуть разом з виміром і кажуть хмарі, за яких умов його зроблено. */
#define TELEMETRY_FLAG_HEATING    0x01u /* у момент виміру грів котел */
#define TELEMETRY_FLAG_FROM_CACHE 0x02u /* вимір зроблено без зв'язку, пролежав у буфері */

typedef struct {
    uint32_t timestamp;           /* локальні мілісекунди від старту чи RTC */
    float    measured_temperature;
    uint16_t current_power_watts;
    uint8_t  flags;
} telemetry_entry_t;

typedef struct {
    telemetry_entry_t slots[TELEMETRY_QUEUE_CAPACITY];
    uint16_t head;                /* куди кладемо наступний */
    uint16_t tail;                /* звідки беремо найстаріший */
    uint16_t count;
    uint32_t dropped_total;       /* скільки вимірів затерто через переповнення */
} telemetry_queue_t;

void telemetry_queue_init(telemetry_queue_t *q);

/* Кладе звіт. Повертає true, якщо буфер був повний і найстаріший вимір затерто. */
bool telemetry_queue_push(telemetry_queue_t *q, const telemetry_entry_t *entry);

/* Найстаріший звіт без вилучення (NULL — черга порожня).
   Peek + pop потрібні саме тому, що передача може не вдатися:
   вилучати можна лише після підтвердженої відправки. */
const telemetry_entry_t *telemetry_queue_peek(const telemetry_queue_t *q);

bool telemetry_queue_pop(telemetry_queue_t *q);

uint16_t telemetry_queue_count(const telemetry_queue_t *q);
bool     telemetry_queue_empty(const telemetry_queue_t *q);
uint32_t telemetry_queue_dropped(const telemetry_queue_t *q);

#endif /* TELEMETRY_QUEUE_H */

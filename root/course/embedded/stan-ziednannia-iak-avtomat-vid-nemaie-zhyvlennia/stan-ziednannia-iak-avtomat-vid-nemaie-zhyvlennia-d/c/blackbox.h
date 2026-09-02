#ifndef BLACKBOX_H
#define BLACKBOX_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Чорна скринька з'єднання: кільце переходів у пам'яті, що переживає
   знеструмлення. Кадр журналу їде на сервер першим же успішним сеансом. */

#define BLACKBOX_DEPTH  32u
#define BLACKBOX_REC_SZ 16u

typedef struct {
    uint32_t timestamp_ms;    /* Системний час моменту переходу */
    uint8_t  from_state;      /* Початковий стан */
    uint8_t  to_state;        /* Новий стан */
    uint8_t  event_id;        /* Подія, що викликала перехід */
    uint8_t  retry_count;     /* Поточний лічильник спроб */
    int8_t   rssi_dbm;        /* Рівень сигналу в момент події (дБм) */
    uint16_t cme_error_code;  /* Останній числовий код CME/CMS ERROR */
    uint16_t voltage_vbat_mv; /* Напруга живлення (мілівольти) */
    uint8_t  reserved[2];     /* Вирівнювання структури до 16 байтів */
} fsm_transition_log_t;

void blackbox_init(void); /* підіймає кільце зі збереженої пам'яті */
void blackbox_record(uint8_t from_state, uint8_t to_state, uint8_t event_id,
                     uint8_t retry_count, int8_t rssi_dbm, uint16_t cme_code,
                     uint16_t vbat_mv);
void blackbox_flush(void); /* запис у NV перед знеструмленням модема */

/* Пакує найстаріші записи в кадр телеметрії; повертає довжину в байтах. */
size_t blackbox_export(uint8_t *buf, size_t cap);

/* Викидає підтверджені сервером записи (bytes = довжина кадру). */
void blackbox_mark_sent(size_t bytes);

uint8_t blackbox_count(void);

#endif /* BLACKBOX_H */

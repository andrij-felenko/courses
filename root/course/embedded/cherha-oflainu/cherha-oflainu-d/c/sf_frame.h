/* Формат самодостатнього кадру черги офлайну у NOR Flash.
 *
 * Розкладка байтів на носії (little-endian, без вирівнювання):
 *
 *   зсув  розмір  поле
 *   0     2       magic 0xAA55
 *   2     4       seq          — монотонний лічильник кадрів
 *   6     8       ts_ms        — Unix Epoch у мілісекундах
 *   14    2       len          — довжина корисного навантаження
 *   16    1       type         — клас даних (подія / статус / сирий потік)
 *   17    len     payload
 *   17+len 4      crc32        — IEEE 802.3 по байтах [0, 17+len)
 *
 * Структуру НЕ накладаємо на буфер вказівником: на носії живе байтовий
 * формат, а не образ пам'яті Cortex-M. Явна серіалізація рятує від
 * трьох різних бід — вирівнювання (seq стоїть на непарному зсуві),
 * порядку байтів і мовчазної зміни розкладки компілятором.
 */
#ifndef SF_FRAME_H
#define SF_FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define SF_MAGIC       0xAA55u
#define SF_HDR_SIZE    17u
#define SF_CRC_SIZE    4u
#define SF_MAX_PAYLOAD 512u
#define SF_MAX_FRAME   (SF_HDR_SIZE + SF_MAX_PAYLOAD + SF_CRC_SIZE)

/* Класи даних із політики витіснення. Сканер їх не тлумачить — вони
 * потрібні диспетчеру черги, коли сховище переповнене. */
enum {
    SF_TYPE_EVENT  = 0, /* Клас 0 — аварії, ніколи не витісняються */
    SF_TYPE_STATUS = 1, /* Клас 1 — періодичний агрегований статус */
    SF_TYPE_RAW    = 2  /* Клас 2 — високочастотний сирий потік */
};

typedef struct {
    uint32_t seq;
    uint64_t ts_ms;
    uint16_t len;
    uint8_t  type;
} sf_hdr_t;

typedef enum {
    SF_OK = 0,
    SF_ERR_ERASED,    /* 0xFF 0xFF — далі в секторі порожньо */
    SF_ERR_MAGIC,     /* байти є, але це не початок кадру */
    SF_ERR_LENGTH,    /* len за межами дозволеного */
    SF_ERR_TRUNCATED, /* кадр не вміщується в те, що лишилось у секторі */
    SF_ERR_CRC        /* запис обірвано знеструмленням або биті комірки */
} sf_status_t;

uint32_t sf_crc32(const uint8_t *data, size_t len);

/* Повний розмір кадру на носії для заданого навантаження. */
size_t sf_frame_size(uint16_t payload_len);

/* Складає кадр у dst. Повертає розмір кадру або 0, якщо не вміщується
 * чи навантаження задовге. payload може бути NULL лише при len == 0. */
size_t sf_encode(uint8_t *dst, size_t dst_cap,
                 const sf_hdr_t *hdr, const uint8_t *payload);

/* Розбирає кадр із початку buf. avail — скільки байтів сектора реально
 * прочитано. При SF_OK заповнює out і кладе в out_total повний розмір
 * кадру, щоб викликач зсунувся до наступного запису. */
sf_status_t sf_parse(const uint8_t *buf, size_t avail,
                     sf_hdr_t *out, size_t *out_total);

/* Порівняння номерів із урахуванням переповнення 32-бітного лічильника:
 * після 0xFFFFFFFF іде 1, і різниця, взята зі знаком, це переживає. */
bool sf_seq_after(uint32_t a, uint32_t b);

#endif /* SF_FRAME_H */

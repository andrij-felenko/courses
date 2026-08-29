/* sf_queue.h — черга «збережи-й-перешли» поверх кільця секторів NOR.
 *
 * Кільце з N секторів по 4 КіБ. Кадри дозаписуються в сектор голови
 * підряд; кадр ніколи не ділиться між секторами, бо стирання працює
 * секторами, і половинка кадру в стертому сусіді — це втрачений кадр.
 *
 * Дві колії вивантаження:
 *   жива     — свіжий кадр пішов у ефір одразу після push(), квитанція
 *              приходить окремо: sf_queue_ack_live();
 *   історія  — sf_queue_drain_batch() віддає пачку старих кадрів від
 *              хвоста, сервер квитує пачку одним номером:
 *              sf_queue_commit_ack().
 *
 * Хвіст рухається тільки по квитанціях і тільки суцільно: сектор
 * звільняється, лише коли ВСІ його кадри або квитовані, або зіпсовані.
 * Живі квитанції з верху нумерації хвоста самі по собі не рухають —
 * вони чекають у sf_ackset, поки історія доповзе.
 *
 * Динамічної пам'яті немає жодного байта: увесь стан у sf_queue_t,
 * буфер кадру — теж.
 */
#ifndef SF_QUEUE_H
#define SF_QUEUE_H

#include <stdbool.h>
#include <stdint.h>

#include "sf_ackset.h"
#include "sf_flash.h"
#include "sf_frame.h"
#include "sf_lock.h"

typedef enum {
    SF_OK = 0,
    SF_E_PARAM,   /* порожнє або задовге навантаження, безглузді межі */
    SF_E_FULL,    /* кільце повне, а кадр не вартий витіснення історії */
    SF_E_IO,      /* носій не відповів */
    SF_E_EMPTY,   /* у черзі нема чого віддавати */
} sf_err_t;

typedef struct {
    uint32_t records_written;
    uint32_t bytes_written;
    uint32_t sectors_erased;
    uint32_t sectors_evicted;    /* витіснено під важливіші дані */
    uint32_t dropped_full;       /* відмовлено низькопріоритетним кадрам */
    uint32_t corrupt_records;    /* биті CRC або чужа преамбула при читанні */
    uint32_t recovered_records;  /* знайдено цілими під час сканування */
    uint32_t flash_errors;
    uint32_t skipped_live_acked; /* історія не перечитувала те, що доїхало живцем */
} sf_stats_t;

/* Кадр, прочитаний з носія. payload дивиться у внутрішній буфер черги
 * і чинний до наступного виклику черги — саме тому мережеве завдання
 * або віддає його в сокет одразу, або копіює. */
typedef struct {
    sf_header_t    hdr;
    const uint8_t *payload;
    uint32_t       stride;
    uint32_t       sector;
    uint32_t       offset;
} sf_record_t;

/* Пачка на одну радіопередачу. Обмежена і числом кадрів, і байтами:
 * канал усе одно має свій MTU, і слати більше немає сенсу. */
#define SF_BATCH_MAX_RECORDS 8u
#define SF_BATCH_ARENA       1024u

typedef struct {
    uint32_t seq;
    uint64_t timestamp_ms;
    uint8_t  type;
    uint8_t  priority;
    uint16_t len;
    uint16_t offset; /* зміщення в arena */
} sf_batch_item_t;

typedef struct {
    sf_batch_item_t item[SF_BATCH_MAX_RECORDS];
    uint8_t         arena[SF_BATCH_ARENA];
    uint32_t        count;
    uint32_t        used;
    uint32_t        first_seq;
    uint32_t        last_seq;
} sf_batch_t;

typedef struct {
    const sf_flash_dev_t *flash;
    sf_lock_t             lock;

    uint32_t base_addr;
    uint32_t sector_count;
    uint32_t sector_size;

    uint32_t head_sector;
    uint32_t head_offset;
    uint32_t tail_sector;
    uint32_t tail_offset;

    /* Читальний курсор історії: біжить попереду хвоста, поки пачки
     * летять у ефір і ще не квитовані. */
    uint32_t drain_sector;
    uint32_t drain_offset;

    uint32_t    next_seq;
    sf_ackset_t ack;
    sf_stats_t  stats;

    uint8_t scratch[SF_RECORD_MAX];
} sf_queue_t;

/* Сканує кільце й відновлює голову, хвіст і лічильник номерів.
 * lock може бути NULL — тоді черга вважає вузол однопотоковим. */
sf_err_t sf_queue_init(sf_queue_t *q, const sf_flash_dev_t *flash, uint32_t base_addr,
                       uint32_t sector_count, const sf_lock_t *lock);

/* Кладе кадр у флеш. out_seq (може бути NULL) отримує присвоєний номер —
 * саме його потім називає квитанція живої колії. */
sf_err_t sf_queue_push(sf_queue_t *q, uint8_t type, sf_priority_t prio, uint64_t ts_ms,
                       const void *payload, uint16_t len, uint32_t *out_seq);

/* Найстаріший кадр черги, БЕЗ зсуву хвоста. */
sf_err_t sf_queue_peek_tail(sf_queue_t *q, sf_record_t *out);

/* Пачка історії від курсора вивантаження. Кадри, уже квитовані живою
 * колією, пропускаються мовчки. */
sf_err_t sf_queue_drain_batch(sf_queue_t *q, sf_batch_t *batch);

/* Пачка не долетіла: повернути курсор історії на хвіст. */
void sf_queue_drain_rewind(sf_queue_t *q);

/* Пакетне квитування: сервер має все до acked_seq включно. */
void sf_queue_commit_ack(sf_queue_t *q, uint32_t acked_seq);

/* Квитанція живої колії на один кадр. */
void sf_queue_ack_live(sf_queue_t *q, uint32_t seq);

bool     sf_queue_is_empty(sf_queue_t *q);
uint32_t sf_queue_bytes_pending(sf_queue_t *q);

static inline const sf_stats_t *sf_queue_stats(const sf_queue_t *q)
{
    return &q->stats;
}

#endif /* SF_QUEUE_H */

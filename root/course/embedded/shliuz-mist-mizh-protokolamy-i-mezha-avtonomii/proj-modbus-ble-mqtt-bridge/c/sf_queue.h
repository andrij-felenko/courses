#ifndef SF_QUEUE_H
#define SF_QUEUE_H

#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Буфер Store-and-Forward: дві черги в одній структурі.
 *
 * Свіжа черга коротка й має пріоритет — щойно зняті показники йдуть у сокет
 * першими. Коли канал зник і свіжа черга переповнилася, найстаріше з неї
 * переїжджає в архівну; переповнена архівна витісняє найдавніше й рахує втрати.
 * Так свіжі дані ніколи не чекають за спиною в сотні тисяч старих записів.
 *
 * Пам'ять під обидві черги виділено статично, розміром часу компіляції: у
 * шлюза, що працює місяцями без перезапуску, немає ні приводу фрагментувати
 * купу, ні способу пережити відмову malloc() посеред ночі.
 */

#define BUFFER_CAPACITY 512   /* архівна черга */
#define FRESH_CAPACITY  64    /* свіжа черга: рівно стільки, щоб пережити мікрообриви */

#define SF_TOPIC_MAX   64
#define SF_PAYLOAD_MAX 192

typedef struct {
    char topic[SF_TOPIC_MAX];
    char payload[SF_PAYLOAD_MAX];
    uint32_t seq;      /* монотонний, не скидається при обриві мережі */
    int64_t ts_ms;     /* мітка часу зняття, не відправлення */
} telemetry_msg_t;

/* Кільце над чужою пам'яттю: показник дивиться на статичний масив нижче. */
typedef struct {
    telemetry_msg_t *items;
    size_t cap;
    size_t head;
    size_t tail;
    size_t count;
} sf_ring_t;

typedef struct {
    sf_ring_t fresh;
    sf_ring_t backlog;
    telemetry_msg_t fresh_storage[FRESH_CAPACITY];
    telemetry_msg_t backlog_storage[BUFFER_CAPACITY];
    uint32_t dropped;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
} sf_queue_t;

void sf_init(sf_queue_t *q);
void sf_destroy(sf_queue_t *q);

/* Покласти повідомлення у свіжу чергу (витіснення робиться всередині). */
void sf_publish(sf_queue_t *q, const telemetry_msg_t *msg);

/* Подивитися наступне на відправку, НЕ знімаючи його з черги: спершу свіже,
 * далі архівне. Чекає до wait_ms, поки з'явиться хоч щось.
 * true — є що слати, from_backlog каже, з якої саме черги. */
bool sf_peek(sf_queue_t *q, telemetry_msg_t *out, bool *from_backlog, unsigned wait_ms);

/* Зняти повідомлення з черги — лише після PUBACK від брокера. seq звіряється:
 * поки ми чекали підтвердження, витіснення могло зсунути хвіст черги. */
void sf_commit(sf_queue_t *q, bool from_backlog, uint32_t seq);

void sf_stats(sf_queue_t *q, size_t *fresh, size_t *backlog, uint32_t *dropped);

/* Монотонний час у мілісекундах: ним міряють темп дренажу й періоди опитування.
 * Мітку ts_ms ставлять за календарним часом — її читатиме сервер. */
int64_t sf_now_ms(void);

#endif /* SF_QUEUE_H */

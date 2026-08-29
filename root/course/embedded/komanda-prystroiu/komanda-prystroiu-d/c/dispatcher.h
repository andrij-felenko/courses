#ifndef DISPATCHER_H
#define DISPATCHER_H

/* Диспетчер команд: кільцевий буфер ідемпотентності, черга виконання,
 * автомат станів і двофазне квитування. Динамічної пам'яті немає — уся
 * структура статична, її розмір відомий на етапі компіляції. */

#include <stddef.h>
#include <stdint.h>

#include "cmd_proto.h"

#define RING_SIZE   16u   /* слотів дедуплікації: вікно повторів мережі */
#define QUEUE_SIZE   8u   /* глибина черги виконання (залп після сну) */

typedef struct {
    uint64_t token;
    uint8_t  type;
    uint8_t  state;         /* cmd_state_t */
    uint8_t  payload_len;
    uint8_t  payload[CMD_MAX_PAYLOAD];
    uint32_t rx_time_ms;
    uint32_t deadline_ms;   /* rx_time_ms + ttl_ms за монотонним таймером */
    int32_t  result;
    int32_t  detail;
} cmd_record_t;

typedef struct {
    cmd_record_t ring[RING_SIZE];
    uint8_t      ring_head;

    uint8_t      queue[QUEUE_SIZE];   /* індекси слотів кільця */
    uint8_t      q_head;
    uint8_t      q_count;

    uint32_t     last_seq;            /* захист від повторного відтворення */
    int8_t       active;              /* індекс слота в роботі, -1 — привід вільний */

    struct {
        uint32_t dropped;
        uint32_t replays;
        uint32_t duplicates;
        uint32_t expired;
        uint32_t superseded;
        uint32_t executed;
    } stats;
} dispatcher_t;

void      dispatcher_init(dispatcher_t *d);

/* Перевірка журналу FRAM при старті: гомінг і квиток про зірвану транзакцію. */
void      dispatcher_boot_recover(dispatcher_t *d);

/* Прийом кадру з радіоканалу (виклик із обробника мережевої події). */
cmd_err_t dispatcher_on_frame(dispatcher_t *d, const uint8_t *buf, size_t len);

/* Крок автомата з головного циклу: опитування приводу і старт наступної команди. */
void      dispatcher_tick(dispatcher_t *d);

void      dispatcher_print_stats(const dispatcher_t *d);

#endif /* DISPATCHER_H */

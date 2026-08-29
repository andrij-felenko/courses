#ifndef CHANNEL_H
#define CHANNEL_H

#include "link.h"

// Імітатор фізичного каналу з усіма п'ятьма руйнівними режимами:
// спотворення бітів пачкою, втрата, дублювання, перевпорядкування
// і, на виході, розрізання та склеювання байтового потоку.
//
// Генератор випадкових чисел — xorshift32 із фіксованим зерном: прогін відтворюваний.

#define CHANNEL_PKT_CAP    LINK_MAX_WIRE
#define CHANNEL_STREAM_CAP 4096U
#define CHANNEL_MAX_CHUNK  24U

typedef struct {
    uint16_t drop_permille;       // завмирання, колізія, скидання апаратним FIFO
    uint16_t duplicate_permille;  // кадр пройшов лінією двічі
    uint16_t reorder_permille;    // кадр пропускає наступний уперед
    uint16_t burst_permille;      // пачка спотворених сусідніх бітів
} channel_cfg_t;

typedef void (*channel_sink_fn)(const uint8_t *bytes, size_t len, void *ctx);

typedef struct {
    channel_cfg_t cfg;
    uint32_t      rng;

    uint8_t stream[CHANNEL_STREAM_CAP];   // байти в дорозі, кільцем
    size_t  stream_head;
    size_t  stream_len;

    uint8_t held[CHANNEL_PKT_CAP];        // затриманий кадр (перевпорядкування)
    size_t  held_len;
    bool    has_held;

    struct {
        uint32_t offered;     // кадрів віддано в канал
        uint32_t dropped;     // згинуло без сліду
        uint32_t corrupted;   // побито пачкою бітових помилок
        uint32_t duplicated;  // пройшло двічі
        uint32_t reordered;   // пропустило наступний кадр уперед
        uint32_t overflow;    // не влізло у чергу лінії
    } stats;
} channel_t;

void channel_init(channel_t *ch, const channel_cfg_t *cfg, uint32_t seed);

// Передавач віддає в канал готовий кадр разом із роздільником.
void channel_send(channel_t *ch, const uint8_t *frame, size_t len);

// Приймач вичитує з лінії стільки, скільки встигло прийти: шматок довільного розміру.
void channel_pump(channel_t *ch, channel_sink_fn sink, void *ctx);

bool channel_idle(const channel_t *ch);

#endif // CHANNEL_H

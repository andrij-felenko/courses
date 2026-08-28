#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_CAPACITY 64
#define TOTAL_EVENTS 1000

// ── Структура події ────────────────────────────────────────────────────────
typedef struct {
    uint64_t event_id;
    char ip_address[32];
    uint16_t port;
    int payload_size;
    double risk_score;
    bool is_valid;
} SecurityEvent;

// ── Обмежений кільцевий буфер (Bounded Queue на POSIX Threads) ────────────
typedef struct {
    SecurityEvent buffer[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    bool closed;
    pthread_mutex_t mutex;
    pthread_cond_t cv_not_full;
    pthread_cond_t cv_not_empty;
} BoundedChannel;

void channel_init(BoundedChannel* chan) {
    chan->head = 0;
    chan->tail = 0;
    chan->count = 0;
    chan->closed = false;
    pthread_mutex_init(&chan->mutex, NULL);
    pthread_cond_init(&chan->cv_not_full, NULL);
    pthread_cond_init(&chan->cv_not_empty, NULL);
}

void channel_destroy(BoundedChannel* chan) {
    pthread_mutex_destroy(&chan->mutex);
    pthread_cond_destroy(&chan->cv_not_full);
    pthread_cond_destroy(&chan->cv_not_empty);
}

bool channel_push(BoundedChannel* chan, const SecurityEvent* item) {
    pthread_mutex_lock(&chan->mutex);
    while (chan->count == BUFFER_CAPACITY && !chan->closed) {
        pthread_cond_wait(&chan->cv_not_full, &chan->mutex);
    }

    if (chan->closed) {
        pthread_mutex_unlock(&chan->mutex);
        return false;
    }

    chan->buffer[chan->tail] = *item;
    chan->tail = (chan->tail + 1) % BUFFER_CAPACITY;
    chan->count++;

    pthread_cond_signal(&chan->cv_not_empty);
    pthread_mutex_unlock(&chan->mutex);
    return true;
}

bool channel_pop(BoundedChannel* chan, SecurityEvent* out_item) {
    pthread_mutex_lock(&chan->mutex);
    while (chan->count == 0 && !chan->closed) {
        pthread_cond_wait(&chan->cv_not_empty, &chan->mutex);
    }

    if (chan->count == 0 && chan->closed) {
        pthread_mutex_unlock(&chan->mutex);
        return false;
    }

    *out_item = chan->buffer[chan->head];
    chan->head = (chan->head + 1) % BUFFER_CAPACITY;
    chan->count--;

    pthread_cond_signal(&chan->cv_not_full);
    pthread_mutex_unlock(&chan->mutex);
    return true;
}

void channel_close(BoundedChannel* chan) {
    pthread_mutex_lock(&chan->mutex);
    chan->closed = true;
    pthread_cond_broadcast(&chan->cv_not_empty);
    pthread_cond_broadcast(&chan->cv_not_full);
    pthread_mutex_unlock(&chan->mutex);
}

// ── Контексти потоків конвеєра ─────────────────────────────────────────────
typedef struct {
    BoundedChannel* in_chan;
    BoundedChannel* out_chan;
    uint64_t stat_count;
} StageContext;

void* stage_parser(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        usleep(100); // 100 мкс роботи
        ctx->stat_count++;
        if (!channel_push(ctx->out_chan, &event)) {
            break;
        }
    }
    channel_close(ctx->out_chan);
    return NULL;
}

void* stage_validator(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        if (event.port == 0 || event.payload_size < 0 || event.payload_size > 65535) {
            ctx->stat_count++; // Рахуємо як відкинуті
            continue;
        }
        usleep(150);
        if (!channel_push(ctx->out_chan, &event)) {
            break;
        }
    }
    channel_close(ctx->out_chan);
    return NULL;
}

void* stage_scorer(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        double score = 0.1;
        if (event.port == 22 || event.port == 3389) {
            score += 0.4;
        }
        if (event.payload_size > 4096) {
            score += 0.35;
        }
        event.risk_score = score;
        usleep(400);
        ctx->stat_count++;
        if (!channel_push(ctx->out_chan, &event)) {
            break;
        }
    }
    channel_close(ctx->out_chan);
    return NULL;
}

void* stage_sink(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        usleep(100);
        ctx->stat_count++;
    }
    return NULL;
}

int main(void) {
    BoundedChannel chan_raw, chan_parsed, chan_validated, chan_scored;
    channel_init(&chan_raw);
    channel_init(&chan_parsed);
    channel_init(&chan_validated);
    channel_init(&chan_scored);

    StageContext ctx_parser = { &chan_raw, &chan_parsed, 0 };
    StageContext ctx_validator = { &chan_parsed, &chan_validated, 0 };
    StageContext ctx_scorer = { &chan_validated, &chan_scored, 0 };
    StageContext ctx_sink = { &chan_scored, NULL, 0 };

    pthread_t th_parser, th_validator, th_scorer, th_sink;
    pthread_create(&th_parser, NULL, stage_parser, &ctx_parser);
    pthread_create(&th_validator, NULL, stage_validator, &ctx_validator);
    pthread_create(&th_scorer, NULL, stage_scorer, &ctx_scorer);
    pthread_create(&th_sink, NULL, stage_sink, &ctx_sink);

    // Генерація подій
    for (size_t i = 1; i <= TOTAL_EVENTS; ++i) {
        SecurityEvent ev;
        ev.event_id = i;
        snprintf(ev.ip_address, sizeof(ev.ip_address), "192.168.1.%zu", (i % 254) + 1);
        ev.port = (i % 20 == 0) ? 0 : ((i % 5 == 0) ? 22 : 443);
        ev.payload_size = (i % 20 == 0) ? -10 : (int)(512 + (i * 37) % 8000);
        ev.risk_score = 0.0;
        ev.is_valid = true;

        channel_push(&chan_raw, &ev);
    }
    channel_close(&chan_raw);

    pthread_join(th_parser, NULL);
    pthread_join(th_validator, NULL);
    pthread_join(th_scorer, NULL);
    pthread_join(th_sink, NULL);

    printf("=== Результати роботи C-конвеєра ===\n");
    printf("Оброблено парсером:          %lu\n", ctx_parser.stat_count);
    printf("Відсіяно валідатором:        %lu\n", ctx_validator.stat_count);
    printf("Оцінено скорингом:           %lu\n", ctx_scorer.stat_count);
    printf("Збережено в базу (Sink):     %lu\n", ctx_sink.stat_count);

    channel_destroy(&chan_raw);
    channel_destroy(&chan_parsed);
    channel_destroy(&chan_validated);
    channel_destroy(&chan_scored);

    return 0;
}

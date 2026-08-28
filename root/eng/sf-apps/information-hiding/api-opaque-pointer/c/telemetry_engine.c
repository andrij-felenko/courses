/* telemetry_engine.c — прихована реалізація модуля */
#include "telemetry_engine.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define RING_BUFFER_SIZE 64

/* ПРИВАТНЕ представлення окремого каналу вимірювань */
typedef struct {
    float  samples[RING_BUFFER_SIZE];
    size_t head;
    size_t count;
    float  running_sum;
} channel_state_t;

/* ПОВНЕ визначення структури — головна таємниця модуля */
struct telemetry_engine {
    uint32_t         sample_rate_hz;
    size_t           channel_count;
    channel_state_t *channels;
    uint32_t         total_samples_processed;
};

/* Приватна допоміжна функція валідації стану (внутрішній інваріант) */
static inline bool te_is_valid(const telemetry_engine_t *e) {
    return (e != NULL && e->channels != NULL && e->channel_count > 0);
}

telemetry_engine_t* te_create(const te_config_t *config) {
    if (!config || config->max_channels == 0) return NULL;

    telemetry_engine_t *e = (telemetry_engine_t*)malloc(sizeof(telemetry_engine_t));
    if (!e) return NULL;

    e->sample_rate_hz = config->sample_rate_hz;
    e->channel_count = config->max_channels;
    e->total_samples_processed = 0;

    e->channels = (channel_state_t*)calloc(e->channel_count, sizeof(channel_state_t));
    if (!e->channels) {
        free(e);
        return NULL;
    }

    return e;
}

void te_destroy(telemetry_engine_t *engine) {
    if (!engine) return;
    free(engine->channels);
    free(engine);
}

te_status_t te_push_sample(telemetry_engine_t *engine, uint16_t channel_id, float value) {
    if (!te_is_valid(engine)) return TE_ERR_INVALID_ARG;
    if (channel_id >= engine->channel_count) return TE_ERR_INVALID_ARG;

    channel_state_t *ch = &engine->channels[channel_id];
    
    if (ch->count == RING_BUFFER_SIZE) {
        ch->running_sum -= ch->samples[ch->head];
    } else {
        ch->count++;
    }

    ch->samples[ch->head] = value;
    ch->running_sum += value;
    ch->head = (ch->head + 1) % RING_BUFFER_SIZE;
    
    engine->total_samples_processed++;
    return TE_OK;
}

te_status_t te_get_channel_mean(const telemetry_engine_t *engine, uint16_t channel_id, float *out_mean) {
    if (!te_is_valid(engine) || !out_mean) return TE_ERR_INVALID_ARG;
    if (channel_id >= engine->channel_count) return TE_ERR_INVALID_ARG;

    const channel_state_t *ch = &engine->channels[channel_id];
    if (ch->count == 0) {
        *out_mean = 0.0f;
        return TE_OK;
    }

    *out_mean = ch->running_sum / (float)ch->count;
    return TE_OK;
}

te_status_t te_reset(telemetry_engine_t *engine) {
    if (!te_is_valid(engine)) return TE_ERR_INVALID_ARG;
    memset(engine->channels, 0, engine->channel_count * sizeof(channel_state_t));
    engine->total_samples_processed = 0;
    return TE_OK;
}

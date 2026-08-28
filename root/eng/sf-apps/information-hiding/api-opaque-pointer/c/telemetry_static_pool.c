/* telemetry_static_pool.c — виділення без використання купи */
#include "telemetry_engine.h"

#define MAX_STATIC_ENGINES 4
#define STATIC_MAX_CHANNELS 8

static telemetry_engine_t g_engine_pool[MAX_STATIC_ENGINES];
static channel_state_t   g_channel_pool[MAX_STATIC_ENGINES][STATIC_MAX_CHANNELS];
static bool               g_engine_in_use[MAX_STATIC_ENGINES] = {false};

telemetry_engine_t* te_create(const te_config_t *config) {
    if (!config || config->max_channels > STATIC_MAX_CHANNELS) return NULL;

    for (size_t i = 0; i < MAX_STATIC_ENGINES; i++) {
        if (!g_engine_in_use[i]) {
            g_engine_in_use[i] = true;
            telemetry_engine_t *e = &g_engine_pool[i];
            e->sample_rate_hz = config->sample_rate_hz;
            e->channel_count = config->max_channels;
            e->total_samples_processed = 0;
            e->channels = g_channel_pool[i];
            memset(e->channels, 0, sizeof(channel_state_t) * config->max_channels);
            return e;
        }
    }
    return NULL; /* Пул переповнений */
}

void te_destroy(telemetry_engine_t *engine) {
    if (!engine) return;
    for (size_t i = 0; i < MAX_STATIC_ENGINES; i++) {
        if (&g_engine_pool[i] == engine) {
            g_engine_in_use[i] = false;
            return;
        }
    }
}

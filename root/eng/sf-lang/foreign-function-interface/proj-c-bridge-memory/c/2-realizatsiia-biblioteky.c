#include "bridge_core.h"
#include <stdlib.h>
#include <string.h>

struct BridgeContext {
    BridgeConfig config;
    double accumulated_scale;
};

BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx) {
    if (!config || !out_ctx) return BRIDGE_ERR_NULL_PTR;
    if (config->sample_rate <= 0 || config->channels <= 0) return BRIDGE_ERR_INVALID_PARAM;

    BridgeContext *ctx = (BridgeContext*)malloc(sizeof(BridgeContext));
    if (!ctx) return BRIDGE_ERR_OUT_OF_MEMORY;

    ctx->config = *config;
    ctx->accumulated_scale = config->scale_factor;
    *out_ctx = ctx;
    return BRIDGE_OK;
}

BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count) {
    if (!ctx || !input || !out_buf || !out_count) return BRIDGE_ERR_NULL_PTR;
    if (count == 0) return BRIDGE_ERR_INVALID_PARAM;

    float *processed = (float*)malloc(sizeof(float) * count);
    if (!processed) return BRIDGE_ERR_OUT_OF_MEMORY;

    double factor = ctx->accumulated_scale;
    for (size_t i = 0; i < count; ++i) {
        processed[i] = (float)(input[i] * factor);
    }

    *out_buf = processed;
    *out_count = count;
    return BRIDGE_OK;
}

BRIDGE_API void bridge_free_buffer(float *buf) {
    if (buf) {
        free(buf);
    }
}

BRIDGE_API void bridge_free_context(BridgeContext *ctx) {
    if (ctx) {
        free(ctx);
    }
}

BRIDGE_API const char* bridge_get_last_error(BridgeStatus status) {
    switch (status) {
        case BRIDGE_OK:                return "Успішне виконання";
        case BRIDGE_ERR_NULL_PTR:      return "Передано нульовий покажчик";
        case BRIDGE_ERR_INVALID_PARAM: return "Некоректні вхідні параметри";
        case BRIDGE_ERR_OUT_OF_MEMORY: return "Недостатньо системної пам'яті";
        case BRIDGE_ERR_COMPUTATION:   return "Помилка обчислень";
        default:                       return "Невідомий код помилки";
    }
}

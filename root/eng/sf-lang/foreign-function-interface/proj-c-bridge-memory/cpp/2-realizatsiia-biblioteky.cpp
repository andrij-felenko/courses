#include "bridge_core.hpp"
#include <vector>
#include <memory>
#include <new>

struct BridgeContext {
    BridgeConfig config;
    double accumulated_scale;

    explicit BridgeContext(const BridgeConfig& cfg)
        : config(cfg), accumulated_scale(cfg.scale_factor) {}
};

BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx) {
    if (!config || !out_ctx) return BridgeStatus::ErrNullPtr;
    if (config->sample_rate <= 0 || config->channels <= 0) return BridgeStatus::ErrInvalidParam;

    try {
        *out_ctx = new BridgeContext(*config);
        return BridgeStatus::Ok;
    } catch (const std::bad_alloc&) {
        return BridgeStatus::ErrOutOfMemory;
    }
}

BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count) {
    if (!ctx || !input || !out_buf || !out_count) return BridgeStatus::ErrNullPtr;
    if (count == 0) return BridgeStatus::ErrInvalidParam;

    float* processed = static_cast<float*>(std::malloc(sizeof(float) * count));
    if (!processed) return BridgeStatus::ErrOutOfMemory;

    const double factor = ctx->accumulated_scale;
    for (size_t i = 0; i < count; ++i) {
        processed[i] = static_cast<float>(input[i] * factor);
    }

    *out_buf = processed;
    *out_count = count;
    return BridgeStatus::Ok;
}

BRIDGE_API void bridge_free_buffer(float *buf) {
    std::free(buf);
}

BRIDGE_API void bridge_free_context(BridgeContext *ctx) {
    delete ctx;
}

BRIDGE_API const char* bridge_get_last_error(BridgeStatus status) {
    switch (status) {
        case BridgeStatus::Ok:              return "Успішне виконання";
        case BridgeStatus::ErrNullPtr:      return "Передано нульовий покажчик";
        case BridgeStatus::ErrInvalidParam: return "Некоректні вхідні параметри";
        case BridgeStatus::ErrOutOfMemory:  return "Недостатньо системної пам'яті";
        case BridgeStatus::ErrComputation:  return "Помилка обчислень";
        default:                            return "Невідомий код помилки";
    }
}

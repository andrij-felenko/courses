// Заголовний файл library.hpp
#pragma once
#include <cstddef>

extern "C" {
    struct EngineContext;

    EngineContext* engine_create(int config_flags);
    int            engine_process(EngineContext *ctx, const double *data, size_t len);
    void           engine_destroy(EngineContext *ctx);
}

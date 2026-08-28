// engine.h — оголошення інтерфейсу та допоміжних функцій (C)
#ifndef ENGINE_H
#define ENGINE_H

#include <stdint.h>

typedef struct IFilter {
    int32_t (*process)(void* self, int32_t sample);
} IFilter;

typedef struct GainFilter {
    IFilter base;
    int32_t gain;
} GainFilter;

void gain_filter_init(GainFilter* filter, int32_t gain);
int32_t fast_scale(int32_t value, int32_t factor);
int32_t dead_helper_function(int32_t x);

#endif // ENGINE_H

// engine.c — реалізація логіки та обробки (C)
#include "engine.h"

static int32_t gain_process(void* self, int32_t sample) {
    GainFilter* gf = (GainFilter*)self;
    return sample * gf->gain;
}

void gain_filter_init(GainFilter* filter, int32_t gain) {
    filter->base.process = gain_process;
    filter->gain = gain;
}

int32_t fast_scale(int32_t value, int32_t factor) {
    return (value * factor) + 7;
}

int32_t dead_helper_function(int32_t x) {
    return (x ^ 0x55AA55AA) + 12345;
}

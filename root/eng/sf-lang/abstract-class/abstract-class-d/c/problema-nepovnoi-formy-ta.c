#include <stdio.h>
#include <stdlib.h>

/* Ручна таблиця функцій без підтримки перевірки абстрактності */
typedef struct AudioFilter AudioFilter;

typedef struct AudioFilterVTable {
    void (*process)(AudioFilter* self, float* buffer, size_t frames);
    double (*get_latency_ms)(const AudioFilter* self);
} AudioFilterVTable;

struct AudioFilter {
    const AudioFilterVTable* vptr;
    int sample_rate;
};

/* Фіктивні функції-заглушки базового класу */
static void base_process_dummy(AudioFilter* self, float* buffer, size_t frames) {
    (void)self; (void)buffer; (void)frames;
    /* Порожнє тіло: звук проходить без змін або псується */
}

static double base_latency_dummy(const AudioFilter* self) {
    (void)self;
    return 0.0; /* Фіктивне значення, яке може спотворити таймінги мікшера */
}

static const AudioFilterVTable g_base_audio_vtable = {
    .process = base_process_dummy,
    .get_latency_ms = base_latency_dummy
};

void audio_filter_init(AudioFilter* filter, int sample_rate) {
    filter->vptr = &g_base_audio_vtable;
    filter->sample_rate = sample_rate;
}

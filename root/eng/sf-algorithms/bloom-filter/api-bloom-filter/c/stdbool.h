#include <stdbool.h>
#include <stddef.h>

typedef struct {
    bloom_filter_t *layers;
    size_t num_layers;
    double target_fp_rate;
} scalable_bloom_filter_t;

void scalable_bloom_add(scalable_bloom_filter_t *sbf, const void *key, size_t len);
bool scalable_bloom_contains(const scalable_bloom_filter_t *sbf, const void *key, size_t len);

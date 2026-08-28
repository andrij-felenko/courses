#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

typedef enum {
    GROWTH_GEOMETRIC_2_0,
    GROWTH_GEOMETRIC_1_5,
    GROWTH_LINEAR_FIXED
} GrowthPolicy;

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
    GrowthPolicy policy;
    size_t linear_step;
    size_t realloc_count;
    size_t copied_elements_total;
} OverBufferC;

OverBufferC* over_buffer_create(size_t initial_cap, GrowthPolicy policy, size_t linear_step) {
    OverBufferC *buf = (OverBufferC*)malloc(sizeof(OverBufferC));
    if (!buf) return NULL;

    buf->size = 0;
    buf->capacity = initial_cap > 0 ? initial_cap : 1;
    buf->policy = policy;
    buf->linear_step = linear_step > 0 ? linear_step : 64;
    buf->realloc_count = 0;
    buf->copied_elements_total = 0;

    buf->data = (int*)malloc(buf->capacity * sizeof(int));
    if (!buf->data) {
        free(buf);
        return NULL;
    }
    return buf;
}

void over_buffer_destroy(OverBufferC *buf) {
    if (buf) {
        free(buf->data);
        free(buf);
    }
}

static size_t compute_next_capacity(OverBufferC *buf) {
    switch (buf->policy) {
        case GROWTH_GEOMETRIC_2_0:
            return buf->capacity * 2;
        case GROWTH_GEOMETRIC_1_5: {
            size_t next_cap = buf->capacity + (buf->capacity >> 1);
            return next_cap > buf->capacity ? next_cap : buf->capacity + 1;
        }
        case GROWTH_LINEAR_FIXED:
            return buf->capacity + buf->linear_step;
    }
    return buf->capacity * 2;
}

bool over_buffer_push(OverBufferC *buf, int val) {
    if (buf->size == buf->capacity) {
        size_t new_cap = compute_next_capacity(buf);
        int *new_data = (int*)realloc(buf->data, new_cap * sizeof(int));
        if (!new_data) return false;

        buf->data = new_data;
        buf->copied_elements_total += buf->size;
        buf->capacity = new_cap;
        buf->realloc_count++;
    }
    buf->data[buf->size++] = val;
    return true;
}

bool over_buffer_pop(OverBufferC *buf, int *out_val) {
    if (buf->size == 0) return false;

    buf->size--;
    if (out_val) *out_val = buf->data[buf->size];

    // Гістерезисне стиснення: зменшення місткості при заповненні <= 25%
    if (buf->size > 0 && buf->size <= buf->capacity / 4 && buf->capacity > 16) {
        size_t new_cap = buf->capacity / 2;
        int *new_data = (int*)realloc(buf->data, new_cap * sizeof(int));
        if (new_data) {
            buf->data = new_data;
            buf->capacity = new_cap;
            buf->realloc_count++;
        }
    }
    return true;
}

void run_c_benchmark(size_t total_ops, GrowthPolicy policy, const char *name) {
    OverBufferC *buf = over_buffer_create(8, policy, 1000);
    if (!buf) return;

    clock_t start = clock();
    for (size_t i = 0; i < total_ops; i++) {
        over_buffer_push(buf, (int)i);
    }
    clock_t end = clock();

    double elapsed_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    printf("[%s] N=%zu | Час: %.2f мс | Реалокацій: %zu | Копіювань: %zu | Співвідношення копій/N: %.2f\n",
           name, total_ops, elapsed_ms, buf->realloc_count,
           buf->copied_elements_total, (double)buf->copied_elements_total / total_ops);

    over_buffer_destroy(buf);
}

int main(void) {
    size_t N = 100000;
    printf("=== Бенчмарк режимів розширення пам'яті (C) ===\n");
    run_c_benchmark(N, GROWTH_GEOMETRIC_2_0, "Геометричний x2.0");
    run_c_benchmark(N, GROWTH_GEOMETRIC_1_5, "Геометричний x1.5");
    run_c_benchmark(N, GROWTH_LINEAR_FIXED, "Лінійний +1000  ");
    return 0;
}

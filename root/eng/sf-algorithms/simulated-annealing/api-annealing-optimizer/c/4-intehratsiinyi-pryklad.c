#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    const int64_t* values;
    size_t count;
    int64_t total_sum;
} partition_context_t;

typedef struct {
    bool* in_set1;
} partition_state_t;

typedef struct {
    size_t flip_index;
} partition_move_t;

static double part_evaluate_full(const void* s, void* ctx) {
    const partition_state_t* state = (const partition_state_t*)s;
    const partition_context_t* context = (const partition_context_t*)ctx;
    int64_t sum1 = 0;
    for (size_t i = 0; i < context->count; ++i) {
        if (state->in_set1[i]) sum1 += context->values[i];
    }
    int64_t sum2 = context->total_sum - sum1;
    return (double)llabs(sum1 - sum2);
}

static void part_propose_move(const void* s, void* move_out, sa_rng_t* rng, void* ctx) {
    (void)s;
    const partition_context_t* context = (const partition_context_t*)ctx;
    partition_move_t* move = (partition_move_t*)move_out;
    move->flip_index = (size_t)(sa_rng_next64(rng) % context->count);
}

static double part_evaluate_delta(const void* s, const void* m, void* ctx) {
    const partition_state_t* state = (const partition_state_t*)s;
    const partition_move_t* move = (const partition_move_t*)m;
    const partition_context_t* context = (const partition_context_t*)ctx;

    int64_t val = context->values[move->flip_index];
    int64_t current_sum1 = 0;
    for (size_t i = 0; i < context->count; ++i) {
        if (state->in_set1[i]) current_sum1 += context->values[i];
    }
    int64_t current_sum2 = context->total_sum - current_sum1;
    double current_diff = (double)llabs(current_sum1 - current_sum2);

    int64_t next_sum1 = state->in_set1[move->flip_index] ? (current_sum1 - val) : (current_sum1 + val);
    int64_t next_sum2 = context->total_sum - next_sum1;
    double next_diff = (double)llabs(next_sum1 - next_sum2);

    return next_diff - current_diff;
}

static void part_apply_move(void* s, const void* m, void* ctx) {
    (void)ctx;
    partition_state_t* state = (partition_state_t*)s;
    const partition_move_t* move = (const partition_move_t*)m;
    state->in_set1[move->flip_index] = !state->in_set1[move->flip_index];
}

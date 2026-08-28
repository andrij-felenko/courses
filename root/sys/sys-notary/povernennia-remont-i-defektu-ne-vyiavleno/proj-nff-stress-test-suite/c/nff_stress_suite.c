/* nff_stress_suite.c - C99 реалізація логіки виявлення дефектів */
#include "nff_stress_suite.h"
#include <string.h>
#include <stdio.h>

/* Лінійний конгруентний генератор / PRBS-31 */
static uint32_t prbs31_step(uint32_t *state) {
    uint32_t b31 = (*state >> 30) & 1U;
    uint32_t b28 = (*state >> 27) & 1U;
    uint32_t new_bit = b31 ^ b28;
    *state = ((*state << 1U) | new_bit) & 0x7FFFFFFFU;
    return *state;
}

void nff_suite_init(stress_suite_context_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(stress_suite_context_t));
    ctx->prbs_state = 0x5A5A5A5AU;
}

static void log_error(stress_suite_context_t *ctx, uint32_t offset, uint32_t expected,
                      uint32_t actual, stress_pattern_type_t pattern, uint32_t time_ms) {
    ctx->stats.error_count++;

    uint32_t diff = expected ^ actual;
    if ((actual & diff) == diff) {
        ctx->stats.stuck_at_ones++;
    } else if ((~actual & diff) == diff) {
        ctx->stats.stuck_at_zeros++;
    } else {
        ctx->stats.bridge_faults++;
    }

    if (ctx->stats.error_count <= NFF_MAX_ERROR_LOG_ENTRIES) {
        size_t idx = ctx->stats.error_count - 1U;
        ctx->error_log[idx].timestamp_ms = time_ms;
        ctx->error_log[idx].memory_offset = offset;
        ctx->error_log[idx].expected_val = expected;
        ctx->error_log[idx].actual_val = actual;
        ctx->error_log[idx].xor_diff = diff;
        ctx->error_log[idx].pattern_type = (uint8_t)pattern;
    }
}

static void run_checkerboard(stress_suite_context_t *ctx, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    const uint32_t p1 = 0x55555555U;
    const uint32_t p2 = 0xAAAAAAAAU;

    /* Фаза 1: Прямий запис */
    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = (i & 1U) ? p1 : p2;
    }
    /* Фаза 2: Верифікація */
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = (i & 1U) ? p1 : p2;
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_CHECKERBOARD, time_ms);
        }
    }
    /* Фаза 3: Інверсний запис */
    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = (i & 1U) ? p2 : p1;
    }
    /* Фаза 4: Інверсна верифікація */
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = (i & 1U) ? p2 : p1;
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_CHECKERBOARD, time_ms);
        }
    }
    ctx->stats.total_words_tested += (word_count * 2U);
}

static void run_walking_bits(stress_suite_context_t *ctx, bool zeros, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    stress_pattern_type_t p_type = zeros ? PATTERN_WALKING_ZEROS : PATTERN_WALKING_ONES;

    for (uint8_t bit = 0; bit < 32; ++bit) {
        uint32_t val = zeros ? ~(1U << bit) : (1U << bit);
        for (size_t i = 0; i < word_count; ++i) {
            ctx->buffer[i] = val;
        }
        for (size_t i = 0; i < word_count; ++i) {
            uint32_t actual = ctx->buffer[i];
            if (actual != val) {
                log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), val, actual, p_type, time_ms);
            }
        }
    }
    ctx->stats.total_words_tested += (word_count * 32U);
}

static void run_bus_inversion(stress_suite_context_t *ctx, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
    }
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_BUS_INVERSION, time_ms);
        }
    }
    ctx->stats.total_words_tested += word_count;
}

static void run_prbs_stress(stress_suite_context_t *ctx, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    uint32_t seed = ctx->prbs_state;

    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = prbs31_step(&seed);
    }
    seed = ctx->prbs_state;
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = prbs31_step(&seed);
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_PRBS31_RANDOM, time_ms);
        }
    }
    ctx->prbs_state = seed;
    ctx->stats.total_words_tested += word_count;
}

bool nff_suite_run_cycle(stress_suite_context_t *ctx, uint32_t current_time_ms) {
    if (!ctx) return false;

    if (ctx->stats.total_cycles == 0) {
        ctx->start_time_ms = current_time_ms;
    }

    run_checkerboard(ctx, current_time_ms);
    run_walking_bits(ctx, false, current_time_ms);
    run_walking_bits(ctx, true, current_time_ms);
    run_bus_inversion(ctx, current_time_ms);
    run_prbs_stress(ctx, current_time_ms);

    ctx->stats.total_cycles++;
    ctx->stats.duration_ms = current_time_ms - ctx->start_time_ms;

    return (ctx->stats.error_count == 0);
}

uint32_t nff_suite_get_error_count(const stress_suite_context_t *ctx) {
    return ctx ? ctx->stats.error_count : 0U;
}

void nff_suite_generate_report(const stress_suite_context_t *ctx, char *out_buffer, size_t max_len) {
    if (!ctx || !out_buffer || max_len == 0) return;

    snprintf(out_buffer, max_len,
             "--- NFF STRESS TEST SUITE REPORT ---\n"
             "Total Cycles: %llu\n"
             "Words Tested: %llu\n"
             "Duration:     %u ms\n"
             "Total Errors: %u\n"
             "  Stuck-At-1: %u\n"
             "  Stuck-At-0: %u\n"
             "  Bridge/Noise: %u\n"
             "VERDICT:      %s\n",
             (unsigned long long)ctx->stats.total_cycles,
             (unsigned long long)ctx->stats.total_words_tested,
             ctx->stats.duration_ms,
             ctx->stats.error_count,
             ctx->stats.stuck_at_ones,
             ctx->stats.stuck_at_zeros,
             ctx->stats.bridge_faults,
             (ctx->stats.error_count == 0) ? "PASS (No Intermittent Faults Detected)" : "FAIL (Hardware Anomaly Captured)");
}

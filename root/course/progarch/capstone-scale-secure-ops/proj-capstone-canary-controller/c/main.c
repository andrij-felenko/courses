#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    CANARY_CONTINUE = 0,
    CANARY_PROMOTE = 1,
    CANARY_ROLLBACK_BURN_RATE = 2,
    CANARY_ROLLBACK_LATENCY = 3,
    CANARY_ERROR_INVALID_CONFIG = -1
} canary_decision_t;

typedef struct {
    uint64_t total_requests;
    uint64_t error_requests;
    double latency_p99_ms;
} window_metrics_t;

typedef struct {
    window_metrics_t short_window;
    window_metrics_t long_window;
} canary_sample_t;

typedef struct {
    double target_slo;
    double max_burn_rate_short;
    double max_burn_rate_long;
    double max_latency_ratio;
    uint64_t min_sample_requests;
} system_config_t;

static double calculate_error_rate(const window_metrics_t* m) {
    if (m->total_requests == 0) return 0.0;
    return (double)m->error_requests / (double)m->total_requests;
}

canary_decision_t evaluate_canary(
    const system_config_t* config,
    const canary_sample_t* baseline,
    const canary_sample_t* canary)
{
    if (!config || !baseline || !canary) return CANARY_ERROR_INVALID_CONFIG;
    if (canary->short_window.total_requests < config->min_sample_requests) {
        return CANARY_CONTINUE;
    }

    double e_slo = 1.0 - config->target_slo;
    if (e_slo <= 0.0) return CANARY_ERROR_INVALID_CONFIG;

    double canary_err_short = calculate_error_rate(&canary->short_window);
    double canary_err_long  = calculate_error_rate(&canary->long_window);

    double burn_short = canary_err_short / e_slo;
    double burn_long  = canary_err_long / e_slo;

    if (burn_short >= config->max_burn_rate_short && burn_long >= config->max_burn_rate_long) {
        return CANARY_ROLLBACK_BURN_RATE;
    }

    if (baseline->short_window.latency_p99_ms > 0.0) {
        double ratio = canary->short_window.latency_p99_ms / baseline->short_window.latency_p99_ms;
        if (ratio > config->max_latency_ratio) {
            return CANARY_ROLLBACK_LATENCY;
        }
    }

    return CANARY_CONTINUE;
}

int main(void) {
    system_config_t cfg = {
        .target_slo = 0.9999,
        .max_burn_rate_short = 14.4,
        .max_burn_rate_long = 14.4,
        .max_latency_ratio = 1.25,
        .min_sample_requests = 1000
    };

    canary_sample_t baseline = {
        .short_window = {50000, 1, 45.0},
        .long_window  = {600000, 10, 44.0}
    };

    canary_sample_t bad_canary = {
        .short_window = {5000, 25, 48.0},
        .long_window  = {10000, 50, 47.0}
    };

    canary_decision_t res = evaluate_canary(&cfg, &baseline, &bad_canary);
    if (res == CANARY_ROLLBACK_ROLLBACK_BURN_RATE || res == CANARY_ROLLBACK_BURN_RATE) {
        printf("[CRITICAL] Canary Rollback Triggered: Burn Rate Exceeded!\n");
    }
    return 0;
}

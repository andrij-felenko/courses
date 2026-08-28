#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_TIERS 4

typedef enum {
    COST_TIER_LIGHT = 0,    // Просте читання з кешу
    COST_TIER_MEDIUM = 1,   // Запит до бази даних
    COST_TIER_HEAVY = 2,    // Складна аналітика / транзакція
    COST_TIER_GPU = 3       // ML-інференс / GPU
} ResourceCostTier;

typedef struct {
    double cpu_cost_per_ms;
    double storage_cost_per_op;
    double net_cost_per_byte;
    double max_budget_per_sec;
    double degradation_threshold; // Поріг деградації (наприклад 0.80 = 80%)
} CostModelConfig;

typedef struct {
    CostModelConfig config;
    double current_spent_sec;
    uint64_t total_requests;
    uint64_t rejected_requests;
    uint64_t degraded_requests;
} CostLimiter;

static const double TIER_BASE_COSTS[MAX_TIERS] = {
    0.0001,   // LIGHT: $0.0001
    0.0010,   // MEDIUM: $0.001
    0.0100,   // HEAVY: $0.01
    0.0500    // GPU: $0.05
};

void cost_limiter_init(CostLimiter *limiter, double max_budget_per_sec) {
    if (!limiter) return;
    limiter->config.cpu_cost_per_ms = 0.00002;
    limiter->config.storage_cost_per_op = 0.0001;
    limiter->config.net_cost_per_byte = 0.00000005;
    limiter->config.max_budget_per_sec = max_budget_per_sec;
    limiter->config.degradation_threshold = 0.80; // 80% бюджету
    limiter->current_spent_sec = 0.0;
    limiter->total_requests = 0;
    limiter->rejected_requests = 0;
    limiter->degraded_requests = 0;
}

double cost_limiter_calculate_cost(const CostLimiter *limiter, ResourceCostTier tier,
                                   uint32_t cpu_time_ms, uint32_t storage_ops, uint32_t net_bytes) {
    if (!limiter || tier >= MAX_TIERS) return 0.0;
    
    double base_cost = TIER_BASE_COSTS[tier];
    double variable_cost = (cpu_time_ms * limiter->config.cpu_cost_per_ms) +
                           (storage_ops * limiter->config.storage_cost_per_op) +
                           (net_bytes * limiter->config.net_cost_per_byte);
    return base_cost + variable_cost;
}

bool cost_limiter_try_consume(CostLimiter *limiter, ResourceCostTier tier,
                              uint32_t cpu_time_ms, uint32_t storage_ops, uint32_t net_bytes,
                              double *out_cost, bool *out_degraded) {
    if (!limiter) return false;
    
    limiter->total_requests++;
    double cost = cost_limiter_calculate_cost(limiter, tier, cpu_time_ms, storage_ops, net_bytes);
    double budget = limiter->config.max_budget_per_sec;
    double spent_ratio = limiter->current_spent_sec / budget;

    // Якщо спожито понад 80% бюджету, відхиляємо важкі та GPU запити
    if (spent_ratio >= limiter->config.degradation_threshold && (tier == COST_TIER_HEAVY || tier == COST_TIER_GPU)) {
        limiter->degraded_requests++;
        limiter->rejected_requests++;
        if (out_cost) *out_cost = cost;
        if (out_degraded) *out_degraded = true;
        return false;
    }

    if (limiter->current_spent_sec + cost > budget) {
        limiter->rejected_requests++;
        if (out_cost) *out_cost = cost;
        if (out_degraded) *out_degraded = false;
        return false;
    }
    
    limiter->current_spent_sec += cost;
    if (out_cost) *out_cost = cost;
    if (out_degraded) *out_degraded = false;
    return true;
}

void cost_limiter_reset_window(CostLimiter *limiter) {
    if (limiter) {
        limiter->current_spent_sec = 0.0;
    }
}

int main(void) {
    CostLimiter limiter;
    cost_limiter_init(&limiter, 0.10); // Бюджет $0.10 на секунду

    printf("=== Cost-Aware Infrastructure Allocator (C) ===\n");

    for (int i = 1; i <= 6; i++) {
        double cost = 0.0;
        bool degraded = false;
        bool allowed = cost_limiter_try_consume(&limiter, COST_TIER_HEAVY, 15, 2, 4096, &cost, &degraded);
        printf("Request #%d [HEAVY]: Allowed=%s, Degraded=%s, Cost=$%.5f, TotalSpent=$%.5f\n",
               i, allowed ? "YES" : "NO ", degraded ? "YES" : "NO ", cost, limiter.current_spent_sec);
    }

    printf("Summary: Total=%lu, Rejected=%lu, Degraded=%lu\n",
           (unsigned long)limiter.total_requests,
           (unsigned long)limiter.rejected_requests,
           (unsigned long)limiter.degraded_requests);

    return 0;
}

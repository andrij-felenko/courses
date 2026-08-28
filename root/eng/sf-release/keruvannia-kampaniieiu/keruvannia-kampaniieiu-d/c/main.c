#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint32_t succeeded;
    uint32_t failed;
    uint32_t rolled_back;
    uint32_t silenced;
} WaveMetrics;

typedef struct {
    uint32_t min_sample_size;
    double max_fail_rate_pct;
    double max_rollback_rate_pct;
    double max_silence_rate_pct;
} ArbitrageThresholds;

bool check_stop_the_line_trigger(const WaveMetrics *m, const ArbitrageThresholds *t) {
    uint32_t total_evaluated = m->succeeded + m->failed + m->rolled_back + m->silenced;
    
    // Захист від передчасного спрацьовування на малій вибірці
    if (total_evaluated < t->min_sample_size) {
        return false;
    }

    double fail_rate = ((double)m->failed / total_evaluated) * 100.0;
    double rb_rate = ((double)m->rolled_back / total_evaluated) * 100.0;
    double silence_rate = ((double)m->silenced / total_evaluated) * 100.0;

    if (fail_rate > t->max_fail_rate_pct) {
        printf("[ALARM] Перевищено поріг відмов: %.2f%% > %.2f%%\n", fail_rate, t->max_fail_rate_pct);
        return true;
    }
    if (rb_rate > t->max_rollback_rate_pct) {
        printf("[ALARM] Перевищено поріг відкатів A/B: %.2f%% > %.2f%%\n", rb_rate, t->max_rollback_rate_pct);
        return true;
    }
    if (silence_rate > t->max_silence_rate_pct) {
        printf("[CRITICAL] Перевищено поріг замовклих пристроїв: %.2f%% > %.2f%%\n", silence_rate, t->max_silence_rate_pct);
        return true;
    }

    return false;
}

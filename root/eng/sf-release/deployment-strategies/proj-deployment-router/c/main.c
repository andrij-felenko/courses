#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define METRIC_SLOTS 10
#define SLOT_DURATION_SEC 1

typedef enum {
    CANARY_STATE_INACTIVE,
    CANARY_STATE_ACTIVE,
    CANARY_STATE_ROLLED_BACK,
    CANARY_STATE_PROMOTED
} CanaryState;

typedef enum {
    TARGET_BASELINE,
    TARGET_CANARY
} RoutingTarget;

typedef struct {
    uint64_t timestamp_sec;
    uint32_t total_requests;
    uint32_t error_requests;
} MetricSlot;

typedef struct {
    char baseline_addr[64];
    char canary_addr[64];
    uint32_t canary_weight_pct;      /* від 0 до 100 */
    double max_allowed_error_rate;    /* поріг помилок, наприклад 0.02 (2%) */
    uint32_t min_sample_size;         /* мінімальна вибірка для аналізу */
    CanaryState state;
    MetricSlot canary_slots[METRIC_SLOTS];
    size_t current_slot_idx;
    uint64_t last_slot_rotation_sec;
} DeploymentRouter;

static uint64_t get_current_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec;
}

void router_init(DeploymentRouter *r, const char *baseline, const char *canary,
                 uint32_t initial_weight, double max_err_rate, uint32_t min_samples) {
    memset(r, 0, sizeof(DeploymentRouter));
    strncpy(r->baseline_addr, baseline, sizeof(r->baseline_addr) - 1);
    strncpy(r->canary_addr, canary, sizeof(r->canary_addr) - 1);
    r->canary_weight_pct = (initial_weight <= 100) ? initial_weight : 0;
    r->max_allowed_error_rate = max_err_rate;
    r->min_sample_size = min_samples;
    r->state = (initial_weight > 0) ? CANARY_STATE_ACTIVE : CANARY_STATE_INACTIVE;
    r->last_slot_rotation_sec = get_current_time_sec();
}

static void router_rotate_slots_if_needed(DeploymentRouter *r, uint64_t now_sec) {
    uint64_t elapsed = now_sec - r->last_slot_rotation_sec;
    if (elapsed >= SLOT_DURATION_SEC) {
        uint64_t steps = elapsed / SLOT_DURATION_SEC;
        if (steps > METRIC_SLOTS) {
            steps = METRIC_SLOTS;
        }
        for (uint64_t i = 0; i < steps; ++i) {
            r->current_slot_idx = (r->current_slot_idx + 1) % METRIC_SLOTS;
            r->canary_slots[r->current_slot_idx].timestamp_sec = now_sec;
            r->canary_slots[r->current_slot_idx].total_requests = 0;
            r->canary_slots[r->current_slot_idx].error_requests = 0;
        }
        r->last_slot_rotation_sec = now_sec;
    }
}

RoutingTarget router_select_target(DeploymentRouter *r) {
    if (r->state != CANARY_STATE_ACTIVE || r->canary_weight_pct == 0) {
        return TARGET_BASELINE;
    }
    uint32_t roll = (uint32_t)(rand() % 100);
    if (roll < r->canary_weight_pct) {
        return TARGET_CANARY;
    }
    return TARGET_BASELINE;
}

void router_record_result(DeploymentRouter *r, RoutingTarget target, bool is_error) {
    if (target != TARGET_CANARY || r->state != CANARY_STATE_ACTIVE) {
        return;
    }

    uint64_t now_sec = get_current_time_sec();
    router_rotate_slots_if_needed(r, now_sec);

    MetricSlot *slot = &r->canary_slots[r->current_slot_idx];
    slot->total_requests++;
    if (is_error) {
        slot->error_requests++;
    }

    /* Агрегація метрик у межах активного ковзного вікна */
    uint32_t window_total = 0;
    uint32_t window_errors = 0;

    for (size_t i = 0; i < METRIC_SLOTS; ++i) {
        if (now_sec - r->canary_slots[i].timestamp_sec <= (METRIC_SLOTS * SLOT_DURATION_SEC)) {
            window_total += r->canary_slots[i].total_requests;
            window_errors += r->canary_slots[i].error_requests;
        }
    }

    /* Перевірка критерію аварійного відкочування */
    if (window_total >= r->min_sample_size) {
        double current_err_rate = (double)window_errors / (double)window_total;
        if (current_err_rate > r->max_allowed_error_rate) {
            r->state = CANARY_STATE_ROLLED_BACK;
            r->canary_weight_pct = 0;
            fprintf(stderr, "[АЛЕРТ] Аварійний відкіт канарки! Помилки: %.2f%% (поріг %.2f%%, вибірка %u)\n",
                    current_err_rate * 100.0, r->max_allowed_error_rate * 100.0, window_total);
        }
    }
}

void router_set_weight(DeploymentRouter *r, uint32_t new_weight) {
    if (r->state == CANARY_STATE_ROLLED_BACK) {
        fprintf(stderr, "[ПОПЕРЕДЖЕННЯ] Неможливо змінити вагу: канарка у стані відкочування.\n");
        return;
    }
    r->canary_weight_pct = (new_weight <= 100) ? new_weight : 100;
    r->state = (r->canary_weight_pct > 0) ? CANARY_STATE_ACTIVE : CANARY_STATE_INACTIVE;
    printf("[ІНФО] Встановлено нову вагу канарки: %u%%\n", r->canary_weight_pct);
}

void router_promote(DeploymentRouter *r) {
    r->state = CANARY_STATE_PROMOTED;
    r->canary_weight_pct = 100;
    printf("[ІНФО] Канарку успішно підвищено до 100%% основного трафіку.\n");
}

int main(void) {
    srand((unsigned int)time(NULL));
    DeploymentRouter router;
    router_init(&router, "10.0.0.1:8080", "10.0.0.2:8080", 20, 0.05, 50);

    printf("Ініціалізація маршрутизатора: Baseline=%s, Canary=%s (Вага=%u%%)\n",
           router.baseline_addr, router.canary_addr, router.canary_weight_pct);

    /* Симуляція живого потоку запитів */
    for (int i = 1; i <= 200; ++i) {
        RoutingTarget tgt = router_select_target(&router);
        bool is_err = false;

        if (tgt == TARGET_CANARY) {
            /* Симулюємо сплеск помилок на канарковому вузлі після 30 запитів */
            if (i > 30 && (rand() % 100 < 25)) {
                is_err = true;
            }
            router_record_result(&router, tgt, is_err);
        }

        if (router.state == CANARY_STATE_ROLLED_BACK) {
            printf("Запит #%d: Трафік на канарку повністю перекрито.\n", i);
            break;
        }
    }

    return 0;
}

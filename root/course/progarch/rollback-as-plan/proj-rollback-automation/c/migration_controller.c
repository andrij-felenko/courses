/* migration_controller.c - POSIX C реалізація контролера відкату */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

typedef enum {
    STATE_IDLE,
    STATE_SCHEMA_EXPANDING,
    STATE_CANARY_MONITORING,
    STATE_ROLLBACK_TRAFFIC,
    STATE_ROLLBACK_SCHEMA,
    STATE_SCHEMA_CONTRACTING,
    STATE_COMPLETED,
    STATE_FAILED
} migration_state_t;

typedef struct {
    double max_p99_latency_ms;
    double max_error_rate_pct;
    uint32_t monitoring_window_sec;
} slo_config_t;

typedef struct {
    double current_p99_ms;
    double current_error_rate_pct;
    uint64_t total_requests;
} telemetry_metrics_t;

typedef struct {
    migration_state_t state;
    slo_config_t slo;
    char version_v1[32];
    char version_v2[32];
    bool schema_is_reversible;
    time_t state_entered_at;
} migration_controller_t;

/* Ініціалізація контролера міграцій */
void controller_init(migration_controller_t *ctrl, const char *v1, const char *v2, slo_config_t slo) {
    if (!ctrl) return;
    memset(ctrl, 0, sizeof(migration_controller_t));
    ctrl->state = STATE_IDLE;
    ctrl->slo = slo;
    snprintf(ctrl->version_v1, sizeof(ctrl->version_v1), "%s", v1);
    snprintf(ctrl->version_v2, sizeof(ctrl->version_v2), "%s", v2);
    ctrl->schema_is_reversible = true;
    ctrl->state_entered_at = time(NULL);
}

/* Імітація виконання DDL Фази 1 (Expand) */
bool execute_schema_expand(migration_controller_t *ctrl) {
    printf("[DDL EXPAND] Додавання колонки `tax_id` (NULLABLE) та тригера дзеркалювання...\n");
    ctrl->state = STATE_SCHEMA_EXPANDING;
    ctrl->state_entered_at = time(NULL);
    /* Імітація успішного створення зворотної схеми */
    ctrl->schema_is_reversible = true;
    printf("[DDL EXPAND] Схема розширена. Стан: REVERSIBLE.\n");
    return true;
}

/* Оцінка метрик спостережуваності */
bool evaluate_telemetry(const slo_config_t *slo, const telemetry_metrics_t *metrics) {
    if (metrics->current_p99_ms > slo->max_p99_latency_ms) {
        printf("[SLO BREACH] P99 Latency %.2f ms перевищує ліміт %.2f ms!\n",
               metrics->current_p99_ms, slo->max_p99_latency_ms);
        return false;
    }
    if (metrics->current_error_rate_pct > slo->max_error_rate_pct) {
        printf("[SLO BREACH] Error Rate %.2f%% перевищує ліміт %.2f%%!\n",
               metrics->current_error_rate_pct, slo->max_error_rate_pct);
        return false;
    }
    return true;
}

/* Виконання автоматичного відкату трафіку */
void execute_traffic_rollback(migration_controller_t *ctrl) {
    ctrl->state = STATE_ROLLBACK_TRAFFIC;
    printf("[ROLLBACK] 🚨 ІНІЦІЙОВАНО АВТОМАТИЧНИЙ ВІДКАТ!\n");
    printf("[ROLLBACK] Перемикання 100%% трафіку назад на версію: %s\n", ctrl->version_v1);
    printf("[ROLLBACK] Вимкнення Feature-Flag `enable_v2_checkout` -> OFF\n");
    
    if (ctrl->schema_is_reversible) {
        ctrl->state = STATE_ROLLBACK_SCHEMA;
        printf("[ROLLBACK] Схема даних залишається у фазі EXPAND. Втрати даних немає.\n");
    } else {
        printf("[CRITICAL] Схема не була позначена як REVERSIBLE! Потрібен Forward-Fix.\n");
    }
    ctrl->state = STATE_COMPLETED;
}

/* Головний цикл оркестрації розгортання */
bool run_deployment_cycle(migration_controller_t *ctrl, telemetry_metrics_t telemetry_samples[], size_t sample_count) {
    if (!execute_schema_expand(ctrl)) {
        ctrl->state = STATE_FAILED;
        return false;
    }

    ctrl->state = STATE_CANARY_MONITORING;
    printf("[CANARY] Запуск канарейки v2 (%s). Початок моніторингу...\n", ctrl->version_v2);

    for (size_t i = 0; i < sample_count; i++) {
        printf("[MONITORING] Замір #%zu: Latency=%.1fms, Errors=%.2f%%\n",
               i + 1, telemetry_samples[i].current_p99_ms, telemetry_samples[i].current_error_rate_pct);

        if (!evaluate_telemetry(&ctrl->slo, &telemetry_samples[i])) {
            execute_traffic_rollback(ctrl);
            return false; /* Відкат успішно виконано */
        }
    }

    printf("[CANARY] Моніторинг успішний. 100%% трафіку переведено на %s.\n", ctrl->version_v2);
    ctrl->state = STATE_SCHEMA_CONTRACTING;
    printf("[DDL CONTRACT] Заплановано видалення застарілих полів через 30 днів.\n");
    ctrl->state = STATE_COMPLETED;
    return true;
}

int main(void) {
    slo_config_t slo = { .max_p99_latency_ms = 150.0, .max_error_rate_pct = 0.5, .monitoring_window_sec = 300 };
    migration_controller_t ctrl;
    controller_init(&ctrl, "v2.1.0", "v2.2.0", slo);

    /* Тестова послідовність вимірів: третій замір містить сплеск помилок */
    telemetry_metrics_t samples[] = {
        { .current_p99_ms = 85.0,  .current_error_rate_pct = 0.01, .total_requests = 10000 },
        { .current_p99_ms = 92.0,  .current_error_rate_pct = 0.05, .total_requests = 12000 },
        { .current_p99_ms = 310.0, .current_error_rate_pct = 2.40, .total_requests = 15000 } /* Збій! */
    };

    printf("=== СТАРТ АВТОМАТИЗОВАНОГО ДЕПЛОЮ ТА ВІДКАТУ ===\n");
    bool result = run_deployment_cycle(&ctrl, samples, sizeof(samples) / sizeof(samples[0]));
    printf("=== ЗАВЕРШЕННЯ ЦИКЛУ: %s ===\n", result ? "SUCCESS" : "ROLLED_BACK");
    return 0;
}

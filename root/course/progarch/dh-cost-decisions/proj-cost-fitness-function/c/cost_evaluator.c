/* cost_evaluator.c — Ядро обчислення unit-cost телеметрії мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define SECONDS_PER_MONTH 2592000.0
#define MQTT_TLS_OVERHEAD_BYTES 78

typedef struct {
    double fleet_size;             /* Кількість будинків (наприклад, 5000000) */
    double broker_price_per_1m;    /* Ціна 1 млн повідомлень брокера ($) */
    double storage_price_per_gb;   /* Ціна 1 GB об'єктного сховища ($) */
    double max_allowed_unit_cost;  /* Максимальний поріг unit-cost ($/дім/міс) */
} CostModelConfig;

typedef struct {
    int sensor_count;
    double sample_interval_sec;
    size_t payload_bytes;
    double delta_filter_ratio;    /* Частка відфільтрованих вимірів (0.0 .. 1.0) */
    int batch_window_sec;
} TelemetrySpec;

typedef struct {
    double monthly_messages_total;
    double monthly_storage_gb;
    double total_monthly_cost;
    double unit_cost_per_home;
    bool is_budget_passed;
} EvaluationResult;

EvaluationResult evaluate_telemetry_cost(const CostModelConfig* config, const TelemetrySpec* spec) {
    EvaluationResult result;
    
    /* Розрахунок ефективної частоти відправки з урахуванням батчингу та дельти */
    double raw_samples_per_month = (SECONDS_PER_MONTH / spec->sample_interval_sec) * spec->sensor_count;
    double passed_samples = raw_samples_per_month * (1.0 - spec->delta_filter_ratio);
    
    /* Кількість батч-пакетів */
    double batches_per_month = (SECONDS_PER_MONTH / spec->batch_window_sec) * spec->sensor_count;
    double total_mqtt_messages_per_home = (passed_samples < batches_per_month) ? passed_samples : batches_per_month;
    
    result.monthly_messages_total = total_mqtt_messages_per_home * config->fleet_size;
    
    /* Розрахунок байтів сховища */
    size_t packet_size = spec->payload_bytes + MQTT_TLS_OVERHEAD_BYTES;
    double total_bytes_per_home = total_mqtt_messages_per_home * packet_size;
    result.monthly_storage_gb = (total_bytes_per_home * config->fleet_size) / (1024.0 * 1024.0 * 1024.0);
    
    /* Фінансовий розрахунок */
    double broker_cost = (result.monthly_messages_total / 1000000.0) * config->broker_price_per_1m;
    double storage_cost = result.monthly_storage_gb * config->storage_price_per_gb;
    
    result.total_monthly_cost = broker_cost + storage_cost;
    result.unit_cost_per_home = result.total_monthly_cost / config->fleet_size;
    result.is_budget_passed = (result.unit_cost_per_home <= config->max_allowed_unit_cost);
    
    return result;
}

int main(int argc, char** argv) {
    CostModelConfig config = {
        .fleet_size = 5000000.0,
        .broker_price_per_1m = 0.05,       /* Self-hosted EMQX amortized cost */
        .storage_price_per_gb = 0.015,     /* Object Storage Parquet tier */
        .max_allowed_unit_cost = 0.015     /* Бюджетний ліміт: $0.015 / дім / міс */
    };
    
    TelemetrySpec spec = {
        .sensor_count = 20,
        .sample_interval_sec = 5.0,
        .payload_bytes = 100,
        .delta_filter_ratio = 0.90,        /* 90% значень відсікаються на хабі */
        .batch_window_sec = 900            /* 15-хвилинне об'єднання */
    };
    
    EvaluationResult res = evaluate_telemetry_cost(&config, &spec);
    
    printf("--- РЕЗУЛЬТАТ ОЦІНКИ ЕКОНОМІКИ ТЕЛЕМЕТРІЇ ---\n");
    printf("Місячна кількість повідомлень: %.0f\n", res.monthly_messages_total);
    printf("Обсяг сховища: %.2f GB / місяць\n", res.monthly_storage_gb);
    printf("Загальні хмарні витрати: $%.2f / місяць\n", res.total_monthly_cost);
    printf("Unit Cost: $%.4f / дім / місяць\n", res.unit_cost_per_home);
    
    if (res.is_budget_passed) {
        printf("[УСПІХ] Бюджет витримано (ліміт $%.3f).\n", config.max_allowed_unit_cost);
        return 0;
    } else {
        printf("[ПОМИЛКА] БЮДЖЕТ ПЕРЕВИЩЕНО! Дозволено: $%.3f, Отримано: $%.4f\n", 
               config.max_allowed_unit_cost, res.unit_cost_per_home);
        return 1;
    }
}

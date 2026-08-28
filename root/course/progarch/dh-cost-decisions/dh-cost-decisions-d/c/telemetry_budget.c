/* telemetry_budget.c — Оцінка бюджетного навантаження телеметрії на мові C */
#include <stdio.h>
#include <stdbool.h>

#define MAX_ALLOWED_UNIT_COST_USD 0.015
#define FLEET_HOMES_COUNT 5000000.0

typedef struct {
    size_t payload_bytes;
    int polling_interval_sec;
    double delta_filter_efficiency;
} TelemetryParam;

bool verify_telemetry_budget(const TelemetryParam* param, double* calculated_unit_cost) {
    /* 2592000 сек у місяці */
    double raw_msgs_per_month = (2592000.0 / param->polling_interval_sec) * 20.0;
    double actual_msgs_per_month = raw_msgs_per_month * (1.0 - param->delta_filter_efficiency);
    
    /* Обчислення витрат на EMQX + S3 Parquet */
    double broker_cost = (actual_msgs_per_month * FLEET_HOMES_COUNT / 1000000.0) * 0.05;
    double storage_gb = (actual_msgs_per_month * (param->payload_bytes + 78) * FLEET_HOMES_COUNT) / (1024.0 * 1024.0 * 1024.0);
    double storage_cost = storage_gb * 0.015;
    
    double total_cost = broker_cost + storage_cost;
    *calculated_unit_cost = total_cost / FLEET_HOMES_COUNT;
    
    return (*calculated_unit_cost <= MAX_ALLOWED_UNIT_COST_USD);
}

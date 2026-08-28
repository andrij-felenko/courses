#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_VEHICLES       64
#define MAX_CLUSTERS       16
#define MAX_ACTIVE_ALERTS  32
#define CLUSTER_RADIUS_PX  45.0f

typedef enum {
    STATUS_NOMINAL  = 0,
    STATUS_ADVISORY = 1,
    STATUS_WARNING  = 2,
    STATUS_CRITICAL = 3
} VehicleStatus;

typedef struct {
    uint8_t id;
    float lat, lon;
    float screen_x, screen_y;
    float battery_pct;
    float speed_mps;
    uint32_t last_heartbeat_ms;
    VehicleStatus status;
    bool active;
} VehicleTelemetry;

typedef struct {
    uint8_t cluster_id;
    uint8_t count;
    float center_x, center_y;
    float avg_speed_mps;
    VehicleStatus worst_status;
    uint8_t member_ids[MAX_VEHICLES];
} ScreenCluster;

typedef struct {
    uint8_t vehicle_id;
    VehicleStatus priority;
    uint32_t timestamp_ms;
    char message[64];
    bool acknowledged;
} FleetAlert;

typedef struct {
    VehicleTelemetry vehicles[MAX_VEHICLES];
    ScreenCluster clusters[MAX_CLUSTERS];
    uint8_t cluster_count;
    FleetAlert alerts[MAX_ACTIVE_ALERTS];
    uint8_t alert_count;
    float current_workload_pct;
} FleetAggregator;

void fleet_init(FleetAggregator *agg) {
    for (int i = 0; i < MAX_VEHICLES; i++) {
        agg->vehicles[i].active = false;
    }
    agg->cluster_count = 0;
    agg->alert_count = 0;
    agg->current_workload_pct = 0.0f;
}

void fleet_update_vehicle(FleetAggregator *agg, uint8_t id, float lat, float lon,
                          float sx, float sy, float batt, float spd, uint32_t now_ms) {
    if (id >= MAX_VEHICLES) return;
    VehicleTelemetry *v = &agg->vehicles[id];
    v->id = id;
    v->lat = lat;
    v->lon = lon;
    v->screen_x = sx;
    v->screen_y = sy;
    v->battery_pct = batt;
    v->speed_mps = spd;
    v->last_heartbeat_ms = now_ms;
    v->active = true;

    // Класифікація статусу за винятком
    if (batt < 15.0f || (now_ms - v->last_heartbeat_ms > 3000)) {
        v->status = STATUS_CRITICAL;
    } else if (batt < 30.0f || (now_ms - v->last_heartbeat_ms > 1500)) {
        v->status = STATUS_WARNING;
    } else if (batt < 45.0f) {
        v->status = STATUS_ADVISORY;
    } else {
        v->status = STATUS_NOMINAL;
    }
}

void fleet_recalculate_clusters(FleetAggregator *agg) {
    agg->cluster_count = 0;
    bool assigned[MAX_VEHICLES] = {false};

    for (int i = 0; i < MAX_VEHICLES; i++) {
        if (!agg->vehicles[i].active || assigned[i]) continue;
        if (agg->cluster_count >= MAX_CLUSTERS) break;

        ScreenCluster *c = &agg->clusters[agg->cluster_count++];
        c->cluster_id = agg->cluster_count;
        c->count = 0;
        c->worst_status = STATUS_NOMINAL;
        float sum_x = 0.0f, sum_y = 0.0f, sum_spd = 0.0f;

        for (int j = i; j < MAX_VEHICLES; j++) {
            if (!agg->vehicles[j].active || assigned[j]) continue;

            float dx = agg->vehicles[i].screen_x - agg->vehicles[j].screen_x;
            float dy = agg->vehicles[i].screen_y - agg->vehicles[j].screen_y;
            float dist = sqrtf(dx * dx + dy * dy);

            if (dist <= CLUSTER_RADIUS_PX || i == j) {
                assigned[j] = true;
                c->member_ids[c->count++] = agg->vehicles[j].id;
                sum_x += agg->vehicles[j].screen_x;
                sum_y += agg->vehicles[j].screen_y;
                sum_spd += agg->vehicles[j].speed_mps;

                // Ескалація за принципом найгіршого стану
                if (agg->vehicles[j].status > c->worst_status) {
                    c->worst_status = agg->vehicles[j].status;
                }
            }
        }
        if (c->count > 0) {
            c->center_x = sum_x / (float)c->count;
            c->center_y = sum_y / (float)c->count;
            c->avg_speed_mps = sum_spd / (float)c->count;
        }
    }
}

void fleet_estimate_workload(FleetAggregator *agg) {
    int active_uavs = 0;
    int critical_events = 0;
    for (int i = 0; i < MAX_VEHICLES; i++) {
        if (agg->vehicles[i].active) {
            active_uavs++;
            if (agg->vehicles[i].status >= STATUS_WARNING) {
                critical_events++;
            }
        }
    }
    // W = базове навантаження рою (1.5% на борт) + навантаження винятків (25% на кожну аварію)
    float base_w = (float)active_uavs * 1.5f;
    float exception_w = (float)critical_events * 25.0f;
    agg->current_workload_pct = base_w + exception_w;
    if (agg->current_workload_pct > 100.0f) {
        agg->current_workload_pct = 100.0f;
    }
}

#include <stdint.h>
#include <stdbool.h>

#define HEALTH_MAX_COMPONENTS 8
#define HEALTH_SCORE_MAX      1000

typedef enum {
    HEALTH_STATE_NOMINAL = 0,
    HEALTH_STATE_DEGRADED,
    HEALTH_STATE_CRITICAL,
    HEALTH_STATE_EMERGENCY
} health_state_t;

typedef uint16_t (*metric_collector_fn)(void *context);

typedef struct {
    const char          *name;
    metric_collector_fn  collector;
    void                *context;
    uint16_t             weight;
    bool                 is_critical;
    uint16_t             smoothed_score; // Q8.8 або [0..1000]
    uint16_t             fault_count;
} health_component_t;

typedef struct {
    health_component_t components[HEALTH_MAX_COMPONENTS];
    uint8_t            component_count;
    uint16_t           system_score;
    health_state_t     current_state;
    uint32_t           last_update_tick;
} health_monitor_t;

static health_monitor_t g_monitor;

void health_monitor_init(void) {
    g_monitor.component_count = 0;
    g_monitor.system_score = HEALTH_SCORE_MAX;
    g_monitor.current_state = HEALTH_STATE_NOMINAL;
    g_monitor.last_update_tick = 0;
}

bool health_monitor_register(const char *name, metric_collector_fn fn, 
                            void *ctx, uint16_t weight, bool is_critical) {
    if (g_monitor.component_count >= HEALTH_MAX_COMPONENTS) {
        return false;
    }
    health_component_t *c = &g_monitor.components[g_monitor.component_count++];
    c->name = name;
    c->collector = fn;
    c->context = ctx;
    c->weight = weight;
    c->is_critical = is_critical;
    c->smoothed_score = HEALTH_SCORE_MAX;
    c->fault_count = 0;
    return true;
}

void health_monitor_step(void) {
    uint32_t weighted_sum = 0;
    uint32_t total_weight = 0;
    bool critical_failure = false;

    for (uint8_t i = 0; i < g_monitor.component_count; ++i) {
        health_component_t *c = &g_monitor.components[i];
        uint16_t raw_score = c->collector ? c->collector(c->context) : 0;
        
        // EWMA фільтрація: H[k] = (raw + 7*H[k-1]) / 8
        c->smoothed_score = (uint16_t)((raw_score + (uint32_t)c->smoothed_score * 7) / 8);
        
        weighted_sum += (uint32_t)c->smoothed_score * c->weight;
        total_weight += c->weight;

        if (c->is_critical && c->smoothed_score < 400) {
            critical_failure = true;
        }
    }

    if (total_weight > 0) {
        g_monitor.system_score = (uint16_t)(weighted_sum / total_weight);
    } else {
        g_monitor.system_score = 0;
    }

    if (critical_failure) {
        g_monitor.system_score = 0;
        g_monitor.current_state = HEALTH_STATE_EMERGENCY;
    } else if (g_monitor.system_score >= 900) {
        g_monitor.current_state = HEALTH_STATE_NOMINAL;
    } else if (g_monitor.system_score >= 700) {
        g_monitor.current_state = HEALTH_STATE_DEGRADED;
    } else if (g_monitor.system_score >= 400) {
        g_monitor.current_state = HEALTH_STATE_CRITICAL;
    } else {
        g_monitor.current_state = HEALTH_STATE_EMERGENCY;
    }
}

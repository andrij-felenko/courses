#ifndef HEALTH_MONITOR_H
#define HEALTH_MONITOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HEALTH_MAX_COMPONENTS       8
#define HEALTH_SCORE_PERFECT        1000
#define HEALTH_CRITICAL_THRESHOLD   400
#define HEALTH_DEGRADED_THRESHOLD   700
#define HEALTH_NOMINAL_THRESHOLD    900
#define HEALTH_WARMUP_TICKS         20

#define HEALTH_BLACKBOX_MAGIC       0xDEADBEEF
#define HEALTH_BLACKBOX_SLOTS       16

typedef enum {
    HEALTH_STATE_NOMINAL = 0,
    HEALTH_STATE_DEGRADED,
    HEALTH_STATE_CRITICAL,
    HEALTH_STATE_EMERGENCY
} health_state_t;

typedef enum {
    HEALTH_BUS_OK = 0,
    HEALTH_BUS_SDA_STUCK_LOW,
    HEALTH_BUS_SCL_STUCK_LOW,
    HEALTH_BUS_TIMEOUT,
    HEALTH_BUS_CRC_ERROR,
    HEALTH_BUS_BUS_OFF
} health_bus_status_t;

typedef uint16_t (*health_collector_fn)(void *user_ctx);

typedef struct {
    const char           *name;
    health_collector_fn   collector;
    void                 *user_ctx;
    uint16_t              weight;
    bool                  is_critical;
    uint16_t              smoothed_score;
    uint32_t              consecutive_failures;
} health_component_desc_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq_num;
    uint64_t timestamp_ms;
    uint16_t system_score;
    uint8_t  system_state;
    uint8_t  fault_component_id;
    uint32_t cfsr_reg;
    uint32_t hfsr_reg;
    uint32_t vdd_mv;
    int16_t  core_temp_c;
    uint16_t min_stack_free_bytes;
    uint32_t crc32;
} health_blackbox_entry_t;

typedef struct {
    health_component_desc_t components[HEALTH_MAX_COMPONENTS];
    uint8_t                 component_count;
    uint16_t                system_score;
    health_state_t          current_state;
    uint32_t                iteration_counter;
    uint32_t                warmup_ticks_left;
    
    // Чорна скринька у статичній або енергонезалежній пам'яті
    health_blackbox_entry_t blackbox_ring[HEALTH_BLACKBOX_SLOTS];
    uint32_t                blackbox_head;
    uint32_t                blackbox_seq;
} health_supervisor_t;

void health_supervisor_init(health_supervisor_t *ctx);
bool health_supervisor_register(health_supervisor_t *ctx,
                                const char *name,
                                health_collector_fn collector,
                                void *user_ctx,
                                uint16_t weight,
                                bool is_critical);

void health_supervisor_tick(health_supervisor_t *ctx, uint64_t timestamp_ms);
void health_supervisor_log_emergency(health_supervisor_t *ctx, 
                                     uint8_t faulty_id, 
                                     uint32_t cfsr, 
                                     uint32_t hfsr,
                                     uint64_t timestamp_ms);

#ifdef __cplusplus
}
#endif

#endif // HEALTH_MONITOR_H

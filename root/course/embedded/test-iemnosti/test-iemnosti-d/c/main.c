/* Обчислення параметрів розряду та кулонометрії (C) */
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint32_t v_cell_mv;
    uint32_t i_load_ma;
    uint64_t accumulated_uas; /* мкА * с */
    uint64_t accumulated_uws; /* мкВт * с */
} discharge_stats_t;

void process_discharge_step(discharge_stats_t *stats, uint32_t v_mv, uint32_t i_ma, uint32_t dt_ms) {
    stats->v_cell_mv = v_mv;
    stats->i_load_ma = i_ma;
    
    /* Інтегрування заряду: I (мА) * 1000 = мкА */
    stats->accumulated_uas += (uint64_t)i_ma * 1000ULL * dt_ms / 1000ULL;
    
    /* Інтегрування енергії: P (мВт) = (V_mv * I_ma) / 1000 */
    uint32_t p_mw = (uint32_t)(((uint64_t)v_mv * i_ma) / 1000ULL);
    stats->accumulated_uws += (uint64_t)p_mw * 1000ULL * dt_ms / 1000ULL;
}

uint32_t get_capacity_mah(const discharge_stats_t *stats) {
    /* 1 мА*год = 3600 мА*с = 3 600 000 мкА*с */
    return (uint32_t)(stats->accumulated_uas / 3600000ULL);
}

uint32_t get_energy_mwh(const discharge_stats_t *stats) {
    /* 1 мВт*год = 3 600 000 мкВт*с */
    return (uint32_t)(stats->accumulated_uws / 3600000ULL);
}

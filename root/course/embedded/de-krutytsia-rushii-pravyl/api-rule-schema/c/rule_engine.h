/*
 * Рушій правил: обчислення умов, виконання дій, програмні таймери,
 * оренда керування від хаба й режим блокування аварії.
 */
#ifndef RULE_ENGINE_H
#define RULE_ENGINE_H

#include "rule_schema.h"

typedef struct {
    bool     armed;
    uint32_t start_ms;
    uint32_t duration_ms;
} soft_timer_t;

typedef struct {
    int32_t           registers[TOTAL_REGISTERS_NUM];
    rule_descriptor_t rules[MAX_RULES_COUNT];
    uint8_t           rule_count;
    soft_timer_t      timers[TIMER_COUNT];
    uint32_t          latched;      /* біт на гніздо: правило зафіксоване */
    uint32_t          fired;        /* біт на гніздо: дія виконана минулого такту */
    bool              remote_inhibited[TOTAL_REGISTERS_NUM];
    bool              emergency;
    bool              fallback;
    uint32_t          hub_lease_ms;
    uint32_t          last_eval_ms;
} rule_engine_t;

void    rule_engine_init(rule_engine_t *e, uint32_t hub_lease_ms, uint32_t now_ms);
void    rule_engine_set_sensor(rule_engine_t *e, uint8_t reg, int32_t value);
int32_t rule_engine_read(const rule_engine_t *e, uint8_t reg);

/* Запис від хаба: давачі — тільки читання, заблоковані регістри відкидаються. */
rule_error_t rule_engine_remote_write(rule_engine_t *e, uint8_t reg, int32_t value);

void rule_engine_hub_heartbeat(rule_engine_t *e, uint32_t now_ms);
void rule_engine_tick(rule_engine_t *e, uint32_t now_ms);
void rule_engine_reset_alarm(rule_engine_t *e);

rule_error_t rule_engine_validate_table(const rule_engine_t *e,
                                        const rule_descriptor_t *table, uint8_t count);
void         rule_engine_commit_table(rule_engine_t *e,
                                      const rule_descriptor_t *table, uint8_t count);

/* Критична секція на час підміни таблиці. На Cortex-M — маска PRIMASK;
   у хостовій збірці прикладу переривань немає, тож заглушка. */
#if defined(__ARM_ARCH) && defined(__GNUC__)
static inline uint32_t rule_critical_enter(void) {
    uint32_t primask;
    __asm volatile("mrs %0, primask" : "=r"(primask));
    __asm volatile("cpsid i" ::: "memory");
    return primask;
}
static inline void rule_critical_exit(uint32_t primask) {
    if ((primask & 1u) == 0u) { __asm volatile("cpsie i" ::: "memory"); }
}
#else
static inline uint32_t rule_critical_enter(void) { return 0u; }
static inline void rule_critical_exit(uint32_t primask) { (void)primask; }
#endif

#endif /* RULE_ENGINE_H */

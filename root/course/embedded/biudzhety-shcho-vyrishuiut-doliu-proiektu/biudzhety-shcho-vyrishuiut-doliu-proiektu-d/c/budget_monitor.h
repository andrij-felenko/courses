#ifndef BUDGET_MONITOR_H
#define BUDGET_MONITOR_H

/*
 * Зведений аудит інженерних бюджетів під час роботи прошивки.
 *
 * Монітор нічого не вимірює сам: він зшиває показання окремих підсистем —
 * вотермарок стеків, кучі, шини живлення, теплової моделі, книги витрат
 * заряду й лічильників критичних секцій — в один вердикт і одну дію.
 * Кожна підсистема лишається придатною до вжитку окремо.
 */

#include "budget_types.h"
#include "energy_ledger.h"
#include "flash_budget.h"
#include "mem_pool.h"
#include "rail_monitor.h"
#include "section_timer.h"
#include "stack_guard.h"
#include "thermal_budget.h"

typedef struct {
    mem_pool_limits_t heap;           /* пороги кучі */
    uint32_t          battery_mah;    /* ємність джерела живлення */
    uint32_t          required_hours; /* заявлений у ТЗ ресурс автономності */
} budget_limits_t;

typedef struct {
    const stack_registry_t *stacks;
    const mem_pool_t       *heap;
    const rail_monitor_t   *rail;
    const thermal_monitor_t *thermal;
    const energy_ledger_t  *energy;
    const section_timer_t  *sections;
    size_t                  section_count;
    flash_layout_t          flash;
    budget_limits_t         limits;
} budget_monitor_t;

typedef struct {
    budget_flags_t    flags;
    budget_severity_t severity;

    stack_report_t   stacks;
    mem_pool_stats_t heap;
    flash_report_t   flash;

    uint16_t vdd_last_mv;
    uint16_t vdd_min_mv;
    int32_t  vdd_headroom_mv;
    uint32_t vdd_sag_events;

    int16_t  ambient_dc;
    int16_t  junction_dc;
    int16_t  junction_peak_dc;
    uint32_t thermal_headroom_mw; /* скільки ще можна розсіяти */

    uint32_t avg_current_ua;
    uint32_t life_hours;
    uint32_t tx_charge_share_pm;
    uint32_t tx_time_share_pm;

    const char *worst_section_name;
    uint32_t    worst_section_us;
    int32_t     worst_section_margin_us;
} budget_report_t;

typedef enum {
    BUDGET_ACTION_RUN = 0,   /* усі бюджети в межах */
    BUDGET_ACTION_DERATE,    /* знизити темп: скоротити передачі, частоту ядра */
    BUDGET_ACTION_SAFE_STATE /* негайно згорнути роботу до безпечного стану */
} budget_action_t;

/* Збирає показання підсистем і виносить вердикт. */
budget_flags_t budget_monitor_run(const budget_monitor_t *monitor,
                                  budget_report_t *report);

budget_action_t budget_monitor_action(budget_flags_t flags);

const char *budget_action_name(budget_action_t action);

/* Друкує звіт у наданий буфер; повертає кількість записаних символів. */
size_t budget_report_format(const budget_report_t *report, char *out, size_t cap);

#endif /* BUDGET_MONITOR_H */

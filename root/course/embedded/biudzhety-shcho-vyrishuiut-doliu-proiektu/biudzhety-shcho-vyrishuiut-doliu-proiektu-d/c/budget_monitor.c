#include "budget_monitor.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

budget_flags_t budget_monitor_run(const budget_monitor_t *monitor,
                                  budget_report_t *report)
{
    if (monitor == NULL || report == NULL) {
        return BUDGET_CRITICAL_MASK;
    }

    memset(report, 0, sizeof *report);
    budget_flags_t flags = BUDGET_OK;

    /* 1. Пам'ять: стеки задач, куча та розкладка Flash під OTA. */
    if (monitor->stacks != NULL) {
        flags |= stack_guard_audit(monitor->stacks, &report->stacks);
    }
    if (monitor->heap != NULL) {
        flags |= mem_pool_audit(monitor->heap, &monitor->limits.heap,
                                &report->heap);
    }
    flags |= flash_budget_audit(&monitor->flash, &report->flash);

    /* 2. Живлення: найгірший відлік шини важить більше за поточний. */
    if (monitor->rail != NULL) {
        report->vdd_last_mv     = monitor->rail->last_mv;
        report->vdd_min_mv      = monitor->rail->min_mv;
        report->vdd_sag_events  = monitor->rail->sag_events;
        report->vdd_headroom_mv = rail_monitor_headroom_mv(monitor->rail);

        if (monitor->rail->brownout_events > 0u) {
            flags |= BUDGET_VDD_BROWNOUT | BUDGET_VDD_SAG;
        } else if (monitor->rail->sag_events > 0u) {
            flags |= BUDGET_VDD_SAG;
        }
    }

    /* 3. Тепло: беремо пікову температуру кристала за весь час роботи. */
    if (monitor->thermal != NULL) {
        const thermal_monitor_t *tm = monitor->thermal;

        report->ambient_dc       = tm->ambient_dc;
        report->junction_dc      = tm->junction_dc;
        report->junction_peak_dc = tm->peak_dc;

        uint32_t max_mw = thermal_max_power_mw(&tm->limits, tm->ambient_dc);
        report->thermal_headroom_mw =
            (max_mw > tm->power_mw) ? max_mw - tm->power_mw : 0u;

        if (tm->trip_events > 0u ||
            tm->peak_dc >= tm->limits.tj_max_dc) {
            flags |= BUDGET_THERMAL_TRIP | BUDGET_THERMAL_WARN;
        } else if (tm->peak_dc >=
                   (int16_t)(tm->limits.tj_max_dc - tm->limits.warn_margin_dc)) {
            flags |= BUDGET_THERMAL_WARN;
        }
    }

    /* 4. Енергія: середній струм проти заявленого ресурсу автономності. */
    if (monitor->energy != NULL) {
        report->avg_current_ua = energy_ledger_avg_current_ua(monitor->energy);
        report->life_hours =
            energy_ledger_life_hours(monitor->energy,
                                     monitor->limits.battery_mah);
        report->tx_charge_share_pm =
            energy_ledger_share_pm(monitor->energy, ENERGY_PHASE_TX);
        report->tx_time_share_pm =
            energy_ledger_time_share_pm(monitor->energy, ENERGY_PHASE_TX);

        flags |= energy_ledger_audit(monitor->energy,
                                     monitor->limits.battery_mah,
                                     monitor->limits.required_hours);
    }

    /* 5. Час: найтісніша критична секція. */
    if (monitor->sections != NULL && monitor->section_count > 0u) {
        size_t worst = 0u;
        flags |= section_timer_audit(monitor->sections, monitor->section_count,
                                     &worst);

        const section_timer_t *st = &monitor->sections[worst];
        report->worst_section_name      = st->name;
        report->worst_section_us        = st->worst_us;
        report->worst_section_margin_us = section_timer_margin_us(st);
    }

    report->flags    = flags;
    report->severity = budget_severity_of(flags);
    return flags;
}

budget_action_t budget_monitor_action(budget_flags_t flags)
{
    switch (budget_severity_of(flags)) {
    case BUDGET_SEVERITY_CRITICAL:
        return BUDGET_ACTION_SAFE_STATE;
    case BUDGET_SEVERITY_WARNING:
        return BUDGET_ACTION_DERATE;
    default:
        return BUDGET_ACTION_RUN;
    }
}

const char *budget_action_name(budget_action_t action)
{
    switch (action) {
    case BUDGET_ACTION_RUN:        return "штатна робота";
    case BUDGET_ACTION_DERATE:     return "знизити темп";
    case BUDGET_ACTION_SAFE_STATE: return "безпечний стан";
    default:                       return "?";
    }
}

static void appendf(char **cursor, size_t *left, const char *fmt, ...)
{
    if (*left <= 1u) {
        return;
    }

    va_list args;
    va_start(args, fmt);
    int written = vsnprintf(*cursor, *left, fmt, args);
    va_end(args);

    if (written < 0) {
        return;
    }

    /* Обрізаний рядок не має зсувати курсор за межі буфера. */
    size_t advance = ((size_t)written >= *left) ? (*left - 1u) : (size_t)written;
    *cursor += advance;
    *left   -= advance;
}

/* Друк температури, збереженої в десятих градуса. */
static void append_temp(char **cursor, size_t *left, const char *label,
                        int16_t deci_celsius)
{
    int whole = deci_celsius / 10;
    int frac  = deci_celsius % 10;
    if (frac < 0) {
        frac = -frac;
    }
    appendf(cursor, left, "%s%d.%d °C", label, whole, frac);
}

size_t budget_report_format(const budget_report_t *report, char *out, size_t cap)
{
    if (report == NULL || out == NULL || cap == 0u) {
        return 0u;
    }

    char  *cursor = out;
    size_t left   = cap;
    out[0] = '\0';

    char flag_list[256];
    budget_flags_format(report->flags, flag_list, sizeof flag_list);

    appendf(&cursor, &left, "АУДИТ БЮДЖЕТІВ: %s\n", flag_list);
    appendf(&cursor, &left, "  дія: %s\n\n",
            budget_action_name(budget_monitor_action(report->flags)));

    appendf(&cursor, &left, "  стеки: найтісніша задача «%s», запас %zu Б\n",
            (report->stacks.worst_name != NULL) ? report->stacks.worst_name : "—",
            report->stacks.worst_free);

    appendf(&cursor, &left,
            "  куча:  вільно %zu Б, найбільший блок %zu Б, розривів %zu, "
            "фрагментація %lu ‰, відмов %lu\n",
            report->heap.free_bytes, report->heap.largest_free,
            report->heap.free_blocks,
            (unsigned long)report->heap.fragmentation_pm,
            (unsigned long)report->heap.failed_calls);

    appendf(&cursor, &left,
            "  flash: слот %lu Б, запас у слоті %lu Б, образ %lu ‰ обсягу, "
            "OTA %s\n",
            (unsigned long)report->flash.slot_bytes,
            (unsigned long)report->flash.slot_free_bytes,
            (unsigned long)report->flash.image_share_pm,
            report->flash.dual_bank_ready ? "можливий" : "НЕМОЖЛИВИЙ");

    appendf(&cursor, &left,
            "  шина:  поточна %u мВ, мінімум %u мВ, запас до BOR %ld мВ, "
            "просідань %lu\n",
            (unsigned)report->vdd_last_mv, (unsigned)report->vdd_min_mv,
            (long)report->vdd_headroom_mv,
            (unsigned long)report->vdd_sag_events);

    appendf(&cursor, &left, "  тепло: ");
    append_temp(&cursor, &left, "середовище ", report->ambient_dc);
    append_temp(&cursor, &left, ", кристал ", report->junction_dc);
    append_temp(&cursor, &left, ", пік ", report->junction_peak_dc);
    appendf(&cursor, &left, ", запас потужності %lu мВт\n",
            (unsigned long)report->thermal_headroom_mw);

    if (report->life_hours == UINT32_MAX) {
        appendf(&cursor, &left,
                "  струм: середній %lu мкА, ресурс поза роздільністю обліку\n",
                (unsigned long)report->avg_current_ua);
    } else {
        appendf(&cursor, &left,
                "  струм: середній %lu мкА, ресурс %lu год (%lu діб), "
                "передавач: %lu ‰ часу й %lu ‰ заряду\n",
                (unsigned long)report->avg_current_ua,
                (unsigned long)report->life_hours,
                (unsigned long)(report->life_hours / 24u),
                (unsigned long)report->tx_time_share_pm,
                (unsigned long)report->tx_charge_share_pm);
    }

    appendf(&cursor, &left,
            "  час:   найтісніша секція «%s», найгірше %lu мкс, запас %ld мкс\n",
            (report->worst_section_name != NULL) ? report->worst_section_name
                                                 : "—",
            (unsigned long)report->worst_section_us,
            (long)report->worst_section_margin_us);

    return (size_t)(cursor - out);
}

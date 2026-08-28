#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define REGIME_CRA   (1U << 0)
#define REGIME_NIS2  (1U << 1)
#define REGIME_GDPR  (1U << 2)
#define REGIME_SEC   (1U << 3)

typedef enum {
    SEVERITY_LOW = 0,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL
} IncidentSeverity;

typedef enum {
    STATE_NEW = 0,
    STATE_TRIAGED,
    STATE_EARLY_WARNING_SENT,
    STATE_DETAILED_NOTICE_SENT,
    STATE_FINAL_REPORT_SENT,
    STATE_CLOSED
} IncidentState;

typedef struct {
    uint64_t incident_id;
    uint32_t active_regimes;
    IncidentSeverity severity;
    IncidentState state;
    time_t detected_at;
    time_t awareness_at;
    time_t early_warning_deadline;
    time_t detailed_notice_deadline;
    time_t final_report_deadline;
    bool has_active_exploit;
    bool pii_compromised;
    bool operational_outage;
} IncidentContext;

/* Додавання робочих днів для вимог SEC (виключаючи суботу й неділю) */
time_t add_business_days(time_t start, int days) {
    struct tm tm_buf;
    time_t current = start;
    int added = 0;

    while (added < days) {
        current += 86400; /* +24 години */
        gmtime_r(&current, &tm_buf);
        if (tm_buf.tm_wday != 0 && tm_buf.tm_wday != 6) {
            added++;
        }
    }
    return current;
}

int incident_triage_init(IncidentContext *ctx, uint64_t id, time_t detected_at) {
    if (!ctx) return -1;
    memset(ctx, 0, sizeof(*ctx));
    ctx->incident_id = id;
    ctx->detected_at = detected_at;
    ctx->awareness_at = detected_at;
    ctx->state = STATE_NEW;
    return 0;
}

void incident_evaluate_regimes(IncidentContext *ctx) {
    ctx->active_regimes = 0;

    /* CRA: активно експлуатована вразливість у продукті */
    if (ctx->has_active_exploit) {
        ctx->active_regimes |= REGIME_CRA;
    }

    /* NIS 2: операційний збій чи суттєвий вплив на сервіси */
    if (ctx->operational_outage || ctx->severity >= SEVERITY_HIGH) {
        ctx->active_regimes |= REGIME_NIS2;
    }

    /* GDPR: несанкціонований доступ або витік персональних даних */
    if (ctx->pii_compromised) {
        ctx->active_regimes |= REGIME_GDPR;
    }

    /* SEC: критичні збитки для публічної компанії */
    if (ctx->severity == SEVERITY_CRITICAL) {
        ctx->active_regimes |= REGIME_SEC;
    }

    /* Розрахунок дедлайнів від моменту усвідомлення (awareness_at) */
    if (ctx->active_regimes & (REGIME_CRA | REGIME_NIS2)) {
        ctx->early_warning_deadline = ctx->awareness_at + (24 * 3600);
        ctx->detailed_notice_deadline = ctx->awareness_at + (72 * 3600);
        ctx->final_report_deadline = ctx->awareness_at + (30 * 86400);
    } else if (ctx->active_regimes & REGIME_GDPR) {
        ctx->early_warning_deadline = 0; /* Не передбачено раннього сповіщення */
        ctx->detailed_notice_deadline = ctx->awareness_at + (72 * 3600);
        ctx->final_report_deadline = 0;
    }

    if (ctx->active_regimes & REGIME_SEC) {
        /* 4 робочі дні з моменту кваліфікації суттєвості */
        time_t sec_deadline = add_business_days(ctx->awareness_at, 4);
        if (ctx->detailed_notice_deadline == 0 || sec_deadline < ctx->detailed_notice_deadline) {
            ctx->detailed_notice_deadline = sec_deadline;
        }
    }

    ctx->state = STATE_TRIAGED;
}

void incident_check_deadlines(const IncidentContext *ctx, time_t current_time) {
    if (ctx->early_warning_deadline > 0 && ctx->state < STATE_EARLY_WARNING_SENT) {
        double diff_hours = difftime(ctx->early_warning_deadline, current_time) / 3600.0;
        if (diff_hours < 0) {
            printf("[CRITICAL] Incident #%llu: 24h Early Warning SLA BREACHED by %.1f hours!\n",
                   (unsigned long long)ctx->incident_id, -diff_hours);
        } else if (diff_hours <= 4.0) {
            printf("[WARNING] Incident #%llu: 24h Early Warning deadline in %.1f hours.\n",
                   (unsigned long long)ctx->incident_id, diff_hours);
        }
    }

    if (ctx->detailed_notice_deadline > 0 && ctx->state < STATE_DETAILED_NOTICE_SENT) {
        double diff_hours = difftime(ctx->detailed_notice_deadline, current_time) / 3600.0;
        if (diff_hours < 0) {
            printf("[CRITICAL] Incident #%llu: Detailed Notification SLA BREACHED by %.1f hours!\n",
                   (unsigned long long)ctx->incident_id, -diff_hours);
        } else if (diff_hours <= 12.0) {
            printf("[ALERT] Incident #%llu: Detailed Notification deadline in %.1f hours.\n",
                   (unsigned long long)ctx->incident_id, diff_hours);
        }
    }
}

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <string.h>

#define SECONDS_PER_DAY 86400LL
#define DEFAULT_EMBARGO_DAYS 90
#define GRACE_PERIOD_DAYS 14
#define EMERGENCY_IN_THE_WILD_DAYS 7
#define EMERGENCY_LEAK_DAYS 2

typedef enum {
    STATE_SUBMITTED = 0,
    STATE_TRIAGED,
    STATE_IN_PROGRESS,
    STATE_PATCH_READY,
    STATE_PRE_NOTIFY,
    STATE_DISCLOSED,
    STATE_EMERGENCY,
    STATE_REJECTED
} cvd_state_t;

typedef struct {
    char case_id[32];
    char cve_id[20];
    cvd_state_t state;
    time_t submitted_time;
    time_t embargo_deadline;
    bool in_the_wild;
    bool public_leak;
    bool grace_applied;
} cvd_case_t;

static time_t adjust_weekend_rollover(time_t target_time) {
    struct tm tm_buf;
#if defined(_WIN32)
    gmtime_s(&tm_buf, &target_time);
#else
    gmtime_r(&target_time, &tm_buf);
#endif
    // tm_wday: 0 = Sunday, 6 = Saturday
    if (tm_buf.tm_wday == 6) {
        return target_time + 2 * SECONDS_PER_DAY; // Перенесення суботи на понеділок
    } else if (tm_buf.tm_wday == 0) {
        return target_time + 1 * SECONDS_PER_DAY; // Перенесення неділі на понеділок
    }
    return target_time;
}

bool cvd_case_init(cvd_case_t *c, const char *case_id, time_t submit_time) {
    if (!c || !case_id) return false;
    memset(c, 0, sizeof(cvd_case_t));
    snprintf(c->case_id, sizeof(c->case_id), "%s", case_id);
    c->state = STATE_SUBMITTED;
    c->submitted_time = submit_time;
    time_t raw_deadline = submit_time + (DEFAULT_EMBARGO_DAYS * SECONDS_PER_DAY);
    c->embargo_deadline = adjust_weekend_rollover(raw_deadline);
    return true;
}

bool cvd_case_triage(cvd_case_t *c, const char *cve_id, bool accepted) {
    if (!c || c->state != STATE_SUBMITTED) return false;
    if (!accepted) {
        c->state = STATE_REJECTED;
        return true;
    }
    if (cve_id) {
        snprintf(c->cve_id, sizeof(c->cve_id), "%s", cve_id);
    }
    c->state = STATE_TRIAGED;
    return true;
}

bool cvd_case_start_remediation(cvd_case_t *c) {
    if (!c || c->state != STATE_TRIAGED) return false;
    c->state = STATE_IN_PROGRESS;
    return true;
}

bool cvd_case_apply_grace_period(cvd_case_t *c) {
    if (!c || c->grace_applied) return false;
    if (c->state != STATE_IN_PROGRESS && c->state != STATE_PATCH_READY) return false;
    
    c->embargo_deadline += (GRACE_PERIOD_DAYS * SECONDS_PER_DAY);
    c->embargo_deadline = adjust_weekend_rollover(c->embargo_deadline);
    c->grace_applied = true;
    return true;
}

bool cvd_case_trigger_emergency(cvd_case_t *c, time_t event_time, bool is_in_the_wild, bool is_leak) {
    if (!c || c->state == STATE_DISCLOSED || c->state == STATE_REJECTED) return false;
    
    c->state = STATE_EMERGENCY;
    if (is_leak) {
        c->public_leak = true;
        c->embargo_deadline = event_time + (EMERGENCY_LEAK_DAYS * SECONDS_PER_DAY);
    } else if (is_in_the_wild) {
        c->in_the_wild = true;
        c->embargo_deadline = event_time + (EMERGENCY_IN_THE_WILD_DAYS * SECONDS_PER_DAY);
    }
    return true;
}

bool cvd_case_disclose(cvd_case_t *c, time_t current_time) {
    if (!c || c->state == STATE_REJECTED || c->state == STATE_DISCLOSED) return false;
    if (current_time >= c->embargo_deadline || c->state == STATE_EMERGENCY || c->state == STATE_PRE_NOTIFY) {
        c->state = STATE_DISCLOSED;
        return true;
    }
    return false;
}

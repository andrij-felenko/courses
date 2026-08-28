#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SP90B_RCT_CUTOFF   35
#define SP90B_APT_WINDOW   512
#define SP90B_APT_CUTOFF   312

typedef enum {
    SP90B_OK = 0,
    SP90B_ERR_RCT_FAILED = 1,
    SP90B_ERR_APT_FAILED = 2
} sp90b_status_t;

typedef struct {
    /* Внутрішній стан тесту RCT */
    uint8_t  rct_last_sample;
    uint32_t rct_rep_count;

    /* Внутрішній стан тесту APT */
    uint8_t  apt_target_sample;
    uint32_t apt_match_count;
    uint32_t apt_window_index;

    bool     initialized;
    bool     alarm_latched;
} sp90b_health_monitor_t;

void sp90b_init(sp90b_health_monitor_t *mon) {
    if (!mon) return;
    mon->rct_last_sample = 0;
    mon->rct_rep_count = 0;
    mon->apt_target_sample = 0;
    mon->apt_match_count = 0;
    mon->apt_window_index = 0;
    mon->initialized = false;
    mon->alarm_latched = false;
}

sp90b_status_t sp90b_process_sample(sp90b_health_monitor_t *mon, uint8_t sample) {
    if (!mon) return SP90B_ERR_RCT_FAILED;
    if (mon->alarm_latched) return SP90B_ERR_RCT_FAILED;

    /* Початкова ініціалізація під час першого відліку */
    if (!mon->initialized) {
        mon->rct_last_sample = sample;
        mon->rct_rep_count = 1;
        mon->apt_target_sample = sample;
        mon->apt_match_count = 1;
        mon->apt_window_index = 1;
        mon->initialized = true;
        return SP90B_OK;
    }

    /* 1. Виконання Repetition Count Test */
    if (sample == mon->rct_last_sample) {
        mon->rct_rep_count++;
        if (mon->rct_rep_count >= SP90B_RCT_CUTOFF) {
            mon->alarm_latched = true;
            return SP90B_ERR_RCT_FAILED;
        }
    } else {
        mon->rct_last_sample = sample;
        mon->rct_rep_count = 1;
    }

    /* 2. Виконання Adaptive Proportion Test */
    if (mon->apt_window_index == 0) {
        mon->apt_target_sample = sample;
        mon->apt_match_count = 1;
        mon->apt_window_index = 1;
    } else {
        if (sample == mon->apt_target_sample) {
            mon->apt_match_count++;
            if (mon->apt_match_count >= SP90B_APT_CUTOFF) {
                mon->alarm_latched = true;
                return SP90B_ERR_APT_FAILED;
            }
        }
        mon->apt_window_index++;
        if (mon->apt_window_index >= SP90B_APT_WINDOW) {
            mon->apt_window_index = 0;
        }
    }

    return SP90B_OK;
}

sp90b_status_t sp90b_process_buffer(sp90b_health_monitor_t *mon,
                                    const uint8_t *buf,
                                    size_t len) {
    for (size_t i = 0; i < len; ++i) {
        sp90b_status_t st = sp90b_process_sample(mon, buf[i]);
        if (st != SP90B_OK) {
            return st;
        }
    }
    return SP90B_OK;
}

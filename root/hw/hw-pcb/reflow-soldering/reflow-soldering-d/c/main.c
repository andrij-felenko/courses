#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define GRADIENT_HISTORY_SIZE 5

typedef enum {
    ZONE_PREHEAT = 0,
    ZONE_SOAK,
    ZONE_REFLOW,
    ZONE_COOLING,
    ZONE_FINISHED
} ReflowZone;

typedef struct {
    double min_preheat_ramp;  /* +1.0 C/s */
    double max_preheat_ramp;  /* +3.0 C/s */
    double soak_temp_min;     /* 150.0 C */
    double soak_temp_max;     /* 200.0 C */
    double min_soak_time;     /* 60.0 s */
    double max_soak_time;     /* 120.0 s */
    double liquidus_temp;     /* 217.0 C */
    double min_tal_time;      /* 45.0 s */
    double max_tal_time;      /* 90.0 s */
    double min_peak_temp;     /* 235.0 C */
    double max_peak_temp;     /* 255.0 C */
    double max_cooling_ramp;  /* -4.0 C/s */
} ProfileLimits;

typedef struct {
    ProfileLimits limits;
    ReflowZone current_zone;
    double current_temp;
    double peak_temp;
    double tal_seconds;
    double soak_start_time;
    double soak_duration;
    double temp_history[GRADIENT_HISTORY_SIZE];
    int history_index;
    bool has_violation;
} ReflowAnalyzer;

void analyzer_init(ReflowAnalyzer *an, const ProfileLimits *lim) {
    an->limits = *lim;
    an->current_zone = ZONE_PREHEAT;
    an->current_temp = 25.0;
    an->peak_temp = 25.0;
    an->tal_seconds = 0.0;
    an->soak_start_time = 0.0;
    an->soak_duration = 0.0;
    an->history_index = 0;
    an->has_violation = false;
    for (int i = 0; i < GRADIENT_HISTORY_SIZE; i++) {
        an->temp_history[i] = 25.0;
    }
}

double analyzer_calculate_ramp_rate(ReflowAnalyzer *an, double dt) {
    double oldest = an->temp_history[an->history_index];
    double current = an->current_temp;
    return (current - oldest) / (GRADIENT_HISTORY_SIZE * dt);
}

void analyzer_update(ReflowAnalyzer *an, double raw_temp, double dt, double total_time) {
    an->current_temp = raw_temp;
    an->temp_history[an->history_index] = raw_temp;
    an->history_index = (an->history_index + 1) % GRADIENT_HISTORY_SIZE;

    double ramp_rate = analyzer_calculate_ramp_rate(an, dt);

    if (raw_temp > an->peak_temp) {
        an->peak_temp = raw_temp;
    }

    if (raw_temp >= an->limits.liquidus_temp) {
        an->tal_seconds += dt;
    }

    switch (an->current_zone) {
        case ZONE_PREHEAT:
            if (ramp_rate > an->limits.max_preheat_ramp) {
                an->has_violation = true;
            }
            if (raw_temp >= an->limits.soak_temp_min) {
                an->current_zone = ZONE_SOAK;
                an->soak_start_time = total_time;
            }
            break;

        case ZONE_SOAK:
            if (raw_temp >= an->limits.liquidus_temp) {
                an->current_zone = ZONE_REFLOW;
                an->soak_duration = total_time - an->soak_start_time;
                if (an->soak_duration < an->limits.min_soak_time ||
                    an->soak_duration > an->limits.max_soak_time) {
                    an->has_violation = true;
                }
            }
            break;

        case ZONE_REFLOW:
            if (raw_temp < an->limits.liquidus_temp && an->peak_temp >= an->limits.min_peak_temp) {
                an->current_zone = ZONE_COOLING;
                if (an->tal_seconds < an->limits.min_tal_time ||
                    an->tal_seconds > an->limits.max_tal_time ||
                    an->peak_temp > an->limits.max_peak_temp) {
                    an->has_violation = true;
                }
            }
            break;

        case ZONE_COOLING:
            if (ramp_rate < an->limits.max_cooling_ramp) {
                an->has_violation = true;
            }
            if (raw_temp <= 50.0) {
                an->current_zone = ZONE_FINISHED;
            }
            break;

        case ZONE_FINISHED:
            break;
    }
}

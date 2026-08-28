/* vi_tracer.h / vi_tracer.c */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_TRACE_POINTS 128

typedef struct {
    float voltage_v;
    float current_ma;
} ViPoint;

typedef struct {
    float v_nom;
    float i_min_ma;
    float i_max_ma;
} ViToleranceBand;

typedef struct {
    bool passed;
    float max_current_deviation_ma;
    uint32_t failed_point_index;
} TraceCompareResult;

TraceCompareResult evaluate_vi_signature(const ViPoint* measured,
                                         const ViToleranceBand* golden_envelope,
                                         uint32_t point_count) {
    TraceCompareResult result = {
        .passed = true,
        .max_current_deviation_ma = 0.0f,
        .failed_point_index = 0
    };

    if (point_count == 0 || point_count > MAX_TRACE_POINTS) {
        result.passed = false;
        return result;
    }

    for (uint32_t i = 0; i < point_count; ++i) {
        float i_meas = measured[i].current_ma;
        float i_min = golden_envelope[i].i_min_ma;
        float i_max = golden_envelope[i].i_max_ma;

        float deviation = 0.0f;
        if (i_meas < i_min) {
            deviation = i_min - i_meas;
        } else if (i_meas > i_max) {
            deviation = i_meas - i_max;
        }

        if (deviation > result.max_current_deviation_ma) {
            result.max_current_deviation_ma = deviation;
        }

        if (deviation > 0.05f) { /* Поріг неприпустимого відхилення: 50 мкА */
            result.passed = false;
            result.failed_point_index = i;
            break;
        }
    }

    return result;
}

#ifndef DIAGNOSE_H
#define DIAGNOSE_H

#include "metrics.h"

typedef enum {
    BAND_HEALTHY = 0,
    BAND_WATCH,        /* ще не біда, але вже не норма */
    BAND_UNDER,        /* замале підсилення / завелика затримка */
    BAND_OVER,         /* надмірне підсилення */
    BAND_UNKNOWN
} MetricBand;

typedef struct {
    MetricBand tau;
    MetricBand rise;
    MetricBand overshoot;
    MetricBand noise;
} MetricBands;

typedef enum {
    TUNE_HEALTHY = 0,
    TUNE_SYSTEM_LAGGY,
    TUNE_D_NOISE,
    TUNE_P_HIGH,
    TUNE_D_LOW,
    TUNE_RISE_TOO_FAST,
    TUNE_P_LOW,
    TUNE_OVERDAMPED,
    TUNE_NOT_SETTLED
} TuneVerdict;

MetricBands diagnose_bands(const StepMetrics *m);
TuneVerdict diagnose(const StepMetrics *m, MetricBands b);

const char *band_mark(MetricBand b);
const char *verdict_title(TuneVerdict v);
const char *verdict_advice(TuneVerdict v);

#endif /* DIAGNOSE_H */

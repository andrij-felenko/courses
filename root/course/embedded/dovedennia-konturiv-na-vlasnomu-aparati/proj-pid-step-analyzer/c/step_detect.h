#ifndef STEP_DETECT_H
#define STEP_DETECT_H

#include "log.h"

/* Ознаки того, що вимірювання спотворене зовнішніми чинниками. */
#define DIST_GYRO_CLIP 0x1u   /* гіроскоп упирався в межу діапазону */
#define DIST_VBAT_SAG  0x2u   /* напруга просіла нижче порога відсічки */

typedef struct {
    size_t   quiet_begin;   /* початок спокійної передісторії */
    size_t   begin;         /* останній відлік перед фронтом завдання */
    size_t   edge_end;      /* відлік, де завдання вийшло на плато */
    size_t   end;           /* останній відлік вікна аналізу */
    double   amplitude;     /* Δ завдання на фронті, deg/s */
    unsigned distorted;     /* маска DIST_* */
} StepWindow;

typedef struct {
    double edge_slope_min;  /* поріг |d(SetPoint)/dt|, deg/s² */
    double edge_min_amp;    /* мінімальна Δ завдання, deg/s */
    double edge_max_ms;     /* фронт має вкластися в цей час */
    double quiet_ms;        /* скільки спокою вимагаємо перед фронтом */
    double quiet_err_max;   /* допустиме |SetPoint − Gyro| у передісторії, deg/s */
    double plateau_ms;      /* скільки завдання має триматися після фронту */
    double plateau_tol;     /* допустиме тремтіння стіка на плато, deg/s */
    double analysis_ms;     /* повна довжина вікна аналізу після фронту */
    double gyro_clip;       /* межа діапазону гіроскопа, deg/s */
    double vbat_cutoff;     /* поріг відсічки батареї, В */
} DetectConfig;

/* Чому сходинки відсіювались — без цього користувач бачить лише «знайдено 0». */
typedef struct {
    size_t edges;              /* фронтів, що подолали поріг швидкості */
    size_t rejected_ramp;      /* завдання їхало довше за edge_max_ms */
    size_t rejected_small;     /* амплітуда менша за edge_min_amp */
    size_t rejected_noisy;     /* апарат ще коливався від попереднього маневру */
    size_t rejected_plateau;   /* стік смикнули назад раніше за plateau_ms */
} DetectStats;

DetectConfig detect_default_config(double vbat_cutoff);

/* Заповнює out придатними до аналізу вікнами; повертає їхню кількість. */
size_t detect_steps(const FlightLog *log, const DetectConfig *cfg,
                    StepWindow *out, size_t max_out, DetectStats *stats);

#endif /* STEP_DETECT_H */

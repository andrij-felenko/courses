#ifndef SIZING_H
#define SIZING_H

#include <stdbool.h>
#include <stddef.h>

#include "motor.h"

/* Вимоги задачі — на ВИХІДНОМУ валу: саме там живе навантаження,
   а редуктор перераховує їх до вала мотора. */
typedef struct {
    const char *label;
    double load_torque_nm;         /* статичний момент опору */
    double load_inertia_kgm2;      /* момент інерції навантаження */
    double target_speed_rpm;       /* потрібні оберти вихідного вала */
    double accel_time_s;           /* час виходу на швидкість */
    double move_duty;              /* частка часу в русі, 0..1 */
    bool holds_under_load;         /* у паузах треба тримати позицію під навантаженням */
    double position_tolerance_deg; /* 0 — позиціонування не потрібне */
    double ambient_temp_c;
    double insulation_limit_c;     /* межа ізоляції обмотки */
    double power_budget_w;         /* 0 — бюджет не заданий */
} MotionTask;

enum {
    /* відмови */
    SZ_BAD_INPUT      = 1u << 0,
    SZ_TORQUE_SHORT   = 1u << 1,
    SZ_STEP_LOSS      = 1u << 2,
    SZ_SPEED_EXCEEDED = 1u << 3,
    SZ_OVERHEAT       = 1u << 4,
    SZ_POWER_BUDGET   = 1u << 5,
    SZ_NO_FEEDBACK    = 1u << 6,
    SZ_PRECISION      = 1u << 7,
    /* попередження: привід придатний, але про це кажуть уголос */
    SZ_W_INRUSH       = 1u << 8,
    SZ_W_TORQUE_FADE  = 1u << 9,
    SZ_W_RUNS_HOT     = 1u << 10
};

typedef struct {
    unsigned fail;
    unsigned warn;
    const char *input_problem;      /* причина SZ_BAD_INPUT, інакше NULL */

    double motor_speed_rpm;
    double cruise_torque_nm;        /* лише статика, приведена до вала мотора */
    double peak_torque_nm;          /* статика + інерція під час розгону */
    double available_torque_nm;
    double margin;                  /* доступний / потрібний */
    double required_margin;
    double peak_current_a;
    double stall_current_a;
    double output_resolution_deg;   /* < 0 — положення не вимірюється */
    double electrical_power_w;

    double copper_move_w;
    double copper_hold_w;
    double copper_average_w;
    double gear_loss_w;
    double winding_temp_c;
} SizingReport;

/* Рахує привід під задачу. Повертає true, коли жодної відмови немає;
   звіт заповнюється завжди — у ньому числа, а не лише вердикт. */
bool sizing_evaluate(const MotorSpecs *m, const Gearbox *g,
                     const MotionTask *task, SizingReport *out);

/* Складає перелік прапорців у людський рядок; повертає кількість записаних байтів. */
size_t sizing_describe(unsigned flags, char *buf, size_t size);

#endif /* SIZING_H */

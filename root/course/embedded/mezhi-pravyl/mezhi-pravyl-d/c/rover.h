#ifndef ROVER_H
#define ROVER_H

#include <stdbool.h>
#include <stddef.h>

/* Спільні типи двоконтурної системи рішень: уставка, стан, параметри апарата
 * й межі безпеки. Числа — інспекційний ровер 18 кг на просілому 4S-пакеті. */

/* Уставка: те, чим планувальник і бар'єр говорять із контуром моторів. */
typedef struct {
    float vx;       /* поздовжня швидкість, м/с */
    float yaw_rate; /* кутова швидкість рискання, рад/с */
} Setpoint;

/* Миттєвий стан, який швидкий контур читає з давачів кожен такт. */
typedef struct {
    float vx;
    float yaw_rate;
    float range_ahead_m;      /* мінімум по передньому сектору лідара */
    float tilt_rad;           /* модуль кута нахилу платформи */
    float pack_ocv_v;         /* ЕРС пакета (оцінка за SoC) */
    float pack_esr_ohm;       /* внутрішній опір пакета */
    float yaw_disturbance_nm; /* момент від бокового вітру, який тримають мотори */
    bool  range_valid;        /* далекомір віддав придатне вимірювання */
} VehicleState;

typedef struct {
    float mass_kg;
    float track_m;        /* колія: плече диференційної тяги */
    float yaw_inertia;    /* I_z, кг·м² */
    float yaw_damping;    /* Н·м·с/рад — тертя ковзання коліс при розвороті */
    float roll_resist_n;  /* опір коченню */
    float drag_coeff;     /* Н·с²/м² — квадратичний опір */
    float force_per_amp;  /* Н на ампер струму ОДНОГО борту */
    float idle_current_a; /* обчислювач, лідар, сервіси */
} RoverParams;

typedef struct {
    float v_max;
    float accel_max;
    float brake_accel;        /* сповільнення, у яке вірить бар'єр, м/с² */
    float yaw_rate_max;
    float yaw_accel_max;
    float lat_accel_max;      /* бічне прискорення за зчепленням */
    float obstacle_margin_m;  /* геометричний зазор d_safe */
    float tilt_max_rad;
    float pack_min_v;         /* нижче — осередки псуються */
    float pack_max_current_a;
    float cbf_gamma;          /* γ в умові dh/dt + γ·h(x) ≥ 0 */
} SafetyLimits;

/* Перешкода як коло: лідарна відмітка або стовп огорожі. */
typedef struct {
    float x, y, radius;
} Obstacle;

static inline RoverParams rover_default_params(void)
{
    RoverParams p = {
        .mass_kg        = 18.0f,
        .track_m        = 0.34f,
        .yaw_inertia    = 0.42f,
        .yaw_damping    = 0.25f,
        .roll_resist_n  = 3.5f,
        .drag_coeff     = 0.9f,
        .force_per_amp  = 6.0f,
        .idle_current_a = 0.9f,
    };
    return p;
}

static inline SafetyLimits rover_default_limits(void)
{
    SafetyLimits l = {
        .v_max              = 2.4f,
        .accel_max          = 1.6f,
        .brake_accel        = 3.0f,
        .yaw_rate_max       = 1.4f,
        .yaw_accel_max      = 4.0f,
        .lat_accel_max      = 2.6f,
        .obstacle_margin_m  = 0.6f,
        .tilt_max_rad       = 0.35f,
        .pack_min_v         = 13.8f,
        .pack_max_current_a = 12.0f,
        .cbf_gamma          = 2.0f,
    };
    return l;
}

#endif /* ROVER_H */

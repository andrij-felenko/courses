#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define R_ROTOR      0.15     /* радіус гвинта квадрокоптера, м */
#define MASS         1.20     /* маса апарата, кг */
#define GRAVITY      9.80665  /* прискорення вільного падіння, м/с² */
#define RHO_AIR      1.225    /* густина повітря на рівні моря, кг/м³ */
#define PI_CONST     3.14159265358979323846

typedef enum {
    REGIME_NORMAL_HOVER,
    REGIME_GROUND_EFFECT,
    REGIME_VORTEX_RING_STATE,
    REGIME_TURBULENT_WAKE,
    REGIME_WINDMILL_BRAKE
} RotorRegime;

typedef struct {
    double z;           /* висота над землею, м */
    double vx;          /* горизонтальна швидкість уперед, м/с */
    double vy;          /* бічна швидкість управо, м/с */
    double vz;          /* вертикальна швидкість (додатна вгору), м/с */
    double thrust_cmd;  /* командна тяга моторів, Н */
    RotorRegime regime; /* поточний аеродинамічний режим */
} VehicleState;

/* Розрахунок індукованої швидкості з урахуванням екрана землі та VRS */
double compute_induced_velocity(double thrust, double z, double vx, double vy, double vz, RotorRegime *out_regime) {
    double disk_area = PI_CONST * R_ROTOR * R_ROTOR;
    if (thrust <= 0.05) {
        if (out_regime) *out_regime = REGIME_NORMAL_HOVER;
        return 0.0;
    }

    double vi0 = sqrt(thrust / (2.0 * RHO_AIR * disk_area));
    double v_horiz = sqrt(vx * vx + vy * vy);
    double v_hat_z = vz / vi0;
    double v_hat_x = v_horiz / vi0;
    double vi_dimless = 1.0;
    RotorRegime reg = REGIME_NORMAL_HOVER;

    /* 1. Перевірка осьового режиму */
    if (v_hat_z >= 0.0) {
        /* Набір або зависання */
        double half_vz = v_hat_z / 2.0;
        vi_dimless = -half_vz + sqrt(half_vz * half_vz + 1.0);
        reg = REGIME_NORMAL_HOVER;
    } else if (v_hat_z <= -2.0) {
        /* Режим вітряка / авторотації */
        double half_vz = v_hat_z / 2.0;
        double disc = half_vz * half_vz - 1.0;
        vi_dimless = -half_vz - sqrt(disc > 0.0 ? disc : 0.0);
        reg = REGIME_WINDMILL_BRAKE;
    } else {
        /* Зона -2.0 < V_hat_z < 0.0: рециркуляція та VRS */
        if (v_hat_x < 1.0) {
            /* Модель Волковича для чистого спуску */
            double vi_vrs = 1.0 - 0.125 * v_hat_z - 1.125 * v_hat_z * v_hat_z - 0.5 * v_hat_z * v_hat_z * v_hat_z;
            /* Корекція на косий потік Лейшмана */
            double vi_skew = 1.0 / sqrt(v_hat_x * v_hat_x + (v_hat_z + vi_vrs) * (v_hat_z + vi_vrs) + 0.01);
            vi_dimless = vi_vrs * (1.0 - v_hat_x) + vi_skew * v_hat_x;

            if (v_hat_z >= -1.25 && v_hat_z <= -0.4) {
                reg = REGIME_VORTEX_RING_STATE;
            } else {
                reg = REGIME_TURBULENT_WAKE;
            }
        } else {
            /* Достатня горизонтальна швидкість — потік косо обдуває диск */
            vi_dimless = 1.0 / sqrt(v_hat_x * v_hat_x + v_hat_z * v_hat_z);
            reg = REGIME_NORMAL_HOVER;
        }
    }

    double vi = vi_dimless * vi0;

    /* 2. Корекція на ефект землі (IGE) при висінні поблизу поверхні */
    if (z > 0.05 && z < 2.5 * R_ROTOR && vz > -0.5 && vz < 0.5 && v_horiz < 1.5) {
        double hr = z / R_ROTOR;
        /* Модель Гейдена для зменшення індукованої швидкості */
        double ige_ratio = 1.0 / (0.9926 + 0.0379 / (hr * hr));
        vi *= ige_ratio;
        reg = REGIME_GROUND_EFFECT;
    }

    if (out_regime) *out_regime = reg;
    return vi;
}

/* Симуляція кроку польоту (інтегрування за Ейлером) */
void step_simulation(VehicleState *s, double dt) {
    double vi = compute_induced_velocity(s->thrust_cmd, s->z, s->vx, s->vy, s->vz, &s->regime);

    /* Фактична тяга: в режимі VRS через падіння кутів атаки та зрив тяга падає */
    double actual_thrust = s->thrust_cmd;
    if (s->regime == REGIME_VORTEX_RING_STATE) {
        /* Втрата ефективної тяги на 35% через тороїдальний зрив */
        actual_thrust *= 0.65;
    } else if (s->regime == REGIME_GROUND_EFFECT) {
        /* Приріст тяги в екрані землі */
        actual_thrust *= 1.18;
    }

    double weight = MASS * GRAVITY;
    double az = (actual_thrust - weight) / MASS;
    double ax = -0.5 * RHO_AIR * 0.05 * s->vx * fabs(s->vx) / MASS;
    double ay = -0.5 * RHO_AIR * 0.05 * s->vy * fabs(s->vy) / MASS;

    s->vz += az * dt;
    s->vx += ax * dt;
    s->vy += ay * dt;
    s->z += s->vz * dt;

    if (s->z < 0.0) {
        s->z = 0.0;
        s->vz = 0.0;
    }
}

int main(void) {
    printf("=== Симуляція потрапляння у VRS та виходу маневром Вюішара ===\n\n");

    /* Сценарій 1: Помилкова спроба дати повний газ у VRS (Settling with Power) */
    VehicleState s_panic = { .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2, .thrust_cmd = MASS * GRAVITY, .regime = REGIME_NORMAL_HOVER };
    printf("--- Сценарій 1: Додавання газу без розгону (залипання у VRS) ---\n");
    for (int t_step = 0; t_step <= 30; ++t_step) {
        double time = t_step * 0.1;
        if (t_step == 5) {
            /* Пілот бачить падіння і дає 140% тяги */
            s_panic.thrust_cmd = MASS * GRAVITY * 1.40;
        }
        step_simulation(&s_panic, 0.1);
        if (t_step % 5 == 0) {
            printf("t=%.1fs | z=%5.2fm | vz=%+5.2fm/s | Тяга=%5.1fН | Режим=%d\n",
                   time, s_panic.z, s_panic.vz, s_panic.thrust_cmd, s_panic.regime);
        }
    }

    /* Сценарій 2: Маневр Вюішара (бічний зсув цикліком + крок) */
    VehicleState s_vuichard = { .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2, .thrust_cmd = MASS * GRAVITY, .regime = REGIME_NORMAL_HOVER };
    printf("\n--- Сценарій 2: Маневр Вюішара (бічний імпульс vy = 3.5 м/с) ---\n");
    for (int t_step = 0; t_step <= 30; ++t_step) {
        double time = t_step * 0.1;
        if (t_step == 3) {
            /* Застосування цикліка вбік та збільшення тяги */
            s_vuichard.vy = 3.5;
            s_vuichard.thrust_cmd = MASS * GRAVITY * 1.25;
        }
        step_simulation(&s_vuichard, 0.1);
        if (t_step % 5 == 0) {
            printf("t=%.1fs | z=%5.2fm | vz=%+5.2fm/s | vy=%4.1fm/s | Режим=%d\n",
                   time, s_vuichard.z, s_vuichard.vz, s_vuichard.vy, s_vuichard.regime);
        }
    }

    return 0;
}

#include "plant.h"

#include "ramp.h"

#include <math.h>

static float clampf(float value, float lo, float hi)
{
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

void quad_plant_init(quad_plant_t *p, float mass_kg, float hover_throttle, float alt0_m)
{
    p->mass_kg = mass_kg;
    /* 1.8 кг * 9.81 / 0.52 ~= 34 Н повної тяги: газ висіння 52 % точно
       врівноважує 17.66 Н ваги — саме це число й тримає інтегратор. */
    p->thrust_max_n = mass_kg * PLANT_G / hover_throttle;
    p->drag_coeff = 0.65f;
    p->altitude_m = alt0_m;
    p->vz_mps = 0.0f;
    p->accel_mps2 = 0.0f;
}

void quad_plant_step(quad_plant_t *p, float throttle, float dt)
{
    const float thrust = clampf(throttle, 0.0f, 1.0f) * p->thrust_max_n;
    const float drag = p->drag_coeff * p->vz_mps;

    p->accel_mps2 = (thrust - drag) / p->mass_kg - PLANT_G;
    p->vz_mps += p->accel_mps2 * dt;
    p->altitude_m += p->vz_mps * dt;

    if (p->altitude_m < 0.0f) {
        /* Земля. Далі падати нікуди, і симуляція не має права це приховати. */
        p->altitude_m = 0.0f;
        if (p->vz_mps < 0.0f) {
            p->vz_mps = 0.0f;
        }
    }
}

float quad_plant_load_factor(const quad_plant_t *p)
{
    return 1.0f + p->accel_mps2 / PLANT_G;
}

void lat_plant_init(lat_plant_t *p, float rate_gain, float trim_bias,
                    float wind_accel, float drag)
{
    p->rate_gain = rate_gain;
    p->trim_bias = trim_bias;
    p->wind_accel = wind_accel;
    p->drag = drag;
    p->position_m = 0.0f;
    p->velocity_mps = 0.0f;
    p->angle_rad = 0.0f;
}

void lat_plant_step(lat_plant_t *p, float actuator, float dt)
{
    const float u = clampf(actuator, -1.0f, 1.0f);

    /* Команда приводу задає кутову швидкість; trim_bias — паразитний момент,
       який доводиться постійно парирувати ненульовою командою. */
    p->angle_rad += p->rate_gain * (u + p->trim_bias) * dt;
    p->angle_rad = clampf(p->angle_rad, -0.6f, 0.6f);

    const float accel = PLANT_G * tanf(p->angle_rad)
                        + p->wind_accel
                        - p->drag * p->velocity_mps;
    p->velocity_mps += accel * dt;
    p->position_m += p->velocity_mps * dt;
}

void servo_init(servo_t *s, float rate_max_dps, float deadband_deg, float position_deg)
{
    s->rate_max_dps = rate_max_dps;
    s->deadband_deg = deadband_deg;
    s->position_deg = position_deg;
}

float servo_step(servo_t *s, float command_deg, float dt)
{
    /* Люфт трансмісії: поки команда не вийшла із зони нечутливості, вал стоїть,
       і автопілот про це не дізнається — він бачить лише власну команду. */
    if (fabsf(command_deg - s->position_deg) <= s->deadband_deg) {
        return s->position_deg;
    }

    s->position_deg = ramp_slew_step(s->position_deg, command_deg,
                                     s->rate_max_dps * dt);
    return s->position_deg;
}

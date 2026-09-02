#include "energy.h"

#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

float air_density(float alt_msl_m)
{
    /* Стандартна атмосфера ISA до тропопаузи. */
    const float ratio = 1.0f - 2.25577e-5f * alt_msl_m;
    if (ratio <= 0.0f) {
        return 0.0f;
    }
    return 1.225f * powf(ratio, 4.2559f);
}

/* Коефіцієнти поляри літака: A — паразитарний опір, B — індуктивний. */
static void fixed_wing_coeffs(const Airframe *ac, float rho, float *a, float *b)
{
    const float weight_n = ac->mass_kg * GRAVITY_MPS2;

    *a = 0.5f * rho * ac->wing_area_m2 * ac->cd0;
    *b = 2.0f * weight_n * weight_n /
         (rho * (float)M_PI * ac->span_m * ac->span_m * ac->oswald_e);
}

float power_level_w(const Airframe *ac, float airspeed_mps, float rho)
{
    if (airspeed_mps < 0.1f || rho <= 0.0f) {
        return power_loiter_w(ac, rho);
    }

    float shaft_w;
    if (ac->kind == AIRFRAME_FIXED_WING) {
        float a, b;
        fixed_wing_coeffs(ac, rho, &a, &b);
        shaft_w = a * airspeed_mps * airspeed_mps * airspeed_mps + b / airspeed_mps;
    } else {
        const float weight_n = ac->mass_kg * GRAVITY_MPS2;
        const float hover_w  = powf(weight_n, 1.5f) / sqrtf(2.0f * rho * ac->disk_area_m2);
        /* Нахилений корпус коптера підставляє потоку більшу площу. */
        shaft_w = hover_w + ac->body_drag_k * airspeed_mps * airspeed_mps * airspeed_mps;
    }

    return shaft_w / ac->eta_prop;
}

float power_climb_w(const Airframe *ac, float climb_rate_mps)
{
    /* Зниження енергії не повертає: рекуперації на гвинті немає. */
    if (climb_rate_mps <= 0.0f) {
        return 0.0f;
    }
    return ac->mass_kg * GRAVITY_MPS2 * climb_rate_mps / ac->eta_prop;
}

bool speed_min_power(const Airframe *ac, float rho, float *out_mps)
{
    if (ac->kind != AIRFRAME_FIXED_WING || rho <= 0.0f) {
        return false;
    }
    float a, b;
    fixed_wing_coeffs(ac, rho, &a, &b);
    *out_mps = powf(b / (3.0f * a), 0.25f);
    return true;
}

bool speed_max_range(const Airframe *ac, float rho, float *out_mps)
{
    if (ac->kind != AIRFRAME_FIXED_WING || rho <= 0.0f) {
        return false;
    }
    float a, b;
    fixed_wing_coeffs(ac, rho, &a, &b);
    *out_mps = powf(b / a, 0.25f);
    return true;
}

float power_loiter_w(const Airframe *ac, float rho)
{
    if (rho <= 0.0f) {
        rho = 1.225f;
    }

    if (ac->kind == AIRFRAME_MULTIROTOR) {
        const float weight_n = ac->mass_kg * GRAVITY_MPS2;
        return powf(weight_n, 1.5f) / sqrtf(2.0f * rho * ac->disk_area_m2) / ac->eta_prop;
    }

    /* Літак «стоїть» на точці віражем на швидкості мінімальної потужності. */
    float v_mp = ac->airspeed_min_mps;
    (void)speed_min_power(ac, rho, &v_mp);
    if (v_mp < ac->airspeed_min_mps) {
        v_mp = ac->airspeed_min_mps;
    }
    if (v_mp > ac->airspeed_max_mps) {
        v_mp = ac->airspeed_max_mps;
    }
    return power_level_w(ac, v_mp, rho);
}

float battery_nominal_wh(const Battery *bat)
{
    return bat->nominal_v * bat->capacity_ah;
}

float battery_temp_factor(float temp_c)
{
    /* Нижче +10 °C зростає внутрішній опір і падає віддача ємності. */
    if (temp_c >= 10.0f) {
        return 1.0f;
    }
    if (temp_c <= -10.0f) {
        return 0.70f;
    }
    return 1.0f - (10.0f - temp_c) * 0.015f;
}

bool battery_current_a(const Battery *bat, float load_w, float *out_a)
{
    if (load_w <= 0.0f) {
        *out_a = 0.0f;
        return true;
    }

    const float v = bat->nominal_v;
    const float r = bat->internal_r_ohm;

    if (r <= 1.0e-4f) {
        *out_a = load_w / v;
        return true;
    }

    /* V*I - I^2*R = P; беремо менший корінь — робочу гілку. */
    const float disc = v * v - 4.0f * r * load_w;
    if (disc <= 0.0f) {
        return false;   /* більше за пікову віддачу пакета */
    }

    *out_a = (v - sqrtf(disc)) / (2.0f * r);
    return true;
}

float battery_delivered_wh(const Battery *bat, float avg_current_a)
{
    float q_ah = bat->capacity_ah;

    /* Закон Пейкерта: під більшим струмом пакет віддає менше ампер-годин.
       Втрати на R_int уже сидять усередині цього коефіцієнта. */
    if (avg_current_a > bat->ref_current_a && bat->peukert_k > 1.0f && bat->ref_current_a > 0.0f) {
        q_ah *= powf(bat->ref_current_a / avg_current_a, bat->peukert_k - 1.0f);
    }

    return q_ah * bat->nominal_v * battery_temp_factor(bat->pack_temp_c) * bat->health;
}

float battery_usable_wh(const Battery *bat, float avg_current_a)
{
    return battery_delivered_wh(bat, avg_current_a) * (1.0f - bat->reserve_margin);
}

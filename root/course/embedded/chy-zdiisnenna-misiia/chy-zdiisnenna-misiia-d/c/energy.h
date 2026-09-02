#ifndef ENERGY_H
#define ENERGY_H

#include <stdbool.h>

#define GRAVITY_MPS2 9.80665f

typedef enum {
    AIRFRAME_FIXED_WING,
    AIRFRAME_MULTIROTOR
} AirframeKind;

typedef struct {
    AirframeKind kind;
    float mass_kg;
    float eta_prop;          /* ККД гвинтомоторної групи з регуляторами, 0.55...0.70 */
    float avionics_w;        /* контролер, радіолінк, камера — не залежить від швидкості */
    float airspeed_min_mps;
    float airspeed_max_mps;
    float max_climb_mps;

    /* Літак: P = A*v^3 + B/v */
    float wing_area_m2;
    float cd0;
    float span_m;
    float oswald_e;

    /* Мультикоптер: P = P_hover + k*v^3 */
    float disk_area_m2;
    float body_drag_k;
} Airframe;

typedef struct {
    float nominal_v;
    float capacity_ah;
    float peukert_k;        /* 1.05...1.10 LiPo, 1.15...1.25 Li-Ion 18650 */
    float ref_current_a;    /* струм, за якого паспортна ємність виміряна */
    float internal_r_ohm;
    float pack_temp_c;
    float health;           /* залишковий ресурс, 0...1 */
    float reserve_margin;   /* недоторканний запас, 0.20...0.25 */
} Battery;

float air_density(float alt_msl_m);

float power_level_w(const Airframe *ac, float airspeed_mps, float rho);
float power_climb_w(const Airframe *ac, float climb_rate_mps);

/* Швидкість мінімальної потужності (тривалість) і максимальної дальності.
   false — для мультикоптера ці поняття не визначені. */
bool speed_min_power(const Airframe *ac, float rho, float *out_mps);
bool speed_max_range(const Airframe *ac, float rho, float *out_mps);

/* Потужність, яку апарат витрачає, стоячи на точці (висіння або віраж). */
float power_loiter_w(const Airframe *ac, float rho);

float battery_nominal_wh(const Battery *bat);
float battery_temp_factor(float temp_c);

/* Струм розряду під заданим навантаженням з урахуванням просадки на R_int.
   false — потужність фізично недосяжна для цієї батареї. */
bool battery_current_a(const Battery *bat, float load_w, float *out_a);

/* Скільки батарея справді віддасть за такого середнього струму
   (Пейкерт + температура + знос), без вирахування резерву. */
float battery_delivered_wh(const Battery *bat, float avg_current_a);

/* Те саме мінус недоторканний резерв — це і є бюджет місії. */
float battery_usable_wh(const Battery *bat, float avg_current_a);

#endif /* ENERGY_H */

#ifndef AHRS_H
#define AHRS_H

#include "quaternion.h"

#include <stdint.h>

#define AHRS_GRAVITY 9.80665f

/* Двошвидкісний оцінювач орієнтації для базису NED/FRD.
   Швидкий контур (1–8 кГц) накопичує приріст кута й конічну поправку,
   повільний (100–250 Гц) застосовує його одним поворотом і підтягує вертикаль. */
typedef struct {
    quat_t   q;              /* орієнтація тіло -> світ */
    vec3_t   gyro_bias;      /* оцінка зсуву нуля гіроскопа, рад/с */
    vec3_t   delta_theta;    /* сума приростів кута за поточний повільний такт */
    vec3_t   prev_delta;     /* попередній мікроприріст — для векторного добутку */
    vec3_t   coning;         /* накопичена конічна поправка */
    uint32_t fast_steps;
    float    kp;             /* сила корекції за акселерометром */
    float    ki;             /* швидкість вивчення зсуву гіроскопа */
    float    accel_gate;     /* допустиме відхилення |a| від 1g, частка */
    bool     coning_enabled;
    uint32_t accel_rejected; /* скільки разів акселерометр відхилено як недовірений */
    uint32_t faults;         /* скільки разів стан довелося скинути */
} ahrs_t;

void    ahrs_init(ahrs_t *f, float kp, float ki, bool coning_enabled);
void    ahrs_push_gyro(ahrs_t *f, vec3_t omega_body, float dt);
/* accel_body == NULL — такт лише поширює орієнтацію, без корекції вертикалі. */
void    ahrs_update(ahrs_t *f, const vec3_t *accel_body, float dt);
euler_t ahrs_euler(const ahrs_t *f);

#endif /* AHRS_H */

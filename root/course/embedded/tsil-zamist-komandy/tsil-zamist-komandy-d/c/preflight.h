#ifndef PREFLIGHT_H
#define PREFLIGHT_H

/* Передстартова перевірка цілі: геозона, здоров'я навігаційної оцінки та
   енергетичний бюджет «дійти до цілі й повернутися додому» з урахуванням вітру. */

#include "goal.h"

typedef struct {
    /* Прямокутна геозона в NED, метри. */
    float min_x;
    float min_y;
    float max_x;
    float max_y;
    float max_altitude;       /* максимальна висота над точкою старту, метри */
    vec3_t home;              /* точка повернення */
    float ekf_variance_limit; /* допустима дисперсія оцінки позиції, м² */
    float rth_voltage;        /* напруга, нижче за яку вмикається повернення, В */
    float rth_airspeed;       /* швидкість на зворотному відрізку, м/с */
    float energy_reserve;     /* коефіцієнт резерву: 1.25 = запас 25% */
} flight_envelope_t;

/* Час прольоту відрізка з урахуванням трикутника швидкостей.
   Повертає секунди або від'ємне значення, якщо трек недосяжний
   (боковий знос більший за повітряну швидкість або зустрічний вітер сильніший). */
float preflight_leg_time(vec3_t from, vec3_t to, float airspeed, vec3_t wind);

/* Енергія на «дійти й повернутися», Вт·год. out_wh може бути NULL. */
goal_check_t preflight_energy(const goal_t *g,
                              const system_state_t *sys,
                              const flight_envelope_t *env,
                              float *out_wh);

/* Повна перевірка допуску цілі. GOAL_CHECK_OK — можна виконувати. */
goal_check_t preflight_check(const goal_t *g,
                             const system_state_t *sys,
                             const flight_envelope_t *env);

#endif /* PREFLIGHT_H */

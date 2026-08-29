#ifndef PILOT_H
#define PILOT_H

#include <stdbool.h>

#include "delayline.h"
#include "pio.h"
#include "vehicle.h"

/* Квазілінійна модель Макруера:
   Y_p(s) = K_p * (T_L*s + 1)/(T_I*s + 1) * exp(-tau_p*s) * 1/(T_N*s + 1) */
typedef struct {
    float kp;      /* базове підсилення */
    float tl;      /* випередження (Lead), с */
    float ti;      /* згладжування (Lag), с */
    float tn;      /* нервово-м'язова стала, с */
    float tau_p;   /* чиста фізіологічна затримка, с */
    float omega_c; /* частота зрізу, під яку людина підганяє підсилення */
} PilotParams;

/* Закон перетину: параметри підбираються так, щоб розімкнений контур
   Y_p*Y_c біля omega_c мав вигляд інтегратора з чистою затримкою. */
PilotParams pilot_crossover_tune(ObjectDynamics obj, float omega_c);

/* Запас по фазі БЕЗ чистих затримок — те саме PM_0 з формули
   PM = PM_0 - (180/pi)*omega_c*tau. */
float pilot_phase_margin0(const PilotParams *p, ObjectDynamics obj, float omega_c);

typedef struct {
    PilotParams p;
    DelayLine reaction; /* чиста затримка сприйняття exp(-tau_p*s) */
    PioMonitor wobble;  /* людина стежить не за похибкою, а за розгойдуванням */
    float lag_state;
    float nm_state;
    float panic;        /* 0…1 — наскільки людина «додала зусилля» */
    bool  ready;
} Pilot;

bool  pilot_init(Pilot *pl, PilotParams params, float dt);
void  pilot_free(Pilot *pl);
float pilot_update(Pilot *pl, float seen_error, float now, float dt);
float pilot_panic(const Pilot *pl);
float pilot_gain(const Pilot *pl);

/* Крива Expo пульта: u = (1 - k)*x + k*x^3 */
float rc_expo(float x, float k_expo);

#endif /* PILOT_H */

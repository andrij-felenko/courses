#include "pilot.h"

#include <math.h>

#define PILOT_PI        3.14159265358979f
#define PANIC_THRESHOLD 0.18f /* рад (~10°) розмаху коливань — межа спокою */
#define PANIC_RISE      2.0f  /* переляк накопичується, с */
#define PANIC_FALL      1.0f  /* і відпускає, с */
#define PANIC_GAIN      2.0f  /* максимум K_p зростає втричі */

PilotParams pilot_crossover_tune(ObjectDynamics obj, float omega_c) {
    PilotParams p;

    p.tn = 0.10f;    /* в'язкопружність м'язів кисті */
    p.tau_p = 0.15f; /* сітківка + кора + провідність нервів */
    p.ti = 0.02f;    /* людина злегка згладжує картинку */
    p.omega_c = omega_c;

    if (obj.integrating) {
        /* Y_c = G/s: потрібний нахил уже є в об'єкті, людині вистачає чистого
           підсилення (T_L = 0). Саме тому режим Rate «дається легко». */
        p.tl = 0.0f;
        p.kp = (obj.gain > 1e-6f) ? omega_c / obj.gain : 1.0f;
    } else {
        /* Y_c = G/(T*s + 1): щоб дістати на omega_c нахил інтегратора, людина
           додає випередження й піднімає підсилення до |Y_p*Y_c| = 1. */
        float wt = obj.lag_tc * omega_c;
        float mag_c = obj.gain / sqrtf(1.0f + wt * wt);
        float lead, nm;

        p.tl = 0.05f;
        lead = sqrtf(1.0f + (p.tl * omega_c) * (p.tl * omega_c));
        nm = sqrtf(1.0f + (p.tn * omega_c) * (p.tn * omega_c));
        p.kp = (mag_c > 1e-6f) ? nm / (mag_c * lead) : 1.0f;
    }
    return p;
}

float pilot_phase_margin0(const PilotParams *p, ObjectDynamics obj, float omega_c) {
    const float k = 180.0f / PILOT_PI;
    float phase = 0.0f;

    if (obj.integrating) {
        phase -= 90.0f;                              /* вільний інтегратор */
    }
    phase -= k * atanf(obj.lag_tc * omega_c);        /* інерція об'єкта */
    phase -= k * atanf(p->tn * omega_c);             /* нервово-м'язова ланка */
    phase += k * atanf(p->tl * omega_c);             /* випередження */
    phase -= k * atanf(p->ti * omega_c);             /* згладжування */
    return 180.0f + phase;
}

bool pilot_init(Pilot *pl, PilotParams params, float dt) {
    if (!pl || dt <= 0.0f || params.ti < dt) {
        return false;
    }
    pl->p = params;
    pl->lag_state = 0.0f;
    pl->nm_state = 0.0f;
    pl->panic = 0.0f;
    pio_init(&pl->wobble, dt);
    pl->ready = delay_init(&pl->reaction, params.tau_p, 0.0f, false, dt, 0xA11CEu);
    return pl->ready;
}

void pilot_free(Pilot *pl) {
    if (pl) {
        delay_free(&pl->reaction);
        pl->ready = false;
    }
}

float pilot_update(Pilot *pl, float seen_error, float now, float dt) {
    LinkPacket in = {{0.0f}};
    float e, alpha, ratio, y, target, tc, cmd, beta;

    if (!pl || !pl->ready) {
        return 0.0f;
    }

    /* 1. Чиста фізіологічна затримка exp(-tau_p*s). Амплітуду не чіпає —
          саме тому вона така підступна: коливання проходять без послаблення. */
    in.v[LINK_STICK] = seen_error;
    delay_push(&pl->reaction, in, now);
    e = delay_pop(&pl->reaction, now).v[LINK_STICK];

    /* 2. Ланка (T_L*s + 1)/(T_I*s + 1) у формі стану:
          dx/dt = (e - x)/T_I,  y = (T_L/T_I)*e + (1 - T_L/T_I)*x. */
    alpha = dt / pl->p.ti;
    if (alpha > 1.0f) {
        alpha = 1.0f;
    }
    pl->lag_state += alpha * (e - pl->lag_state);
    ratio = pl->p.tl / pl->p.ti;
    y = ratio * e + (1.0f - ratio) * pl->lag_state;

    /* 3. Пастка підсилення. Побачивши, що апарат розгойдується, людина
          інстинктивно тисне сильніше — і сама піднімає частоту зрізу, а з
          нею й фазовий набіг затримки. */
    pio_update(&pl->wobble, e);
    target = (pio_amplitude(&pl->wobble) > PANIC_THRESHOLD) ? 1.0f : 0.0f;
    tc = (target > pl->panic) ? PANIC_RISE : PANIC_FALL;
    pl->panic += (target - pl->panic) * (dt / tc);

    cmd = pilot_gain(pl) * y;

    /* 4. Нервово-м'язовий фільтр 1/(T_N*s + 1): рука не рухається миттєво. */
    beta = dt / (pl->p.tn + dt);
    pl->nm_state += beta * (cmd - pl->nm_state);

    /* 5. Хід стіка скінченний — далі край механіки. */
    if (pl->nm_state > 1.0f) {
        pl->nm_state = 1.0f;
    } else if (pl->nm_state < -1.0f) {
        pl->nm_state = -1.0f;
    }
    return pl->nm_state;
}

float pilot_panic(const Pilot *pl) { return pl ? pl->panic : 0.0f; }

float pilot_gain(const Pilot *pl) {
    return pl ? pl->p.kp * (1.0f + PANIC_GAIN * pl->panic) : 0.0f;
}

float rc_expo(float x, float k) {
    if (k < 0.0f) {
        k = 0.0f;
    } else if (k > 1.0f) {
        k = 1.0f;
    }
    return (1.0f - k) * x + k * x * x * x;
}

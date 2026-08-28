#include <complex.h>
#include <math.h>

// Інерційна ланка (полюс): 1 / (1 + jωτ)
static double complex pole(double w, double tau) {
    return 1.0 / (1.0 + I * w * tau);
}

// Чистий мертвий час (у т.ч. пів-такту утримки + обчислення): e^(-jωΔt)
static double complex dead_time(double w, double dt) {
    return cexp(-I * w * dt);   // модуль 1, фаза -ωΔt
}

// П-складова регулятора — просто множник Kp (дійсний, фаза 0)
// І-складова: Ki / (jω);  Д з фільтром: (Kd·jω) / (1 + jω·τ_d)
static double complex pid(double w, double Kp, double Ki, double Kd, double tau_d) {
    double complex integ  = (w > 0.0) ? (Ki / (I * w)) : 0.0;
    double complex deriv  = (Kd * I * w) / (1.0 + I * w * tau_d);
    return Kp + integ + deriv;
}

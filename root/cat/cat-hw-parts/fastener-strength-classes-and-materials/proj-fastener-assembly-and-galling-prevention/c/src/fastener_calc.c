#include "../include/fastener_calc.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Обчислення розрахункової площі поперечного перерізу As */
double fastener_calc_stress_area(const ThreadSpec* thread) {
    if (!thread) return 0.0;
    double d2 = thread->d2;
    double d3 = thread->d3;
    return (M_PI / 4.0) * pow((d2 + d3) / 2.0, 2.0);
}

/* Обчислення сили попереднього натягу Fp */
double fastener_calc_preload(const FastenerMaterial* material, const ThreadSpec* thread, const FrictionParams* friction) {
    if (!material || !thread || !friction) return 0.0;
    double As = fastener_calc_stress_area(thread);
    return friction->preload_factor * material->yield_strength * As;
}

/* Обчислення моменту затягування T */
double fastener_calc_tightening_torque(double f_p, const ThreadSpec* thread, const FrictionParams* friction) {
    if (!thread || !friction) return 0.0;
    /* T = F_p * (0.16 * pitch + 0.58 * d2 * mu_thread + 0.5 * d_head * mu_bearing)
     * Результат у Н*мм, ділимо на 1000.0 для отримання Н*м */
    double term = 0.16 * thread->pitch 
                + 0.58 * thread->d2 * friction->mu_thread 
                + 0.5 * thread->d_head * friction->mu_bearing;
    return (f_p * term) / 1000.0;
}

/* Обчислення пружного подовження стержня delta L */
double fastener_calc_elongation(double f_p, const FastenerMaterial* material, const ThreadSpec* thread, double as) {
    if (!material || !thread || as <= 0.0) return 0.0;
    return (f_p * thread->clamped_length) / (material->young_modulus * as);
}

/* Обчислення еквівалентного напруження фон Мізеса */
double fastener_calc_von_mises(double sigma_tension, double tau_torsion) {
    return sqrt(pow(sigma_tension, 2.0) + 3.0 * pow(tau_torsion, 2.0));
}

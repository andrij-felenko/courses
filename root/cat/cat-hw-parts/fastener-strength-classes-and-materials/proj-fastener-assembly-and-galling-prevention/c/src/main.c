#include <stdio.h>
#include "../include/fastener_calc.h"

void run_analysis(const char* title, const FastenerMaterial* mat, const ThreadSpec* thread, const FrictionParams* friction) {
    printf("==================================================\n");
    printf(" Демонстрація: %s\n", title);
    printf(" Матеріал: %s\n", mat->name);
    printf(" Межа плинності Re: %.1f МПа | Модуль E: %.1f МПа\n", mat->yield_strength, mat->young_modulus);
    printf(" Різьба: M%.1f, Крок: %.2f мм, Довжина: %.1f мм\n", thread->nominal_diameter, thread->pitch, thread->clamped_length);
    printf(" Тертя: різьба=%.2f, опорна поверхня=%.2f\n", friction->mu_thread, friction->mu_bearing);
    printf("--------------------------------------------------\n");

    double As = fastener_calc_stress_area(thread);
    printf(" Площа поперечного перерізу As:    %.3f мм^2\n", As);

    double F_p = fastener_calc_preload(mat, thread, friction);
    printf(" Сила попереднього натягу F_p:     %.2f Н (%.2f кН)\n", F_p, F_p / 1000.0);

    double T = fastener_calc_tightening_torque(F_p, thread, friction);
    printf(" Момент затягування T:             %.2f Н*м\n", T);

    double delta_L = fastener_calc_elongation(F_p, mat, thread, As);
    printf(" Пружне подовження delta L:       %.4f мм\n", delta_L);

    double sigma_tension = F_p / As;
    double T_thread = F_p * (0.16 * thread->pitch + 0.58 * thread->d2 * friction->mu_thread) / 1000.0;
    double tau_torsion = (16.0 * (T_thread * 1000.0)) / (3.141592653589793 * pow(thread->d3, 3.0));

    double sigma_vm = fastener_calc_von_mises(sigma_tension, tau_torsion);
    printf(" Напруження розтягу sigma_t:       %.2f МПа\n", sigma_tension);
    printf(" Напруження кручення tau_torsion:  %.2f МПа\n", tau_torsion);
    printf(" Еквівалентне напруження sigma_vm: %.2f МПа\n", sigma_vm);
    
    if (sigma_vm <= mat->yield_strength) {
        printf(" Статус міцності: УСПІХ (у межах пружності)\n");
    } else {
        printf(" Статус міцності: УВАГА! Перевищено межу плинності!\n");
    }
    printf("==================================================\n\n");
}

int main(void) {
    printf("=== ПОРІВНЯЛЬНИЙ РОЗРАХУНОК РІЗЬБОВИХ З'ЄДНАНЬ M20 ===\n\n");

    ThreadSpec m20 = {
        .nominal_diameter = 20.0,
        .pitch = 2.5,
        .d2 = 18.376,
        .d3 = 16.933,
        .d_head = 30.0,
        .clamped_length = 100.0
    };

    FastenerMaterial steel_10_9 = {
        .name = "Сталь 10.9",
        .yield_strength = 900.0,
        .ultimate_strength = 1040.0,
        .young_modulus = 210000.0
    };

    FastenerMaterial stainless_a4 = {
        .name = "Нержавіюча сталь A4-70",
        .yield_strength = 450.0,
        .ultimate_strength = 700.0,
        .young_modulus = 200000.0
    };

    FastenerMaterial titanium_gr5 = {
        .name = "Титан Grade 5 (Ti-6Al-4V)",
        .yield_strength = 880.0,
        .ultimate_strength = 950.0,
        .young_modulus = 114000.0
    };

    FrictionParams dry = { .mu_thread = 0.14, .mu_bearing = 0.15, .preload_factor = 0.7 };
    FrictionParams lubricated = { .mu_thread = 0.10, .mu_bearing = 0.10, .preload_factor = 0.7 };

    run_analysis("Сталь 10.9 (Сухий контакт)", &steel_10_9, &m20, &dry);
    run_analysis("Сталь 10.9 (Зі змащенням)", &steel_10_9, &m20, &lubricated);
    run_analysis("Нержавійка A4-70 (Зі змащенням)", &stainless_a4, &m20, &lubricated);
    run_analysis("Титан Grade 5 (Зі змащенням)", &titanium_gr5, &m20, &lubricated);

    return 0;
}

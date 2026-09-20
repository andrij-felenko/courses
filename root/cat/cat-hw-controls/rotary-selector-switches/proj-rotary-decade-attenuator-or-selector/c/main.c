#include "attenuator_calc.h"
#include <stdio.h>
#include <stdlib.h>

static void print_attenuator_table(const char *title, const attenuator_step_t *steps, size_t count) {
    printf("========================================================================================\n");
    printf("%s\n", title);
    printf("========================================================================================\n");
    printf("| Крок | Ціль (дБ) | Ідеал R (Ом) | E-ряд R (Ом) | Факт (дБ) | Похибка (дБ) | Похибка (%%) |\n");
    printf("+------+-----------+--------------+--------------+-----------+--------------+-------------+\n");

    for (size_t i = 0; i < count; i++) {
        printf("|  %2zu  |  %7.2f  |   %9.2f  |   %9.2f  |  %7.2f  |   %9.3f  |   %8.2f%% |\n",
               steps[i].step_index,
               steps[i].ideal_attenuation_db,
               steps[i].ideal_resistor_ohm,
               steps[i].actual_resistor_ohm,
               steps[i].actual_attenuation_db,
               steps[i].error_db,
               steps[i].error_percent);
    }
    printf("========================================================================================\n\n");
}

int main(void) {
    printf("--- Розрахунок логарифмічного атенюатора на галетній секції (12 позицій) ---\n\n");

    // Конфігурація 12-позиційного атенюатора 10 кОм з ряду E96
    attenuator_config_t config_e96 = {
        .total_resistance_ohm = 10000.0,
        .source_impedance_ohm = 50.0,     // Вихідний опір джерела 50 Ом
        .load_impedance_ohm = 100000.0,   // Навантаження підсилювача 100 кОм
        .max_attenuation_db = -55.0,      // Діапазон згасання від -55 дБ до 0 дБ
        .num_steps = 12,
        .taper = ATTENUATION_LOGARITHMIC,
        .eseries = ESERIES_E96
    };

    attenuator_step_t steps_e96[ATTENUATOR_MAX_STEPS];
    size_t count_e96 = 0;

    if (attenuator_calculate(&config_e96, steps_e96, ATTENUATOR_MAX_STEPS, &count_e96)) {
        print_attenuator_table("Розрахунок з прецизійними резисторами рядів E96 (допуск 1%)", steps_e96, count_e96);
    } else {
        fprintf(stderr, "Помилка розрахунку атенюатора E96\n");
    }

    // Порівняльний розрахунок із задіюванням стандартного ряду E24 (допуск 5%)
    attenuator_config_t config_e24 = config_e96;
    config_e24.eseries = ESERIES_E24;

    attenuator_step_t steps_e24[ATTENUATOR_MAX_STEPS];
    size_t count_e24 = 0;

    if (attenuator_calculate(&config_e24, steps_e24, ATTENUATOR_MAX_STEPS, &count_e24)) {
        print_attenuator_table("Розрахунок зі стандартними резисторами рядів E24 (допуск 5%)", steps_e24, count_e24);
    } else {
        fprintf(stderr, "Помилка розрахунку атенюатора E24\n");
    }

    return 0;
}

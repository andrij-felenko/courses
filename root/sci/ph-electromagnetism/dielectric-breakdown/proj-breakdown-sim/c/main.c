#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Фізичні константи та параметри діелектрика (наприклад, SiO2)
typedef struct {
    double E_field;       // Напруженість поля [В/м]
    double thickness;     // Товщина шару [м]
    double T_env;         // Температура довкілля [К]
    double E_g;           // Ширина забороненої зони [еВ]
    double alpha_0;       // Базовий коефіцієнт іонізації [1/м]
    double B_param;       // Параметр поля іонізації [В/м]
    double sigma_0;       // Початкова провідність [См/м]
    double E_act;         // Енергія активації провідності [еВ]
    double C_vol;         // Об'ємна теплоємність [Дж/(м³·К)]
    double lambda_heat;   // Коефіцієнт тепловідведення [Вт/(м²·К)]
} DielectricParams;

typedef struct {
    double time_s;
    double n_electrons;
    double temperature_K;
    bool is_broken_down;
} SimulationResult;

SimulationResult run_breakdown_simulation(const DielectricParams* params, double dt_s, double max_time_s) {
    const double k_B_eV = 8.617333e-5; // Стала Больцмана в еВ/К

    double n_e = 1.0e10;  // Початкова концентрація вільних носіїв [1/м³]
    double T = params->T_env;
    double time = 0.0;
    bool breakdown = false;

    double max_n_crit = 1.0e24; // Критична концентрація лавини
    double max_T_crit = params->T_env + 1000.0; // Критичний нагрів

    while (time < max_time_s) {
        // 1. Коефіцієнт ударної іонізації Таунсенда α(E)
        double alpha = params->alpha_0 * exp(-params->B_param / params->E_field);
        
        // 2. Дрейфова швидкість електронів v_d ≈ μ * E
        double mobility = 0.0020; // [м²/(В·с)]
        double v_d = mobility * params->E_field;

        // 3. Приріст носіїв за рахунок ударної іонізації
        double dn_dt = alpha * v_d * n_e;
        n_e += dn_dt * dt_s;

        // 4. Температурна залежність провідності σ(T)
        double sigma = params->sigma_0 * exp(-params->E_act / (k_B_eV * T));
        
        // 5. Виділення тепла (Джоуль-Ленц) та тепловідведення
        double Q_gen = sigma * params->E_field * params->E_field;
        double Q_loss = (params->lambda_heat / params->thickness) * (T - params->T_env);
        
        double dT_dt = (Q_gen - Q_loss) / params->C_vol;
        T += dT_dt * dt_s;

        // Перевірка порогових умов пробою
        if (n_e >= max_n_crit || T >= max_T_crit) {
            breakdown = true;
            break;
        }

        time += dt_s;
    }

    SimulationResult res = { time, n_e, T, breakdown };
    return res;
}

int main(void) {
    DielectricParams SiO2 = {
        .E_field = 8.5e8,       // 8.5 МВ/см (поблизу порогу SiO2)
        .thickness = 100.0e-9,  // 100 нм
        .T_env = 300.0,         // 300 К (27 °C)
        .E_g = 9.0,             // 9 еВ
        .alpha_0 = 1.0e8,
        .B_param = 3.0e9,
        .sigma_0 = 1.0e-3,
        .E_act = 0.6,
        .C_vol = 1.6e6,
        .lambda_heat = 5000.0
    };

    printf("=== Моделювання пробою SiO2 плівки (100 нм) ===\n");
    SimulationResult res = run_breakdown_simulation(&SiO2, 1.0e-13, 1.0e-8);

    if (res.is_broken_down) {
        printf("СТАТУС: Пробій зафіксовано!\n");
        printf("Час до пробою: %.3e с (%.3f пс)\n", res.time_s, res.time_s * 1.0e12);
        printf("Фінальна концентрація електронів: %.3e 1/м³\n", res.n_electrons);
        printf("Фінальна температура: %.1f К\n", res.temperature_K);
    } else {
        printf("СТАТУС: Діелектрик витримав поле без пробою.\n");
    }

    return 0;
}

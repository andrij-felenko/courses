#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Структура параметрів вхідного каскаду перетворювача
typedef struct {
    double v_rms_nominal;     // Номінальна напруга мережі, В (напр. 230 В)
    double c_filter_uf;       // Ємність накопичувача, мкФ (напр. 470 мкФ)
    double r_inrush_ohms;     // Холодний опір NTC + дроти, Ом (напр. 10.5 Ом)
    double p_load_watts;      // Вихідна потужність джерела, Вт (напр. 200 Вт)
    double efficiency;        // ККД перетворювача, 0..1 (напр. 0.88)
    double power_factor;      // Коефіцієнт потужності PF, 0..1 (напр. 0.95)
    double t_ambient_c;       // Робоча температура всередині корпусу, °C
    int    target_cycles;     // Цільовий ресурс за кількістю увімкнень (напр. 50000)
} PowerStageParams;

// Структура каталожного запобіжника
typedef struct {
    const char* part_number;  // Маркування
    double current_rating_a;  // Номінальний струм, А
    double i2t_melting_a2s;   // Паспортний інтеграл плавлення Melting I²t, А²·с
} FuseCandidate;

// База даних стандартних повільних запобіжників серії 5x20 мм (Time-Lag / T)
static const FuseCandidate FUSE_CATALOG[] = {
    { "5x20mm T1.0A 250V",  1.0,   2.8  },
    { "5x20mm T1.6A 250V",  1.6,   6.5  },
    { "5x20mm T2.0A 250V",  2.0,  11.2  },
    { "5x20mm T2.5A 250V",  2.5,  18.5  },
    { "5x20mm T3.15A 250V", 3.15, 29.0  },
    { "5x20mm T4.0A 250V",  4.0,  46.0  },
    { "5x20mm T5.0A 250V",  5.0,  78.0  },
    { "5x20mm T6.3A 250V",  6.3, 130.0  }
};
static const int FUSE_CATALOG_SIZE = sizeof(FUSE_CATALOG) / sizeof(FUSE_CATALOG[0]);

// Розрахунок коефіцієнта стійкості до повторних імпульсів (Pulse Derating)
double calculate_pulse_derating_factor(int cycles) {
    if (cycles <= 1) return 1.0;
    if (cycles <= 10) return 0.70;
    if (cycles <= 100) return 0.50;
    if (cycles <= 1000) return 0.38;
    if (cycles <= 10000) return 0.29;
    if (cycles <= 50000) return 0.23;
    if (cycles <= 100000) return 0.20;
    // Апроксимація для більшої кількості циклів
    return 1.0 * pow((double)cycles, -0.14);
}

// Температурний коефіцієнт для повільних запобіжників
double calculate_temperature_derating(double temp_c) {
    if (temp_c <= 25.0) return 1.0;
    // Лінійне зниження струму: ~0.35% на кожен градус понад 25 °C
    double factor = 1.0 - 0.0035 * (temp_c - 25.0);
    return factor > 0.5 ? factor : 0.5;
}

int main(void) {
    PowerStageParams sys = {
        .v_rms_nominal = 230.0,
        .c_filter_uf = 470.0,
        .r_inrush_ohms = 10.5,
        .p_load_watts = 200.0,
        .efficiency = 0.88,
        .power_factor = 0.95,
        .t_ambient_c = 55.0,
        .target_cycles = 50000
    };

    printf("=== РОЗРАХУНОК ВХІДНОГО ЗАПОБІЖНИКА SMPS ===\n");

    // 1. Пікова напруга та струм заряду
    double v_peak = sys.v_rms_nominal * sqrt(2.0);
    double i_inrush_peak = v_peak / sys.r_inrush_ohms;
    double c_farads = sys.c_filter_uf * 1e-6;
    double tau_seconds = sys.r_inrush_ohms * c_farads;

    // 2. Інтеграл Джоуля пускового імпульсу: I²t = 0.5 * I_pk² * tau
    double i2t_inrush = 0.5 * (i_inrush_peak * i_inrush_peak) * tau_seconds;

    // 3. Коефіцієнт циклічної втоми та мінімальний необхідний Melting I²t
    double k_pulse = calculate_pulse_derating_factor(sys.target_cycles);
    double i2t_required = i2t_inrush / k_pulse;

    // 4. Тривалий робочий струм та температурний дерайтинг
    double p_in = sys.p_load_watts / sys.efficiency;
    // Найнижча напруга мережі (наприклад, 180 В)
    double v_rms_min = 180.0;
    double i_rms_load = p_in / (v_rms_min * sys.power_factor);

    double k_temp = calculate_temperature_derating(sys.t_ambient_c);
    // Нормативний запас 75% за стандартом IEC/UL
    double i_nom_required = i_rms_load / (k_temp * 0.75);

    printf("Пікова напруга мережі: %.1f В\n", v_peak);
    printf("Піковий пусковий струм: %.2f А (стала часу tau = %.2f мс)\n",
           i_inrush_peak, tau_seconds * 1000.0);
    printf("Пускова енергія I²t_inrush: %.3f А²·с\n", i2t_inrush);
    printf("Коефіцієнт циклічного дерайтингу (%d пусків): %.2f (запас %.2f×)\n",
           sys.target_cycles, k_pulse, 1.0 / k_pulse);
    printf("Мінімальний паспортний Melting I²t: >= %.2f А²·с\n", i2t_required);
    printf("Робочий струм навантаження: %.2f А (T_amb = %.0f °C, K_temp = %.2f)\n",
           i_rms_load, sys.t_ambient_c, k_temp);
    printf("Мінімальний номінальний струм: >= %.2f А\n\n", i_nom_required);

    // 5. Підбір відповідного запобіжника з каталогу
    const FuseCandidate* selected_fuse = NULL;
    for (int i = 0; i < FUSE_CATALOG_SIZE; ++i) {
        if (FUSE_CATALOG[i].current_rating_a >= i_nom_required &&
            FUSE_CATALOG[i].i2t_melting_a2s >= i2t_required) {
            selected_fuse = &FUSE_CATALOG[i];
            break;
        }
    }

    if (selected_fuse != NULL) {
        printf(">>> РЕЗУЛЬТАТ ПІДБОРУ: ОБРАНО %s <<<\n", selected_fuse->part_number);
        printf("  Паспортний номінал струму: %.2f А (запас %.1f%%)\n",
               selected_fuse->current_rating_a,
               (selected_fuse->current_rating_a / i_nom_required - 1.0) * 100.0);
        printf("  Паспортний Melting I²t: %.1f А²·с (запас %.1f%%)\n",
               selected_fuse->i2t_melting_a2s,
               (selected_fuse->i2t_melting_a2s / i2t_required - 1.0) * 100.0);
    } else {
        printf("ПОМИЛКА: Жоден стандартний запобіжник 5x20 мм не задовольняє обидва критерії.\n");
    }

    return 0;
}

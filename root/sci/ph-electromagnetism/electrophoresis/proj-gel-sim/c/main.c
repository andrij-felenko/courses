#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int length_bp;        /* Довжина фрагмента у парах основ */
    double position_mm;   /* Поточна координата смуги (мм) */
    double mobility;      /* Розрахована рухливість */
} DnaFragment;

typedef struct {
    double length_mm;     /* Довжина гелевого блоку (мм) */
    double gel_concentration; /* Концентрація агарози (%) */
    double electric_field_v_cm; /* Напруженість поля (В/см) */
    double temperature_c;  /* Поточна температура гелю (°C) */
    double ambient_temp_c;  /* Температура довкілля (°C) */
    double conductivity;   /* Електропровідність буферу (См/м) */
} GelChamber;

/* Обчислення рухливості за моделлю Огстона */
double calculate_mobility(int length_bp, double gel_conc) {
    double v0 = 3.5e-4; /* Базова рухливість у вільному розчині (см² / (В · с)) */
    double k_retard = 0.045 * gel_conc;
    return v0 * exp(-k_retard * sqrt((double)length_bp));
}

/* Крок симуляції часом dt (секунди) */
void simulate_step(GelChamber* chamber, DnaFragment* fragments, int count, double dt_sec) {
    /* 1. Гідродинамічний рух смуг ДНК */
    for (int i = 0; i < count; i++) {
        /* Враховуємо температурний коефіцієнт в'язкості (зменшення в'язкості при нагріванні) */
        double temp_factor = 1.0 + 0.02 * (chamber->temperature_c - 25.0);
        double current_v = fragments[i].mobility * chamber->electric_field_v_cm * temp_factor;
        /* Переведення швидкості з см/с у мм/с (* 10.0) */
        fragments[i].position_mm += current_v * 10.0 * dt_sec;
    }

    /* 2. Тепловий баланс (Джоулеве нагрівання та охолодження) */
    double field_v_m = chamber->electric_field_v_cm * 100.0;
    double joule_power_w_m3 = chamber->conductivity * field_v_m * field_v_m; /* Вт / м³ */
    
    /* Константи теплообміну для стандартної камери */
    double heat_capacity = 4184.0; /* Дж / (кг · °C) */
    double density = 1000.0;       /* кг / м³ */
    double cooling_coeff = 0.05;   /* 1 / с */

    double dT_dt = (joule_power_w_m3 / (density * heat_capacity)) - 
                   cooling_coeff * (chamber->temperature_c - chamber->ambient_temp_c);
    
    chamber->temperature_c += dT_dt * dt_sec;
}

int main(void) {
    GelChamber gel = {
        .length_mm = 100.0,
        .gel_concentration = 1.0, /* 1% агарозний гель */
        .electric_field_v_cm = 5.0, /* 5 В/см */
        .temperature_c = 22.0,
        .ambient_temp_c = 22.0,
        .conductivity = 0.15
    };

    DnaFragment ladder[] = {
        { .length_bp = 1000, .position_mm = 0.0, .mobility = 0.0 },
        { .length_bp = 500,  .position_mm = 0.0, .mobility = 0.0 },
        { .length_bp = 200,  .position_mm = 0.0, .mobility = 0.0 },
        { .length_bp = 100,  .position_mm = 0.0, .mobility = 0.0 }
    };
    int num_fragments = sizeof(ladder) / sizeof(ladder[0]);

    for (int i = 0; i < num_fragments; i++) {
        ladder[i].mobility = calculate_mobility(ladder[i].length_bp, gel.gel_concentration);
    }

    printf("=== Симуляція гелевого електрофорезу (C) ===\n");
    printf("Напруженість поля: %.1f В/см, Гель: %.1f%%\n\n", gel.electric_field_v_cm, gel.gel_concentration);

    double dt = 10.0; /* Крок 10 секунд */
    double total_time = 1800.0; /* 30 хвилин */

    for (double t = 0; t <= total_time; t += dt) {
        simulate_step(&gel, ladder, num_fragments, dt);
        if ((int)t % 600 == 0) {
            printf("Час: %4.0f с | Температура гелю: %.2f °C\n", t, gel.temperature_c);
            for (int i = 0; i < num_fragments; i++) {
                printf("  Фрагмент %4d п.н. -> Координата: %5.2f мм\n", 
                       ladder[i].length_bp, ladder[i].position_mm);
            }
            printf("----------------------------------------\n");
        }
    }

    return 0;
}

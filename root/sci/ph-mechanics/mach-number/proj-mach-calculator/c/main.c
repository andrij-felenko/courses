#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Константи сухого повітря за стандартних умов ISA */
#define DEFAULT_GAMMA 1.4
#define DEFAULT_R_GAS 287.058

typedef enum {
    REGIME_SUBSONIC_INCOMPRESSIBLE,
    REGIME_SUBSONIC_COMPRESSIBLE,
    REGIME_TRANSONIC,
    REGIME_SUPERSONIC,
    REGIME_HYPERSONIC
} FlowRegime;

typedef struct {
    double speed_of_sound;      /* м/с */
    double mach_number;         /* безрозмірне */
    FlowRegime regime;
    double total_temperature;   /* К */
    double total_pressure;      /* Па */
    double prandtl_glauert;     /* фактор стисливості, 0 якщо M >= 1 */
} GasDynamicsResult;

/* Головна функція розрахунку газодинамічних параметрів */
int compute_gas_dynamics(double velocity, double static_temp_k, double static_press_pa,
                         double gamma, double r_gas, GasDynamicsResult *out_res) {
    if (!out_res || static_temp_k <= 0.0 || static_press_pa <= 0.0 || gamma <= 1.0 || r_gas <= 0.0 || velocity < 0.0) {
        return -1; /* Помилка некоректних вхідних даних */
    }

    /* 1. Локальна швидкість звуку */
    double a = sqrt(gamma * r_gas * static_temp_k);
    out_res->speed_of_sound = a;

    /* 2. Число Маха */
    double M = velocity / a;
    out_res->mach_number = M;

    /* 3. Класифікація режиму */
    if (M < 0.3) {
        out_res->regime = REGIME_SUBSONIC_INCOMPRESSIBLE;
    } else if (M < 0.8) {
        out_res->regime = REGIME_SUBSONIC_COMPRESSIBLE;
    } else if (M <= 1.2) {
        out_res->regime = REGIME_TRANSONIC;
    } else if (M <= 5.0) {
        out_res->regime = REGIME_SUPERSONIC;
    } else {
        out_res->regime = REGIME_HYPERSONIC;
    }

    /* 4. Параметри гальмування */
    double temp_ratio = 1.0 + ((gamma - 1.0) / 2.0) * M * M;
    out_res->total_temperature = static_temp_k * temp_ratio;
    
    double press_ratio = pow(temp_ratio, gamma / (gamma - 1.0));
    out_res->total_pressure = static_press_pa * press_ratio;

    /* 5. Поправка Прандтля-Ґлауерта */
    if (M < 0.95) {
        out_res->prandtl_glauert = 1.0 / sqrt(1.0 - M * M);
    } else {
        out_res->prandtl_glauert = 0.0; /* Не застосовується у білязвуковому та надзвуковому режимах */
    }

    return 0;
}

const char* regime_to_string(FlowRegime r) {
    switch (r) {
        case REGIME_SUBSONIC_INCOMPRESSIBLE: return "Дозвуковий (нестислий)";
        case REGIME_SUBSONIC_COMPRESSIBLE:   return "Дозвуковий (стислий)";
        case REGIME_TRANSONIC:               return "Трансзвуковий";
        case REGIME_SUPERSONIC:              return "Надзвуковий";
        case REGIME_HYPERSONIC:              return "Гіперзвуковий";
        default:                             return "Невідомий";
    }
}

int main(void) {
    double v = 550.0;           /* 550 м/с (близько 1980 км/год) */
    double T_static = 216.65;   /* Стратосфера -56.5 °C */
    double p_static = 22632.0;  /* 22.63 кПа на висоті 11 км */

    GasDynamicsResult res;
    if (compute_gas_dynamics(v, T_static, p_static, DEFAULT_GAMMA, DEFAULT_R_GAS, &res) == 0) {
        printf("Швидкість потоку:    %.1f м/с\n", v);
        printf("Швидкість звуку:     %.2f м/с\n", res.speed_of_sound);
        printf("Число Маха:          %.3f\n", res.mach_number);
        printf("Режим течії:         %s\n", regime_to_string(res.regime));
        printf("Повна температура:   %.2f K (Статична: %.2f K)\n", res.total_temperature, T_static);
        printf("Повний тиск:         %.1f Па (Статичний: %.1f Па)\n", res.total_pressure, p_static);
    }

    return 0;
}

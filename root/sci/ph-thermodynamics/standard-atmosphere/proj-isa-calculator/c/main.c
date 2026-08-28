#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Константи ISA ISO 2533 / US Standard 1976 */
#define ISA_G0        9.80665
#define ISA_R_SPEC    287.05287
#define ISA_RE        6356766.0
#define ISA_GAMMA     1.40
#define ISA_BETA_S    1.458e-6
#define ISA_SUTHERLAND 110.4

#define ISA_T0        288.15
#define ISA_P0        101325.0
#define ISA_RHO0      1.2250

#define ISA_NUM_LAYERS 7
#define ISA_MAX_H     84852.0

/* Результат розрахунку ISA */
typedef struct {
    double h_geopotential; /* м */
    double z_geometric;    /* м */
    double temperature;    /* K */
    double temp_celsius;   /* °C */
    double pressure;       /* Па */
    double density;        /* кг/м³ */
    double sound_speed;    /* м/с */
    double dynamic_visc;   /* кг/(м·с) */
    double kinematic_visc; /* м²/с */
} isa_state_t;

/* Структура шару атмосфери */
typedef struct {
    double h_base;   /* Геопотенціальна висота основи, м */
    double t_base;   /* Температура на основі, K */
    double lapse;    /* Градієнт dT/dh, K/м */
    double p_base;   /* Тиск на основі, Па */
} isa_layer_t;

/* Фіксована таблиця 7 шарів ISA */
static const isa_layer_t ISA_LAYERS[ISA_NUM_LAYERS] = {
    {     0.0, 288.15, -0.00650, 101325.0  }, /* 0: Тропосфера */
    { 11000.0, 216.65,  0.00000,  22632.1  }, /* 1: Тропопауза / Нижня стратосфера */
    { 20000.0, 216.65,  0.00100,   5474.89 }, /* 2: Середня стратосфера 1 */
    { 32000.0, 228.65,  0.00280,    868.019}, /* 3: Середня стратосфера 2 */
    { 47000.0, 270.65,  0.00000,    110.906}, /* 4: Стратопауза */
    { 51000.0, 270.65, -0.00280,     66.9389},/* 5: Середня мезосфера */
    { 71000.0, 214.65, -0.00200,      3.95642}/* 6: Верхня мезосфера */
};

/* Перетворення геометричної висоти Z у геопотенціальну h */
double isa_z_to_h(double z_m) {
    return (ISA_RE * z_m) / (ISA_RE + z_m);
}

/* Перетворення геопотенціальної висоти h у геометричну Z */
double isa_h_to_z(double h_m) {
    if (h_m >= ISA_RE) return ISA_RE * 100.0; /* захист від ділення на нуль */
    return (ISA_RE * h_m) / (ISA_RE - h_m);
}

/* Основна функція розрахунку стану атмосфери ISA за висотою h */
bool isa_evaluate_h(double h_m, isa_state_t *res) {
    if (!res || h_m < 0.0 || h_m > ISA_MAX_H) {
        return false;
    }

    /* Знаходимо шар */
    int idx = 0;
    for (int i = 0; i < ISA_NUM_LAYERS - 1; i++) {
        if (h_m >= ISA_LAYERS[i + 1].h_base) {
            idx = i + 1;
        } else {
            break;
        }
    }

    const isa_layer_t *layer = &ISA_LAYERS[idx];
    double dh = h_m - layer->h_base;
    double T = layer->t_base + layer->lapse * dh;
    double P = 0.0;

    if (fabs(layer->lapse) < 1e-10) {
        /* Ізотермічний шар */
        P = layer->p_base * exp(- (ISA_G0 * dh) / (ISA_R_SPEC * layer->t_base));
    } else {
        /* Градієнтний шар */
        double n_p = - ISA_G0 / (ISA_R_SPEC * layer->lapse);
        P = layer->p_base * pow(T / layer->t_base, n_p);
    }

    double rho = P / (ISA_R_SPEC * T);
    double a = sqrt(ISA_GAMMA * ISA_R_SPEC * T);

    /* В'язкість Сазерленда */
    double mu = (ISA_BETA_S * pow(T, 1.5)) / (T + ISA_SUTHERLAND);
    double nu = mu / rho;

    res->h_geopotential = h_m;
    res->z_geometric = isa_h_to_z(h_m);
    res->temperature = T;
    res->temp_celsius = T - 273.15;
    res->pressure = P;
    res->density = rho;
    res->sound_speed = a;
    res->dynamic_visc = mu;
    res->kinematic_visc = nu;

    return true;
}

/* Обчислення барометричної висоти в тропосфері за тиском P (Па) */
double isa_pressure_altitude(double pressure_pa) {
    if (pressure_pa <= 0.0) return 0.0;
    double n_p_inv = 1.0 / 5.25588;
    return (ISA_T0 / 0.0065) * (1.0 - pow(pressure_pa / ISA_P0, n_p_inv));
}

/* Перерахунок індикаторної швидкості CAS у істинну TAS */
double isa_cas_to_tas(double cas_ms, double density_kg_m3) {
    if (density_kg_m3 <= 0.0) return cas_ms;
    return cas_ms * sqrt(ISA_RHO0 / density_kg_m3);
}

int main(void) {
    isa_state_t state;
    double test_h = 10000.0; /* 10 км */

    if (isa_evaluate_h(test_h, &state)) {
        printf("--- ISA стан на h = %.1f м (Z = %.1f м) ---\n", state.h_geopotential, state.z_geometric);
        printf("Температура: %.2f K (%.2f °C)\n", state.temperature, state.temp_celsius);
        printf("Тиск:        %.1f Па (%.2f гПа)\n", state.pressure, state.pressure / 100.0);
        printf("Густина:     %.4f кг/м³\n", state.density);
        printf("Шв. звуку:   %.1f м/с (%.1f км/год)\n", state.sound_speed, state.sound_speed * 3.6);
        printf("Динам. в'язкість: %.3e кг/(м·с)\n", state.dynamic_visc);

        double cas = 150.0; /* 150 м/с CAS */
        double tas = isa_cas_to_tas(cas, state.density);
        printf("Швидкість CAS = %.1f м/с -> TAS = %.1f м/с\n", cas, tas);
    }
    return 0;
}

#include <stdio.h>
#include <math.h>

/* Фізичні константи */
#define FARADAY_CONST 96485.33215  /* Кл/моль */
#define MOLAR_GAS_VOL 22.414       /* л/моль за НУ */

/* Структура параметрів речовини */
typedef struct {
    double molar_mass_g;    /* Молярна маса, г/моль */
    int valence;            /* Заряд іона z */
    double density_g_cm3;   /* Густина металу, г/см³ */
    double faraday_eff;     /* Вихід за струмом (0.0 .. 1.0) */
} IonParams;

/* Структура геометрії та електроліту */
typedef struct {
    double area_cm2;        /* Площа електрода, см² */
    double distance_cm;     /* Відстань між електродами, см */
    double resist_ohm_cm;   /* Питомий опір електроліту, Ом·см */
    double bubble_fraction; /* Газовміст ε (0.0 .. 0.3) */
    double e0_cell_v;       /* Рівноважна напруга розкладу, В */
    double tafel_a_anode;   /* Константа Тафеля a для анода, В */
    double tafel_b_anode;   /* Константа Тафеля b для анода, В */
    double tafel_a_cath;    /* Константа Тафеля a для катода, В */
    double tafel_b_cath;    /* Константа Тафеля b для катода, В */
} CellConfig;

/* Результати моделювання */
typedef struct {
    double total_charge_c;      /* Пропущений заряд, Кл */
    double mass_deposited_g;    /* Маса осадженого металу, г */
    double thickness_um;        /* Товщина покриття, мкм */
    double gas_volume_liters;   /* Об'єм виділеного газу при НУ, л */
    double overpotential_anode; /* Анодна перенапруга, В */
    double overpotential_cath;  /* Катодна перенапруга, В */
    double ohmic_drop_v;        /* Омічне падіння напруги, В */
    double applied_voltage_v;   /* Повна прикладена напруга, В */
    double total_energy_wh;     /* Витрачена енергія, Вт·год */
    double specific_energy_kwh_kg; /* Питома витрата енергії, кВт·год/кг */
    double energy_efficiency_pct;  /* Енергетичний ККД, % */
} SimResult;

/* Функція моделювання розрахунку електролізу */
int simulate_electrolysis(const IonParams* ion, const CellConfig* cell,
                          double current_a, double time_sec, SimResult* res) {
    if (!ion || !cell || !res || current_a <= 0.0 || time_sec <= 0.0) {
        return -1;
    }

    /* 1. Розрахунок заряду та маси за законом Фарадея */
    res->total_charge_c = current_a * time_sec;
    
    double mass_theo_g = (ion->molar_mass_g * res->total_charge_c) / 
                         (ion->valence * FARADAY_CONST);
    res->mass_deposited_g = mass_theo_g * ion->faraday_eff;

    /* 2. Товщина гальванічного покриття у мікронах (1 см = 10000 мкм) */
    double volume_cm3 = res->mass_deposited_g / ion->density_g_cm3;
    res->thickness_um = (volume_cm3 / cell->area_cm2) * 10000.0;

    /* 3. Об'єм побічного газу (наприклад, H₂ при z_gas = 2) */
    double moles_electrons = res->total_charge_c / FARADAY_CONST;
    double moles_gas = (moles_electrons / 2.0) * (1.0 - ion->faraday_eff);
    res->gas_volume_liters = moles_gas * MOLAR_GAS_VOL;

    /* 4. Розрахунок густини струму (А/см²) */
    double current_density = current_a / cell->area_cm2;

    /* 5. Обчислення перенапруг за рівнянням Тафеля η = a + b * lg(j) */
    res->overpotential_anode = cell->tafel_a_anode + 
                               cell->tafel_b_anode * log10(current_density);
    res->overpotential_cath = cell->tafel_a_cath + 
                              cell->tafel_b_cath * log10(current_density);
    if (res->overpotential_anode < 0.0) res->overpotential_anode = 0.0;
    if (res->overpotential_cath < 0.0) res->overpotential_cath = 0.0;

    /* 6. Омічний опір розчину з урахуванням газовмісту за Бруггеманом */
    double eps = cell->bubble_fraction;
    if (eps < 0.0) eps = 0.0;
    if (eps > 0.4) eps = 0.4;
    double eff_resist = cell->resist_ohm_cm / pow(1.0 - eps, 1.5);
    double r_solution = (eff_resist * cell->distance_cm) / cell->area_cm2;
    res->ohmic_drop_v = current_a * r_solution;

    /* 7. Повна прикладена напруга */
    res->applied_voltage_v = cell->e0_cell_v + res->overpotential_anode + 
                             res->overpotential_cath + res->ohmic_drop_v;

    /* 8. Енергетичні характеристики */
    res->total_energy_wh = (res->applied_voltage_v * current_a * time_sec) / 3600.0;
    
    if (res->mass_deposited_g > 0.0) {
        res->specific_energy_kwh_kg = (res->total_energy_wh / 1000.0) / 
                                      (res->mass_deposited_g / 1000.0);
    } else {
        res->specific_energy_kwh_kg = 0.0;
    }

    res->energy_efficiency_pct = ion->faraday_eff * 
                                 (cell->e0_cell_v / res->applied_voltage_v) * 100.0;

    return 0;
}

int main(void) {
    /* Налаштування для покриття міддю (Cu²⁺ z=2) */
    IonParams copper = {
        .molar_mass_g = 63.546,
        .valence = 2,
        .density_g_cm3 = 8.96,
        .faraday_eff = 0.96
    };

    CellConfig bath = {
        .area_cm2 = 250.0,        /* Деталь площею 250 см² */
        .distance_cm = 10.0,      /* Відстань 10 см */
        .resist_ohm_cm = 4.5,     /* Розчин CuSO₄ + H₂SO₄ */
        .bubble_fraction = 0.08,  /* 8% газів у об'ємі */
        .e0_cell_v = 0.89,
        .tafel_a_anode = 0.35,
        .tafel_b_anode = 0.12,
        .tafel_a_cath = 0.15,
        .tafel_b_cath = 0.08
    };

    SimResult res;
    double current = 12.5;        /* Струм 12.5 А */
    double duration = 3600.0;     /* 1 година = 3600 с */

    if (simulate_electrolysis(&copper, &bath, current, duration, &res) == 0) {
        printf("=== Результати симуляції електролізу міді ===\n");
        printf("Пропущений заряд:     %.2f Кл\n", res.total_charge_c);
        printf("Маса осадженої міді:  %.3f г\n", res.mass_deposited_g);
        printf("Товщина покриття:     %.2f мкм\n", res.thickness_um);
        printf("Виділений водень H2:  %.3f л\n", res.gas_volume_liters);
        printf("Перенапруга анода:    %.3f В\n", res.overpotential_anode);
        printf("Перенапруга катода:   %.3f В\n", res.overpotential_cath);
        printf("Омічне падіння IR:    %.3f В\n", res.ohmic_drop_v);
        printf("Повна напруга бака:   %.3f В\n", res.applied_voltage_v);
        printf("Витрачено енергії:    %.2f Вт·год\n", res.total_energy_wh);
        printf("Питома енергія:       %.2f кВт·год/кг\n", res.specific_energy_kwh_kg);
        printf("Енергетичний ККД:     %.1f %%\n", res.energy_efficiency_pct);
    }

    return 0;
}

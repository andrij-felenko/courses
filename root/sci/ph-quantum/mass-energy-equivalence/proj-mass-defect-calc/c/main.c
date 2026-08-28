#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

/* Фізичні фундаментальні константи (CODATA 2018) */
#define AMU_TO_KG 1.66053906660e-27
#define AMU_TO_MEV 931.494102
#define SPEED_OF_LIGHT 299792458.0
#define PROTON_MASS_AMU 1.007276466621
#define NEUTRON_MASS_AMU 1.00866491595
#define HYDROGEN1_MASS_AMU 1.00782503207
#define ELECTRON_MASS_AMU 0.000548579909

/* Структура для опису атомного ядра */
typedef struct {
    const char* symbol;  /* Хімічний символ ядра */
    int Z;              /* Кількість протонів (заряд) */
    int A;              /* Масове число (протони + нейтрони) */
    double mass_amu;    /* Маса нейтрального атома у а. о. м. */
} Nucleus;

/* Результати розрахунку енергії зв'язку */
typedef struct {
    double mass_defect_amu;
    double mass_defect_kg;
    double binding_energy_mev;
    double binding_energy_joules;
    double binding_energy_per_nucleon_mev;
} BindingEnergyResult;

/* Структура для опису компонента реакції */
typedef struct {
    const char* name;
    double mass_amu;
    int count;
} ReactionComponent;

/* Обчислення дефекту маси та енергії зв'язку ядра */
bool calculate_binding_energy(const Nucleus* n, BindingEnergyResult* res) {
    if (!n || !res || n->Z <= 0 || n->A < n->Z || n->mass_amu <= 0.0) {
        return false;
    }
    
    int N = n->A - n->Z;
    /* Використовуємо маси атома водню-1 для точного урахування електронів */
    double sum_free_components = n->Z * HYDROGEN1_MASS_AMU + N * NEUTRON_MASS_AMU;
    
    res->mass_defect_amu = sum_free_components - n->mass_amu;
    if (res->mass_defect_amu < 0.0) {
        return false; /* Нестабільний стан / помилка даних */
    }
    
    res->mass_defect_kg = res->mass_defect_amu * AMU_TO_KG;
    res->binding_energy_mev = res->mass_defect_amu * AMU_TO_MEV;
    res->binding_energy_joules = res->mass_defect_kg * SPEED_OF_LIGHT * SPEED_OF_LIGHT;
    res->binding_energy_per_nucleon_mev = res->binding_energy_mev / n->A;
    
    return true;
}

/* Обчислення Q-значення та порогової енергії для ядерної реакції */
bool analyze_reaction(const ReactionComponent reactants[], size_t num_reactants,
                      const ReactionComponent products[], size_t num_products,
                      double* q_value_mev, double* threshold_mev) {
    if (!reactants || !products || num_reactants == 0 || num_products == 0 || !q_value_mev) {
        return false;
    }
    
    double m_in = 0.0;
    for (size_t i = 0; i < num_reactants; ++i) {
        if (reactants[i].mass_amu <= 0.0 || reactants[i].count <= 0) return false;
        m_in += reactants[i].mass_amu * reactants[i].count;
    }
    
    double m_out = 0.0;
    for (size_t j = 0; j < num_products; ++j) {
        if (products[j].mass_amu <= 0.0 || products[j].count <= 0) return false;
        m_out += products[j].mass_amu * products[j].count;
    }
    
    double delta_m = m_in - m_out;
    *q_value_mev = delta_m * AMU_TO_MEV;
    
    if (threshold_mev) {
        if (*q_value_mev < 0.0 && num_reactants >= 2) {
            /* Поріг для ендотермічної реакції: E_th = |Q| * (1 + m_proj / M_target) */
            double m_proj = reactants[0].mass_amu;
            double m_target = reactants[1].mass_amu;
            *threshold_mev = fabs(*q_value_mev) * (1.0 + m_proj / m_target);
        } else {
            *threshold_mev = 0.0; /* Екзотермічна реакція не має кінематичного порогу */
        }
    }
    
    return true;
}

int main(void) {
    printf("=====================================================\n");
    printf("  ЯДЕРНИЙ КАЛЬКУЛЯТОР ДЕФЕКТУ МАСИ ТА РЕАКЦІЙ (C)\n");
    printf("=====================================================\n\n");
    
    /* 1. Розрахунок енергії зв'язку ядра Гелію-4 (4He) */
    Nucleus he4 = {"4He", 2, 4, 4.002603}; /* Маса атома 4He */
    BindingEnergyResult res_he4;
    
    if (calculate_binding_energy(&he4, &res_he4)) {
        printf("--- Аналіз ядра %s ---\n", he4.symbol);
        printf("  Протонів Z:     %d, Нейтронів N: %d\n", he4.Z, he4.A - he4.Z);
        printf("  Дефект маси:   %.6f u (%.6e кг)\n", res_he4.mass_defect_amu, res_he4.mass_defect_kg);
        printf("  Енергія зв'язку: %.3f МеВ (%.6e Дж)\n", res_he4.binding_energy_mev, res_he4.binding_energy_joules);
        printf("  Питома енергія:  %.3f МеВ/нуклон\n\n", res_he4.binding_energy_per_nucleon_mev);
    }
    
    /* 2. Аналіз реакції термоядерного синтезу: 2H + 3H -> 4He + n */
    ReactionComponent reactants[] = {
        {"Deuterium (2H)", 2.014102, 1},
        {"Tritium (3H)", 3.016049, 1}
    };
    
    ReactionComponent products[] = {
        {"Helium-4 (4He)", 4.001506, 1},
        {"Neutron (n)", 1.008665, 1}
    };
    
    double q_val = 0.0, e_th = 0.0;
    if (analyze_reaction(reactants, 2, products, 2, &q_val, &e_th)) {
        printf("--- Реакція синтезу D + T -> 4He + n ---\n");
        printf("  Q-значення реакції: %+.3f МеВ\n", q_val);
        if (q_val > 0.0) {
            printf("  Режим: Екзотермічний (виділення %.3f МеВ кінетичної енергії)\n", q_val);
        } else {
            printf("  Режим: Ендотермічний (порогова енергія: %.3f МеВ)\n", e_th);
        }
    }
    
    return 0;
}

#ifndef GAS_STATE_API_H
#define GAS_STATE_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define R_GAS_CONST 8.314462618
#define KB_BOLTZMANN 1.380649e-23
#define NA_AVOGADRO 6.02214076e23

typedef enum {
    GAS_IDEAL = 0,
    GAS_HELIUM,
    GAS_HYDROGEN,
    GAS_NITROGEN,
    GAS_OXYGEN,
    GAS_AIR,
    GAS_CO2,
    GAS_METHANE,
    GAS_WATER_VAPOR
} gas_type_t;

typedef struct {
    double pressure_pa;     // Тиск у Паскалях
    double volume_m3;       // Об'єм у м³
    double temp_kelvin;     // Температура в Кельвінах
    double mass_kg;         // Маса газу в кг
    double molar_mass_kg;   // Молярна маса в кг/моль
    gas_type_t type;        // Тип газу для поправок Ван-дер-Ваальса
} gas_state_t;

// Розрахунок тиску P = (m / M) * R * T / V (Ідеальний газ)
bool gas_state_solve_p(const gas_state_t *st, double *out_p_pa);

// Розрахунок об'єму V = (m / M) * R * T / P (Ідеальний газ)
bool gas_state_solve_v(const gas_state_t *st, double *out_v_m3);

// Розрахунок температури T = (P * V * M) / (m * R) (Ідеальний газ)
bool gas_state_solve_t(const gas_state_t *st, double *out_t_k);

// Розрахунок тиску реального газу Ван-дер-Ваальса: P = (n*R*T)/(V - n*b) - a*(n/V)^2
bool gas_state_vdw_p(const gas_state_t *st, double *out_p_vdw_pa);

// Розрахунок коефіцієнта стискуваності Z = (P * V) / (n * R * T)
double gas_state_compressibility_factor(double p_pa, double v_m3, double moles, double temp_k);

#ifdef __cplusplus
}
#endif

#endif // GAS_STATE_API_H

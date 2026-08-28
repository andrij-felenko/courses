#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define EPS_0 8.854187817e-12
#define EPS_OX 3.9
#define Q_ELEM 1.602176634e-19
#define KB 1.380649e-23
#define T_KELVIN 300.0

typedef struct {
    double t_ox_nm;           /* Товщина оксиду (нм) */
    double vth_erase_init;    /* Початковий Vth Erase (В) */
    double vth_prog_init;     /* Початковий Vth Program (В) */
    double s_subthreshold_0;  /* Початковий підпороговий нахил (В/декада) */
    double area_cell_um2;     /* Площа комірки (мкм²) */
} flash_cell_params_t;

typedef struct {
    unsigned long n_pe;       /* Кількість P/E-циклів */
    double n_ot_cm3;          /* Об'ємна густина пасток N_ot (см⁻³) */
    double n_it_cm2;          /* Поверхнева густина пасток N_it (см⁻²) */
    double vth_erase;         /* Поточний Vth Erase (В) */
    double vth_prog;          /* Поточний Vth Program (В) */
    double vth_window;        /* Робоче вікно пам'яті (В) */
    double subthreshold_s;    /* Підпороговий нахил S (В/декада) */
    double rber;              /* Частота первинних помилок */
} wear_state_t;

wear_state_t simulate_flash_wear(const flash_cell_params_t* params, unsigned long n_pe) {
    wear_state_t state;
    state.n_pe = n_pe;

    /* 1. Кінетика накопичення пасток */
    double a_ot = 1.2e15;
    double alpha_ot = 0.45;
    state.n_ot_cm3 = a_ot * pow((double)n_pe, alpha_ot);

    double a_it = 8.0e9;
    double alpha_it = 0.40;
    state.n_it_cm2 = a_it * pow((double)n_pe, alpha_it);

    /* 2. Фізичні константи діелектрика */
    double t_ox_m = params->t_ox_nm * 1.0e-9;
    double c_ox = (EPS_OX * EPS_0) / t_ox_m; /* Ф/м² */

    /* Переведення густини пасток у SI (м⁻³ та м⁻²) */
    double n_ot_m3 = state.n_ot_cm3 * 1.0e6;
    double n_it_m2 = state.n_it_cm2 * 1.0e4;

    /* 3. Зсув Vth через захоплений негативний заряд N_ot та N_it */
    double delta_vth_ot = (Q_ELEM * n_ot_m3 * t_ox_m * t_ox_m) / (2.0 * EPS_OX * EPS_0);
    double delta_vth_it = (Q_ELEM * n_it_m2) / c_ox;

    state.vth_erase = params->vth_erase_init + delta_vth_ot + delta_vth_it;
    
    /* Зниження Vth Program через екранування затворного поля */
    double screening_factor = 0.35;
    state.vth_prog = params->vth_prog_init - screening_factor * delta_vth_ot;

    state.vth_window = state.vth_prog - state.vth_erase;

    /* 4. Деградація підпорогового нахилу S */
    double thermal_voltage = (KB * T_KELVIN) / Q_ELEM;
    state.subthreshold_s = params->s_subthreshold_0 + log(10.0) * thermal_voltage * (Q_ELEM * n_it_m2 / c_ox);

    /* 5. Моделювання RBER (функція розмиття границь Vth та витоків SILC) */
    double read_reference = (params->vth_prog_init + params->vth_erase_init) / 2.0;
    double sigma_vth = 0.15 + 0.05 * log10((double)n_pe + 1.0);
    
    double z_erase = (read_reference - state.vth_erase) / sigma_vth;
    double z_prog = (state.vth_prog - read_reference) / sigma_vth;

    /* Наближення Гауссової функції помилок erfc(z) */
    double p_err_erase = 0.5 * erfc(z_erase / sqrt(2.0));
    double p_err_prog = 0.5 * erfc(z_prog / sqrt(2.0));
    
    state.rber = 0.5 * (p_err_erase + p_err_prog);

    return state;
}

int main(void) {
    flash_cell_params_t cell = {
        .t_ox_nm = 8.0,
        .vth_erase_init = -2.5,
        .vth_prog_init = 6.0,
        .s_subthreshold_0 = 0.080,
        .area_cell_um2 = 0.0025
    };

    unsigned long test_cycles[] = {1, 100, 1000, 3000, 10000, 50000, 100000};
    size_t num_tests = sizeof(test_cycles) / sizeof(test_cycles[0]);

    printf("=== СИМУЛЯЦІЯ ЗНОСУ FLASH (C API) ===\n");
    printf("%-8s | %-10s | %-10s | %-8s | %-8s | %-10s\n",
           "N_PE", "N_ot (cm⁻³)", "N_it (cm⁻²)", "V_ERS(V)", "V_PGM(V)", "RBER");
    printf("-------------------------------------------------------------------\n");

    for (size_t i = 0; i < num_tests; ++i) {
        wear_state_t res = simulate_flash_wear(&cell, test_cycles[i]);
        printf("%-8lu | %-10.2e | %-10.2e | %-8.2f | %-8.2f | %-10.2e\n",
               res.n_pe, res.n_ot_cm3, res.n_it_cm2, res.vth_erase, res.vth_prog, res.rber);
    }

    return 0;
}

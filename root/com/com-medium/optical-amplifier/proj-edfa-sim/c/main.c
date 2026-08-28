#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PLANCK_CONST 6.62607015e-34
#define SPEED_OF_LIGHT 2.99792458e8
#define BW_OPTICAL_01NM 12.5e9 /* 0.1 nm reference bandwidth at 1550 nm (~12.5 GHz) */

typedef struct {
    double wavelength_nm; /* Довжина хвилі (нм) */
    double power_dbm;      /* Вхідна потужність каналу (дБм) */
} WdmChannel;

typedef struct {
    double small_signal_gain_db; /* G0 (дБ) */
    double sat_power_dbm;        /* Psat (дБм) */
    double noise_figure_db;      /* NF (дБ) */
} EdfaConfig;

typedef struct {
    double total_output_power_dbm;
    double accumulated_ase_dbm;
    double osnr_db;
} CascadeResult;

/* Перетворення дБм у Вати */
static inline double dbm_to_watts(double dbm) {
    return 1e-3 * pow(10.0, dbm / 10.0);
}

/* Перетворення Ватів у дБм */
static inline double watts_to_dbm(double watts) {
    if (watts <= 0.0) return -100.0;
    return 10.0 * log10(watts / 1e-3);
}

/* Чисельне розв'язання рівняння насичення EDFA методом Ньютона-Рафсона */
double solve_edfa_gain(double g0_linear, double psat_watts, double pin_total_watts) {
    if (pin_total_watts <= 0.0) return g0_linear;
    
    double g = g0_linear; /* Початкове наближення */
    const double tol = 1e-7;
    const int max_iter = 100;
    
    for (int i = 0; i < max_iter; i++) {
        double exp_factor = exp(-(g - 1.0) * (pin_total_watts / psat_watts));
        double f_val = g - g0_linear * exp_factor;
        
        if (fabs(f_val) < tol) break;
        
        double df_dg = 1.0 + g0_linear * exp_factor * (pin_total_watts / psat_watts);
        g = g - f_val / df_dg;
        if (g < 1.0) g = 1.0;
    }
    return g;
}

/* Симуляція каскаду з N підсилювачів EDFA */
CascadeResult simulate_edfa_cascade(const WdmChannel* channels, int num_channels,
                                     double span_loss_db, EdfaConfig edfa, int num_spans) {
    double pin_total_watts = 0.0;
    for (int i = 0; i < num_channels; i++) {
        pin_total_watts += dbm_to_watts(channels[i].power_dbm);
    }
    
    double g0_linear = pow(10.0, edfa.small_signal_gain_db / 10.0);
    double psat_watts = dbm_to_watts(edfa.sat_power_dbm);
    double nf_linear = pow(10.0, edfa.noise_figure_db / 10.0);
    
    /* Шум-фактор пов'язаний з фактором інверсії nsp: NF = 2*nsp */
    double nsp = nf_linear / 2.0;
    if (nsp < 1.0) nsp = 1.0;
    
    double current_signal_watts = pin_total_watts;
    double accumulated_ase_watts = 0.0;
    
    double span_attenuation_linear = pow(10.0, -span_loss_db / 10.0);
    double freq_hz = SPEED_OF_LIGHT / 1550e-9;
    
    for (int span = 0; span < num_spans; span++) {
        /* Проходження прольоту волокна (загасання) */
        current_signal_watts *= span_attenuation_linear;
        accumulated_ase_watts *= span_attenuation_linear;
        
        /* Вхід підсилювача EDFA */
        double total_in_watts = current_signal_watts + accumulated_ase_watts;
        double g_actual = solve_edfa_gain(g0_linear, psat_watts, total_in_watts);
        
        /* Підсилення сигналу та наявного шуму */
        current_signal_watts *= g_actual;
        accumulated_ase_watts *= g_actual;
        
        /* Додавання нового шуму ASE підсилювача */
        double single_stage_ase = 2.0 * nsp * (g_actual - 1.0) * PLANCK_CONST * freq_hz * BW_OPTICAL_01NM;
        accumulated_ase_watts += single_stage_ase;
    }
    
    CascadeResult res;
    res.total_output_power_dbm = watts_to_dbm(current_signal_watts);
    res.accumulated_ase_dbm = watts_to_dbm(accumulated_ase_watts);
    
    /* OSNR першого каналу */
    double ch1_pout_watts = dbm_to_watts(channels[0].power_dbm) * (current_signal_watts / pin_total_watts);
    res.osnr_db = 10.0 * log10(ch1_pout_watts / (accumulated_ase_watts / num_channels));
    
    return res;
}

int main(void) {
    WdmChannel wdm_system[8];
    for (int i = 0; i < 8; i++) {
        wdm_system[i].wavelength_nm = 1550.0 + i * 0.8;
        wdm_system[i].power_dbm = -10.0; /* -10 дБм на канал */
    }
    
    EdfaConfig edfa = {
        .small_signal_gain_db = 20.0,
        .sat_power_dbm = 15.0,
        .noise_figure_db = 4.5
    };
    
    int spans = 10;
    double span_loss_db = 18.0;
    
    CascadeResult result = simulate_edfa_cascade(wdm_system, 8, span_loss_db, edfa, spans);
    
    printf("=== Результати симуляції лінки EDFA (%d прольотів по %.1f дБ) ===\n", spans, span_loss_db);
    printf("Загальна вихідна потужність сигналу: %.2f дБм\n", result.total_output_power_dbm);
    printf("Накопичена потужність шуму ASE (0.1 нм): %.2f дБм\n", result.accumulated_ase_dbm);
    printf("Оптичне відношення сигнал/шум (OSNR): %.2f дБ\n", result.osnr_db);
    
    return 0;
}

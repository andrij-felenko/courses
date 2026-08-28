#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT 299792458.0
#define FREQ_GPS_L1    1575.42e6
#define LAMBDA_L1      (SPEED_OF_LIGHT / FREQ_GPS_L1)
#define CHIP_RATE_CA   1.023e6
#define THERMAL_NOISE_DENSITY -174.0 /* дБм/Гц при 290 K */

typedef enum {
    JAMMER_BARRAGE_NOISE,
    JAMMER_CW_TONE,
    JAMMER_CHIRP_SWEPT,
    JAMMER_PULSED
} JammerType;

typedef struct {
    JammerType type;
    double power_watts;      /* Потужність передавача завади, Вт */
    double tx_gain_dbi;       /* Підсилення антени завади, дБі */
    double bandwidth_hz;     /* Смуга випромінювання завади, Гц */
    double duty_cycle;       /* Шпаруватість (для імпульсних), 0.0 .. 1.0 */
} JammerConfig;

typedef struct {
    double sat_power_dbm;    /* Номінальна потужність супутника на Землі, дБм */
    double rx_noise_fig_db;  /* Коефіцієнт шуму МШУ, дБ */
    double rx_gain_dbi;      /* Підсилення антени БПЛА в напрямку завади, дБі */
    double acq_threshold_js; /* Поріг зриву захоплення (J/S), дБ */
    double trk_threshold_js; /* Поріг зриву супроводу (J/S), дБ */
} ReceiverConfig;

typedef struct {
    double distance_m;
    double fspl_db;
    double jammer_power_dbm;
    double j_over_s_db;
    double effective_cn0_db_hz;
    double adc_clip_ratio;
    bool is_acquisition_blocked;
    bool is_tracking_lost;
} SimulationResult;

/* Обчислення коефіцієнта спектрального розсіювання Q за типом завади */
static double get_spectral_factor_q(JammerType type) {
    switch (type) {
        case JAMMER_BARRAGE_NOISE: return 1.1;
        case JAMMER_CW_TONE:       return 0.7;
        case JAMMER_CHIRP_SWEPT:   return 1.8;
        case JAMMER_PULSED:        return 1.4;
        default:                   return 1.0;
    }
}

/* Обчислення втрат у вільному просторі (FSPL) */
static double calculate_fspl_db(double distance_m, double wavelength_m) {
    if (distance_m < 1.0) distance_m = 1.0;
    double loss = 20.0 * log10(distance_m) + 20.0 * log10(4.0 * M_PI / wavelength_m);
    return loss;
}

/* Симуляція лінк-бюджету на заданій дистанції */
SimulationResult simulate_jamming_point(const JammerConfig* jam, 
                                        const ReceiverConfig* rx, 
                                        double distance_m) {
    SimulationResult res;
    res.distance_m = distance_m;
    res.fspl_db = calculate_fspl_db(distance_m, LAMBDA_L1);
    
    double jammer_power_dbm = 10.0 * log10(jam->power_watts * 1000.0);
    res.jammer_power_dbm = jammer_power_dbm + jam->tx_gain_dbi + rx->rx_gain_dbi - res.fspl_db;
    res.j_over_s_db = res.jammer_power_dbm - rx->sat_power_dbm;
    
    /* Розрахунок номінального C/N0 */
    double cn0_nom_db_hz = rx->sat_power_dbm - THERMAL_NOISE_DENSITY - rx->rx_noise_fig_db;
    double cn0_nom_lin = pow(10.0, cn0_nom_db_hz / 10.0);
    
    /* Модель деградації Беца */
    double js_linear = pow(10.0, res.j_over_s_db / 10.0);
    double q_factor = get_spectral_factor_q(jam->type);
    double jammer_term = js_linear / (q_factor * CHIP_RATE_CA);
    
    double cn0_eff_lin = 1.0 / ((1.0 / cn0_nom_lin) + jammer_term);
    res.effective_cn0_db_hz = 10.0 * log10(cn0_eff_lin);
    
    /* Оцінка кліпінгу 2-бітного АЦП */
    if (res.jammer_power_dbm > -60.0) {
        res.adc_clip_ratio = 1.0;
    } else if (res.jammer_power_dbm < -100.0) {
        res.adc_clip_ratio = 0.33; /* Оптимальний режим теплового шуму */
    } else {
        res.adc_clip_ratio = 0.33 + 0.67 * ((res.jammer_power_dbm + 100.0) / 40.0);
    }
    
    res.is_acquisition_blocked = (res.j_over_s_db >= rx->acq_threshold_js);
    res.is_tracking_lost = (res.j_over_s_db >= rx->trk_threshold_js);
    
    return res;
}

/* Обчислення критичних радіусів завадової зони */
void calculate_critical_radii(const JammerConfig* jam, 
                              const ReceiverConfig* rx, 
                              double* out_r_acq_m, 
                              double* out_r_trk_m) {
    double jammer_eirp_dbm = 10.0 * log10(jam->power_watts * 1000.0) + jam->tx_gain_dbi;
    double base_const = 20.0 * log10(4.0 * M_PI / LAMBDA_L1);
    
    /* Радіус зриву захоплення */
    double max_p_j_acq = rx->sat_power_dbm + rx->acq_threshold_js;
    double max_fspl_acq = jammer_eirp_dbm + rx->rx_gain_dbi - max_p_j_acq;
    *out_r_acq_m = pow(10.0, (max_fspl_acq - base_const) / 20.0);
    
    /* Радіус зриву супроводу */
    double max_p_j_trk = rx->sat_power_dbm + rx->trk_threshold_js;
    double max_fspl_trk = jammer_eirp_dbm + rx->rx_gain_dbi - max_p_j_trk;
    *out_r_trk_m = pow(10.0, (max_fspl_trk - base_const) / 20.0);
}

int main(void) {
    ReceiverConfig rx = {
        .sat_power_dbm = -130.0,
        .rx_noise_fig_db = 2.5,
        .rx_gain_dbi = 0.0,
        .acq_threshold_js = 27.0,
        .trk_threshold_js = 45.0
    };
    
    JammerConfig chirper = {
        .type = JAMMER_CHIRP_SWEPT,
        .power_watts = 10.0,
        .tx_gain_dbi = 3.0,
        .bandwidth_hz = 30.0e6,
        .duty_cycle = 1.0
    };
    
    double r_acq, r_trk;
    calculate_critical_radii(&chirper, &rx, &r_acq, &r_trk);
    
    /* Табличний аналіз залежності від відстані */
    double test_distances[] = { 1000.0, 5000.0, 15000.0, 30000.0, 60000.0 };
    size_t count = sizeof(test_distances) / sizeof(test_distances[0]);
    
    for (size_t i = 0; i < count; ++i) {
        SimulationResult r = simulate_jamming_point(&chirper, &rx, test_distances[i]);
    }
    
    return 0;
}

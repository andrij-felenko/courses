#include <math.h>
#include <stdbool.h>
#include <stdio.h>

typedef struct {
    float power_tx_dbm;     // Вихідна потужність передавача SX1262 (dBm)
    float gain_tx_dbi;      // Підсилення антени передавача (dBi)
    float gain_rx_dbi;      // Підсилення антени приймача (dBi)
    float loss_misc_db;     // Втрати у кабелях та роз'ємах (dB)
    float freq_mhz;         // Робоча частота (МГц)
    float distance_km;      // Відстань (км)
    float bandwidth_hz;     // Ширина смуги BW (Гц)
    int spreading_factor;   // Фактор розширення SF (7-12)
    float noise_figure_db;  // Коефіцієнт шуму NF (dB)
} link_budget_config_t;

static float get_snr_min(int sf) {
    switch (sf) {
        case 7:  return -7.5f;
        case 8:  return -10.0f;
        case 9:  return -12.5f;
        case 10: return -15.0f;
        case 11: return -17.5f;
        case 12: return -20.0f;
        default: return -7.5f;
    }
}

float calculate_fspl(float distance_km, float freq_mhz) {
    return 20.0f * log10f(distance_km) + 20.0f * log10f(freq_mhz) + 32.44f;
}

float calculate_sensitivity(float bandwidth_hz, int sf, float noise_figure_db) {
    float snr_min = get_snr_min(sf);
    return -174.0f + 10.0f * log10f(bandwidth_hz) + noise_figure_db + snr_min;
}

bool evaluate_link_budget(const link_budget_config_t *cfg, float *out_margin_db) {
    float fspl = calculate_fspl(cfg->distance_km, cfg->freq_mhz);
    float p_rx = cfg->power_tx_dbm + cfg->gain_tx_dbi + cfg->gain_rx_dbi - fspl - cfg->loss_misc_db;
    float s_rx = calculate_sensitivity(cfg->bandwidth_hz, cfg->spreading_factor, cfg->noise_figure_db);
    
    *out_margin_db = p_rx - s_rx;
    return (*out_margin_db >= 10.0f); // Надійне з'єднання при запасі >= 10 dB
}

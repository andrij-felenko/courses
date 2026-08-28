#include <math.h>
#include <stdint.h>

// Втрати вільного простору, дБ.  d — метри, f — МГц.
// FSPL = 20·log10(d_км) + 20·log10(f_МГц) + 32.44
static float fspl_db(float d_m, float f_mhz) {
    float d_km = d_m / 1000.0f;
    return 20.0f * log10f(d_km) + 20.0f * log10f(f_mhz) + 32.44f;
}

// Поріг чутливості з чотирьох доданків, дБм.
// b_hz — смуга (Гц), nf_db — коеф. шуму, snr_min_db — запит модуляції.
static float sensitivity_dbm(float b_hz, float nf_db, float snr_min_db) {
    return -174.0f + 10.0f * log10f(b_hz) + nf_db + snr_min_db;
}

typedef struct {
    float p_rx_dbm;    // потужність на вході приймача
    float s_rx_dbm;    // поріг чутливості
    float margin_db;   // запас лінії
} link_result_t;

// Повний потермовий бюджет.  Усе, крім p_tx і результату, — відносні дБ/дБі.
link_result_t link_budget(float p_tx_dbm,
                          float g_tx_dbi, float l_cable_tx_db,
                          float d_m, float f_mhz, float l_misc_db,
                          float g_rx_dbi, float l_cable_rx_db,
                          float b_hz, float nf_db, float snr_min_db) {
    float eirp = p_tx_dbm - l_cable_tx_db + g_tx_dbi;   // згорнули TX-сторону
    float l_path = fspl_db(d_m, f_mhz) + l_misc_db;
    float p_rx = eirp - l_path + g_rx_dbi - l_cable_rx_db;
    float s_rx = sensitivity_dbm(b_hz, nf_db, snr_min_db);
    link_result_t r = { p_rx, s_rx, p_rx - s_rx };
    return r;
}

// Наш приклад: +14 дБм, антени 5/2 дБі, кабелі 1/0.5 дБ, 40 м на 2.4 ГГц,
// стіна 8 дБ; приймач BLE-класу: 1 МГц, NF 8 дБ, SNR_min 17 дБ.
// → p_rx ≈ −60.8 дБм, s_rx ≈ −89 дБм, запас ≈ 28.2 дБ.
link_result_t r = link_budget(14.0f, 5.0f, 1.0f,
                             40.0f, 2450.0f, 8.0f,
                             2.0f, 0.5f,
                             1.0e6f, 8.0f, 17.0f);

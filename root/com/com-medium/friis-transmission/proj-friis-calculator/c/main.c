#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define C_SPEED 299792458.0  /* Швидкість світла у м/с */

/* Структура вхідних параметрів радіолінії */
typedef struct {
    double p_tx_dbm;        /* Потужність передавача (дБм) */
    double g_tx_dbi;        /* Підсилення передавальної антени (dBi) */
    double g_rx_dbi;        /* Підсилення приймальної антени (dBi) */
    double freq_hz;         /* Несуча частота (Гц) */
    double distance_m;      /* Відстань між антенами (м) */
    double rx_sens_dbm;     /* Чутливість приймача (дБм) */
    double sys_losses_db;   /* Додаткові системні втрати (дБ) */
    double antenna_d_m;     /* Максимальний розмір апертури антени (м) */
} rf_link_params_t;

/* Структура результатів розрахунку */
typedef struct {
    double wavelength_m;    /* Довжина хвилі (м) */
    double eirp_dbm;        /* Ефективна ізотропно випромінювана потужність (дБм) */
    double fspl_db;         /* Втрати у вільному просторі (дБ) */
    double p_rx_dbm;        /* Прийнята потужність (дБм) */
    double p_rx_mw;         /* Прийнята потужність (мВт) */
    double margin_db;       /* Запас лінка (дБ) */
    double far_field_m;     /* Межа дальньої зони Фраунгофера (м) */
    bool is_far_field;      /* Прапорець перебування у дальній зоні */
    bool is_link_viable;    /* Прапорець працездатності зв'язку */
} rf_link_result_t;

/* Обчислення довжини хвилі */
static inline double calculate_wavelength(double freq_hz) {
    return C_SPEED / freq_hz;
}

/* Обчислення втрат у вільному просторі (FSPL) у дБ */
double calculate_fspl(double freq_hz, double distance_m) {
    double lambda = calculate_wavelength(freq_hz);
    double ratio = (4.0 * M_PI * distance_m) / lambda;
    return 20.0 * log10(ratio);
}

/* Обчислення межі дальньої зони (відстань Фраунгофера) */
double calculate_far_field_distance(double antenna_d_m, double freq_hz) {
    double lambda = calculate_wavelength(freq_hz);
    return (2.0 * antenna_d_m * antenna_d_m) / lambda;
}

/* Повний розрахунок лінка за рівнянням Фріїса */
bool compute_friis_link(const rf_link_params_t *params, rf_link_result_t *result) {
    if (!params || !result || params->freq_hz <= 0.0 || params->distance_m <= 0.0) {
        return false;
    }

    result->wavelength_m = calculate_wavelength(params->freq_hz);
    result->eirp_dbm = params->p_tx_dbm + params->g_tx_dbi;
    result->fspl_db = calculate_fspl(params->freq_hz, params->distance_m);

    /* Рівняння Фріїса у дБм */
    result->p_rx_dbm = result->eirp_dbm + params->g_rx_dbi - result->fspl_db - params->sys_losses_db;
    
    /* Перетворення дБм у мВт: P(мВт) = 10^(P_dBm / 10) */
    result->p_rx_mw = pow(10.0, result->p_rx_dbm / 10.0);

    /* Запас лінка */
    result->margin_db = result->p_rx_dbm - params->rx_sens_dbm;
    result->is_link_viable = (result->margin_db >= 0.0);

    /* Перевірка дальньої зони */
    if (params->antenna_d_m > 0.0) {
        result->far_field_m = calculate_far_field_distance(params->antenna_d_m, params->freq_hz);
        result->is_far_field = (params->distance_m >= result->far_field_m);
    } else {
        result->far_field_m = 0.0;
        result->is_far_field = true; /* Точкове джерело */
    }

    return true;
}

int main(void) {
    rf_link_params_t link = {
        .p_tx_dbm = 14.0,        /* +14 дБм (25 мВт LoRa / Wi-Fi) */
        .g_tx_dbi = 3.0,         /* +3 dBi антена передавача */
        .g_rx_dbi = 3.0,         /* +3 dBi антена приймача */
        .freq_hz = 2.4e9,        /* 2.4 ГГц */
        .distance_m = 500.0,     /* 500 метрів */
        .rx_sens_dbm = -95.0,    /* -95 дБм чутливість */
        .sys_losses_db = 2.0,    /* 2 дБ втрат у кабелях */
        .antenna_d_m = 0.12      /* 12 см розмір антени */
    };

    rf_link_result_t res;
    if (compute_friis_link(&link, &res)) {
        printf("--- РЕЗУЛЬТАТИ РОЗРАХУНКУ ЗА ФРІЇСОМ ---\n");
        printf("Довжина хвилі:      %.4f м\n", res.wavelength_m);
        printf("Втрати FSPL:        %.2f дБ\n", res.fspl_db);
        printf("Прийнята потужність: %.2f дБм (%.4e мВт)\n", res.p_rx_dbm, res.p_rx_mw);
        printf("Запас лінка:        %.2f дБ [%s]\n", res.margin_db, res.is_link_viable ? "OK" : "НЕСТАБІЛЬНО");
        printf("Межа дальньої зони: %.2f м [%s]\n", res.far_field_m, res.is_far_field ? "ДАЛЬНЯ ЗОНА" : "УВАГА: БЛИЖНЯ ЗОНА!");
    }

    return 0;
}

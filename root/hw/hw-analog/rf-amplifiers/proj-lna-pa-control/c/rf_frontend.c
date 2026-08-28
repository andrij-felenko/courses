/* rf_frontend.c — Імплементація драйвера мовою C */
#include "rf_frontend.h"

/* Зовнішні залежності від Hardware Abstraction Layer (HAL) МК */
extern void hw_gpio_write_tx_en(bool level);
extern void hw_gpio_write_rx_en(bool level);
extern void hw_gpio_write_lna_bypass(bool level);
extern void hw_gpio_write_pa_bias(bool level);
extern void hw_delay_us(uint32_t us);
extern float hw_adc_read_pa_temp(void);
extern float hw_adc_read_fwd_pwr_dbm(void);
extern float hw_adc_read_rev_pwr_dbm(void);

static rf_mode_t g_current_mode = RF_MODE_SHUTDOWN;

void rf_frontend_init(void) {
    hw_gpio_write_pa_bias(false);
    hw_gpio_write_tx_en(false);
    hw_gpio_write_rx_en(false);
    hw_gpio_write_lna_bypass(true);
    g_current_mode = RF_MODE_SHUTDOWN;
}

rf_status_t rf_frontend_set_mode(rf_mode_t new_mode) {
    if (new_mode == g_current_mode) {
        return RF_OK;
    }

    /* 1. Перевірка температурного захисту перед увімкненням TX */
    if (new_mode == RF_MODE_TX) {
        float t = hw_adc_read_pa_temp();
        if (t > RF_MAX_TEMP_C) {
            rf_frontend_init(); /* Аварійний скид */
            return RF_ERR_OVERTEMP;
        }
    }

    /* 2. Безпечна послідовність перемикання режимів */
    if (g_current_mode == RF_MODE_TX) {
        /* Послідовність вимкнення TX -> RX / Shutdown */
        hw_gpio_write_pa_bias(false);  /* Спочатку знімаємо зсув PA */
        hw_delay_us(5);                /* Пауза для розряду ємності затвора */
        hw_gpio_write_tx_en(false);   /* Вимикаємо TX ключ */
        hw_delay_us(2);
    } else if (g_current_mode == RF_MODE_RX_HIGH_GAIN || g_current_mode == RF_MODE_RX_BYPASS) {
        /* Вимикаємо RX каскади */
        hw_gpio_write_rx_en(false);
        hw_delay_us(2);
    }

    /* 3. Встановлення нового стану мікросхеми */
    switch (new_mode) {
        case RF_MODE_SHUTDOWN:
            hw_gpio_write_lna_bypass(true);
            break;

        case RF_MODE_RX_HIGH_GAIN:
            hw_gpio_write_lna_bypass(false);
            hw_gpio_write_rx_en(true);
            break;

        case RF_MODE_RX_BYPASS:
            hw_gpio_write_lna_bypass(true);
            hw_gpio_write_rx_en(true);
            break;

        case RF_MODE_TX:
            hw_gpio_write_tx_en(true);
            hw_delay_us(5);               /* Даємо ключю час для стабілізації */
            hw_gpio_write_pa_bias(true);  /* Лише тепер вмикаємо PA */
            break;

        default:
            return RF_ERR_INVALID_MODE;
    }

    g_current_mode = new_mode;
    return RF_OK;
}

rf_mode_t rf_frontend_get_mode(void) {
    return g_current_mode;
}

rf_status_t rf_frontend_read_telemetry(rf_telemetry_t *telemetry) {
    if (!telemetry) return RF_ERR_NULL_PTR;

    telemetry->temp_celsius = hw_adc_read_pa_temp();
    telemetry->forward_power_dbm = hw_adc_read_fwd_pwr_dbm();
    telemetry->reverse_power_dbm = hw_adc_read_rev_pwr_dbm();

    /* Спрощений розрахунок VSWR з виміряної потужності */
    float p_fwd_mw = 0.001f * (telemetry->forward_power_dbm);
    float p_rev_mw = 0.001f * (telemetry->reverse_power_dbm);

    if (p_fwd_mw > 0.001f && p_rev_mw >= 0.0f) {
        float gamma = 0.0f;
        if (p_rev_mw < p_fwd_mw) {
            gamma = p_rev_mw / p_fwd_mw; /* Коефіцієнт відбиття за потужністю */
        } else {
            gamma = 0.99f;
        }
        float gamma_mag = (gamma > 0.0f) ? gamma : 0.0f;
        telemetry->vswr = (1.0f + gamma_mag) / (1.0f - gamma_mag + 0.0001f);
    } else {
        telemetry->vswr = 1.0f;
    }

    /* Перевірка аварії за VSWR під час передачі */
    if (g_current_mode == RF_MODE_TX && telemetry->vswr > RF_MAX_VSWR) {
        rf_frontend_init(); /* Аварійно вимикаємо передавач */
        return RF_ERR_HIGH_VSWR;
    }

    return RF_OK;
}

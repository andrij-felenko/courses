/* Задача моніторингу радіоканалу FreeRTOS (C) */
void vRadioLinkMonitorTask(void *pvParameters) {
    rf_tx_params_t tx_cfg = { .power_dbm = 14.0f, .tx_cable_loss_db = 0.5f, .antenna_gain_dbi = 2.15f };
    rf_rx_params_t rx_cfg = { .rx_antenna_gain_dbi = 2.15f, .rx_cable_loss_db = 0.5f, 
                              .bandwidth_hz = 125000.0f, .noise_figure_db = 5.0f, .required_snr_db = -10.0f };
    rf_channel_params_t ch_cfg = { .frequency_mhz = 868.0f, .distance_km = 5.0f, 
                                   .atmospheric_loss_db = 0.2f, .fading_margin_db = 10.0f };
    rf_budget_report_t report;

    for (;;) {
        /* Чекаємо повідомлення від драйвера трансивера про прийом нового пакету */
        if (ulTaskNotifyTake(pdTRUE, portMAX_DELAY) == pdTRUE) {
            rf_budget_status_t status = rf_calculate_link_budget(&tx_cfg, &ch_cfg, &rx_cfg, &report);
            
            if (status == RF_BUDGET_OK && report.link_margin_db < 5.0f) {
                vSendNetworkAlert(report.link_margin_db);
            }
        }
    }
}

/* Алгоритм обчислення необхідної потужності P_TX (C) */
rf_budget_status_t rf_estimate_required_tx_power(float target_margin_db,
                                                 const rf_channel_params_t *channel,
                                                 const rf_rx_params_t *rx,
                                                 float tx_gain_dbi,
                                                 float tx_cable_loss_db,
                                                 float *req_power_dbm) {
    if (!channel || !rx || !req_power_dbm) return RF_BUDGET_ERR_INVALID_PARAM;
    if (channel->frequency_mhz <= 0.0f)     return RF_BUDGET_ERR_FREQ_OUT_OF_RANGE;
    if (channel->distance_km <= 0.0f)        return RF_BUDGET_ERR_ZERO_DISTANCE;

    /* FSPL = 20*log10(d) + 20*log10(f) + 32.44 */
    float fspl = 20.0f * log10f(channel->distance_km) + 
                 20.0f * log10f(channel->frequency_mhz) + 32.44f;
    float path_loss = fspl + channel->atmospheric_loss_db + 
                      channel->fading_margin_db + channel->polarization_loss_db;

    /* P_sens = -173.98 + 10*log10(B) + N_F + SNR_min */
    float sensitivity = -173.98f + 10.0f * log10f(rx->bandwidth_hz) + 
                        rx->noise_figure_db + rx->required_snr_db;

    /* Target P_RX = P_sens + target_margin */
    float target_p_rx = sensitivity + target_margin_db;

    /* P_TX = target_P_RX + path_loss - G_TX + L_tx - G_RX + L_rx */
    *req_power_dbm = target_p_rx + path_loss - tx_gain_dbi + tx_cable_loss_db - 
                      rx->rx_antenna_gain_dbi + rx->rx_cable_loss_db;

    return RF_BUDGET_OK;
}

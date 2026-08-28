// Задача моніторингу радіоканалу C++23 (FreeRTOS wrapper)
void radio_monitor_task(std::stop_token stop_tok) {
    const rf::TxParams tx{.power_dbm = 14.0f, .tx_cable_loss_db = 0.5f, .antenna_gain_dbi = 2.15f};
    const rf::RxParams rx{.rx_antenna_gain_dbi = 2.15f, .rx_cable_loss_db = 0.5f, 
                          .bandwidth_hz = 125000.0f, .noise_figure_db = 5.0f, .required_snr_db = -10.0f};
    const rf::ChannelParams ch{.frequency_mhz = 868.0f, .distance_km = 5.0f, 
                               .atmospheric_loss_db = 0.2f, .fading_margin_db = 10.0f};

    while (!stop_tok.stop_requested()) {
        if (auto report_opt = rf::LinkPlanner::compute(tx, ch, rx); report_opt.has_value()) {
            if (report_opt->link_margin_db < 5.0f) {
                send_network_alert(report_opt->link_margin_db);
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}

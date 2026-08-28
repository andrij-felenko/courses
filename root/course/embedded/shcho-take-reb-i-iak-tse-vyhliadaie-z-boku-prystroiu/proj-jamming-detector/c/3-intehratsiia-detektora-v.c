#include <stdio.h>

void on_radio_packet_received(ew_detector_t *det, int16_t rssi, int8_t snr, uint8_t agc, bool ok) {
    ew_rf_sample_t sample = {
        .rssi_dbm = rssi,
        .snr_db = snr,
        .agc_gain_code = agc,
        .preamble_detected = ok,
        .crc_error = !ok
    };

    ew_detector_push_rf(det, &sample);
    ew_threat_type_t threat = ew_detector_evaluate(det, NULL);

    switch (threat) {
        case EW_THREAT_SPOT_JAMMING:
            /* Негайно переходимо на резервний псевдовипадковий канал */
            // rf_fhss_force_channel_hop();
            break;
        case EW_THREAT_BARRAGE_BLOCKING:
            /* Вмикаємо атенюатор RF Front-End, щоб вивести LNA з насичення */
            // rf_frontend_set_attenuator(true);
            break;
        case EW_THREAT_PULSE_JAMMING:
            /* Збільшуємо надлишковість прямого виправлення помилок (FEC) */
            // rf_set_fec_rate(FEC_RATE_4_8);
            break;
        default:
            break;
    }
}

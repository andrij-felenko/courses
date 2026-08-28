#include <iostream>

void handleRadioTelemetry(embedded::ew::ThreatClassifier<16>& detector,
                          int16_t rssi, int8_t snr, uint8_t agc, bool packetOk) {
    detector.pushSample({
        .rssi_dbm = rssi,
        .snr_db = snr,
        .agc_gain_code = agc,
        .preamble_detected = packetOk,
        .crc_error = !packetOk
    });

    const auto threat = detector.evaluate();

    switch (threat) {
        case embedded::ew::ThreatType::SpotJamming:
            // rf_fhss_force_channel_hop();
            break;
        case embedded::ew::ThreatType::BarrageBlocking:
            // rf_frontend_set_attenuator(true);
            break;
        case embedded::ew::ThreatType::PulseJamming:
            // rf_set_fec_rate(FEC_RATE_4_8);
            break;
        default:
            break;
    }
}

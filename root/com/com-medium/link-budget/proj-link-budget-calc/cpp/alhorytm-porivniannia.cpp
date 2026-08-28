// Приклад зчитування регістрів з трансивера Semtech SX1276 (C++23)
struct TelemetryPacket {
    float measured_snr_db;
    float measured_rssi_dbm;
    float measured_margin_db;
};

[[nodiscard]] inline TelemetryPacket 
decode_sx1276_telemetry(int8_t raw_snr, int16_t raw_rssi, float required_snr_min_db) noexcept {
    float snr = static_cast<float>(raw_snr) * 0.25f;
    float rssi = -157.0f + static_cast<float>(raw_rssi);
    if (snr < 0.0f) {
        rssi += snr;
    }
    return TelemetryPacket{
        .measured_snr_db = snr,
        .measured_rssi_dbm = rssi,
        .measured_margin_db = snr - required_snr_min_db
    };
}

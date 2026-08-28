// Згенерована типізована структура C++
namespace mavlink::custom::msg {

struct alignas(8) PAYLOAD_SPECTRAL_STATUS {
    uint32_t time_boot_ms;
    float integration_time_ms;
    float sensor_temperature;
    uint16_t spectral_irradiance;
    uint8_t filter_mode;
    uint8_t status_flags;
    uint32_t calibration_crc;
    uint8_t gain_level;
};

} // namespace mavlink::custom::msg

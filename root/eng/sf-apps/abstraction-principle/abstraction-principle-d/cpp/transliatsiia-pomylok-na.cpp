#include <cstdint>
#include <expected>

// ── Погана абстракція: код помилки POSIX у клієнтському коді
int raw_res = get_raw_sensor_altitude();
if (raw_res == -110) { // -ETIMEDOUT
    trigger_failsafe();
}

// ── Правильна абстракція: строгий типізований результат через std::expected
enum class AltitudeError : uint8_t {
    Unavailable,
    DataCorrupted,
    OutOfRange
};

struct AltitudeMeasurement {
    int32_t millimeters;
};

std::expected<AltitudeMeasurement, AltitudeError> reading = read_altitude_abstract();
if (!reading.has_value() && reading.error() == AltitudeError::Unavailable) {
    trigger_failsafe();
}

#include <cstdint>

namespace autopilot::failsafe {

enum class Fault : uint32_t {
    RcLost        = 1u << 0,  // Втрата сигналу пульта керування
    GcsLost       = 1u << 1,  // Втрата телеметрії наземної станції
    GnssGlitch    = 1u << 2,  // Стрибок HDOP / втрата 3D Fix
    BatteryLow    = 1u << 3,  // Перший поріг розряду (Warning)
    BatteryCrit   = 1u << 4,  // Критичний поріг розряду (Land)
    Geofence      = 1u << 5,  // Вихід за межі дозволеного радіуса/стелі
    ActuatorFail  = 1u << 6,  // Відмова мотора, ESC або сервоприводу
    AttitudeLoss  = 1u << 7   // Втрата розрахунку просторової орієнтації
};

constexpr uint32_t to_mask(Fault f) noexcept {
    return static_cast<uint32_t>(f);
}

} // namespace autopilot::failsafe

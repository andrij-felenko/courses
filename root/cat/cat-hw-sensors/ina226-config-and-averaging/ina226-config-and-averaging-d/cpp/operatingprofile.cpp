// Клас селектора профілів налаштування INA226 для C++17
#include <cstdint>

enum class OperatingProfile {
    FastProtection, // Мінімальна затримка для виявлення аварійних струмів
    Balanced,       // Оптимальне усереднення для загальної телеметрії
    PrecisionLog    // Максимальне пригнічення шуму для логування енергії
};

class INA226ProfileSelector {
public:
    static constexpr uint16_t get_config_word(OperatingProfile profile) noexcept {
        switch (profile) {
            case OperatingProfile::FastProtection:
                // AVG=1, VBUS=140us, VSHUNT=140us, Mode=Continuous Both
                return (0x00u << 9) | (0x00u << 6) | (0x00u << 3) | 0x07u;
            case OperatingProfile::PrecisionLog:
                // AVG=512, VBUS=8.244ms, VSHUNT=8.244ms, Mode=Continuous Both
                return (0x06u << 9) | (0x07u << 6) | (0x07u << 3) | 0x07u;
            case OperatingProfile::Balanced:
            default:
                // AVG=16, VBUS=1.1ms, VSHUNT=1.1ms, Mode=Continuous Both
                return (0x02u << 9) | (0x04u << 6) | (0x04u << 3) | 0x07u;
        }
    }
};

#include <cstdint>
#include <optional>
#include <string_view>

enum class PoeDetectionStatus : uint8_t {
    Unknown,
    Valid25k,  // Виявлено валідну сигнатуру 24.9 кОм
    LowRes,    // Занижений опір (коротке замикання)
    HighRes,   // Завищений опір або обрив
    HighCap    // Ємність лінії перевищує 150 нФ
};

struct PoeRawTelemetry {
    uint16_t voltage_raw_mv{0};  // Напруга порту в мілівольтах
    uint16_t current_raw_ma{0};  // Струм порту в міліамперах
    uint8_t  detection_code{0};  // Код статусу детекції
    uint8_t  fault_flags{0};     // Маска аварійних прапорців
};

struct PoePortMetrics {
    float voltage_v{0.0f};
    float current_a{0.0f};
    float power_w{0.0f};
    PoeDetectionStatus status{PoeDetectionStatus::Unknown};
    bool is_powered{false};
    bool has_fault{false};

    [[nodiscard]] constexpr std::string_view status_str() const noexcept {
        switch (status) {
            case PoeDetectionStatus::Valid25k: return "Підключено PD (25 кОм)";
            case PoeDetectionStatus::LowRes:   return "Помилка: низький опір";
            case PoeDetectionStatus::HighRes:  return "Лінія вільна (High-Z)";
            case PoeDetectionStatus::HighCap:  return "Помилка: завада ємності";
            default:                           return "Невідомий стан";
        }
    }
};

class PoePortMonitor {
public:
    [[nodiscard]] static std::optional<PoePortMetrics> parse(const PoeRawTelemetry& raw) noexcept {
        PoePortMetrics metrics;
        metrics.voltage_v = static_cast<float>(raw.voltage_raw_mv) / 1000.0f;
        metrics.current_a = static_cast<float>(raw.current_raw_ma) / 1000.0f;
        metrics.power_w   = metrics.voltage_v * metrics.current_a;

        switch (raw.detection_code) {
            case 0x01: metrics.status = PoeDetectionStatus::Valid25k; break;
            case 0x02: metrics.status = PoeDetectionStatus::LowRes;   break;
            case 0x03: metrics.status = PoeDetectionStatus::HighRes;  break;
            case 0x04: metrics.status = PoeDetectionStatus::HighCap;  break;
            default:   metrics.status = PoeDetectionStatus::Unknown;  break;
        }

        metrics.is_powered = (raw.voltage_raw_mv >= 44000);
        metrics.has_fault  = (raw.fault_flags != 0);

        return metrics;
    }
};

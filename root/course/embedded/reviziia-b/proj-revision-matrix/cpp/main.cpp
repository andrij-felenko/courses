#include <cstdint>
#include <array>
#include <optional>
#include <span>

/**
 * @brief Типізоване перерахування апаратних ревізій плати.
 */
enum class BoardRevision : uint8_t {
    RevA = 1,
    RevB = 2,
    RevC = 3,
    RevD = 4,
    RevE = 5
};

struct RevisionThreshold {
    BoardRevision revision;
    uint16_t adc_min;
    uint16_t adc_max;

    [[nodiscard]] constexpr bool matches(uint16_t raw_adc) const noexcept {
        return raw_adc >= adc_min && raw_adc <= adc_max;
    }
};

/**
 * @brief Клас розпізнавання конфігурації апаратної платформи.
 */
class HardwareIdentifier {
public:
    static constexpr std::array<RevisionThreshold, 5> Thresholds{{
        { BoardRevision::RevA,    0,  300 },   // 0.00 В (GND)
        { BoardRevision::RevB,  850, 1200 },   // 0.825 В
        { BoardRevision::RevC, 1850, 2250 },   // 1.650 В
        { BoardRevision::RevD, 2900, 3300 },   // 2.475 В
        { BoardRevision::RevE, 3850, 4095 }    // 3.300 В (Vdda)
    }};

    /**
     * @brief Визначення ревізії з набору відліків АЦП із відсіканням шумів.
     * 
     * @param samples Послідовність послідовних вимірів для усереднення.
     * @return std::optional<BoardRevision> Ревізія або std::nullopt при виході за вікна.
     */
    [[nodiscard]] static std::optional<BoardRevision> detect(std::span<const uint16_t> samples) noexcept {
        if (samples.empty()) {
            return std::nullopt;
        }

        uint32_t accumulator = 0;
        for (const auto val : samples) {
            accumulator += val;
        }
        const uint16_t average = static_cast<uint16_t>(accumulator / samples.size());

        for (const auto& entry : Thresholds) {
            if (entry.matches(average)) {
                return entry.revision;
            }
        }
        return std::nullopt;
    }
};

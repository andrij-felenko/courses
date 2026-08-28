#include <cstdint>
#include <cmath>
#include <optional>
#include <algorithm>
#include <span>

namespace embedded::safety {

enum class DiagnosticFault : uint16_t {
    None           = 0x0000,
    NanOrInf       = 0x0001,
    ElectricalLow  = 0x0002, // Обрив сигнального дроту або КЗ на землю
    ElectricalHigh = 0x0004, // Коротке замикання на лінію живлення
    StaticRange    = 0x0008, // Вихід за межі фізично можливого діапазону
    SlewRateUp     = 0x0010, // Темп наростання перевищує теплову/кінематичну модель
    SlewRateDown   = 0x0020, // Темп спадання перевищує теплову/кінематичну модель
    CrossCheckFail = 0x0040, // Порушення перехресної кореляції каналів
    StaleTimeout   = 0x0080  // Відсутність оновлення даних у встановлений час
};

[[nodiscard]] constexpr DiagnosticFault operator|(DiagnosticFault a, DiagnosticFault b) noexcept {
    return static_cast<DiagnosticFault>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

constexpr DiagnosticFault& operator|=(DiagnosticFault& a, DiagnosticFault b) noexcept {
    a = a | b;
    return a;
}

[[nodiscard]] constexpr bool hasFlag(DiagnosticFault mask, DiagnosticFault flag) noexcept {
    return (static_cast<uint16_t>(mask) & static_cast<uint16_t>(flag)) != 0;
}

enum class TrustGrade : uint8_t {
    Trusted = 0, // Повна довіра, 100% вага в системі керування
    Degraded,    // Підозрілий сигнал, обмежена швидкість і знижена вага
    Isolated     // Відмова каналу, дані заблоковані, перехід у Failsafe
};

struct SanitizerProfile {
    float electricalMinV    {0.2f};
    float electricalMaxV    {3.1f};
    float rangeMin          {-40.0f};
    float rangeMax          {125.0f};
    float maxSlewUpPerSec   {5.0f};
    float maxSlewDownPerSec {2.0f};
    uint32_t timeoutMs      {100};
    uint8_t penaltyWeight   {20};
    uint8_t leakRate        {1};
    uint8_t thresholdDegrade{25};
    uint8_t thresholdIsolate{80};
};

struct ValidationResult {
    float value;
    TrustGrade grade;
    DiagnosticFault faults;
    bool isValid;
};

template <typename NumericType = float>
class SensorSanitizer {
public:
    constexpr explicit SensorSanitizer(const SanitizerProfile& profile) noexcept
        : profile_(profile) {}

    [[nodiscard]] ValidationResult process(NumericType rawVoltageV,
                                          NumericType physicalValue,
                                          bool crossCheckValid,
                                          uint32_t nowMs) noexcept {
        DiagnosticFault currentFaults = DiagnosticFault::None;
        bool stepValid = true;

        // 1. Перевірка на нечислові значення
        if (std::isnan(physicalValue) || std::isinf(physicalValue) || std::isnan(rawVoltageV)) {
            currentFaults |= DiagnosticFault::NanOrInf;
            stepValid = false;
        }

        // 2. Електричні захисні зони
        if (rawVoltageV < profile_.electricalMinV) {
            currentFaults |= DiagnosticFault::ElectricalLow;
            stepValid = false;
        } else if (rawVoltageV > profile_.electricalMaxV) {
            currentFaults |= DiagnosticFault::ElectricalHigh;
            stepValid = false;
        }

        // 3. Статичні межі діапазону
        if (physicalValue < profile_.rangeMin || physicalValue > profile_.rangeMax) {
            currentFaults |= DiagnosticFault::StaticRange;
            stepValid = false;
        }

        // 4. Перевірка свіжості та динаміки
        if (isInitialized_) {
            const uint32_t dtMs = nowMs - lastUpdateTimeMs_;
            if (dtMs > profile_.timeoutMs) {
                currentFaults |= DiagnosticFault::StaleTimeout;
                stepValid = false;
            }

            if (stepValid && dtMs > 0) {
                const auto dtSec = static_cast<NumericType>(dtMs) * NumericType{0.001};
                const NumericType delta = physicalValue - lastValidValue_;
                const NumericType maxUp = profile_.maxSlewUpPerSec * dtSec;
                const NumericType maxDown = profile_.maxSlewDownPerSec * dtSec;

                if (delta > maxUp) {
                    currentFaults |= DiagnosticFault::SlewRateUp;
                    stepValid = false;
                    physicalValue = lastValidValue_ + maxUp;
                } else if (delta < -maxDown) {
                    currentFaults |= DiagnosticFault::SlewRateDown;
                    stepValid = false;
                    physicalValue = lastValidValue_ - maxDown;
                }
            }
        }

        // 5. Перехресна перевірка моделі
        if (!crossCheckValid) {
            currentFaults |= DiagnosticFault::CrossCheckFail;
            stepValid = false;
        }

        // 6. Інтегратор штрафів Leaky Bucket
        if (!stepValid) {
            const auto updatedScore = static_cast<uint16_t>(penaltyScore_) + profile_.penaltyWeight;
            penaltyScore_ = static_cast<uint8_t>(std::min<uint16_t>(255, updatedScore));
        } else {
            penaltyScore_ = (penaltyScore_ >= profile_.leakRate)
                                ? (penaltyScore_ - profile_.leakRate)
                                : 0;
        }

        // 7. Градація рівня довіри
        if (penaltyScore_ >= profile_.thresholdIsolate) {
            trustGrade_ = TrustGrade::Isolated;
        } else if (penaltyScore_ >= profile_.thresholdDegrade) {
            trustGrade_ = TrustGrade::Degraded;
        } else {
            trustGrade_ = TrustGrade::Trusted;
        }

        // 8. Оновлення та повернення результату
        if (trustGrade_ != TrustGrade::Isolated && (stepValid || !isInitialized_)) {
            lastValidValue_ = physicalValue;
            lastUpdateTimeMs_ = nowMs;
            isInitialized_ = true;
        }

        return ValidationResult{
            .value = lastValidValue_,
            .grade = trustGrade_,
            .faults = currentFaults,
            .isValid = (trustGrade_ != TrustGrade::Isolated)
        };
    }

    void reset() noexcept {
        lastValidValue_ = NumericType{0};
        lastUpdateTimeMs_ = 0;
        penaltyScore_ = 0;
        trustGrade_ = TrustGrade::Trusted;
        isInitialized_ = false;
    }

    [[nodiscard]] TrustGrade getTrustGrade() const noexcept { return trustGrade_; }
    [[nodiscard]] uint8_t getPenaltyScore() const noexcept { return penaltyScore_; }

private:
    SanitizerProfile profile_;
    NumericType lastValidValue_{0};
    uint32_t lastUpdateTimeMs_{0};
    uint8_t penaltyScore_{0};
    TrustGrade trustGrade_{TrustGrade::Trusted};
    bool isInitialized_{false};
};

} // namespace embedded::safety

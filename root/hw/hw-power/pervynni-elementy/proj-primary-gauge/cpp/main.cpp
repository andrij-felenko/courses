#include <cstdint>
#include <chrono>
#include <algorithm>

namespace embedded::power {

enum class Chemistry : uint8_t {
    LithiumThionyl, /* Li-SOCl2 */
    CoinCr2032,     /* Li-MnO2 */
    Alkaline        /* Zn-MnO2 */
};

struct BatterySpecs {
    Chemistry chem{Chemistry::LithiumThionyl};
    uint32_t nominalCapacityMicroAmpHours{2400000}; /* 2.4 А·год */
    uint32_t esrMilliohm{50000};                    /* 50 Ом для бобінного елемента */
    uint16_t brownoutLimitMilliVolts{2200};         /* 2.2 В */
    uint16_t baseSelfDischargePpmYear{10000};       /* 1% = 10000 ppm/рік */
};

class PrimaryBatteryGauge {
public:
    constexpr explicit PrimaryBatteryGauge(const BatterySpecs& specs) noexcept
        : specs_(specs), consumedNanoAmpHours_(0), lastPulseTimeSeconds_(0), depassivationNeeded_(false) {}

    /* Облік глибокого сну */
    void trackSleep(std::chrono::milliseconds duration, uint32_t sleepCurrentNanoAmps) noexcept {
        const auto consumedNah = (static_cast<uint64_t>(sleepCurrentNanoAmps) * duration.count()) / 3600000ULL;
        consumedNanoAmpHours_ += consumedNah;
    }

    /* Облік активного імпульсу */
    void trackPulse(std::chrono::microseconds duration, uint32_t currentMicroAmps, uint32_t currentTimeSeconds) noexcept {
        const auto consumedNah = (static_cast<uint64_t>(currentMicroAmps) * duration.count()) / 3600000ULL;
        consumedNanoAmpHours_ += consumedNah;
        lastPulseTimeSeconds_ = currentTimeSeconds;
        depassivationNeeded_ = false;
    }

    /* Оновлення саморозряду з урахуванням температури */
    void updateSelfDischarge(int8_t temperatureCelsius, std::chrono::hours interval) noexcept {
        float tempFactor = 1.0f;
        if (temperatureCelsius > 25) {
            tempFactor += static_cast<float>(temperatureCelsius - 25) * 0.08f;
        } else if (temperatureCelsius < 10) {
            tempFactor = 0.6f;
        }

        const uint64_t nominalNah = static_cast<uint64_t>(specs_.nominalCapacityMicroAmpHours) * 1000ULL;
        const uint64_t annualLossNah = (nominalNah * specs_.baseSelfDischargePpmYear) / 1000000ULL;
        const uint64_t hourLossNah = static_cast<uint64_t>((annualLossNah / 8760ULL) * tempFactor);

        consumedNanoAmpHours_ += (hourLossNah * interval.count());

        if (specs_.chem == Chemistry::LithiumThionyl) {
            if (interval.count() > 720 || (temperatureCelsius < 0 && interval.count() > 168)) {
                depassivationNeeded_ = true;
            }
        }
    }

    /* Прогнозування клемної напруги під час імпульсу (мВ) */
    [[nodiscard]] constexpr uint16_t predictPulseVoltage(uint16_t ocvMilliVolts, uint32_t pulseCurrentMicroAmps) const noexcept {
        const uint32_t sagMilliVolts = (static_cast<uint64_t>(pulseCurrentMicroAmps) * specs_.esrMilliohm) / 1000000ULL;
        if (ocvMilliVolts <= sagMilliVolts) {
            return 0;
        }
        return static_cast<uint16_t>(ocvMilliVolts - sagMilliVolts);
    }

    /* Чи безпечно запускати передачу без ризику Brownout */
    [[nodiscard]] constexpr bool isSafeForTransmission(uint16_t ocvMilliVolts, uint32_t pulseCurrentMicroAmps) const noexcept {
        return predictPulseVoltage(ocvMilliVolts, pulseCurrentMicroAmps) >= specs_.brownoutLimitMilliVolts;
    }

    /* Відсоток залишкової ємності (0..100) */
    [[nodiscard]] constexpr uint8_t stateOfChargePercent() const noexcept {
        const uint64_t nominalNah = static_cast<uint64_t>(specs_.nominalCapacityMicroAmpHours) * 1000ULL;
        if (consumedNanoAmpHours_ >= nominalNah) {
            return 0;
        }
        const uint64_t remainingNah = nominalNah - consumedNanoAmpHours_;
        return static_cast<uint8_t>((remainingNah * 100ULL) / nominalNah);
    }

    [[nodiscard]] constexpr bool isDepassivationNeeded() const noexcept {
        return depassivationNeeded_;
    }

private:
    BatterySpecs specs_;
    uint64_t consumedNanoAmpHours_{0};
    uint32_t lastPulseTimeSeconds_{0};
    bool depassivationNeeded_{false};
};

} // namespace embedded::power

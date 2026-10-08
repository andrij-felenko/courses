#include <cstdint>

enum class ThermalState {
    Ok = 0,
    ErrorNoTip,
    ErrorRunaway,
    ErrorMosfetShort
};

class ThermalProtectionManager {
private:
    uint32_t m_runawayTimerMs{0};

public:
    struct Inputs {
        int16_t tempMeasC;
        int16_t tempSetC;
        uint8_t pwmDuty;
        uint16_t adcRaw;
    };

    ThermalState update(const Inputs& in, uint32_t dtMs) noexcept {
        // Перевірка обриву термопари
        if (in.adcRaw > 4000 || in.tempMeasC > 500 || in.tempMeasC < -10) {
            m_runawayTimerMs = 0;
            return ThermalState::ErrorNoTip;
        }

        // Перевірка відсутності динаміки нагріву при активній подачі живлення
        if (in.pwmDuty > 200 && (in.tempSetC - in.tempMeasC) > 30) {
            m_runawayTimerMs += dtMs;
            if (m_runawayTimerMs > 5000) {
                return ThermalState::ErrorRunaway;
            }
        } else {
            m_runawayTimerMs = (m_runawayTimerMs >= dtMs) ? (m_runawayTimerMs - dtMs) : 0;
        }

        return ThermalState::Ok;
    }
};

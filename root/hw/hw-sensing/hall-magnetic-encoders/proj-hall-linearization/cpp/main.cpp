#include <cstdint>
#include <cmath>
#include <optional>
#include <numbers>
#include <span>

class MagneticEncoderAS5048 {
public:
    static constexpr uint16_t Cpr = 16384;
    static constexpr double TwoPi = std::numbers::pi_v<double> * 2.0;

    struct HarmonicCalibration {
        float offsetRad{0.0f};
        float a1{0.0f}, b1{0.0f}; // 1-ша гармоніка (ексцентриситет)
        float a2{0.0f}, b2{0.0f}; // 2-га гармоніка (кутовий нахил)
    };

    struct State {
        float positionRad{0.0f};
        float velocityRadS{0.0f};
        int32_t totalTurns{0};
    };

    explicit MagneticEncoderAS5048(float sampleTimeS, HarmonicCalibration cal = {})
        : dt_{sampleTimeS}, cal_{cal} {
        alpha_ = 0.25f;
        beta_ = 0.05f / dt_;
    }

    // Обробка 16-бітного SPI кадру з поверненням фільтрованого стану
    [[nodiscard]] std::optional<State> processFrame(uint16_t rxFrame) noexcept {
        if (!verifyEvenParity(rxFrame)) {
            return std::nullopt; // Помилка парності
        }
        if (rxFrame & 0x4000) {
            return std::nullopt; // Error Flag мікросхеми
        }

        const auto raw = static_cast<uint16_t>(rxFrame & 0x3FFF);

        if (!initialized_) {
            prevRaw_ = raw;
            initialized_ = true;
            state_.positionRad = (static_cast<float>(raw) / static_cast<float>(Cpr)) * static_cast<float>(TwoPi);
        }

        // Розгортання переходу через 0 (Unwrap)
        const auto delta = static_cast<int32_t>(raw) - static_cast<int32_t>(prevRaw_);
        if (delta > (Cpr / 2)) {
            state_.totalTurns--;
        } else if (delta < -(Cpr / 2)) {
            state_.totalTurns++;
        }
        prevRaw_ = raw;

        // Розрахунок неперервного кута
        const float totalCounts = static_cast<float>(state_.totalTurns) * static_cast<float>(Cpr) + static_cast<float>(raw);
        const float uncalibratedRad = (totalCounts / static_cast<float>(Cpr)) * static_cast<float>(TwoPi);

        // Гармонійна корекція
        const float thetaSingle = (static_cast<float>(raw) / static_cast<float>(Cpr)) * static_cast<float>(TwoPi);
        const float sin1 = std::sin(thetaSingle), cos1 = std::cos(thetaSingle);
        const float sin2 = std::sin(2.0f * thetaSingle), cos2 = std::cos(2.0f * thetaSingle);

        const float error = cal_.offsetRad 
                          + (cal_.a1 * cos1 + cal_.b1 * sin1)
                          + (cal_.a2 * cos2 + cal_.b2 * sin2);

        const float calibratedRad = uncalibratedRad - error;

        // Альфа-бета фільтрація
        const float predPos = state_.positionRad + state_.velocityRadS * dt_;
        const float residual = calibratedRad - predPos;

        state_.positionRad = predPos + alpha_ * residual;
        state_.velocityRadS += (beta_ * dt_) * residual;

        return state_;
    }

    void updateCalibration(const HarmonicCalibration& cal) noexcept {
        cal_ = cal;
    }

    void resetTurns(int32_t initialTurn = 0) noexcept {
        state_.totalTurns = initialTurn;
    }

private:
    static constexpr bool verifyEvenParity(uint16_t word) noexcept {
        uint16_t count = 0;
        for (int i = 0; i < 16; ++i) {
            if ((word >> i) & 1) ++count;
        }
        return (count % 2) == 0;
    }

    float dt_;
    HarmonicCalibration cal_;
    float alpha_{0.25f};
    float beta_{10.0f};
    uint16_t prevRaw_{0};
    bool initialized_{false};
    State state_{};
};

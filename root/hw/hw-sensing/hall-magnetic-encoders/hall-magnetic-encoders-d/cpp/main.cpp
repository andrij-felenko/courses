#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <expected>

class MagneticEncoderAS5048A {
public:
    static constexpr uint16_t Cpr = 16384;              // 14 біт роздільність
    static constexpr uint16_t LutPoints = 32;
    static constexpr uint16_t LutStep = Cpr / LutPoints; // 512 відліків
    static constexpr uint16_t ReadAngleCmd = 0xFFFF;    // Команда з парністю

    enum class Error : uint8_t {
        ParityMismatch,
        DeviceErrorFlag,
        InvalidResponse
    };

    struct AngleReading {
        double totalDegrees;       // Неперервний багатооборотний кут
        double singleTurnDegrees;  // Кут у межах 0..360°
        int32_t turns;             // Кількість повних обертів
    };

    explicit MagneticEncoderAS5048A(std::span<const int16_t, LutPoints> errorLut = {}) noexcept {
        if (!errorLut.empty()) {
            std::copy(errorLut.begin(), errorLut.end(), errorLut_.begin());
        } else {
            errorLut_.fill(0);
        }
    }

    // Обробка сирого 16-бітного SPI кадру
    [[nodiscard]] std::expected<AngleReading, Error> processSpiFrame(uint16_t rxFrame) noexcept {
        if (!validateParity(rxFrame)) {
            return std::unexpected(Error::ParityMismatch);
        }
        if (rxFrame & 0x4000) {
            return std::unexpected(Error::DeviceErrorFlag);
        }

        const auto raw = static_cast<uint16_t>(rxFrame & 0x3FFF);

        if (!initialized_) {
            prevRaw_ = raw;
            initialized_ = true;
        }

        // Обробка переходу через границю 360° (Unwrap)
        const auto delta = static_cast<int32_t>(raw) - static_cast<int32_t>(prevRaw_);
        if (delta > (Cpr / 2)) {
            totalTurns_--;
        } else if (delta < -(Cpr / 2)) {
            totalTurns_++;
        }
        prevRaw_ = raw;

        // Лінеаризація за LUT
        const double errorLsb = interpolateError(raw);
        const double singleTurnLsb = static_cast<double>(raw) - errorLsb;

        const double singleTurnDeg = (singleTurnLsb * 360.0) / static_cast<double>(Cpr);
        const double totalCounts = static_cast<double>(totalTurns_) * static_cast<double>(Cpr) + singleTurnLsb;
        const double totalDeg = (totalCounts * 360.0) / static_cast<double>(Cpr);

        return AngleReading{
            .totalDegrees = totalDeg,
            .singleTurnDegrees = singleTurnDeg,
            .turns = totalTurns_
        };
    }

    void resetZero() noexcept {
        totalTurns_ = 0;
        initialized_ = false;
    }

    void setCalibrationTable(std::span<const int16_t, LutPoints> errorLut) noexcept {
        std::copy(errorLut.begin(), errorLut.end(), errorLut_.begin());
    }

private:
    static constexpr bool validateParity(uint16_t word) noexcept {
        uint16_t count = 0;
        for (int i = 0; i < 16; ++i) {
            if ((word >> i) & 1) ++count;
        }
        return (count % 2) == 0;
    }

    [[nodiscard]] double interpolateError(uint16_t rawAngle) const noexcept {
        const uint16_t indexLow = rawAngle / LutStep;
        const uint16_t indexHigh = (indexLow + 1) % LutPoints;
        const uint16_t fraction = rawAngle % LutStep;
        const double t = static_cast<double>(fraction) / static_cast<double>(LutStep);

        const auto errLow = static_cast<double>(errorLut_[indexLow]);
        const auto errHigh = static_cast<double>(errorLut_[indexHigh]);

        return errLow + t * (errHigh - errLow);
    }

    std::array<int16_t, LutPoints> errorLut_{};
    int32_t totalTurns_{0};
    uint16_t prevRaw_{0};
    bool initialized_{false};
};

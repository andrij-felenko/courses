#include <array>
#include <chrono>
#include <cmath>
#include <algorithm>

enum class ControlMode : uint8_t {
    Fresh = 0,
    Extrapolated,
    FallbackPid,
    SafeStop
};

template <size_t OutputDim>
class DeadlineWatchdog {
public:
    using FrameType = PredictionFrame<float, OutputDim>;

    struct Config {
        std::chrono::microseconds deadlineLimit{50'000};
        std::chrono::microseconds maxExtrapolation{100'000};
        std::chrono::microseconds fatalTimeout{500'000};
        float decayLambda{15.0f};
    };

    explicit DeadlineWatchdog(Config config) noexcept : cfg_{config} {
        lastDerivative_.fill(0.0f);
    }

    std::pair<std::array<float, OutputDim>, ControlMode> evaluate(
        const FrameType& incomingData,
        bool isFresh,
        std::chrono::microseconds currentTime) noexcept 
    {
        if (isFresh) {
            if (lastValidFrame_.timestamp.count() > 0) {
                auto deltaUs = incomingData.timestamp - lastValidFrame_.timestamp;
                float dtSec = std::chrono::duration<float>(deltaUs).count();
                if (dtSec > 1e-4f) {
                    for (size_t i = 0; i < OutputDim; ++i) {
                        lastDerivative_[i] = (incomingData.values[i] - lastValidFrame_.values[i]) / dtSec;
                    }
                }
            }
            lastValidFrame_ = incomingData;
        }

        std::array<float, OutputDim> correction{};

        if (lastValidFrame_.timestamp.count() == 0) {
            return { correction, ControlMode::FallbackPid };
        }

        auto age = currentTime - lastValidFrame_.timestamp;

        // Режим 1: Свіжі дані в межах дедлайну
        if (age <= cfg_.deadlineLimit) {
            return { lastValidFrame_.values, ControlMode::Fresh };
        }

        // Режим 2: Екстраполяція з урахуванням швидкості зміни та згасання
        if (age <= cfg_.maxExtrapolation) {
            auto extrapDelta = age - cfg_.deadlineLimit;
            float dtExtrap = std::chrono::duration<float>(extrapDelta).count();
            float decay = std::exp(-cfg_.decayLambda * dtExtrap);

            for (size_t i = 0; i < OutputDim; ++i) {
                float rawExtrap = lastValidFrame_.values[i] + lastDerivative_[i] * dtExtrap;
                correction[i] = rawExtrap * decay;
            }
            return { correction, ControlMode::Extrapolated };
        }

        // Режим 3: Перехід на детермінований Fallback PID
        if (age <= cfg_.fatalTimeout) {
            return { correction, ControlMode::FallbackPid };
        }

        // Режим 4: Фатальний таймаут -> Безпечна аварійна зупинка
        return { correction, ControlMode::SafeStop };
    }

private:
    Config cfg_;
    FrameType lastValidFrame_{};
    std::array<float, OutputDim> lastDerivative_{};
};

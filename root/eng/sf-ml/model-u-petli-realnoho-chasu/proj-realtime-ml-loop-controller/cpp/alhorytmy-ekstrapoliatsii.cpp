namespace realtime::control {

template <typename T, size_t Dim>
class RealTimeMLController {
public:
    using Frame = PredictionFrame<T, Dim>;

    explicit RealTimeMLController(WatchdogConfig cfg) noexcept 
        : cfg_{cfg} {
        lastDerivatives_.fill(T{0});
        lastAppliedOutput_.fill(T{0});
    }

    std::pair<std::array<T, Dim>, ControlStatus> update(
        const Frame& incomingFrame,
        bool isFresh,
        Microseconds currentTime) noexcept 
    {
        if (isFresh) {
            totalFrames_++;
            if (lastValidFrame_.timestamp.count() > 0) {
                auto latency = currentTime - incomingFrame.timestamp;
                if (latency > maxObservedLatency_) {
                    maxObservedLatency_ = latency;
                }

                auto dt = incomingFrame.timestamp - lastValidFrame_.timestamp;
                float dtSec = std::chrono::duration<float>(dt).count();
                if (dtSec > 1e-4f) {
                    for (size_t i = 0; i < Dim; ++i) {
                        lastDerivatives_[i] = (incomingFrame.values[i] - lastValidFrame_.values[i]) / dtSec;
                    }
                }
            }
            lastValidFrame_ = incomingFrame;
        }

        std::array<T, Dim> correction{};

        if (lastValidFrame_.timestamp.count() == 0) {
            return { correction, ControlStatus::FallbackPid };
        }

        auto age = currentTime - lastValidFrame_.timestamp;

        // 1. Fresh
        if (age <= cfg_.deadlineLimit) {
            for (size_t i = 0; i < Dim; ++i) {
                correction[i] = lastValidFrame_.values[i];
                lastAppliedOutput_[i] = correction[i];
            }
            return { correction, ControlStatus::Fresh };
        }

        deadlineMissCount_++;

        // 2. Extrapolated
        if (age <= cfg_.maxExtrapolation) {
            auto dtExtrap = age - cfg_.deadlineLimit;
            float dtSec = std::chrono::duration<float>(dtExtrap).count();
            float decay = std::exp(-cfg_.decayLambda * dtSec);

            for (size_t i = 0; i < Dim; ++i) {
                float rawVal = lastValidFrame_.values[i] + lastDerivatives_[i] * dtSec;
                correction[i] = static_cast<T>(rawVal * decay);
                lastAppliedOutput_[i] = correction[i];
            }
            return { correction, ControlStatus::Extrapolated };
        }

        fallbackCount_++;

        // 3. Fallback PID
        if (age <= cfg_.fatalTimeout) {
            return { correction, ControlStatus::FallbackPid };
        }

        // 4. Emergency Stop
        return { correction, ControlStatus::EmergencyStop };
    }

    [[nodiscard]] uint32_t getDeadlineMissCount() const noexcept { return deadlineMissCount_; }
    [[nodiscard]] Microseconds getMaxLatency() const noexcept { return maxObservedLatency_; }

private:
    WatchdogConfig cfg_;
    Frame lastValidFrame_{};
    std::array<T, Dim> lastAppliedOutput_{};
    std::array<T, Dim> lastDerivatives_{};

    uint32_t totalFrames_{0};
    uint32_t deadlineMissCount_{0};
    uint32_t fallbackCount_{0};
    Microseconds maxObservedLatency_{0};
};

template <std::floating_point T>
class FallbackPID {
public:
    struct Gains {
        T kp{1.0};
        T ki{0.1};
        T kd{0.05};
        T ts{0.001};
        T minVal{-100.0};
        T maxVal{100.0};
    };

    explicit FallbackPID(Gains g) noexcept : g_{g} {}

    T step(T setpoint, T feedback, T externalActiveU, bool isFallbackActive) noexcept {
        T error = setpoint - feedback;
        T pTerm = g_.kp * error;
        T dTerm = (g_.ts > T{1e-6}) ? (g_.kd * (error - prevError_) / g_.ts) : T{0};
        prevError_ = error;

        if (!isFallbackActive) {
            // Bumpless transfer tracking
            if (std::abs(g_.ki) > T{1e-6}) {
                integralAccum_ = (externalActiveU - pTerm - dTerm) / g_.ki;
            }
            return externalActiveU;
        }

        integralAccum_ += error * g_.ts;
        T rawU = pTerm + g_.ki * integralAccum_ + dTerm;

        // Anti-windup clamping
        if (rawU > g_.maxVal) {
            rawU = g_.maxVal;
            if (error > T{0}) integralAccum_ -= error * g_.ts;
        } else if (rawU < g_.minVal) {
            rawU = g_.minVal;
            if (error < T{0}) integralAccum_ -= error * g_.ts;
        }

        return rawU;
    }

private:
    Gains g_;
    T integralAccum_{0};
    T prevError_{0};
};

} // namespace realtime::control

#include <cstdint>
#include <algorithm>

/* Стан автомата софтстартера */
enum class SoftStartState : uint8_t {
    Idle,
    Kickstart,
    RampUp,
    FullOn,
    Bypass,
    RampDown,
    Fault
};

/* Коди помилок захисту приводу */
enum class SoftStartFault : uint8_t {
    None = 0,
    PhaseLoss,
    Overcurrent,
    Stall,
    Overheat
};

/* Параметри конфігурації приводу */
struct SoftStartConfig {
    uint32_t kickstartTimeMs{200};    // Час імпульсу поштовху, мс (0 = вимкнено)
    float    kickstartAlphaDeg{45.0f}; // Кут для поштовху (типово 45..60 град)
    uint32_t rampUpTimeMs{5000};      // Час розгону напруги, мс
    uint32_t rampDownTimeMs{3000};    // Час плавної зупинки, мс
    float    initialAlphaDeg{135.0f};  // Початковий кут пуску (типово 135 град)
    float    stopAlphaDeg{145.0f};     // Кінцевий кут зупинки (типово 145 град)
    float    currentLimitAmps{150.0f}; // Максимально допустимий пусковий струм
    float    kp{0.8f};                 // Пропорційний коефіцієнт струмового ПІД
    float    ki{1.5f};                 // Інтегральний коефіцієнт струмового ПІД
};

/* Об'єктно-орієнтований контролер трифазного софтстартера */
class SoftStartController {
public:
    explicit constexpr SoftStartController(const SoftStartConfig& config)
        : cfg_{config},
          state_{SoftStartState::Idle},
          fault_{SoftStartFault::None},
          currentAlphaDeg_{config.initialAlphaDeg} {}

    void start() noexcept {
        if (state_ != SoftStartState::Idle) return;

        stateTimerMs_ = 0;
        integralError_ = 0.0f;
        gatePulsesEnabled_ = true;
        bypassRelayCmd_ = false;
        fault_ = SoftStartFault::None;

        if (cfg_.kickstartTimeMs > 0) {
            state_ = SoftStartState::Kickstart;
            currentAlphaDeg_ = cfg_.kickstartAlphaDeg;
        } else {
            state_ = SoftStartState::RampUp;
            currentAlphaDeg_ = cfg_.initialAlphaDeg;
        }
    }

    void stop() noexcept {
        if (state_ == SoftStartState::Bypass || state_ == SoftStartState::FullOn) {
            state_ = SoftStartState::RampDown;
            stateTimerMs_ = 0;
            gatePulsesEnabled_ = true;  // Тиристори миттєво підхоплюють струм
            bypassRelayCmd_ = false;    // Контактор розмикається
            currentAlphaDeg_ = 0.0f;
        }
    }

    void processHalfCycle(float measuredCurrentRms, uint32_t dtMs) noexcept {
        stateTimerMs_ += dtMs;

        switch (state_) {
            case SoftStartState::Idle:
                gatePulsesEnabled_ = false;
                bypassRelayCmd_ = false;
                break;

            case SoftStartState::Kickstart:
                if (stateTimerMs_ >= cfg_.kickstartTimeMs) {
                    state_ = SoftStartState::RampUp;
                    stateTimerMs_ = 0;
                    currentAlphaDeg_ = cfg_.initialAlphaDeg;
                }
                break;

            case SoftStartState::RampUp: {
                const float rampProgress = std::clamp(
                    static_cast<float>(stateTimerMs_) / static_cast<float>(cfg_.rampUpTimeMs),
                    0.0f, 1.0f
                );

                float targetAlpha = cfg_.initialAlphaDeg * (1.0f - rampProgress);

                // Замкнений контур обмеження струму (Current Limit PI)
                if (measuredCurrentRms > cfg_.currentLimitAmps) {
                    const float err = measuredCurrentRms - cfg_.currentLimitAmps;
                    integralError_ += err * (static_cast<float>(dtMs) / 1000.0f);
                    const float piCorrection = (cfg_.kp * err) + (cfg_.ki * integralError_);
                    targetAlpha = std::min(targetAlpha + piCorrection, cfg_.initialAlphaDeg);
                } else if (integralError_ > 0.0f) {
                    integralError_ = std::max(0.0f, integralError_ - 0.1f * (static_cast<float>(dtMs) / 1000.0f));
                }

                currentAlphaDeg_ = targetAlpha;

                if (rampProgress >= 1.0f && currentAlphaDeg_ <= 2.0f) {
                    currentAlphaDeg_ = 0.0f;
                    state_ = SoftStartState::FullOn;
                    stateTimerMs_ = 0;
                }
                break;
            }

            case SoftStartState::FullOn:
                currentAlphaDeg_ = 0.0f;
                bypassRelayCmd_ = true;
                if (stateTimerMs_ >= 100) { // 100 мс на спрацьовування котушки контактора
                    state_ = SoftStartState::Bypass;
                    gatePulsesEnabled_ = false;
                }
                break;

            case SoftStartState::Bypass:
                gatePulsesEnabled_ = false;
                bypassRelayCmd_ = true;
                break;

            case SoftStartState::RampDown: {
                const float stopProgress = std::clamp(
                    static_cast<float>(stateTimerMs_) / static_cast<float>(cfg_.rampDownTimeMs),
                    0.0f, 1.0f
                );

                currentAlphaDeg_ = cfg_.stopAlphaDeg * stopProgress;

                if (stopProgress >= 1.0f) {
                    state_ = SoftStartState::Idle;
                    gatePulsesEnabled_ = false;
                    bypassRelayCmd_ = false;
                }
                break;
            }

            case SoftStartState::Fault:
                gatePulsesEnabled_ = false;
                bypassRelayCmd_ = false;
                break;
        }
    }

    [[nodiscard]] uint32_t firingDelayUs() const noexcept {
        constexpr float kHalfCycleUs = 10000.0f; // 10 мс для 50 Гц
        const float clampedAlpha = std::clamp(currentAlphaDeg_, 0.0f, 180.0f);
        return static_cast<uint32_t>((clampedAlpha / 180.0f) * kHalfCycleUs);
    }

    [[nodiscard]] SoftStartState state() const noexcept { return state_; }
    [[nodiscard]] SoftStartFault fault() const noexcept { return fault_; }
    [[nodiscard]] bool isBypassActive() const noexcept { return bypassRelayCmd_; }
    [[nodiscard]] bool areGatesEnabled() const noexcept { return gatePulsesEnabled_; }
    [[nodiscard]] float alphaDeg() const noexcept { return currentAlphaDeg_; }

private:
    SoftStartConfig  cfg_;
    SoftStartState   state_{SoftStartState::Idle};
    SoftStartFault   fault_{SoftStartFault::None};
    float            currentAlphaDeg_{135.0f};
    uint32_t         stateTimerMs_{0};
    float            integralError_{0.0f};
    bool             bypassRelayCmd_{false};
    bool             gatePulsesEnabled_{false};
};

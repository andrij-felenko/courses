// corona_driver.cpp — Ідіоматична реалізація драйвера корони мовою C++20

#include <cstdint>
#include <optional>
#include <system_error>

namespace PowerElectronics {

enum class CoronaState : uint8_t {
    Off,
    SoftStart,
    Running,
    ArcTripped,
    FaultHardware
};

struct CoronaConfig {
    uint32_t targetCurrentUa{200};
    uint32_t tripCurrentUa{1500};
    uint16_t maxPwmDuty{1024};
    uint32_t recoveryDelayMs{50};
    int32_t kp{2};
    int32_t ki{1};
};

class CoronaPowerSupply {
public:
    explicit CoronaPowerSupply(CoronaConfig config)
        : config_(config), state_(CoronaState::Off) {}

    ~CoronaPowerSupply() {
        stopHardwarePwm();
    }

    // Заборона копіювання (RAII керування високою напругою)
    CoronaPowerSupply(const CoronaPowerSupply&) = delete;
    CoronaPowerSupply& operator=(const CoronaPowerSupply&) = delete;

    CoronaPowerSupply(CoronaPowerSupply&&) noexcept = default;
    CoronaPowerSupply& operator=(CoronaPowerSupply&&) noexcept = default;

    void start() noexcept {
        state_ = CoronaState::SoftStart;
        pwmDuty_ = 50;
        integral_ = 0;
        applyHardwarePwm(pwmDuty_);
    }

    void stop() noexcept {
        state_ = CoronaState::Off;
        stopHardwarePwm();
    }

    // Швидкий обробник АЦП (викликається з ISR)
    void processAdcSample(uint32_t measuredCurrentUa) noexcept {
        currentUa_ = measuredCurrentUa;

        if (state_ == CoronaState::Off || state_ == CoronaState::FaultHardware) {
            return;
        }

        // Аварійний захист від пробою дуги
        if (measuredCurrentUa >= config_.tripCurrentUa) {
            stopHardwarePwm();
            state_ = CoronaState::ArcTripped;
            tripCount_++;
            recoveryTimerMs_ = config_.recoveryDelayMs;
            return;
        }

        if (state_ == CoronaState::Running || state_ == CoronaState::SoftStart) {
            updateControlLoop(measuredCurrentUa);
        }
    }

    void handleSysTick1ms() noexcept {
        if (state_ == CoronaState::ArcTripped) {
            if (recoveryTimerMs_ > 0) {
                --recoveryTimerMs_;
            } else {
                start(); // М'який перезапуск
            }
        }
    }

    [[nodiscard]] CoronaState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t currentUa() const noexcept { return currentUa_; }
    [[nodiscard]] uint16_t pwmDuty() const noexcept { return pwmDuty_; }
    [[nodiscard]] uint32_t tripCount() const noexcept { return tripCount_; }

private:
    void updateControlLoop(uint32_t iMeas) noexcept {
        const int32_t error = static_cast<int32_t>(config_.targetCurrentUa) - static_cast<int32_t>(iMeas);
        integral_ += error;

        if (integral_ > 5000) integral_ = 5000;
        if (integral_ < -5000) integral_ = -5000;

        const int32_t output = (config_.kp * error) + ((config_.ki * integral_) / 100);
        int32_t newDuty = static_cast<int32_t>(pwmDuty_) + (output / 10);

        if (newDuty > static_cast<int32_t>(config_.maxPwmDuty)) newDuty = config_.maxPwmDuty;
        if (newDuty < 0) newDuty = 0;

        pwmDuty_ = static_cast<uint16_t>(newDuty);
        applyHardwarePwm(pwmDuty_);

        if (state_ == CoronaState::SoftStart && iMeas >= (config_.targetCurrentUa * 8 / 10)) {
            state_ = CoronaState::Running;
        }
    }

    void applyHardwarePwm(uint16_t duty) noexcept {
        // Реєстровий виклик периферії MCU
        pwmDuty_ = duty;
    }

    void stopHardwarePwm() noexcept {
        pwmDuty_ = 0;
        applyHardwarePwm(0);
    }

    CoronaConfig config_;
    CoronaState state_;
    uint32_t currentUa_{0};
    uint16_t pwmDuty_{0};
    uint32_t tripCount_{0};
    uint32_t recoveryTimerMs_{0};
    int32_t integral_{0};
};

} // namespace PowerElectronics

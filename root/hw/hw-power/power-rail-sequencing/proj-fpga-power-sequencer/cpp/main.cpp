#include <array>
#include <cstdint>
#include <string_view>
#include <span>

/* Апаратний інтерфейс платформи (драйвер вводу-виводу та АЦП) */
class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;
    virtual void setPin(uint8_t pin, bool level) noexcept = 0;
    virtual uint16_t readAdcMv(uint8_t channel) noexcept = 0;
};

class PowerSequencer {
public:
    enum class State : uint8_t {
        Idle,
        StartCore,
        StartAux,
        StartIo,
        Running,
        StopIo,
        StopAux,
        StopCore,
        Fault
    };

    enum class FaultReason : uint8_t {
        None,
        CoreTimeout,
        AuxTimeout,
        IoTimeout,
        RuntimeCoreDrop,
        RuntimeAuxDrop,
        RuntimeIoDrop
    };

    struct RailConfig {
        std::string_view name;
        uint16_t vMinMv;
        uint16_t vMaxMv;
        uint8_t  enablePin;
        uint8_t  dischargePin;
    };

    static constexpr size_t RailCount = 3;
    static constexpr uint32_t TimeoutTicks = 25;
    static constexpr uint32_t StabilizeTicks = 5;

    explicit PowerSequencer(IHardwareDriver& hwDriver) noexcept
        : hw_(hwDriver),
          state_(State::Idle),
          fault_(FaultReason::None),
          timerTicks_(0),
          measuredMv_{}
    {
        for (const auto& rail : rails_) {
            hw_.setPin(rail.enablePin, false);
            hw_.setPin(rail.dischargePin, true); /* За замовчуванням розряд увімкнено */
        }
    }

    void start() noexcept {
        if (state_ == State::Idle) {
            hw_.setPin(rails_[0].dischargePin, false);
            hw_.setPin(rails_[0].enablePin, true);
            state_ = State::StartCore;
            timerTicks_ = 0;
            fault_ = FaultReason::None;
        }
    }

    void shutdown() noexcept {
        if (state_ == State::Running) {
            hw_.setPin(rails_[2].enablePin, false);
            hw_.setPin(rails_[2].dischargePin, true);
            state_ = State::StopIo;
            timerTicks_ = 0;
        }
    }

    void poll1ms() noexcept {
        for (size_t i = 0; i < RailCount; ++i) {
            measuredMv_[i] = hw_.readAdcMv(static_cast<uint8_t>(i));
        }
        ++timerTicks_;

        switch (state_) {
            case State::Idle:
                break;

            case State::StartCore:
                handleStartCore();
                break;

            case State::StartAux:
                handleStartAux();
                break;

            case State::StartIo:
                handleStartIo();
                break;

            case State::Running:
                handleRunning();
                break;

            case State::StopIo:
                handleStopIo();
                break;

            case State::StopAux:
                handleStopAux();
                break;

            case State::StopCore:
                handleStopCore();
                break;

            case State::Fault:
                break;
        }
    }

    [[nodiscard]] State getState() const noexcept { return state_; }
    [[nodiscard]] FaultReason getFault() const noexcept { return fault_; }
    [[nodiscard]] std::span<const uint16_t, RailCount> getVoltages() const noexcept {
        return measuredMv_;
    }

private:
    [[nodiscard]] bool isRailInRange(size_t index) const noexcept {
        const auto v = measuredMv_[index];
        return (v >= rails_[index].vMinMv && v <= rails_[index].vMaxMv);
    }

    void handleStartCore() noexcept {
        if (isRailInRange(0)) {
            if (timerTicks_ >= StabilizeTicks) {
                hw_.setPin(rails_[1].dischargePin, false);
                hw_.setPin(rails_[1].enablePin, true);
                state_ = State::StartAux;
                timerTicks_ = 0;
            }
        } else if (timerTicks_ > TimeoutTicks) {
            fault_ = FaultReason::CoreTimeout;
            state_ = State::StopCore;
        }
    }

    void handleStartAux() noexcept {
        if (isRailInRange(1) && isRailInRange(0)) {
            if (timerTicks_ >= StabilizeTicks) {
                hw_.setPin(rails_[2].dischargePin, false);
                hw_.setPin(rails_[2].enablePin, true);
                state_ = State::StartIo;
                timerTicks_ = 0;
            }
        } else if (timerTicks_ > TimeoutTicks) {
            fault_ = FaultReason::AuxTimeout;
            state_ = State::StopAux;
        }
    }

    void handleStartIo() noexcept {
        if (isRailInRange(2) && isRailInRange(1) && isRailInRange(0)) {
            if (timerTicks_ >= StabilizeTicks) {
                state_ = State::Running;
                timerTicks_ = 0;
            }
        } else if (timerTicks_ > TimeoutTicks) {
            fault_ = FaultReason::IoTimeout;
            state_ = State::StopIo;
        }
    }

    void handleRunning() noexcept {
        if (!isRailInRange(0)) {
            fault_ = FaultReason::RuntimeCoreDrop;
            shutdown();
        } else if (!isRailInRange(1)) {
            fault_ = FaultReason::RuntimeAuxDrop;
            shutdown();
        } else if (!isRailInRange(2)) {
            fault_ = FaultReason::RuntimeIoDrop;
            shutdown();
        }
    }

    void handleStopIo() noexcept {
        if (timerTicks_ >= StabilizeTicks) {
            hw_.setPin(rails_[1].enablePin, false);
            hw_.setPin(rails_[1].dischargePin, true);
            state_ = State::StopAux;
            timerTicks_ = 0;
        }
    }

    void handleStopAux() noexcept {
        if (timerTicks_ >= StabilizeTicks) {
            hw_.setPin(rails_[0].enablePin, false);
            hw_.setPin(rails_[0].dischargePin, true);
            state_ = State::StopCore;
            timerTicks_ = 0;
        }
    }

    void handleStopCore() noexcept {
        if (timerTicks_ >= StabilizeTicks) {
            state_ = (fault_ == FaultReason::None) ? State::Idle : State::Fault;
        }
    }

    IHardwareDriver& hw_;
    State state_;
    FaultReason fault_;
    uint32_t timerTicks_;
    std::array<uint16_t, RailCount> measuredMv_;

    static constexpr std::array<RailConfig, RailCount> rails_{{
        { "V_CORE", 800,  900,  10, 11 },
        { "V_AUX",  1710, 1890, 12, 13 },
        { "V_IO",   3130, 3470, 14, 15 }
    }};
};

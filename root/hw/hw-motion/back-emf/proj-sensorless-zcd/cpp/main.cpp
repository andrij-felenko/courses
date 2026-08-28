#include <cstdint>
#include <array>
#include <algorithm>

enum class MotorState : uint8_t {
    Idle = 0,
    Align,
    OpenLoopRamp,
    ClosedLoop
};

enum class ZcdEdge : uint8_t {
    Rising = 0,
    Falling
};

struct StepConfig {
    uint8_t high_side_pin;
    uint8_t low_side_pin;
    uint8_t floating_phase;
    ZcdEdge expected_edge;
};

// Апаратний інтерфейс (ін'єкція залежностей)
struct IBldcHardware {
    virtual void setInverterStep(uint8_t step) = 0;
    virtual void setPwmDuty(uint16_t duty) = 0;
    virtual void selectComparatorPhase(uint8_t phaseIndex) = 0;
    virtual void scheduleTimerInterrupt(uint32_t delayUs) = 0;
    virtual uint32_t getMicros() const = 0;
    virtual ~IBldcHardware() = default;
};

class BldcSensorlessController {
public:
    static constexpr size_t kNumSteps = 6;

    explicit BldcSensorlessController(IBldcHardware& hardware)
        : hw_(hardware) {}

    void start(uint16_t alignDuty = 300) {
        state_ = MotorState::Align;
        currentStep_ = 0;
        hw_.setPwmDuty(alignDuty);
        hw_.setInverterStep(0);
        hw_.scheduleTimerInterrupt(50000); // 50 мс на вирівнювання
    }

    void stop() {
        state_ = MotorState::Idle;
        hw_.setPwmDuty(0);
    }

    // Викликається з ISR аналогового компаратора
    void onComparatorEdge() {
        if (state_ != MotorState::ClosedLoop) {
            return;
        }

        const uint32_t now = hw_.getMicros();
        const uint32_t elapsed = now - lastCommTimeUs_;

        // Фільтрація комутаційного викиду індуктивності
        if (elapsed < blankingTimeUs_) {
            return;
        }

        if (!zcdDetected_) {
            zcdDetected_ = true;

            // 30° затримка: тривалість від початку кроку до перетину нуля
            uint32_t delay30DegUs = elapsed;
            constexpr uint32_t kRcFilterLagUs = 15;

            if (delay30DegUs > kRcFilterLagUs) {
                delay30DegUs -= kRcFilterLagUs;
            }

            if (delay30DegUs > 10) {
                hw_.scheduleTimerInterrupt(delay30DegUs);
            } else {
                advanceCommutation();
            }
        }
    }

    // Викликається з ISR таймера
    void onTimerEvent() {
        switch (state_) {
            case MotorState::Align:
                state_ = MotorState::OpenLoopRamp;
                openLoopDelayUs_ = 4000;
                advanceCommutation();
                hw_.scheduleTimerInterrupt(openLoopDelayUs_);
                break;

            case MotorState::OpenLoopRamp:
                advanceCommutation();
                if (openLoopDelayUs_ > 800) {
                    openLoopDelayUs_ -= 100;
                    hw_.scheduleTimerInterrupt(openLoopDelayUs_);
                } else {
                    state_ = MotorState::ClosedLoop;
                    lastCommTimeUs_ = hw_.getMicros();
                }
                break;

            case MotorState::ClosedLoop:
                advanceCommutation();
                break;

            default:
                break;
        }
    }

    [[nodiscard]] MotorState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t stepDurationUs() const noexcept { return stepDurationUs_; }

private:
    void advanceCommutation() {
        const uint32_t now = hw_.getMicros();
        stepDurationUs_ = now - lastCommTimeUs_;
        lastCommTimeUs_ = now;

        currentStep_ = (currentStep_ + 1) % kNumSteps;
        hw_.setInverterStep(currentStep_);

        // Динамічне вікно маскування: 20% від тривалості сектора (мін. 20 мкс)
        blankingTimeUs_ = std::max<uint32_t>(20, stepDurationUs_ / 5);
        zcdDetected_ = false;

        const auto& cfg = kSixStepTable[currentStep_];
        hw_.selectComparatorPhase(cfg.floating_phase);
    }

    static constexpr std::array<StepConfig, kNumSteps> kSixStepTable = {{
        {0, 1, 2, ZcdEdge::Rising},   // 0: U+, V-, W floating
        {0, 2, 1, ZcdEdge::Falling},  // 1: U+, W-, V floating
        {1, 2, 0, ZcdEdge::Rising},   // 2: V+, W-, U floating
        {1, 0, 2, ZcdEdge::Falling},  // 3: V+, U-, W floating
        {2, 0, 1, ZcdEdge::Rising},   // 4: W+, U-, V floating
        {2, 1, 0, ZcdEdge::Falling}   // 5: W+, V-, U floating
    }};

    IBldcHardware& hw_;
    MotorState state_{MotorState::Idle};
    uint8_t currentStep_{0};
    uint32_t lastCommTimeUs_{0};
    uint32_t stepDurationUs_{2000};
    uint32_t blankingTimeUs_{400};
    uint32_t openLoopDelayUs_{5000};
    bool zcdDetected_{false};
};

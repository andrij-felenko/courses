namespace Health {

enum class FaultInjectMode : uint8_t {
    None = 0,
    StackCorrupt,
    Undervoltage,
    CanBusOff,
    I2cLockup
};

class FaultInjector {
public:
    constexpr FaultInjector() noexcept = default;

    void trigger(FaultInjectMode mode, uint32_t duration_ticks) noexcept {
        active_mode_ = mode;
        duration_ticks_ = duration_ticks;
    }

    [[nodiscard]] uint16_t apply(FaultInjectMode target_mode, uint16_t actual_value) noexcept {
        if (active_mode_ != target_mode || duration_ticks_ == 0) {
            return actual_value;
        }

        --duration_ticks_;
        if (duration_ticks_ == 0) {
            active_mode_ = FaultInjectMode::None;
        }

        switch (target_mode) {
            case FaultInjectMode::Undervoltage: return 100;
            case FaultInjectMode::CanBusOff:   return 0;
            case FaultInjectMode::I2cLockup:   return 50;
            case FaultInjectMode::StackCorrupt: return 0;
            default: return actual_value;
        }
    }

    [[nodiscard]] bool is_active() const noexcept { return active_mode_ != FaultInjectMode::None; }

private:
    FaultInjectMode active_mode_{FaultInjectMode::None};
    uint32_t        duration_ticks_{0};
};

} // namespace Health

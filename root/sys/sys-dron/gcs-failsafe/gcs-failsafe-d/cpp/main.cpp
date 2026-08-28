#include <cstdint>
#include <chrono>

struct ManualAxes {
    int16_t pitch{0};    // -1000 .. +1000
    int16_t roll{0};     // -1000 .. +1000
    int16_t throttle{0}; // 0 .. 1000
    int16_t yaw{0};      // -1000 .. +1000
};

class JoystickFailsafe {
public:
    using Milliseconds = std::chrono::milliseconds;
    using TimePoint = std::chrono::steady_clock::time_point;

    explicit JoystickFailsafe(Milliseconds timeout = Milliseconds{1000})
        : timeoutThreshold_(timeout) {}

    void onManualControlPacket(const ManualAxes& axes, TimePoint now = std::chrono::steady_clock::now()) noexcept {
        currentAxes_ = axes;
        lastPacketTime_ = now;
        isActive_ = true;
        isFailsafeEngaged_ = false;
    }

    void update(TimePoint now = std::chrono::steady_clock::now()) noexcept {
        if (!isActive_) {
            return;
        }

        auto elapsed = std::chrono::duration_cast<Milliseconds>(now - lastPacketTime_);
        if (elapsed >= timeoutThreshold_) {
            // Примусове центрування осей керування
            currentAxes_.pitch = 0;
            currentAxes_.roll = 0;
            currentAxes_.yaw = 0;
            currentAxes_.throttle = 500; // Нейтральна тяга утримання висоти
            isFailsafeEngaged_ = true;
        }
    }

    [[nodiscard]] const ManualAxes& axes() const noexcept { return currentAxes_; }
    [[nodiscard]] bool isFailsafeEngaged() const noexcept { return isFailsafeEngaged_; }
    [[nodiscard]] bool isActive() const noexcept { return isActive_; }

private:
    Milliseconds timeoutThreshold_;
    ManualAxes currentAxes_{};
    TimePoint lastPacketTime_{};
    bool isActive_{false};
    bool isFailsafeEngaged_{false};
};

#include <cstdint>
#include <chrono>
#include <optional>

class PirDigitalDetector {
public:
    using Milliseconds = std::chrono::milliseconds;

    constexpr PirDigitalDetector(Milliseconds debounceTime, Milliseconds holdTime) noexcept
        : debounceTime_{debounceTime}, holdTime_{holdTime} {}

    struct Event {
        enum class Type : uint8_t {
            MotionStarted,
            MotionEnded
        };
        Type type;
        Milliseconds timestamp;
    };

    [[nodiscard]] std::optional<Event> update(bool pinLevel, Milliseconds currentTime) noexcept {
        std::optional<Event> result = std::nullopt;

        // Перевірка зміни фізичного рівня сигналу
        if (pinLevel != rawState_) {
            rawState_ = pinLevel;
            lastEdgeTime_ = currentTime;
        }

        // Перевірка стабільності рівня протягом вікна антибрязку
        if ((currentTime - lastEdgeTime_) >= debounceTime_) {
            if (rawState_ != stableState_) {
                stableState_ = rawState_;

                if (stableState_) {
                    motionActive_ = true;
                    motionStartTime_ = currentTime;
                    result = Event{Event::Type::MotionStarted, currentTime};
                }
            }
        }

        // Логіка утримання активного стану присутності
        if (motionActive_) {
            if (stableState_) {
                motionStartTime_ = currentTime;
            } else if ((currentTime - motionStartTime_) >= holdTime_) {
                motionActive_ = false;
                result = Event{Event::Type::MotionEnded, currentTime};
            }
        }

        return result;
    }

    [[nodiscard]] bool isOccupied() const noexcept {
        return motionActive_;
    }

    void reset() noexcept {
        rawState_ = false;
        stableState_ = false;
        motionActive_ = false;
        lastEdgeTime_ = Milliseconds{0};
        motionStartTime_ = Milliseconds{0};
    }

private:
    Milliseconds debounceTime_{100};
    Milliseconds holdTime_{3000};
    Milliseconds lastEdgeTime_{0};
    Milliseconds motionStartTime_{0};

    bool rawState_{false};
    bool stableState_{false};
    bool motionActive_{false};
};

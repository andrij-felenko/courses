#include <cstdint>
#include <algorithm>

namespace drone::autonomy {

class GoalTransitionFilter {
public:
    constexpr GoalTransitionFilter(float upperThreshold,
                                   float lowerThreshold,
                                   uint32_t debounceUs,
                                   uint32_t dwellUs,
                                   uint32_t nowUs) noexcept
        : upperThreshold_(upperThreshold),
          lowerThreshold_(lowerThreshold),
          debounceTimeUs_(debounceUs),
          dwellTimeUs_(dwellUs),
          stateEnteredUs_(nowUs) {}

    [[nodiscard]] bool update(float metricValue,
                              uint32_t nowUs,
                              bool emergencyOverride = false) noexcept
    {
        // 0. Аварійне переривання нульового рангу (FTS, парашут)
        if (emergencyOverride) {
            currentState_ = false;
            schmittState_ = false;
            pendingActivation_ = false;
            stateEnteredUs_ = nowUs;
            return false;
        }

        // 1. Скалярний тригер Шмітта
        if (schmittState_) {
            if (metricValue <= lowerThreshold_) {
                schmittState_ = false;
            }
        } else {
            if (metricValue >= upperThreshold_) {
                schmittState_ = true;
            }
        }

        // 2. Фільтрація перемикання через Dwell та Debounce
        if (currentState_) {
            if (!schmittState_) {
                const uint32_t timeInState = nowUs - stateEnteredUs_;
                if (timeInState >= dwellTimeUs_) {
                    currentState_ = false;
                    stateEnteredUs_ = nowUs;
                    pendingActivation_ = false;
                }
            } else {
                pendingActivation_ = false;
            }
        } else {
            if (schmittState_) {
                if (!pendingActivation_) {
                    pendingActivation_ = true;
                    conditionStartUs_ = nowUs;
                } else {
                    const uint32_t debounceElapsed = nowUs - conditionStartUs_;
                    if (debounceElapsed >= debounceTimeUs_) {
                        currentState_ = true;
                        stateEnteredUs_ = nowUs;
                        pendingActivation_ = false;
                    }
                }
            } else {
                pendingActivation_ = false;
            }
        }

        return currentState_;
    }

    [[nodiscard]] constexpr bool state() const noexcept { return currentState_; }
    [[nodiscard]] constexpr uint32_t stateEnteredTimeUs() const noexcept { return stateEnteredUs_; }

private:
    float    upperThreshold_{0.0f};
    float    lowerThreshold_{0.0f};
    uint32_t debounceTimeUs_{0};
    uint32_t dwellTimeUs_{0};
    uint32_t conditionStartUs_{0};
    uint32_t stateEnteredUs_{0};
    bool     schmittState_{false};
    bool     pendingActivation_{false};
    bool     currentState_{false};
};

} // namespace drone::autonomy

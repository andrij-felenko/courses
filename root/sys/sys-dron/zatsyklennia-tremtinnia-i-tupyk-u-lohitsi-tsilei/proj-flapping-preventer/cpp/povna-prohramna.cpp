#include <cstdint>
#include <array>
#include <algorithm>
#include <span>

namespace drone::autonomy {

enum class EscalationLevel : uint8_t {
    None = 0,
    StochasticJitter = 1,
    VirtualObstacle  = 2,
    AltitudeLayer    = 3,
    AbortLoiter      = 4
};

struct StateSignature {
    uint16_t stateId{0};
    int16_t  gridX{0};
    int16_t  gridY{0};
    int16_t  gridZ{0};
    uint32_t timestampMs{0};

    [[nodiscard]] constexpr bool operator==(const StateSignature& o) const noexcept {
        return (stateId == o.stateId) && (gridX == o.gridX) &&
               (gridY == o.gridY) && (gridZ == o.gridZ);
    }
};

template <size_t BufferSize = 16, size_t MaxNgram = 4>
class SpatialCycleDetector {
public:
    constexpr explicit SpatialCycleDetector(float gridResXy = 5.0f,
                                            float gridResZ = 2.0f,
                                            uint8_t repeatThreshold = 3) noexcept
        : gridResXy_(gridResXy > 0.1f ? gridResXy : 5.0f),
          gridResZ_(gridResZ > 0.1f ? gridResZ : 2.0f),
          repeatThreshold_(repeatThreshold) {}

    [[nodiscard]] uint8_t push(uint16_t stateId, float x, float y, float z, uint32_t nowMs) noexcept {
        const auto gx = static_cast<int16_t>(x / gridResXy_);
        const auto gy = static_cast<int16_t>(y / gridResXy_);
        const auto gz = static_cast<int16_t>(z / gridResZ_);

        if (count_ > 0) {
            const auto& last = atOffset(0);
            if (last.stateId == stateId && last.gridX == gx && last.gridY == gy && last.gridZ == gz) {
                return 0;
            }
            const float dx = x - lastPosX_;
            const float dy = y - lastPosY_;
            const float dz = z - lastPosZ_;
            if (last.stateId == stateId &&
                (dx * dx + dy * dy < 0.25f * gridResXy_ * gridResXy_) &&
                (dz * dz < 0.25f * gridResZ_ * gridResZ_))
            {
                return 0;
            }
        }

        history_[headIdx_] = StateSignature{stateId, gx, gy, gz, nowMs};
        headIdx_ = (headIdx_ + 1) % BufferSize;
        if (count_ < BufferSize) {
            count_++;
        }
        lastPosX_ = x;
        lastPosY_ = y;
        lastPosZ_ = z;

        for (uint8_t len = 2; len <= static_cast<uint8_t>(MaxNgram); ++len) {
            const size_t needed = static_cast<size_t>(len) * repeatThreshold_;
            if (count_ < needed) continue;

            bool match = true;
            for (uint8_t rep = 1; rep < repeatThreshold_; ++rep) {
                for (uint8_t i = 0; i < len; ++i) {
                    if (atOffset(i) != atOffset(static_cast<size_t>(rep) * len + i)) {
                        match = false;
                        break;
                    }
                }
                if (!match) break;
            }

            if (match) {
                return len;
            }
        }
        return 0;
    }

    void reset() noexcept {
        headIdx_ = 0;
        count_ = 0;
        lastPosX_ = -1e9f;
        lastPosY_ = -1e9f;
        lastPosZ_ = -1e9f;
    }

private:
    [[nodiscard]] constexpr const StateSignature& atOffset(size_t offset) const noexcept {
        const size_t idx = (headIdx_ + BufferSize - 1 - offset) % BufferSize;
        return history_[idx];
    }

    std::array<StateSignature, BufferSize> history_{};
    size_t   headIdx_{0};
    size_t   count_{0};
    float    gridResXy_{5.0f};
    float    gridResZ_{2.0f};
    float    lastPosX_{-1e9f};
    float    lastPosY_{-1e9f};
    float    lastPosZ_{-1e9f};
    uint8_t  repeatThreshold_{3};
};

class FlappingPreventer {
public:
    constexpr FlappingPreventer(float thHigh, float thLow,
                                uint32_t debounceUs, uint32_t dwellUs,
                                float gridXy, float gridZ,
                                uint32_t nowUs) noexcept
        : thHigh_(thHigh),
          thLow_(thLow),
          debounceUs_(debounceUs),
          dwellUs_(dwellUs),
          stateEnteredUs_(nowUs),
          cycleDetector_(gridXy, gridZ, 3) {}

    [[nodiscard]] bool process(float metricValue,
                               uint16_t stateId,
                               float x, float y, float z,
                               uint32_t nowUs,
                               bool emergency = false) noexcept
    {
        // 0. Аварійне переривання
        if (emergency) {
            activeState_ = false;
            schmittState_ = false;
            pendingActivation_ = false;
            stateEnteredUs_ = nowUs;
            return false;
        }

        // 1. Гістерезис
        if (schmittState_) {
            if (metricValue <= thLow_) schmittState_ = false;
        } else {
            if (metricValue >= thHigh_) schmittState_ = true;
        }

        // 2. Debounce та Dwell
        const bool prevActive = activeState_;
        if (activeState_) {
            if (!schmittState_) {
                if (nowUs - stateEnteredUs_ >= dwellUs_) {
                    activeState_ = false;
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
                    if (nowUs - conditionStartUs_ >= debounceUs_) {
                        activeState_ = true;
                        stateEnteredUs_ = nowUs;
                        pendingActivation_ = false;
                    }
                }
            } else {
                pendingActivation_ = false;
            }
        }

        if (schmittState_ != activeState_) {
            suppressedSwitches_++;
        }

        if (activeState_ != prevActive) {
            recordRate(nowUs);
        }

        // 3. Детекція зациклень
        const uint8_t cycle = cycleDetector_.push(stateId, x, y, z, nowUs / 1000);
        if (cycle > 0) {
            detectedCycleLen_ = cycle;
            if (escalation_ < EscalationLevel::AbortLoiter) {
                escalation_ = static_cast<EscalationLevel>(static_cast<uint8_t>(escalation_) + 1);
            }
        }

        return activeState_;
    }

    [[nodiscard]] constexpr bool state() const noexcept { return activeState_; }
    [[nodiscard]] constexpr EscalationLevel escalation() const noexcept { return escalation_; }
    [[nodiscard]] constexpr uint8_t detectedCycleLength() const noexcept { return detectedCycleLen_; }
    [[nodiscard]] constexpr uint32_t suppressedSwitches() const noexcept { return suppressedSwitches_; }
    [[nodiscard]] constexpr float switchingRateHz() const noexcept { return currentRateHz_; }

    void resetEscalation() noexcept {
        escalation_ = EscalationLevel::None;
        detectedCycleLen_ = 0;
        cycleDetector_.reset();
    }

private:
    void recordRate(uint32_t nowUs) noexcept {
        rateTimestamps_[rateHead_] = nowUs;
        rateHead_ = (rateHead_ + 1) % rateTimestamps_.size();
        if (rateCount_ < rateTimestamps_.size()) rateCount_++;
        if (rateCount_ >= 2) {
            const size_t oldest = (rateHead_ + rateTimestamps_.size() - rateCount_) % rateTimestamps_.size();
            const uint32_t dt = nowUs - rateTimestamps_[oldest];
            if (dt > 0) {
                currentRateHz_ = (static_cast<float>(rateCount_ - 1) * 1000000.0f) / static_cast<float>(dt);
            }
        }
    }

    float           thHigh_{0.0f};
    float           thLow_{0.0f};
    uint32_t        debounceUs_{0};
    uint32_t        dwellUs_{0};
    uint32_t        conditionStartUs_{0};
    uint32_t        stateEnteredUs_{0};
    bool            schmittState_{false};
    bool            pendingActivation_{false};
    bool            activeState_{false};
    uint32_t        suppressedSwitches_{0};
    float           currentRateHz_{0.0f};

    std::array<uint32_t, 8> rateTimestamps_{};
    size_t          rateHead_{0};
    size_t          rateCount_{0};

    SpatialCycleDetector<16, 4> cycleDetector_{};
    EscalationLevel escalation_{EscalationLevel::None};
    uint8_t         detectedCycleLen_{0};
};

} // namespace drone::autonomy

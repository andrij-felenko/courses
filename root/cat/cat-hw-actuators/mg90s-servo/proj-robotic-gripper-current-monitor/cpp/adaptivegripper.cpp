#include <cstdint>
#include <algorithm>

class AdaptiveGripper {
public:
    enum class State : uint8_t {
        Open,
        Approach,
        ContactDetect,
        Squeeze,
        Hold,
        StallError
    };

    struct Config {
        float minAngleDeg = 10.0f;
        float maxAngleDeg = 80.0f;
        uint16_t stallCurrentLimitMa = 750;
        uint16_t blankingTimeMs = 30;
        uint16_t squeezeTimeoutMs = 350;
        int16_t derivThreshold = 30;
    };

    AdaptiveGripper(const Config& cfg) : config_(cfg) {}

    void init() {
        state_ = State::Open;
        currentAngle_ = config_.minAngleDeg;
        stateTimerMs_ = 0;
        blankingTimerMs_ = 0;
        filteredCurrentQ8_ = 0;
        historyIdx_ = 0;
        std::fill(std::begin(history_), std::end(history_), 0);
    }

    void startGrasp(float targetForceN) {
        if (state_ == State::Open || state_ == State::Hold) {
            targetForceN_ = targetForceN;
            state_ = State::Approach;
            stateTimerMs_ = 0;
            blankingTimerMs_ = config_.blankingTimeMs;
        }
    }

    void open() {
        state_ = State::Open;
        currentAngle_ = config_.minAngleDeg;
        stateTimerMs_ = 0;
    }

    // Швидкий такт фільтрації (2 мс)
    void processAdc(uint16_t rawCurrentMa) {
        int32_t rawQ8 = static_cast<int32_t>(rawCurrentMa) << 8;
        filteredCurrentQ8_ = (26 * rawQ8 + 230 * filteredCurrentQ8_) >> 8;
        uint16_t currentMa = static_cast<uint16_t>(filteredCurrentQ8_ >> 8);

        history_[historyIdx_] = currentMa;
        historyIdx_ = (historyIdx_ + 1) & 0x03;

        // Аварійний переривник заклинювання
        if (state_ != State::Open && state_ != State::StallError) {
            if (currentMa >= config_.stallCurrentLimitMa) {
                state_ = State::StallError;
                currentAngle_ -= 5.0f;
            }
        }
    }

    // Такт логіки автомата (10 мс)
    void updateFsm(uint32_t dtMs) {
        stateTimerMs_ += dtMs;
        if (blankingTimerMs_ > 0) {
            blankingTimerMs_ = (blankingTimerMs_ >= dtMs) ? (blankingTimerMs_ - dtMs) : 0;
        }

        uint16_t currentMa = static_cast<uint16_t>(filteredCurrentQ8_ >> 8);
        uint8_t oldestIdx = historyIdx_;
        int16_t diDt = (static_cast<int16_t>(currentMa) - static_cast<int16_t>(history_[oldestIdx])) / 8;

        switch (state_) {
            case State::Open:
                break;

            case State::Approach:
                currentAngle_ += 2.0f;
                if (blankingTimerMs_ == 0) state_ = State::ContactDetect;
                break;

            case State::ContactDetect:
                currentAngle_ += 1.0f;
                if (diDt >= config_.derivThreshold) {
                    state_ = State::Squeeze;
                    stateTimerMs_ = 0;
                }
                break;

            case State::Squeeze: {
                currentAngle_ += 0.5f;
                float forceN = (currentMa > 165) ? static_cast<float>(currentMa - 165) * 0.013f : 0.0f;
                if (forceN >= targetForceN_) {
                    state_ = State::Hold;
                    currentAngle_ -= 0.8f; // Безпечний відкат
                } else if (stateTimerMs_ >= config_.squeezeTimeoutMs) {
                    state_ = State::StallError;
                }
                break;
            }

            case State::Hold:
            case State::StallError:
                break;
        }
    }

    State getState() const { return state_; }
    float getTargetAngle() const { return currentAngle_; }
    uint16_t getCurrentMa() const { return static_cast<uint16_t>(filteredCurrentQ8_ >> 8); }

private:
    Config config_;
    State state_ = State::Open;
    float currentAngle_ = 10.0f;
    float targetForceN_ = 3.0f;
    uint32_t stateTimerMs_ = 0;
    uint32_t blankingTimerMs_ = 0;
    int32_t filteredCurrentQ8_ = 0;
    uint16_t history_[4] = {0};
    uint8_t historyIdx_ = 0;
};

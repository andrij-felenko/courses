#include <cstdint>

enum class PiezoState {
    Idle,
    Integrating,
    Blanking
};

class PiezoDetector {
public:
    PiezoDetector(float v_start, float v_stop, float e_min, uint32_t blank_ticks)
        : v_th_start_(v_start), v_th_stop_(v_stop), e_min_(e_min),
          blank_ticks_(blank_ticks), state_(PiezoState::Idle),
          accumulated_energy_(0.0f), timer_(0) {}

    bool processSample(float voltage, float dt) {
        bool event_detected = false;
        const float v_sq = voltage * voltage;

        switch (state_) {
            case PiezoState::Idle:
                if (voltage >= v_th_start_) {
                    accumulated_energy_ = v_sq * dt;
                    state_ = PiezoState::Integrating;
                }
                break;
            case PiezoState::Integrating:
                accumulated_energy_ += v_sq * dt;
                if (voltage < v_th_stop_) {
                    if (accumulated_energy_ >= e_min_) {
                        event_detected = true;
                        timer_ = blank_ticks_;
                        state_ = PiezoState::Blanking;
                    } else {
                        state_ = PiezoState::Idle;
                    }
                }
                break;
            case PiezoState::Blanking:
                if (timer_ > 0) {
                    timer_--;
                } else if (voltage < v_th_stop_) {
                    state_ = PiezoState::Idle;
                }
                break;
        }
        return event_detected;
    }

private:
    float v_th_start_;
    float v_th_stop_;
    float e_min_;
    uint32_t blank_ticks_;
    PiezoState state_;
    float accumulated_energy_;
    uint32_t timer_;
};

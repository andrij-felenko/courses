#include <cstdint>
#include <cmath>
#include <algorithm>

enum class LandState : uint8_t {
    Flying = 0,
    Descending,
    NearGround,
    GroundContact,
    Landed
};

struct LandDetectorConfig {
    float v_z_descend_target   {-0.40f}; // м/с
    float v_z_stopped_thresh   { 0.15f}; // м/с
    float throttle_min_limit   { 0.12f}; // 0.0 .. 1.0
    float accel_shock_thresh   { 3.50f}; // м/с^2
    float current_drop_ratio   { 0.65f}; // частка від висіння
    uint32_t contact_time_ms   { 350};   // мс
    uint32_t disarm_delay_ms   { 500};   // мс
};

struct LandSensorData {
    float alt_ground_relative  {0.0f};
    float v_z_filtered         {0.0f};
    float throttle_out         {0.0f};
    float accel_z_raw          {9.81f};
    float battery_current      {0.0f};
    float hover_current        {15.0f};
    bool is_landing_commanded  {false};
};

class LandDetector {
public:
    explicit LandDetector(const LandDetectorConfig& config = LandDetectorConfig{})
        : cfg_{config} {}

    void update(const LandSensorData& sensors, uint32_t dt_ms) noexcept {
        if (!sensors.is_landing_commanded) {
            state_ = LandState::Flying;
            state_timer_ms_ = 0;
            i_term_freeze_ = false;
            disarm_request_ = false;
            return;
        }

        switch (state_) {
            case LandState::Flying:
                state_ = LandState::Descending;
                state_timer_ms_ = 0;
                i_term_freeze_ = false;
                break;

            case LandState::Descending:
                if (sensors.alt_ground_relative <= 1.5f && sensors.alt_ground_relative > 0.0f) {
                    state_ = LandState::NearGround;
                    state_timer_ms_ = 0;
                    i_term_freeze_ = true;
                }
                break;

            case LandState::NearGround: {
                i_term_freeze_ = true;
                const bool v_z_stopped = std::abs(sensors.v_z_filtered) < cfg_.v_z_stopped_thresh;
                const bool throttle_low = sensors.throttle_out <= cfg_.throttle_min_limit;
                const bool accel_shock = std::abs(sensors.accel_z_raw - 9.81f) > cfg_.accel_shock_thresh;
                const bool current_dropped = sensors.battery_current < (sensors.hover_current * cfg_.current_drop_ratio);

                if (throttle_low && (v_z_stopped || accel_shock || current_dropped)) {
                    state_timer_ms_ += dt_ms;
                    if (state_timer_ms_ >= cfg_.contact_time_ms) {
                        state_ = LandState::GroundContact;
                        state_timer_ms_ = 0;
                    }
                } else {
                    state_timer_ms_ = 0;
                }
                break;
            }

            case LandState::GroundContact:
                i_term_freeze_ = true;
                state_timer_ms_ += dt_ms;

                // Захист від помилкового детектування (порив вітру підкинув апарат)
                if (sensors.throttle_out > cfg_.throttle_min_limit * 1.5f ||
                    sensors.v_z_filtered > cfg_.v_z_stopped_thresh * 2.0f) {
                    state_ = LandState::NearGround;
                    state_timer_ms_ = 0;
                    break;
                }

                if (state_timer_ms_ >= cfg_.disarm_delay_ms) {
                    state_ = LandState::Landed;
                    disarm_request_ = true;
                }
                break;

            case LandState::Landed:
                disarm_request_ = true;
                i_term_freeze_ = true;
                break;
        }
    }

    [[nodiscard]] LandState state() const noexcept { return state_; }
    [[nodiscard]] bool should_freeze_i_term() const noexcept { return i_term_freeze_; }
    [[nodiscard]] bool should_disarm() const noexcept { return disarm_request_; }

private:
    LandState state_{LandState::Flying};
    uint32_t state_timer_ms_{0};
    bool i_term_freeze_{false};
    bool disarm_request_{false};
    LandDetectorConfig cfg_{};
};

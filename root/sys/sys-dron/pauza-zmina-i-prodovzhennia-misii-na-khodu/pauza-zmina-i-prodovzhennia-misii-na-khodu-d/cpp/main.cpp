#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <expected>
#include <numbers>
#include <optional>
#include <span>

namespace autopilot::mission {

constexpr size_t MaxWaypoints = 64;

enum class DynamicState : uint8_t {
    Idle = 0,
    Navigating,
    PausedHold,
    Rejoining,
    Completed
};

enum class ControllerError : uint8_t {
    InvalidState,
    IndexOutOfBounds,
    ActivePointLocked,
    BufferFull
};

struct WaypointNed {
    double x_ned{0.0};              // North, метри
    double y_ned{0.0};              // East, метри
    float z_ned{0.0f};              // Down, метри
    float acceptance_rad_m{5.0f};   // Радіус прийняття
    float cruise_speed_mps{14.0f};  // Швидкість
    uint16_t action_id{0};
};

struct PauseContext {
    double hold_x{0.0};
    double hold_y{0.0};
    float hold_z{0.0f};
    double proj_x{0.0};
    double proj_y{0.0};
    float remaining_dist{0.0f};
    uint16_t saved_seq{0};
};

struct alignas(64) MissionStorage {
    std::array<WaypointNed, MaxWaypoints> items{};
    uint16_t count{0};
    uint32_t version{0};
};

class DynamicMissionEngine {
public:
    DynamicMissionEngine() = default;

    [[nodiscard]] DynamicState state() const noexcept {
        return state_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint16_t current_sequence() const noexcept {
        return current_seq_.load(std::memory_order_relaxed);
    }

    std::expected<void, ControllerError> pause(double cur_x, double cur_y, float cur_z) noexcept {
        auto expected = DynamicState::Navigating;
        if (!state_.compare_exchange_strong(expected, DynamicState::PausedHold,
                                            std::memory_order_acq_rel)) {
            if (expected != DynamicState::Rejoining) {
                return std::unexpected(ControllerError::InvalidState);
            }
            state_.store(DynamicState::PausedHold, std::memory_order_release);
        }

        pause_ctx_.hold_x = cur_x;
        pause_ctx_.hold_y = cur_y;
        pause_ctx_.hold_z = cur_z;
        pause_ctx_.saved_seq = current_seq_.load(std::memory_order_relaxed);
        return {};
    }

    std::expected<void, ControllerError> resume() noexcept {
        auto expected = DynamicState::PausedHold;
        if (!state_.compare_exchange_strong(expected, DynamicState::Rejoining,
                                            std::memory_order_acq_rel)) {
            return std::unexpected(ControllerError::InvalidState);
        }
        return {};
    }

    std::expected<void, ControllerError> replace_tail(uint16_t start_seq,
                                                      std::span<const WaypointNed> new_tail) noexcept {
        const auto cur_state = state_.load(std::memory_order_relaxed);
        const uint16_t cur_seq = current_seq_.load(std::memory_order_relaxed);

        if (cur_state == DynamicState::Navigating && start_seq <= cur_seq) {
            return std::unexpected(ControllerError::ActivePointLocked);
        }
        if ((start_seq + new_tail.size()) > MaxWaypoints) {
            return std::unexpected(ControllerError::BufferFull);
        }

        const uint8_t active_idx = active_idx_.load(std::memory_order_relaxed);
        const uint8_t staging_idx = 1 - active_idx;

        auto& staging = buffers_[staging_idx];
        const auto& active = buffers_[active_idx];

        if (start_seq > 0) {
            std::copy_n(active.items.begin(), start_seq, staging.items.begin());
        }
        std::copy(new_tail.begin(), new_tail.end(), staging.items.begin() + start_seq);
        staging.count = static_cast<uint16_t>(start_seq + new_tail.size());
        staging.version = active.version + 1;

        seqlock_.fetch_add(1, std::memory_order_release);
        active_idx_.store(staging_idx, std::memory_order_release);
        seqlock_.fetch_add(1, std::memory_order_release);

        return {};
    }

    void update(double cur_x, double cur_y, float cur_z,
                std::span<float, 3> out_vel_ned, float& out_yaw_rad) noexcept {
        const auto cur_state = state_.load(std::memory_order_acquire);
        if (cur_state == DynamicState::PausedHold) {
            out_vel_ned[0] = 0.0f;
            out_vel_ned[1] = 0.0f;
            out_vel_ned[2] = 0.0f;
            return;
        }

        const uint8_t idx = active_idx_.load(std::memory_order_acquire);
        const auto& buf = buffers_[idx];
        const uint16_t seq = current_seq_.load(std::memory_order_relaxed);

        if (seq >= buf.count) {
            state_.store(DynamicState::Completed, std::memory_order_release);
            out_vel_ned[0] = 0.0f;
            out_vel_ned[1] = 0.0f;
            out_vel_ned[2] = 0.0f;
            return;
        }

        const auto& target_wp = buf.items[seq];
        const double dx = target_wp.x_ned - cur_x;
        const double dy = target_wp.y_ned - cur_y;
        const double dist = std::hypot(dx, dy);

        if (dist <= static_cast<double>(target_wp.acceptance_rad_m)) {
            current_seq_.fetch_add(1, std::memory_order_relaxed);
        }

        const float cruise = (target_wp.cruise_speed_mps > 1.0f) ? target_wp.cruise_speed_mps : 12.0f;
        const float track_yaw = static_cast<float>(std::atan2(dy, dx));

        out_vel_ned[0] = std::cos(track_yaw) * cruise;
        out_vel_ned[1] = std::sin(track_yaw) * cruise;
        out_vel_ned[2] = 0.0f;
        out_yaw_rad = track_yaw;
    }

private:
    std::array<MissionStorage, 2> buffers_{};
    std::atomic<uint8_t> active_idx_{0};
    std::atomic<uint32_t> seqlock_{0};

    std::atomic<DynamicState> state_{DynamicState::Idle};
    std::atomic<uint16_t> current_seq_{0};
    PauseContext pause_ctx_{};

    float max_intercept_rad_{35.0f * (std::numbers::pi_v<float> / 180.0f)};
    float lookahead_time_s_{3.0f};
};

} // namespace autopilot::mission

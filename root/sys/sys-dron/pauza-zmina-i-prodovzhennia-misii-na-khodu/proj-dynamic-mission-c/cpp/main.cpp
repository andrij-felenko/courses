#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <expected>

namespace autopilot::mission {

constexpr size_t MaxWaypoints = 64;

enum class ControllerState : uint8_t {
    Idle = 0,
    Navigating,
    PausedHold,
    Rejoining,
    Completed
};

enum class MissionError : uint8_t {
    InvalidState,
    BufferOverflow,
    InvalidSequenceIndex,
    ValidationFailed
};

struct WaypointItem {
    double lat{0.0};             // Градуси WGS-84
    double lon{0.0};             // Градуси WGS-84
    float alt_m{0.0f};           // Висота над Home, метри
    float acceptance_rad_m{5.0f};// Радіус захоплення цілі
    float cruise_speed_mps{15.0f};
    uint16_t action_cmd{0};
};

struct PauseContext {
    double x_proj{0.0};
    double y_proj{0.0};
    float remaining_dist_m{0.0f};
    std::array<float, 3> hold_pos_ned{0.0f, 0.0f, 0.0f};
    uint16_t saved_seq{0};
};

struct alignas(64) MissionBuffer {
    std::array<WaypointItem, MaxWaypoints> items{};
    uint16_t count{0};
    uint32_t version{0};
};

class DynamicMissionController {
public:
    DynamicMissionController() = default;

    [[nodiscard]] ControllerState state() const noexcept {
        return state_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint16_t current_sequence() const noexcept {
        return current_seq_.load(std::memory_order_relaxed);
    }

    std::expected<void, MissionError> pause(std::span<const float, 3> curr_ned) noexcept {
        auto expected_state = ControllerState::Navigating;
        if (!state_.compare_exchange_strong(expected_state, ControllerState::PausedHold,
                                            std::memory_order_acq_rel)) {
            if (expected_state != ControllerState::Rejoining) {
                return std::unexpected(MissionError::InvalidState);
            }
            state_.store(ControllerState::PausedHold, std::memory_order_release);
        }

        pause_ctx_.saved_seq = current_seq_.load(std::memory_order_relaxed);
        pause_ctx_.hold_pos_ned = {curr_ned[0], curr_ned[1], curr_ned[2]};
        return {};
    }

    std::expected<void, MissionError> resume() noexcept {
        auto expected_state = ControllerState::PausedHold;
        if (!state_.compare_exchange_strong(expected_state, ControllerState::Rejoining,
                                            std::memory_order_acq_rel)) {
            return std::unexpected(MissionError::InvalidState);
        }
        return {};
    }

    std::expected<void, MissionError> replace_tail(uint16_t start_seq,
                                                  std::span<const WaypointItem> new_items) noexcept {
        const uint16_t cur = current_seq_.load(std::memory_order_relaxed);
        if (start_seq > cur + 1 || (start_seq + new_items.size()) > MaxWaypoints) {
            return std::unexpected(MissionError::InvalidSequenceIndex);
        }

        const uint8_t cur_active = active_idx_.load(std::memory_order_relaxed);
        const uint8_t next_active = 1 - cur_active;

        auto& staging = buffers_[next_active];
        const auto& active = buffers_[cur_active];

        // Копіювання незмінного префікса та нового хвоста
        std::copy_n(active.items.begin(), start_seq, staging.items.begin());
        std::copy(new_items.begin(), new_items.end(), staging.items.begin() + start_seq);
        staging.count = static_cast<uint16_t>(start_seq + new_items.size());
        staging.version = active.version + 1;

        // Атомарна публікація через SeqLock
        seqlock_.fetch_add(1, std::memory_order_release);
        active_idx_.store(next_active, std::memory_order_release);
        seqlock_.fetch_add(1, std::memory_order_release);

        return {};
    }

    void update_guidance(std::span<const float, 3> curr_ned,
                         std::span<float, 3> target_vel_ned,
                         float& target_yaw_rad) noexcept {
        const auto current_state = state_.load(std::memory_order_acquire);
        if (current_state == ControllerState::PausedHold) {
            target_vel_ned[0] = 0.0f;
            target_vel_ned[1] = 0.0f;
            target_vel_ned[2] = 0.0f;
            return;
        }

        const uint8_t act = active_idx_.load(std::memory_order_acquire);
        const auto& buf = buffers_[act];
        const uint16_t seq = current_seq_.load(std::memory_order_relaxed);

        if (seq >= buf.count) {
            state_.store(ControllerState::Completed, std::memory_order_release);
            target_vel_ned[0] = 0.0f;
            target_vel_ned[1] = 0.0f;
            target_vel_ned[2] = 0.0f;
            return;
        }

        const auto& wp = buf.items[seq];
        const float dx = static_cast<float>(wp.lat * 111319.5) - curr_ned[0];
        const float dy = static_cast<float>(wp.lon * 111319.5) - curr_ned[1];
        const float dist = std::hypot(dx, dy);

        if (dist <= wp.acceptance_rad_m) {
            current_seq_.fetch_add(1, std::memory_order_relaxed);
        }

        const float speed = (wp.cruise_speed_mps > 0.1f) ? wp.cruise_speed_mps : 12.0f;
        const float heading = std::atan2(dy, dx);
        target_vel_ned[0] = std::cos(heading) * speed;
        target_vel_ned[1] = std::sin(heading) * speed;
        target_vel_ned[2] = 0.0f;
        target_yaw_rad = heading;
    }

private:
    std::array<MissionBuffer, 2> buffers_{};
    std::atomic<uint8_t> active_idx_{0};
    std::atomic<uint32_t> seqlock_{0};

    std::atomic<ControllerState> state_{ControllerState::Idle};
    std::atomic<uint16_t> current_seq_{0};
    PauseContext pause_ctx_{};

    float max_intercept_deg_{35.0f};
    float lookahead_time_s_{3.0f};
    float max_accel_mps2_{2.0f};
};

} // namespace autopilot::mission

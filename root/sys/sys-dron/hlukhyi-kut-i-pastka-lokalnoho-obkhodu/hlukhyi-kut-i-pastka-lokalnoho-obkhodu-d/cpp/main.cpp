#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

struct Vector3f {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    [[nodiscard]] constexpr float dist_sq(const Vector3f& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return (dx * dx) + (dy * dy) + (dz * dz);
    }

    [[nodiscard]] float dist(const Vector3f& other) const noexcept {
        return std::sqrt(dist_sq(other));
    }
};

enum class NavEscapeState : uint8_t {
    Normal = 0,
    StuckDetected,
    Backtracking,
    ReplanTriggered
};

template <size_t Capacity>
class BreadcrumbTracker {
public:
    explicit constexpr BreadcrumbTracker(float min_step = 0.5F) noexcept
        : min_dist_sq_(min_step * min_step) {}

    void push(const Vector3f& pos) noexcept {
        if (count_ > 0) {
            const size_t last_idx = (head_ + Capacity - 1) % Capacity;
            if (buffer_[last_idx].dist_sq(pos) < min_dist_sq_) {
                return;
            }
        }
        buffer_[head_] = pos;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] size_t count() const noexcept { return count_; }
    [[nodiscard]] size_t head() const noexcept { return head_; }

    [[nodiscard]] std::optional<Vector3f> pop_back(size_t& current_idx) noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        const Vector3f pt = buffer_[current_idx];
        current_idx = (current_idx + Capacity - 1) % Capacity;
        --count_;
        return pt;
    }

    [[nodiscard]] const Vector3f& at(size_t idx) const noexcept {
        return buffer_[idx % Capacity];
    }

private:
    std::array<Vector3f, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
    float min_dist_sq_{0.25F};
};

class LocalMinimaEscapeDetector {
public:
    static constexpr size_t kHistoryWindow = 50;
    static constexpr size_t kCrumbCapacity = 128;

    explicit LocalMinimaEscapeDetector(float dt) noexcept
        : window_dt_(dt) {}

    bool update(const Vector3f& cur_pos,
                const Vector3f& cur_vel,
                const Vector3f& goal_pos,
                bool active_thrust,
                Vector3f& out_setpoint) noexcept {
        if (cooldown_timer_ > 0.0F) {
            cooldown_timer_ -= window_dt_;
        }

        if (state_ == NavEscapeState::Normal) {
            crumbs_.push(cur_pos);

            const Vector3f to_goal{goal_pos.x - cur_pos.x, goal_pos.y - cur_pos.y, goal_pos.z - cur_pos.z};
            const float dist_goal = std::sqrt(to_goal.x * to_goal.x + to_goal.y * to_goal.y + to_goal.z * to_goal.z);

            float v_prog = 0.0F;
            if (dist_goal > 1e-3F) {
                v_prog = (cur_vel.x * to_goal.x + cur_vel.y * to_goal.y + cur_vel.z * to_goal.z) / dist_goal;
            }

            progress_history_[window_idx_] = (v_prog > 0.0F) ? (v_prog * window_dt_) : 0.0F;
            window_idx_ = (window_idx_ + 1) % kHistoryWindow;
            if (window_idx_ == 0) {
                window_filled_ = true;
            }

            if (window_filled_ && cooldown_timer_ <= 0.0F && active_thrust) {
                float total_prog = 0.0F;
                for (const float step : progress_history_) {
                    total_prog += step;
                }

                if (total_prog < progress_threshold_ && crumbs_.count() > 4) {
                    state_ = NavEscapeState::StuckDetected;
                    backtrack_dist_accum_ = 0.0F;
                    backtrack_target_idx_ = (crumbs_.head() + kCrumbCapacity - 1) % kCrumbCapacity;
                }
            }
            return false;
        }

        if (state_ == NavEscapeState::StuckDetected || state_ == NavEscapeState::Backtracking) {
            state_ = NavEscapeState::Backtracking;

            if (crumbs_.count() == 0) {
                state_ = NavEscapeState::ReplanTriggered;
                return true;
            }

            const Vector3f target_wp = crumbs_.at(backtrack_target_idx_);
            out_setpoint = target_wp;

            const float dist_to_wp = cur_pos.dist(target_wp);
            if (dist_to_wp < 0.6F) {
                backtrack_dist_accum_ += dist_to_wp;
                if (crumbs_.count() > 1) {
                    backtrack_target_idx_ = (backtrack_target_idx_ + kCrumbCapacity - 1) % kCrumbCapacity;
                }
                auto popped = crumbs_.pop_back(backtrack_target_idx_);
                (void)popped;
            }

            if (backtrack_dist_accum_ >= backtrack_required_dist_ || crumbs_.count() == 0) {
                state_ = NavEscapeState::ReplanTriggered;
                cooldown_timer_ = 5.0F;
                return true;
            }
        }

        return false;
    }

    [[nodiscard]] NavEscapeState state() const noexcept { return state_; }
    void reset_to_normal() noexcept { state_ = NavEscapeState::Normal; }

private:
    float window_dt_{0.02F};
    float progress_threshold_{0.25F};
    float backtrack_required_dist_{4.0F};
    float cooldown_timer_{0.0F};

    std::array<float, kHistoryWindow> progress_history_{};
    size_t window_idx_{0};
    bool window_filled_{false};

    BreadcrumbTracker<kCrumbCapacity> crumbs_{0.5F};
    NavEscapeState state_{NavEscapeState::Normal};
    size_t backtrack_target_idx_{0};
    float backtrack_dist_accum_{0.0F};
};

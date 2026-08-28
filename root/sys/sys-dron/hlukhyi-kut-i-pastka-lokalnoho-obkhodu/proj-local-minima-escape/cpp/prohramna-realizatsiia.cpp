#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    [[nodiscard]] constexpr float len_sq() const noexcept {
        return (x * x) + (y * y) + (z * z);
    }

    [[nodiscard]] float len() const noexcept {
        return std::sqrt(len_sq());
    }

    [[nodiscard]] constexpr float dist_sq(const Vec3& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return (dx * dx) + (dy * dy) + (dz * dz);
    }

    [[nodiscard]] float dist(const Vec3& other) const noexcept {
        return std::sqrt(dist_sq(other));
    }
};

struct Vec2 {
    float x{0.0F};
    float y{0.0F};

    [[nodiscard]] float norm() const noexcept {
        return std::sqrt((x * x) + (y * y));
    }

    [[nodiscard]] Vec2 normalized() const noexcept {
        const float n = norm();
        if (n > 1e-4F) {
            return {x / n, y / n};
        }
        return {0.0F, 0.0F};
    }
};

struct LidarBeam {
    float angle_rad{0.0F};
    float range_m{0.0F};
};

struct VoxelEntry {
    int16_t x{0};
    int16_t y{0};
    uint16_t visit_count{0};
};

enum class EscapeFsmState : uint8_t {
    Monitor = 0,
    EvaluateTrap,
    Vertical,
    Backtrack,
    WallFollow,
    Replan
};

template <size_t Capacity>
class CrumbRingBuffer {
public:
    explicit constexpr CrumbRingBuffer(float min_step = 0.5F) noexcept
        : min_spacing_sq_(min_step * min_step) {}

    void push(const Vec3& p) noexcept {
        if (count_ > 0) {
            const size_t last_idx = (head_ + Capacity - 1) % Capacity;
            if (buffer_[last_idx].dist_sq(p) < min_spacing_sq_) {
                return;
            }
        }
        buffer_[head_] = p;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] size_t count() const noexcept { return count_; }
    [[nodiscard]] size_t head() const noexcept { return head_; }

    [[nodiscard]] const Vec3& at(size_t idx) const noexcept {
        return buffer_[idx % Capacity];
    }

    void pop_one(size_t& idx) noexcept {
        if (count_ > 0) {
            idx = (idx + Capacity - 1) % Capacity;
            --count_;
        }
    }

    void clear() noexcept {
        count_ = 0;
        head_ = 0;
    }

private:
    std::array<Vec3, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
    float min_spacing_sq_{0.25F};
};

class LocalMinimaEscapeModule {
public:
    static constexpr size_t kProgressWindow = 50;
    static constexpr size_t kCrumbCapacity = 128;
    static constexpr size_t kVoxelHashSize = 64;

    struct Config {
        float loop_dt{0.02F};
        float progress_threshold_m{0.30F};
        float backtrack_target_dist_m{4.5F};
        float vertical_step_m{3.0F};
        float wall_distance_target_m{1.5F};
        float cooldown_duration_s{5.0F};
        float max_oscillation_ratio{4.0F};
    };

    struct StepResult {
        bool override_setpoint{false};
        bool request_global_replan{false};
        Vec3 setpoint{};
    };

    explicit LocalMinimaEscapeModule(const Config& cfg = Config{}) noexcept
        : cfg_(cfg) {}

    StepResult update(const Vec3& cur_pos,
                      const Vec3& cur_vel,
                      const Vec3& goal_pos,
                      bool thruster_active,
                      float top_clearance_m,
                      std::span<const LidarBeam> lidar_beams) noexcept {
        StepResult res{};

        if (cooldown_timer_ > 0.0F) {
            cooldown_timer_ -= cfg_.loop_dt;
        }

        switch (state_) {
        case EscapeFsmState::Monitor: {
            crumbs_.push(cur_pos);
            update_voxel_tracker(cur_pos);

            const Vec3 to_goal{goal_pos.x - cur_pos.x, goal_pos.y - cur_pos.y, goal_pos.z - cur_pos.z};
            const float dist_goal = to_goal.len();

            float v_prog = 0.0F;
            if (dist_goal > 1e-2F) {
                v_prog = (cur_vel.x * to_goal.x + cur_vel.y * to_goal.y + cur_vel.z * to_goal.z) / dist_goal;
            }

            progress_history_[window_idx_] = (v_prog > 0.0F) ? (v_prog * cfg_.loop_dt) : 0.0F;
            speed_history_[window_idx_] = cur_vel.len() * cfg_.loop_dt;
            pos_history_[window_idx_] = cur_pos;

            window_idx_ = (window_idx_ + 1) % kProgressWindow;
            if (window_idx_ == 0) {
                window_filled_ = true;
            }

            if (window_filled_ && cooldown_timer_ <= 0.0F && thruster_active) {
                float total_prog = 0.0F;
                float total_path = 0.0F;
                Vec3 pos_mean{};

                for (size_t i = 0; i < kProgressWindow; ++i) {
                    total_prog += progress_history_[i];
                    total_path += speed_history_[i];
                    pos_mean.x += pos_history_[i].x;
                    pos_mean.y += pos_history_[i].y;
                    pos_mean.z += pos_history_[i].z;
                }
                pos_mean.x /= static_cast<float>(kProgressWindow);
                pos_mean.y /= static_cast<float>(kProgressWindow);
                pos_mean.z /= static_cast<float>(kProgressWindow);

                float max_disp = 0.0F;
                for (size_t i = 0; i < kProgressWindow; ++i) {
                    const float d = pos_history_[i].dist(pos_mean);
                    if (d > max_disp) {
                        max_disp = d;
                    }
                }

                const bool stuck_by_progress = (total_prog < cfg_.progress_threshold_m);
                const bool stuck_by_oscillation = (total_path > 3.0F && (total_path / std::max(max_disp, 0.1F)) > cfg_.max_oscillation_ratio);

                if ((stuck_by_progress || stuck_by_oscillation) && crumbs_.count() > 4) {
                    state_ = EscapeFsmState::EvaluateTrap;
                    trap_entry_pos_ = cur_pos;
                    initial_goal_pos_ = goal_pos;
                }
            }
            break;
        }

        case EscapeFsmState::EvaluateTrap: {
            if (top_clearance_m >= cfg_.vertical_step_m + 1.0F) {
                state_ = EscapeFsmState::Vertical;
                target_altitude_z_ = cur_pos.z + cfg_.vertical_step_m;
            } else if (crumbs_.count() > 2) {
                state_ = EscapeFsmState::Backtrack;
                backtrack_accum_dist_ = 0.0F;
                backtrack_idx_ = (crumbs_.head() + kCrumbCapacity - 1) % kCrumbCapacity;
            } else {
                state_ = EscapeFsmState::WallFollow;
            }
            break;
        }

        case EscapeFsmState::Vertical: {
            res.override_setpoint = true;
            res.setpoint = Vec3{cur_pos.x, cur_pos.y, target_altitude_z_};

            if (std::abs(cur_pos.z - target_altitude_z_) < 0.3F) {
                state_ = EscapeFsmState::Replan;
            }
            break;
        }

        case EscapeFsmState::Backtrack: {
            if (crumbs_.count() == 0) {
                state_ = EscapeFsmState::Replan;
                break;
            }

            const Vec3 target_crumb = crumbs_.at(backtrack_idx_);
            res.override_setpoint = true;
            res.setpoint = target_crumb;

            const float d_crumb = cur_pos.dist(target_crumb);
            if (d_crumb < 0.6F) {
                backtrack_accum_dist_ += d_crumb;
                crumbs_.pop_one(backtrack_idx_);
            }

            if (backtrack_accum_dist_ >= cfg_.backtrack_target_dist_m || crumbs_.count() == 0) {
                state_ = EscapeFsmState::Replan;
            }
            break;
        }

        case EscapeFsmState::WallFollow: {
            const Vec2 tangent = calculate_wall_tangent(lidar_beams, cfg_.wall_distance_target_m);
            res.override_setpoint = true;
            res.setpoint = Vec3{cur_pos.x + (tangent.x * 1.5F), cur_pos.y + (tangent.y * 1.5F), cur_pos.z};

            const float cur_dist_to_goal = cur_pos.dist(initial_goal_pos_);
            const float trap_dist_to_goal = trap_entry_pos_.dist(initial_goal_pos_);

            if (cur_dist_to_goal < trap_dist_to_goal - 1.0F) {
                state_ = EscapeFsmState::Replan;
            }
            break;
        }

        case EscapeFsmState::Replan: {
            res.request_global_replan = true;
            cooldown_timer_ = cfg_.cooldown_duration_s;
            state_ = EscapeFsmState::Monitor;
            break;
        }
        }

        return res;
    }

    [[nodiscard]] EscapeFsmState state() const noexcept { return state_; }
    void reset() noexcept {
        state_ = EscapeFsmState::Monitor;
        crumbs_.clear();
        cooldown_timer_ = 0.0F;
        window_filled_ = false;
        window_idx_ = 0;
        voxel_table_.fill(VoxelEntry{});
    }

private:
    void update_voxel_tracker(const Vec3& pos) noexcept {
        const auto vx = static_cast<int16_t>(std::floor(pos.x / 0.5F));
        const auto vy = static_cast<int16_t>(std::floor(pos.y / 0.5F));
        const auto hash = static_cast<uint8_t>(((vx * 73856093) ^ (vy * 19349663)) % kVoxelHashSize);

        if (voxel_table_[hash].x == vx && voxel_table_[hash].y == vy) {
            voxel_table_[hash].visit_count++;
        } else {
            voxel_table_[hash].x = vx;
            voxel_table_[hash].y = vy;
            voxel_table_[hash].visit_count = 1;
        }
    }

    [[nodiscard]] static Vec2 calculate_wall_tangent(std::span<const LidarBeam> beams, float desired_dist) noexcept {
        float min_range = 999.0F;
        float closest_angle = 0.0F;

        for (const auto& beam : beams) {
            if (beam.range_m > 0.1F && beam.range_m < min_range) {
                min_range = beam.range_m;
                closest_angle = beam.angle_rad;
            }
        }

        if (min_range > 10.0F) {
            return Vec2{1.0F, 0.0F};
        }

        const float nx = std::cos(closest_angle);
        const float ny = std::sin(closest_angle);

        const float tx = -ny;
        const float ty = nx;

        const float dist_err = min_range - desired_dist;
        constexpr float kCorrGain = 0.6F;

        const Vec2 raw_cmd{tx + (nx * dist_err * kCorrGain), ty + (ny * dist_err * kCorrGain)};
        return raw_cmd.normalized();
    }

    Config cfg_{};
    EscapeFsmState state_{EscapeFsmState::Monitor};

    std::array<float, kProgressWindow> progress_history_{};
    std::array<float, kProgressWindow> speed_history_{};
    std::array<Vec3, kProgressWindow> pos_history_{};
    size_t window_idx_{0};
    bool window_filled_{false};

    CrumbRingBuffer<kCrumbCapacity> crumbs_{0.5F};
    std::array<VoxelEntry, kVoxelHashSize> voxel_table_{};

    size_t backtrack_idx_{0};
    float backtrack_accum_dist_{0.0F};
    float target_altitude_z_{0.0F};
    float cooldown_timer_{0.0F};

    Vec3 trap_entry_pos_{};
    Vec3 initial_goal_pos_{};
};

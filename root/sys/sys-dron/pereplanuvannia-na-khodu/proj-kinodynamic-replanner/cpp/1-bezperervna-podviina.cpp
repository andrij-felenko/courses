#include <atomic>
#include <array>

class DoubleBufferedTrajectory {
public:
    void update(const KinodynamicReplanner& replanner, double t_now,
                const SphereObstacle& obstacle, const Vec3& goal) {
        const size_t current_idx = active_idx_.load(std::memory_order_relaxed);
        const size_t next_idx = 1 - current_idx;

        const auto new_traj = replanner.replan(trajectories_[current_idx], t_now, obstacle, goal);
        if (new_traj) {
            trajectories_[next_idx] = *new_traj;
            active_idx_.store(next_idx, std::memory_order_release);
        }
    }

    [[nodiscard]] KinematicState sample(double t_current) const noexcept {
        const size_t current_idx = active_idx_.load(std::memory_order_acquire);
        return trajectories_[current_idx].evaluate(t_current);
    }

private:
    std::array<Trajectory, 2> trajectories_{};
    std::atomic<size_t> active_idx_{0};
};

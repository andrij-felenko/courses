#pragma once

#include <expected>
#include <optional>
#include <span>

#include "safety_filter.hpp"

namespace rover {

struct Pose {
    float x{0.0f};
    float y{0.0f};
    float theta{0.0f};
};

/* Усе, що бачить повільний контур на одному переплануванні. */
struct PlanRequest {
    Pose pose{};
    Setpoint current{};
    std::span<const Obstacle> obstacles{};
};

/* Чисельний пошук уставки-кандидата: вибірка допустимих команд, прогін
 * кожної на горизонті T, мінімум інтегральної вартості J. Може не знайти
 * нічого — і це нормально, бо за безпеку відповідає не він. */
class TrajectoryPlanner {
public:
    TrajectoryPlanner(const Limits& l, float goal_x, float goal_y) noexcept
        : limits_{l}, goal_x_{goal_x}, goal_y_{goal_y} {}

    [[nodiscard]] std::optional<Setpoint> solve(const PlanRequest& req) const noexcept;

private:
    [[nodiscard]] float rollout_cost(const PlanRequest& req, Setpoint u) const noexcept;

    Limits limits_;
    float  goal_x_{0.0f};
    float  goal_y_{0.0f};
    float  horizon_s_{1.6f};
    float  step_s_{0.1f};
    float  window_s_{0.30f};  // динамічне вікно допустимої зміни уставки
    float  w_goal_{1.0f};
    float  w_effort_{0.15f};
    float  w_risk_{0.05f};
};

struct TickReport {
    Setpoint output{};
    Decision barrier{};
    std::optional<Reject> reject{};  // чому кандидата не взяли
    unsigned verdict_changes{0};     // метрика брязкання
    unsigned rejects{0};
};

/* Регламент взаємодії двох контурів: повільний кладе кандидата, швидкий
 * щотакту перевіряє його на придатність і свіжість, зшиває без ривків
 * і пропускає крізь бар'єр. */
class DecisionLoop {
public:
    DecisionLoop(const Params& p, const Limits& l, float goal_x, float goal_y) noexcept
        : params_{p}, limits_{l}, filter_{p, l}, planner_{l, goal_x, goal_y},
          held_range_{l.obstacle_margin_m} {}

    void replan(const PlanRequest& req);              // повільний контур, 20 Гц
    [[nodiscard]] TickReport tick(const VehicleState& raw, float dt); // 200 Гц

private:
    [[nodiscard]] std::expected<Setpoint, Reject> take_candidate() const noexcept;
    [[nodiscard]] Setpoint slew(Setpoint want, float dt) const noexcept;
    [[nodiscard]] VehicleState sanitize(const VehicleState& raw, float dt) noexcept;

    static constexpr float kMaxAge = 0.15f;  // три періоди планувальника
    static constexpr int   kMaxDropouts = 40; // 0.2 с на 200 Гц

    Params        params_;
    Limits        limits_;
    SafetyFilter  filter_;
    TrajectoryPlanner planner_;

    std::optional<Setpoint> candidate_{};
    bool     plan_failed_{false};
    float    candidate_age_{0.0f};
    Setpoint last_output_{};
    Verdict  last_verdict_{Verdict::Pass};
    unsigned verdict_changes_{0};
    unsigned rejects_{0};
    int      dropouts_{0};
    float    held_range_{0.0f};
};

} // namespace rover

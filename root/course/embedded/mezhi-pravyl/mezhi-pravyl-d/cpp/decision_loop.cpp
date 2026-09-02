#include "decision_loop.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace rover {
namespace {

[[nodiscard]] float clearance(std::span<const Obstacle> obs, float x, float y) noexcept
{
    float best = 1.0e6f;
    for (const Obstacle& o : obs) {
        const float dx = x - o.x;
        const float dy = y - o.y;
        best = std::min(best, std::sqrt(dx * dx + dy * dy) - o.radius);
    }
    return best;
}

[[nodiscard]] bool finite(Setpoint u) noexcept
{
    return std::isfinite(u.vx) && std::isfinite(u.yaw_rate);
}

} // namespace

float TrajectoryPlanner::rollout_cost(const PlanRequest& req, Setpoint u) const noexcept
{
    const int steps = static_cast<int>(horizon_s_ / step_s_);
    float x = req.pose.x;
    float y = req.pose.y;
    float th = req.pose.theta;
    float cost = 0.0f;

    for (int k = 0; k < steps; ++k) {
        th += u.yaw_rate * step_s_;
        x  += u.vx * std::cos(th) * step_s_;
        y  += u.vx * std::sin(th) * step_s_;

        const float c = clearance(req.obstacles, x, y);
        if (c < limits_.obstacle_margin_m) {
            return std::numeric_limits<float>::infinity(); // траєкторія неприпустима
        }
        cost += w_risk_ / (c * c);
    }

    const float dx = goal_x_ - x;
    const float dy = goal_y_ - y;
    cost += w_goal_ * std::sqrt(dx * dx + dy * dy);
    cost += w_effort_ * (0.05f * u.vx * u.vx + u.yaw_rate * u.yaw_rate);
    return cost;
}

std::optional<Setpoint> TrajectoryPlanner::solve(const PlanRequest& req) const noexcept
{
    constexpr int kV = 7;
    constexpr int kW = 13;

    const float dv = limits_.accel_max * window_s_;
    const float dw = limits_.yaw_accel_max * window_s_;
    const float v_lo = std::max(0.0f, req.current.vx - dv);
    const float v_hi = std::min(limits_.v_max, req.current.vx + dv);
    const float w_lo = std::max(-limits_.yaw_rate_max, req.current.yaw_rate - dw);
    const float w_hi = std::min(limits_.yaw_rate_max, req.current.yaw_rate + dw);

    std::optional<Setpoint> best{};
    float best_cost = std::numeric_limits<float>::infinity();

    for (int i = 0; i < kV; ++i) {
        const float v = v_lo + (v_hi - v_lo) * static_cast<float>(i) / (kV - 1);
        for (int j = 0; j < kW; ++j) {
            const float w = w_lo + (w_hi - w_lo) * static_cast<float>(j) / (kW - 1);
            const Setpoint u{v, w};
            const float cost = rollout_cost(req, u);
            if (cost < best_cost) {
                best_cost = cost;
                best = u;
            }
        }
    }
    return best; // nullopt — жодна траєкторія не пройшла перевірку зазору
}

void DecisionLoop::replan(const PlanRequest& req)
{
    if (auto plan = planner_.solve(req)) {
        candidate_ = *plan;
        candidate_age_ = 0.0f;
        plan_failed_ = false;
    } else {
        plan_failed_ = true;
    }
}

std::expected<Setpoint, Reject> DecisionLoop::take_candidate() const noexcept
{
    if (!candidate_) {
        return std::unexpected(plan_failed_ ? Reject::NoPlan : Reject::Stale);
    }
    if (candidate_age_ > kMaxAge) {
        return std::unexpected(plan_failed_ ? Reject::NoPlan : Reject::Stale);
    }
    if (!finite(*candidate_)) {
        return std::unexpected(Reject::NotFinite);
    }
    if (candidate_->vx < -0.01f || candidate_->vx > limits_.v_max * 1.5f ||
        std::fabs(candidate_->yaw_rate) > limits_.yaw_rate_max * 1.5f) {
        return std::unexpected(Reject::OutOfEnvelope);
    }
    return *candidate_;
}

Setpoint DecisionLoop::slew(Setpoint want, float dt) const noexcept
{
    // Безударність: розгін не швидше accel_max, гальмування — до brake_accel,
    // бо це рух у бік безпеки.
    const float up   = limits_.accel_max * dt;
    const float down = limits_.brake_accel * dt;
    const float dw   = limits_.yaw_accel_max * dt;

    return Setpoint{
        std::clamp(want.vx, last_output_.vx - down, last_output_.vx + up),
        std::clamp(want.yaw_rate, last_output_.yaw_rate - dw,
                   last_output_.yaw_rate + dw)};
}

VehicleState DecisionLoop::sanitize(const VehicleState& raw, float dt) noexcept
{
    VehicleState st = raw;

    if (raw.range_valid && std::isfinite(raw.range_ahead_m)) {
        dropouts_ = 0;
        held_range_ = raw.range_ahead_m;
        return st;
    }

    // Провал далекоміра не робить простір вільним: тримаємо останнє дійсне
    // значення й підсуваємо його на пройдений шлях.
    ++dropouts_;
    held_range_ = std::max(held_range_ - std::max(raw.vx, 0.0f) * dt, 0.0f);
    st.range_ahead_m = held_range_;
    st.range_valid = dropouts_ <= kMaxDropouts;
    return st;
}

TickReport DecisionLoop::tick(const VehicleState& raw, float dt)
{
    const VehicleState st = sanitize(raw, dt);
    candidate_age_ += dt;

    TickReport rep;
    Setpoint want{};

    if (const auto cand = take_candidate(); cand) {
        want = *cand;
    } else {
        // Власна безумовна поведінка швидкого контуру: рівне гальмування
        // з утриманням курсу.
        rep.reject = cand.error();
        ++rejects_;
        want = Setpoint{std::max(last_output_.vx - limits_.brake_accel * dt, 0.0f), 0.0f};
    }

    rep.barrier = filter_.enforce(st, slew(want, dt), dt);
    rep.output = rep.barrier.output;

    if (rep.barrier.verdict != last_verdict_) {
        ++verdict_changes_;
        last_verdict_ = rep.barrier.verdict;
    }
    last_output_ = rep.output;
    rep.verdict_changes = verdict_changes_;
    rep.rejects = rejects_;
    return rep;
}

} // namespace rover

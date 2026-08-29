#include "conditions.hpp"

#include <cmath>

namespace mission {
namespace {

template <class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };

}  // namespace

Condition make_delay(float seconds, const ConditionContext& ctx) noexcept
{
    const auto ms = seconds > 0.0F ? static_cast<std::uint32_t>(seconds * 1000.0F) : 0U;
    return Delay{ .started = ctx.now, .duration_ms = ms };
}

Condition make_distance(float metres) noexcept
{
    return Distance{ .trigger_m = metres > 0.0F ? metres : 0.0F };
}

Condition make_yaw(float target_deg, float rate_dps, const ConditionContext& ctx) noexcept
{
    return Yaw{ .started    = ctx.now,
                .start_deg  = ctx.yaw_deg,
                .target_deg = heading_deg(target_deg),
                .rate_dps   = rate_dps > 0.0F ? rate_dps : kYawDefaultDps };
}

bool is_met(const Condition& c, const ConditionContext& ctx) noexcept
{
    return std::visit(overloaded{
        [&](const Delay& d) {
            return ctx.now.since(d.started) >= d.duration_ms;
        },
        [&](const Distance& d) {
            return distance_sq(ctx.position, ctx.next_waypoint)
                   <= d.trigger_m * d.trigger_m;
        },
        [&](const Yaw& y) {
            return std::fabs(wrap_deg(ctx.yaw_deg - y.target_deg)) <= kYawToleranceDeg;
        }
    }, c);
}

std::optional<float> yaw_setpoint(const Condition& c, const ConditionContext& ctx) noexcept
{
    const auto* y = std::get_if<Yaw>(&c);
    if (y == nullptr) {
        return std::nullopt;
    }

    /* Найкоротший шлях до цілі: нормалізація вирішує, куди крутити. */
    const float full_deg  = wrap_deg(y->target_deg - y->start_deg);
    const float elapsed_s = static_cast<float>(ctx.now.since(y->started)) / 1000.0F;
    const float done_deg  = y->rate_dps * elapsed_s;

    if (done_deg >= std::fabs(full_deg)) {
        return y->target_deg;
    }
    return heading_deg(y->start_deg + std::copysign(done_deg, full_deg));
}

float BatteryFilter::update(float raw_v, float dt_s) noexcept
{
    if (!primed_) {
        /* Перше читання беремо як є: інакше фільтр повзе з нуля
           й перші секунди польоту вважає батарею розрядженою. */
        value_v_ = raw_v;
        primed_  = true;
        return value_v_;
    }
    if (dt_s <= 0.0F) {
        return value_v_;
    }

    const float alpha = dt_s / (tau_s_ + dt_s);
    value_v_ += alpha * (raw_v - value_v_);
    return value_v_;
}

}  // namespace mission

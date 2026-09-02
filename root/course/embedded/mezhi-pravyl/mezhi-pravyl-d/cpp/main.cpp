#include <algorithm>
#include <cmath>
#include <format>
#include <iostream>
#include <span>
#include <string>
#include <vector>

#include "decision_loop.hpp"

/* Сценарій із трьома збуреннями одночасно: огорожа за 3.8 м, боковий вітер
 * 12 м/с і просілий 4S-пакет. Стенд мінімальний — предмет тут не симуляція,
 * а поведінка двох контурів під час конфлікту цілей. */

namespace {

using rover::Obstacle;
using rover::Pose;
using rover::Setpoint;
using rover::VehicleState;

constexpr float kDt = 0.005f;   // 200 Гц — жорсткий цикл бар'єра
constexpr int   kPlanPeriod = 10; // 20 Гц — повільний контур
constexpr int   kTicks = 1200;  // 6 секунд

struct Plant {
    float x{1.85f};
    float y{0.0f};
    float theta{0.0f};
    float v{2.2f};
    float w{0.0f};
    float ocv{14.25f};
};

[[nodiscard]] std::vector<Obstacle> build_fence()
{
    std::vector<Obstacle> fence;
    fence.reserve(11);
    for (int i = 0; i < 11; ++i) {
        fence.push_back(Obstacle{6.0f, -3.0f + 0.6f * static_cast<float>(i), 0.35f});
    }
    return fence;
}

[[nodiscard]] float ray_range(std::span<const Obstacle> obs,
                              float x, float y, float th) noexcept
{
    const float dx = std::cos(th);
    const float dy = std::sin(th);
    float best = 30.0f;

    for (const Obstacle& o : obs) {
        const float ox = o.x - x;
        const float oy = o.y - y;
        const float t_ca = ox * dx + oy * dy;
        if (t_ca < 0.0f) {
            continue; // позаду
        }
        const float d2 = ox * ox + oy * oy - t_ca * t_ca;
        const float r2 = o.radius * o.radius;
        if (d2 > r2) {
            continue; // промінь мимо
        }
        best = std::min(best, std::max(t_ca - std::sqrt(r2 - d2), 0.0f));
    }
    return best;
}

// Мінімум по передньому сектору ±25°, спроєктований на курс: один промінь
// був би пасткою — поворот на пів градуса «ховає» огорожу.
[[nodiscard]] float sector_range(std::span<const Obstacle> obs,
                                 float x, float y, float th) noexcept
{
    float best = 30.0f;
    for (int k = -5; k <= 5; ++k) {
        const float a = 0.0873f * static_cast<float>(k);
        best = std::min(best, ray_range(obs, x, y, th + a) * std::cos(a));
    }
    return best;
}

[[nodiscard]] float true_clearance(std::span<const Obstacle> obs, const Plant& pl) noexcept
{
    float best = 1.0e6f;
    for (const Obstacle& o : obs) {
        const float dx = pl.x - o.x;
        const float dy = pl.y - o.y;
        best = std::min(best, std::sqrt(dx * dx + dy * dy) - o.radius);
    }
    return best;
}

} // namespace

int main()
{
    const rover::Params params{};
    const rover::Limits limits{};
    const std::vector<Obstacle> fence = build_fence();

    rover::DecisionLoop loop{params, limits, 12.0f, 5.0f};
    Plant pl{};

    float min_clear = 1.0e6f;
    float min_h = 1.0e6f;
    float next_print = 0.0f;
    rover::TickReport rep{};

    std::cout << "    t     v      w  range      h   i_pr  budget  V_term  вердикт\n";

    for (int tick = 0; tick < kTicks; ++tick) {
        const float t = static_cast<float>(tick) * kDt;

        VehicleState st;
        st.vx = pl.v;
        st.yaw_rate = pl.w;
        st.range_ahead_m = sector_range(fence, pl.x, pl.y, pl.theta);
        st.range_valid = !(t > 1.00f && t < 1.15f);  // провал лідара на 150 мс
        st.tilt_rad = 0.05f;
        st.pack_ocv_v = pl.ocv;
        st.pack_esr_ohm = 0.12f;                     // просілий пакет
        st.yaw_disturbance_nm = 1.9f;                // боковий вітер 12 м/с

        // Повільний контур; з 2.0 до 2.4 с планувальник «завис».
        if (tick % kPlanPeriod == 0 && !(t > 2.0f && t < 2.4f)) {
            loop.replan(rover::PlanRequest{Pose{pl.x, pl.y, pl.theta},
                                           Setpoint{pl.v, pl.w},
                                           std::span<const Obstacle>{fence}});
        }

        rep = loop.tick(st, kDt);

        // Стенд: приводи відпрацьовують уставку з першим порядком.
        pl.v += (rep.output.vx - pl.v) * (kDt / 0.25f);
        pl.w += (rep.output.yaw_rate - pl.w) * (kDt / 0.12f);
        pl.theta += pl.w * kDt;
        pl.x += pl.v * std::cos(pl.theta) * kDt;
        pl.y += pl.v * std::sin(pl.theta) * kDt + 0.28f * kDt; // знос вітром
        pl.ocv -= rep.barrier.predicted_a * kDt / 3600.0f / 5.2f * 1.5f;

        min_clear = std::min(min_clear, true_clearance(fence, pl));
        min_h = std::min(min_h, rep.barrier.barrier_h);

        if (t >= next_print) {
            next_print += 0.25f;
            std::cout << std::format(
                "{:5.2f} {:5.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:7.2f} {:7.2f}  {}{}\n",
                t, pl.v, pl.w, st.range_ahead_m, rep.barrier.barrier_h,
                rep.barrier.predicted_a, rep.barrier.budget_a,
                st.pack_ocv_v - rep.barrier.predicted_a * st.pack_esr_ohm,
                rover::name(rep.barrier.verdict),
                rep.reject ? std::format(" [кандидат: {}]", rover::name(*rep.reject))
                           : std::string{});
        }
    }

    std::cout << std::format(
        "\nмінімальний зазор до огорожі: {:.2f} м (зазор безпеки {:.2f} м)\n",
        min_clear, limits.obstacle_margin_m);
    std::cout << std::format(
        "мінімум бар'єрної функції h(x): {:.2f} (h < 0 = вихід за безпечну множину)\n",
        min_h);
    std::cout << std::format("перемикань вердикту: {}, відкинутих кандидатів: {}\n",
                             rep.verdict_changes, rep.rejects);
    std::cout << std::format("фінал: v = {:.2f} м/с — {}\n", pl.v,
                             min_clear > 0.05f ? "зіткнення не сталося" : "ЗІТКНЕННЯ");
    return 0;
}

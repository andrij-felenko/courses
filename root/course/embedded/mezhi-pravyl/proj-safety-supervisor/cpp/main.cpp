#include <array>
#include <optional>
#include <print>

#include "supervisor.hpp"

// Прогін фільтра на найпростішій моделі ровера. Модель тут лише для того,
// щоб згодувати супервізору правдоподібний потік давачів: приводи вважаємо
// ідеальними, тобто фактична швидкість дорівнює виданій уставці.

namespace {

using safety::Seconds;

constexpr Seconds kDt{1.0f / 200.0f};   // швидкий контур — 200 Гц
constexpr Seconds kPlanPeriod{0.05f};   // планувальник — 20 Гц
constexpr Seconds kSimEnd{9.6f};
constexpr float   kWallX{14.0f};        // стіна попереду, м від старту
constexpr float   kTiltLimit{0.52f};    // ~30° перекидання

bool lidar_blind(Seconds t)    { return t >= Seconds{1.0f} && t < Seconds{1.3f}; }
bool planner_frozen(Seconds t) { return t >= Seconds{4.5f} && t < Seconds{5.5f}; }
bool estop_pressed(Seconds t)  { return t >= Seconds{9.0f}; }

// Просідання напруги під струмом розгону, потім глибокий розряд
float battery_voltage(Seconds t)
{
    const float s = t.count();
    if (s < 3.2f) return 16.0f;
    if (s < 4.5f) return 16.0f - (s - 3.2f) * 1.4f;
    return 14.2f;
}

// Виїзд на схил і повернення на рівне
float tilt_rad(Seconds t)
{
    const float s = t.count();
    if (s < 2.2f || s >= 3.2f) return 0.05f;
    return 0.05f + (s - 2.2f) * 0.50f;
}

void print_row(Seconds t, const safety::Sensors& sn, float wish_vx, const safety::Outcome& out)
{
    std::println("{:6.3f}  {:>6}  {:5.2f}  {:5.3f} | {:6.2f}  {:6.2f}  {:6.2f} | {}",
                 t.count(),
                 sn.obstacle_dist_m ? std::format("{:6.2f}", *sn.obstacle_dist_m)
                                    : std::string{"---"},
                 sn.battery_voltage.value_or(0.0f), sn.tilt_rad,
                 wish_vx, out.cmd.vx, out.cmd.yaw_rate,
                 safety::name(out.status));
}

void dump_blackbox(const safety::Supervisor::Log& log)
{
    std::println("\n=== Чорна скринька: {} епізодів (затерто {}) ===", log.size(), log.dropped());

    // Розгортаємо кільце у суцільний масив — так його віддають телеметрії
    std::array<safety::Event, 48> flat{};
    for (const safety::Event& e : log.snapshot(flat)) {
        std::println("  {:6.3f}…{:6.3f} с  {:<11} {:<16} знач={:8.3f}  тактів={}",
                     e.t_begin.count(), e.t_end.count(),
                     safety::name(e.status), safety::name(e.reason),
                     e.value, e.repeats);
    }
}

} // namespace

int main()
{
    safety::Supervisor sup;

    Seconds t{0.0f};
    Seconds next_plan{0.0f};
    Seconds next_report{0.0f};
    float rover_x = 0.0f;
    auto prev_status = safety::Status::PassThrough;
    bool first = true;

    std::println("  час    dist   вольт  крен  |  vx_кмд  vx_безп  yaw_бзп | статус");

    while (t < kSimEnd) {
        // Повільний потік: «жадібний» планувальник просить повний хід
        if (!planner_frozen(t) && t >= next_plan) {
            if (!sup.submit_plan(safety::Command{2.2f, 0.0f, 0.6f})) {
                std::println("!! уставку відкинуто: нечислове значення");
            }
            next_plan = t + kPlanPeriod;
        }

        safety::Sensors sensors{
            .obstacle_dist_m = lidar_blind(t) ? std::nullopt
                                              : std::optional{kWallX - rover_x},
            .battery_voltage = battery_voltage(t),
            .tilt_rad        = tilt_rad(t),
            .tilt_limit_rad  = kTiltLimit,
            .emergency_stop  = estop_pressed(t)
        };

        const auto result = sup.step(sensors, kDt);
        if (!result) {
            // Fault — це помилка виклику, а не режим машини: далі йти нікуди
            std::println("!! супервізор відмовив, код {}", static_cast<int>(result.error()));
            return 1;
        }

        // Ідеальні приводи: що видали, те й поїхало
        rover_x += result->cmd.vx * kDt.count();

        if (first || result->status != prev_status || t >= next_report) {
            print_row(t, sensors, sup.held_plan().vx, *result);
            next_report = t + Seconds{0.5f};
            first = false;
        }
        prev_status = result->status;
        t += kDt;
    }

    std::println("\nпройдено {:.2f} м, до стіни лишилось {:.2f} м", rover_x, kWallX - rover_x);
    dump_blackbox(sup.log());
    return 0;
}

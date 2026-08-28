// test_simulation.cpp - Числова перевірка динаміки на C++20
#include <iostream>
#include <iomanip>
#include "L1Controller.hpp"

int main() {
    using namespace navigation;

    L1Controller ctrl{L1Params{
        .period_l1 = 18.0f,
        .damping_ratio = 0.7071f,
        .k_i = 0.035f,
        .roll_limit_rad = 30.0f * PI / 180.0f
    }};

    Vector2D pos{0.0f, 60.0f};
    const Vector2D wa{0.0f, 0.0f};
    const Vector2D wb{2000.0f, 0.0f};

    const float wind_y = 6.0f;
    const float airspeed = 20.0f;
    float heading = 0.0f;
    constexpr float dt = 0.1f;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Час(с) | X(м)    | Y(м)   | CTE(м) | Крен(град) | L1(м)\n";
    std::cout << "--------------------------------------------------------\n";

    for (int step = 0; step <= 250; ++step) {
        const float t = static_cast<float>(step) * dt;

        Vector2D vel{
            airspeed * std::cos(heading),
            airspeed * std::sin(heading) + wind_y
        };

        const auto result = ctrl.updateLine(pos, vel, wa, wb, dt);
        if (!result) {
            std::cerr << "Помилка оновлення навігації\n";
            break;
        }

        const auto& out = result.value();
        const float turn_rate = (GRAVITY / airspeed) * std::tan(out.roll_setpoint_rad);
        heading += turn_rate * dt;

        pos.x += vel.x * dt;
        pos.y += vel.y * dt;

        if (step % 25 == 0) {
            std::cout << std::setw(6) << t << " | "
                      << std::setw(7) << pos.x << " | "
                      << std::setw(6) << pos.y << " | "
                      << std::setw(6) << out.cross_track_error_m << " | "
                      << std::setw(10) << (out.roll_setpoint_rad * 180.0f / PI) << " | "
                      << std::setw(5) << out.lookahead_distance_m << "\n";
        }
    }

    return 0;
}

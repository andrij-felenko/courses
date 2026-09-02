#include <algorithm>
#include <iomanip>
#include <iostream>

#include "dispatcher.hpp"

namespace {

constexpr int kSimSteps = 10;
constexpr float kSimDtS = 1.0f;
constexpr float kMaxSpeedMps = 15.0f;   // маршова швидкість апарата
constexpr float kSensorRangeM = 25.0f;  // далі перешкода виходить з поля зору

// Груба модель апарата: за такт він проходить у бік заданої точки не більше
// kMaxSpeedMps * dt метрів. Регулятора й планувальника траєкторії тут немає —
// нас цікавить лише те, які цілі диспетчер вмикає і коли.
void plant_advance(mission::VehicleTelemetry& telem,
                   const mission::DispatcherOutput& cmd,
                   float dt_s) {
    if (cmd.mode != mission::OutputMode::Track) {
        return;  // Idle/Hold/Land — апарат тримає поточну позицію
    }

    const float dist = telem.position.distance_to(cmd.setpoint);
    if (dist < 1e-3f) {
        return;
    }

    const float k = std::min(kMaxSpeedMps * dt_s / dist, 1.0f);
    telem.position.x += (cmd.setpoint.x - telem.position.x) * k;
    telem.position.y += (cmd.setpoint.y - telem.position.y) * k;
    telem.position.z += (cmd.setpoint.z - telem.position.z) * k;

    telem.battery_v -= 0.05f * dt_s;  // політ їсть заряд
}

// Другий бік мосту: потік телеметрії забирає події й пакує їх у MAVLink.
// Тут замість пакувальника — друк, решта поведінки та сама.
void drain_outbox(mission::Outbox& outbox, float t_s) {
    while (const auto ev = outbox.pop()) {
        std::cout << "  t=" << std::setw(4) << t_s << " с | ціль #" << ev->id << ' '
                  << std::setw(9) << std::left << mission::to_string(ev->state) << std::right
                  << " | MAVLink msg " << static_cast<int>(ev->msg)
                  << ", result " << static_cast<int>(ev->result)
                  << " | точка [" << ev->target.x << ", " << ev->target.y
                  << ", " << ev->target.z << "]\n";
    }
}

}  // namespace

int main() {
    std::cout << std::fixed << std::setprecision(1);

    mission::Outbox outbox;
    mission::MissionDispatcher dispatcher{outbox};

    mission::VehicleTelemetry telemetry{
        .position = {0.0f, 0.0f, -10.0f},
        .battery_v = 24.2f,
        .geofence_valid = true,
        .ekf_healthy = true,
        .obstacle_detected = false
    };

    const mission::GoalItem survey_goal{
        .id = 101,
        .action = mission::GoalAction::SurveyPolygon,
        .priority = 50,
        .target = {100.0f, 50.0f, -50.0f},
        .tolerance_m = 3.0f,
        .timeout_s = 60.0f
    };

    if (!dispatcher.enqueue(survey_goal)) {
        std::cerr << "черга цілей повна вже на старті — місію не завантажено\n";
        return 1;
    }

    std::cout << "=== СИМУЛЯЦІЯ АВТОНОМНОГО ДИСПЕТЧЕРА (C++) ===\n";

    // Точка, де далекомір побачив перешкоду: доки апарат від неї не відійшов,
    // давач продовжує її бачити.
    std::optional<mission::Vec3> detection{};
    float t_s = 0.0f;

    for (int step = 0; step < kSimSteps; ++step, t_s += kSimDtS) {
        if (step == 3) {
            std::cout << "\n--- ПОДІЯ: далекомір бачить перешкоду на курсі ---\n";
            telemetry.obstacle_detected = true;
            detection = telemetry.position;
        }

        const auto cmd = dispatcher.step(telemetry, kSimDtS);
        drain_outbox(outbox, t_s);
        plant_advance(telemetry, cmd, kSimDtS);

        if (detection && telemetry.position.distance_to(*detection) > kSensorRangeM) {
            // Маневр відпрацьовано: перешкода вийшла з поля зору давача.
            telemetry.obstacle_detected = false;
            detection.reset();
        }
    }

    std::cout << "\nПідсумок: #101 " << mission::to_string(dispatcher.state_of(101))
              << ", #9999 " << mission::to_string(dispatcher.state_of(9999))
              << ", подій загублено: " << outbox.dropped() << '\n';
    return 0;
}

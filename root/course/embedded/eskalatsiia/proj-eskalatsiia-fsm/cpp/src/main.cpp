// Прогін автомата на сцені зі статті: ровер 350 кг, 4 м/с, силует за 20 м.
// Модель руху груба навмисно — предмет тут автомат, а не динаміка платформи.
#include "escalation/manager.hpp"

#include <array>
#include <cstddef>
#include <format>
#include <iostream>

namespace {

using namespace std::chrono_literals;

constexpr auto  kTick        = 20ms;   // петля керування 50 Гц
constexpr float kObstacleXM  = 60.0f;
constexpr float kDetectRange = 20.0f;

// Планувальник знайшов лише два виходи: вузький об'їзд праворуч і зупинку
constexpr std::array<esc::Option, 2> kPlannerOptions{
    esc::Option{1, "Обхід праворуч", 6.5f, 0.35f},
    esc::Option{2, "Зупинка",        0.0f, 0.05f},
};

struct Sim {
    float                     x{0.0f};
    float                     speed{4.0f};
    std::chrono::milliseconds now{0ms};
    std::chrono::milliseconds last_heartbeat{0ms};
    bool                      link{true};
};

float target_speed(const esc::Command& c) noexcept {
    return std::visit([](const auto& v) -> float {
        using T = std::decay_t<decltype(v)>;
        if constexpr (std::is_same_v<T, esc::cmd::Continue>)          return 4.0f;
        else if constexpr (std::is_same_v<T, esc::cmd::FollowOption>) return 2.0f;   // об'їзд повільніше
        else if constexpr (std::is_same_v<T, esc::cmd::GoTo>)         return -1.5f;  // реверс по слідах
        else                                                          return 0.0f;
    }, c);
}

void step_motion(Sim& s, const esc::Command& c) noexcept {
    const float dt  = std::chrono::duration<float>(kTick).count();
    float       dv  = target_speed(c) - s.speed;
    const float lim = 2.0f * dt;                 // ±2 м/с²
    dv = std::clamp(dv, -lim, lim);
    s.speed += dv;
    s.x     += s.speed * dt;
}

// Те, що бачить оператор: станція розбирає кадр і показує варіанти
void gcs_show(std::span<const std::byte> frame) {
    const auto q = esc::unpack_query(frame);
    if (!q) {
        std::cout << std::format("  [GCS] кадр не розібрано: {}\n", esc::to_string(q.error()));
        return;
    }
    std::cout << std::format("  [GCS] {} Б у ефірі: запит #{}, тригер {}, дедлайн {} мс{}\n",
                             frame.size(), q->query_id,
                             static_cast<int>(q->trigger), q->deadline.count(),
                             (q->flags & esc::kFlagRoiDropped) ? ", мініатюру відкинуто" : "");
    for (const auto& o : q->offered()) {
        std::cout << std::format("        [{}] {}  +{:.1f} м, ризик {:.2f}\n",
                                 o.id, o.description, o.estimated_cost_detour_m, o.risk_score);
    }
}

void run(std::string_view title, bool operator_answers,
         std::chrono::milliseconds answer_delay, bool link_dies) {
    std::cout << std::format("\n=== {} ===\n", title);

    esc::Manager mgr{1500ms};
    Sim          sim{};
    std::array<std::byte, 96> roi{};    // умовна мініатюра спірної ділянки кадру
    roi.fill(std::byte{0xA5});

    esc::State shown      = mgr.state();
    bool       query_sent = false;
    bool       reply_done = false;
    auto       reply_due  = 0ms;

    for (int tick = 0; tick < 3000; ++tick) {
        sim.now = tick * kTick;
        if (sim.link) sim.last_heartbeat = sim.now;

        const float dist = kObstacleXM - sim.x;

        esc::Manager::Inputs in{};
        in.now                = sim.now;
        in.dist_to_obstacle_m = dist;
        in.speed_mps          = sim.speed;
        in.pose.x             = sim.x;
        in.pose.stamp         = sim.now;
        in.pose.rssi_dbm      = sim.link ? -78 : -110;
        in.last_heartbeat     = sim.last_heartbeat;
        if (!query_sent && dist <= kDetectRange) {
            in.trigger = esc::Trigger::BorderlineCritical;  // 49% мішок / 51% людина
            in.options = kPlannerOptions;
            in.roi     = roi;
        }
        // Об'їзд вважаємо завершеним, коли ровер проминув перешкоду
        in.maneuver_done = (sim.x > kObstacleXM + 3.0f);

        const auto out = mgr.tick(in);

        if (mgr.state() != shown) {
            std::cout << std::format("[{:6} мс] {} -> {} (x={:.1f} м, v={:.2f} м/с, слідів {})\n",
                                     sim.now.count(), esc::to_string(shown),
                                     esc::to_string(mgr.state()), sim.x, sim.speed,
                                     mgr.trail().size());
            shown = mgr.state();
        }
        if (!out.frame.empty()) {
            query_sent = true;
            reply_due  = sim.now + answer_delay;
            gcs_show(out.frame);
            if (link_dies) {
                sim.link = false;      // радіо вмирає одразу після відправлення
                std::cout << "  [радіо] HEARTBEAT зник\n";
            }
        }
        if (const auto* abort = std::get_if<esc::cmd::SafeAbort>(&out.command);
            abort != nullptr && abort->persist_incident) {
            std::cout << std::format("  [NVRAM] інцидент #{} записано, мотори знеструмлено\n",
                                     mgr.query_id());
        }

        // Оператор натискає кнопку: станція шле відповідь тим самим протоколом
        if (operator_answers && query_sent && !reply_done && sim.now >= reply_due) {
            reply_done = true;
            std::array<std::byte, 16> frame{};
            const esc::Reply rep{mgr.query_id(), 1, sim.now};
            if (const auto packed = esc::pack_reply(rep, frame); packed) {
                const auto verdict = mgr.handle_reply(*packed, sim.now);
                std::cout << std::format("  [оператор] опція 1 на {} мс: {}\n",
                                         (sim.now - mgr.request_started()).count(),
                                         verdict ? std::string_view{"прийнято"}
                                                 : esc::to_string(verdict.error()));
            }
        }

        step_motion(sim, out.command);
        if (mgr.state() == esc::State::FailsafeSafeAbort && sim.speed == 0.0f) break;
        if (mgr.state() == esc::State::Autonomous && query_sent && sim.x > kObstacleXM + 5.0f) break;
    }
}

}  // namespace

int main() {
    run("Оператор відповів вчасно", true, 900ms, false);
    run("Оператор спізнився на 200 мс після дедлайну", true, 4200ms, false);
    run("Радіо мовчить: HOLD -> BACKTRACK -> SAFE_ABORT", false, 0ms, true);
    return 0;
}

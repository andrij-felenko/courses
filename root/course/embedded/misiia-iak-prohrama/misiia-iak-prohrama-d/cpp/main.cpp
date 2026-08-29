/* Прогін бортової VM на настільній машині: замість польотного контуру
   підставлено найпростішу кінематику, замість давачів — її стан. Цього
   досить, щоб побачити роботу циклів, умов і сторожів у трасі. */

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <print>
#include <span>
#include <string_view>

#include "geo.hpp"
#include "mission_vm.hpp"

namespace {

using namespace mission;

constexpr std::uint32_t kTickMs = 20;   /* 50 Гц — типовий такт диспетчера */

constexpr GeoPoint kHome{ .lat_e7 = 504501000, .lon_e7 = 305234000, .alt_m = 0.0F };

/* ---------- модель апарата ---------- */

class Vehicle {
public:
    explicit Vehicle(GeoPoint home) noexcept : home_{home} {}

    [[nodiscard]] GeoPoint position() const noexcept
    {
        GeoPoint p = shifted(home_, east_m_, north_m_);
        p.alt_m = alt_m_;
        return p;
    }

    [[nodiscard]] float yaw_deg() const noexcept { return yaw_deg_; }
    [[nodiscard]] float soc_pct() const noexcept { return soc_pct_; }
    [[nodiscard]] float alt_m() const noexcept { return alt_m_; }

    /* 4S: 17.0 В на повній, 14.0 В на порожній. Плюс періодичне
       просідання під ривками тяги — саме воно й ламає перевірку
       за сирою напругою. */
    [[nodiscard]] float pack_v() const noexcept
    {
        return 14.0F + 0.030F * soc_pct_ - sag_v_;
    }

    void step(const Outputs& out, float dt, float drain_pct_s) noexcept
    {
        const GeoPoint pos = position();
        const Offset   d   = offset_between(pos, out.target);
        const float    dist = std::hypot(d.east_m, d.north_m);

        if (const float move = out.speed_mps * dt; dist > 0.01F) {
            const float k = move < dist ? move / dist : 1.0F;
            east_m_  += d.east_m * k;
            north_m_ += d.north_m * k;
        }

        const float dz = out.target.alt_m - alt_m_;
        const float vz = 2.5F * dt;
        alt_m_ += std::fabs(dz) < vz ? dz : std::copysign(vz, dz);
        alt_m_  = std::max(alt_m_, 0.0F);

        /* Курс: або нав'язаний CONDITION_YAW, або просто на ціль. */
        const float want = out.yaw_setpoint_deg.value_or(bearing_deg(pos, out.target));
        const float err  = wrap_deg(want - yaw_deg_);
        const float slew = 90.0F * dt;
        yaw_deg_ = heading_deg(yaw_deg_ +
                               (std::fabs(err) < slew ? err : std::copysign(slew, err)));

        t_s_ += dt;
        soc_pct_ = std::max(0.0F, soc_pct_ - drain_pct_s * dt);
        sag_v_   = dist > 1.0F ? 0.9F * (0.5F + 0.5F * std::sin(t_s_ * 3.0F)) : 0.0F;
    }

private:
    GeoPoint home_{};
    float east_m_{0.0F};
    float north_m_{0.0F};
    float alt_m_{0.0F};
    float yaw_deg_{0.0F};
    float soc_pct_{100.0F};
    float sag_v_{0.0F};
    float t_s_{0.0F};
};

/* ---------- складання байткоду ---------- */

[[nodiscard]] Instruction nav_wp(float east_m, float north_m, float alt_m,
                                 std::int16_t hold_s, std::int16_t radius_m,
                                 bool autocontinue = true) noexcept
{
    const GeoPoint p = shifted(kHome, east_m, north_m);
    return Instruction{ .opcode = Opcode::NavWaypoint,
                        .flags  = autocontinue ? kFlagAutocontinue : std::uint8_t{0},
                        .p1     = hold_s,
                        .p2     = radius_m,
                        .lat_e7 = p.lat_e7,
                        .lon_e7 = p.lon_e7,
                        .alt_m  = alt_m };
}

/* Координати нульові — «тут же, де апарат». */
[[nodiscard]] Instruction nav_here(Opcode op, float alt_m, std::int16_t radius_m) noexcept
{
    return Instruction{ .opcode = op, .p2 = radius_m, .alt_m = alt_m };
}

[[nodiscard]] Instruction op2(Opcode op, std::int16_t p1, std::int16_t p2) noexcept
{
    return Instruction{ .opcode = op, .p1 = p1, .p2 = p2 };
}

/* ---------- прогін ---------- */

void run_mission(std::string_view title, std::span<const Instruction> program,
                 float drain_pct_s, std::uint32_t limit_ms)
{
    std::println("\n=== {} ===", title);

    auto loaded = MissionVm::load(program);
    if (!loaded) {
        std::println("  верифікатор відхилив місію: {}", describe(loaded.error()));
        return;
    }
    MissionVm& vm = *loaded;

    Vehicle veh{kHome};
    vm.start(kHome, Millis{0});

    std::optional<std::uint16_t> last_nav{};
    std::uint16_t last_servo{0};
    Status        last_status{Status::Idle};
    std::uint32_t paused_at{0};

    for (std::uint32_t now = 0; now <= limit_ms; now += kTickMs) {
        const Telemetry t{ .now = Millis{now},
                           .position = veh.position(),
                           .yaw_deg = veh.yaw_deg(),
                           .battery_v = veh.pack_v(),
                           .battery_soc_pct = veh.soc_pct(),
                           .gnss_ok = true,
                           .link_ok = true };
        vm.tick(t);

        const float t_s = static_cast<float>(now) / 1000.0F;

        if (vm.status() != last_status) {
            std::println("[{:6.1f} с] {}", t_s, describe(vm.status()));
            if (vm.status() == Status::Paused) {
                paused_at = now;
            }
            last_status = vm.status();
        }
        if (const auto nav = vm.active_nav(); nav && nav != last_nav) {
            std::println("[{:6.1f} с] seq {:2}  {:<20}  SoC {:3.0f}%  висота {:5.1f} м",
                         t_s, *nav, describe(vm.opcode_at(*nav)),
                         veh.soc_pct(), veh.alt_m());
            last_nav = nav;
        }
        if (vm.outputs().servo_pwm[0] != last_servo) {
            last_servo = vm.outputs().servo_pwm[0];
            std::println("[{:6.1f} с]          DO_SET_SERVO ch1 = {} мкс", t_s, last_servo);
        }

        /* Наземна станція знімає покрокову паузу через 3 секунди. */
        if (vm.status() == Status::Paused && now - paused_at >= 3000U) {
            std::println("[{:6.1f} с]          НСУ → MAV_CMD_MISSION_START", t_s);
            vm.resume();
        }

        if (vm.stopped()) {
            return;
        }
        veh.step(vm.outputs(), static_cast<float>(kTickMs) / 1000.0F, drain_pct_s);
    }
    std::println("  ліміт часу симуляції вичерпано, стан: {}", describe(vm.status()));
}

}  // namespace

int main()
{
    /* Місія з розділу про DO_JUMP: три точки й дворазовий повтор.
       Разом контур мусить пройти A, B, C тричі й сісти. */
    const std::array loop_mission{
        nav_here(Opcode::NavTakeoff, 30.0F, 0),        // 0
        nav_wp(  0.0F, 120.0F, 30.0F, 0, 5),           // 1: A
        nav_wp(150.0F, 120.0F, 30.0F, 0, 5),           // 2: B
        nav_wp(150.0F,   0.0F, 30.0F, 0, 5),           // 3: C
        op2(Opcode::DoJump, 1, 2),                     // 4
        nav_here(Opcode::NavLand, 0.0F, 5)             // 5
    };
    run_mission("Цикл DO_JUMP(1, 2): три проходи A-B-C", loop_mission, 0.05F, 300'000);

    /* Патрулювання без обмеження повторів: вихід дає не лічильник,
       а умова за станом батареї. Дорогою — умовне скидання вантажу
       й покрокова зупинка на другій точці. */
    const std::array patrol_mission{
        nav_here(Opcode::NavTakeoff, 40.0F, 0),               // 0
        nav_wp(-200.0F, 300.0F, 40.0F, 0, 8),                 // 1: P1
        op2(Opcode::ConditionDistance, 50, 0),                // 2
        op2(Opcode::DoSetServo, 1, 1900),                     // 3
        nav_wp( 200.0F, 300.0F, 40.0F, 0, 8, false),          // 4: P2, autocontinue = 0
        op2(Opcode::JumpIfBatteryLow, 30, 7),                 // 5
        op2(Opcode::DoJump, 1, -1),                           // 6: нескінченний цикл
        nav_here(Opcode::NavRtl, 0.0F, 8)                     // 7
    };
    run_mission("Патруль із виходом за станом батареї", patrol_mission, 0.30F, 400'000);

    /* Те саме, але з биткою ціллю переходу: рівень 1 мусить відхилити
       місію ще при завантаженні, до MISSION_ACK. */
    const std::array broken_mission{
        nav_here(Opcode::NavTakeoff, 30.0F, 0),
        nav_wp(0.0F, 100.0F, 30.0F, 0, 5),
        op2(Opcode::DoJump, 9, 1)
    };
    run_mission("Статичний верифікатор: DO_JUMP за межі місії", broken_mission, 0.05F, 10'000);

    return 0;
}

// scenario.cpp — прогін місій на настільній машині.
//
// Тут два різні предмети:
//   · Simulator — груба модель апарата, потрібна лише щоб було звідки взяти
//     телеметрію: рівномірний рух до уставки, стала швидкість підйому, лінійне
//     просідання батареї. Ніякої аеродинаміки, і не треба;
//   · scenario_* — власне перевірки, кожна зі своїм питанням до машини.
//
// Складання: c++ -std=c++23 -Iinclude src/vm.cpp test/scenario.cpp -o scenario
#include "mission/vm.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <format>
#include <iostream>
#include <limits>
#include <span>
#include <string_view>

using namespace mission;
using namespace std::chrono_literals;

namespace {

int g_failures = 0;

void check(bool ok, std::string_view what)
{
    std::cout << std::format("  [{}] {}\n", ok ? "ок " : "ЗБІЙ", what);
    if (!ok) {
        ++g_failures;
    }
}

constexpr float kDt         = 0.05F; // 20 Гц — типова частота задачі місії
constexpr Millis kDtMs      = 50ms;
constexpr float kClimbMps   = 2.5F;
constexpr float kDefaultMps = 6.0F;
constexpr double kMetersPerDeg = 111'320.0;
constexpr double kDegToRad     = 3.14159265358979323846 / 180.0;

class Simulator {
public:
    Simulator(double lat_deg, double lon_deg) : lat_{lat_deg}, lon_{lon_deg} {}

    void set_drain(float pct_per_s) noexcept { drain_ = pct_per_s; }
    void set_yaw_rate(float dps) noexcept { yaw_rate_ = dps; }
    void set_gnss(bool ok) noexcept { gnss_ok_ = ok; }
    void set_gcs_link(bool ok) noexcept { gcs_link_ok_ = ok; }

    [[nodiscard]] float battery() const noexcept { return battery_; }
    [[nodiscard]] float yaw() const noexcept { return yaw_; }

    Telemetry update(const Actuators &act) noexcept
    {
        double dist = 0.0;

        if (act.nav_valid) {
            const double target_lat = static_cast<double>(act.target_lat_1e7) * 1e-7;
            const double target_lon = static_cast<double>(act.target_lon_1e7) * 1e-7;
            const float  speed = act.target_speed_mps > 0.0F ? act.target_speed_mps
                                                             : kDefaultMps;

            dist = distance_to(target_lat, target_lon);
            const double stride = static_cast<double>(speed) * kDt;
            if (dist > 1e-9) {
                const double f = stride >= dist ? 1.0 : stride / dist;
                lat_ += (target_lat - lat_) * f;
                lon_ += (target_lon - lon_) * f;
            }

            const float dalt  = act.target_alt_m - alt_;
            const float climb = kClimbMps * kDt;
            alt_ += std::fabs(dalt) <= climb ? dalt : (dalt > 0.0F ? climb : -climb);

            dist = distance_to(target_lat, target_lon);
        }

        yaw_ += yaw_rate_ * kDt;
        if (yaw_ >= 360.0F) {
            yaw_ -= 360.0F;
        }
        battery_ = std::max(0.0F, battery_ - drain_ * kDt);

        Telemetry t{};
        t.lat_1e7         = static_cast<std::int32_t>(std::lround(lat_ * 1e7));
        t.lon_1e7         = static_cast<std::int32_t>(std::lround(lon_ * 1e7));
        t.alt_m           = alt_;
        t.yaw_deg         = yaw_;
        t.battery_soc_pct = battery_;
        t.gcs_link_ok     = gcs_link_ok_;
        // Без позиції навігатор не має ні відстані, ні права сказати «на
        // місці». Саме так це виглядає при відмові GNSS.
        t.dist_to_wp_m = gnss_ok_ ? static_cast<float>(dist)
                                  : std::numeric_limits<float>::quiet_NaN();
        t.wp_reached = gnss_ok_ && act.nav_valid && dist <= 2.0 &&
                       std::fabs(act.target_alt_m - alt_) <= 1.5F;
        return t;
    }

private:
    // Плоска апроксимація: на масштабах кількох сотень метрів вона точніша,
    // ніж потрібно польотному завданню, і коштує два множення.
    [[nodiscard]] double distance_to(double lat_deg, double lon_deg) const noexcept
    {
        const double dy = (lat_deg - lat_) * kMetersPerDeg;
        const double dx = (lon_deg - lon_) * kMetersPerDeg * std::cos(lat_ * kDegToRad);
        return std::sqrt(dx * dx + dy * dy);
    }

    double lat_;
    double lon_;
    float  alt_{0.0F};
    float  yaw_{0.0F};
    float  yaw_rate_{0.0F};
    float  battery_{100.0F};
    float  drain_{0.02F};
    bool   gnss_ok_{true};
    bool   gcs_link_ok_{true};
};

struct RunResult {
    unsigned watch_hits{}; // скільки разів виконано інструкцію watch_pc
    Millis   elapsed{};
};

RunResult run(Vm &vm, Simulator &sim, Actuators &act, std::uint16_t watch_pc,
              unsigned max_steps)
{
    Telemetry telem{};
    telem.dist_to_wp_m = std::numeric_limits<float>::quiet_NaN();

    RunResult result{};
    for (unsigned i = 0; i < max_steps && is_active(vm.status()); ++i) {
        const std::uint16_t pc_before = vm.pc();
        vm.step(telem, act, result.elapsed);
        if (pc_before == watch_pc && vm.pc() != pc_before) {
            ++result.watch_hits;
        }
        telem = sim.update(act);
        result.elapsed += kDtMs;
    }
    return result;
}

constexpr Home kHome{.lat_1e7 = 504'500'000, .lon_1e7 = 305'200'000, .alt_m = 180.0F};
constexpr std::uint16_t kPcServo = 4; // індекс DO_SET_SERVO у програмі нижче

// Обліт периметра ділянки: зліт, перевірка батареї, точка A, скидання маркера
// за 30 метрів до неї, точка B, повторити тричі, повернення. Нумерація
// інструкцій — це і є мітки стрибків, тому вона в коментарях.
constexpr std::array<Instruction, 8> kPatrol{{
    /* 0 */ {.opcode = Opcode::NavTakeoff, .alt_m = 30.0F},
    /* 1 */ {.opcode = Opcode::JumpIfBatLow, .param1 = 25, .param2 = 7},
    /* 2 */ {.opcode  = Opcode::NavWaypoint,
             .flags   = std::to_underlying(Flag::AutoContinue),
             .lat_1e7 = 504'507'000,
             .lon_1e7 = 305'212'000,
             .alt_m   = 30.0F},
    /* 3 */ {.opcode = Opcode::CondDistance, .param1 = 30},
    /* 4 */ {.opcode = Opcode::DoSetServo, .param1 = 5, .param2 = 1900},
    /* 5 */ {.opcode  = Opcode::NavWaypoint,
             .lat_1e7 = 504'512'000,
             .lon_1e7 = 305'224'000,
             .alt_m   = 30.0F},
    /* 6 */ {.opcode = Opcode::DoJump, .param1 = 1, .param2 = 3},
    /* 7 */ {.opcode = Opcode::NavRtl},
}};

void scenario_patrol()
{
    std::cout << "обліт периметра\n";
    Vm        vm;
    Simulator sim{50.45, 30.52};
    Actuators act{};

    vm.set_home(kHome);
    check(vm.load(kPatrol).has_value(), "місію прийнято");

    const RunResult r = run(vm, sim, act, kPcServo, 40'000);
    std::cout << std::format("  {}, кіл {}, стрибків {}, кроків {}, час {:.1f} с\n",
                             to_string(vm.status()), r.watch_hits, vm.total_jumps(),
                             vm.steps_executed(),
                             std::chrono::duration<double>(r.elapsed).count());

    check(vm.status() == Status::Completed, "програма завершилася");
    check(act.rtl_triggered, "повернення на точку старту видано");
    check(act.servo_pwm_us == 1900 && act.servo_channel == 5, "маркер скинуто");
    // Три стрибки DO_JUMP означають чотири проходи ділянки. Батарея жодного
    // разу не просіла, тож JumpIfBatLow не спрацював — усі переходи від циклу.
    check(r.watch_hits == 4, "ділянку пройдено чотири рази");
    check(vm.total_jumps() == 3, "рівно три повтори циклу");
    check(sim.battery() > 25.0F, "заряд лишався вище порога");
}

// Та сама програма, але батарея сідає: перевірка на першій інструкції кола має
// відправити апарат додому, не дочекавшись трьох повторів.
void scenario_low_battery()
{
    std::cout << "просідання батареї\n";
    Vm        vm;
    Simulator sim{50.45, 30.52};
    Actuators act{};

    sim.set_drain(1.2F);
    sim.set_gcs_link(false); // зв'язок із наземною станцією втрачено
    vm.set_home(kHome);
    check(vm.load(kPatrol).has_value(), "місію прийнято");

    const RunResult r = run(vm, sim, act, kPcServo, 40'000);
    std::cout << std::format("  {}, кіл {}, залишок {:.1f}%\n", to_string(vm.status()),
                             r.watch_hits, sim.battery());

    check(vm.status() == Status::Completed, "програма завершилася");
    check(act.rtl_triggered, "повернення видано достроково");
    check(r.watch_hits < 4, "до трьох повторів не дійшло");
    check(sim.battery() < 25.0F, "заряд справді просів");
    // Втрата зв'язку з оператором на автономну програму не вплинула жодним
    // чином: машина взагалі не дивиться на це поле.
}

// Дії й неблокуючі умови: зміна швидкості, витримка за часом, очікування
// курсу, посадка.
constexpr std::array<Instruction, 4> kActions{{
    /* 0 */ {.opcode = Opcode::DoChangeSpeed, .param2 = 250}, // 2,5 м/с
    /* 1 */ {.opcode = Opcode::CondDelay, .param1 = 2},
    /* 2 */ {.opcode = Opcode::CondYaw, .param1 = 90},
    /* 3 */ {.opcode = Opcode::NavLand},
}};

void scenario_actions()
{
    std::cout << "дії та умови\n";
    Vm        vm;
    Simulator sim{50.45, 30.52};
    Actuators act{};

    sim.set_yaw_rate(10.0F); // апарат повільно обертається: 90° за 9 с
    vm.set_home(kHome);
    check(vm.load(kActions).has_value(), "місію прийнято");

    const RunResult r = run(vm, sim, act, 0xFFFF, 4'000);
    std::cout << std::format("  {}, швидкість {:.2f} м/с, курс {:.1f}°, час {:.1f} с\n",
                             to_string(vm.status()), act.target_speed_mps, sim.yaw(),
                             std::chrono::duration<double>(r.elapsed).count());

    check(vm.status() == Status::Completed, "програма завершилася");
    check(act.land_triggered, "посадку видано");
    check(std::fabs(act.target_speed_mps - 2.5F) < 1e-6F, "швидкість змінено");
    // Дві секунди витримки, а потім розворот до 85° (курс 90° із допуском 5°)
    // — разом близько восьми з половиною секунд, і жодного блокувального
    // очікування: самі лише повернення з WaitingCond.
    check(r.elapsed >= 8s, "обидві умови справді чекали");
}

void scenario_loop_guard()
{
    std::cout << "сторож нескінченних циклів\n";
    static constexpr std::array<Instruction, 2> kLooping{{
        /* 0 */ {.opcode = Opcode::DoJump, .param1 = 0, .param2 = 1000},
        /* 1 */ {.opcode = Opcode::Halt},
    }};
    Vm        vm;
    Simulator sim{50.45, 30.52};
    Actuators act{};

    vm.set_home(kHome);
    check(vm.load(kLooping).has_value(), "місію прийнято");
    run(vm, sim, act, 0xFFFF, 5'000);

    std::cout << std::format("  {} після {} стрибків\n", to_string(vm.status()),
                             vm.total_jumps());

    check(vm.status() == Status::ErrorInfiniteLoop, "машину спинено бюджетом стрибків");
    check(vm.total_jumps() == kMaxTotalJumps, "витрачено рівно бюджет");
    check(act.failsafe_request, "супервізору подано аварійний сигнал");
    check(!act.nav_valid, "чинну уставку знято");
}

void expect_load(std::span<const Instruction> code, bool set_home, LoadError want)
{
    Vm vm;
    if (set_home) {
        vm.set_home(kHome);
    }
    const auto got = vm.load(code);
    const bool ok  = !got.has_value() && got.error() == want;
    check(ok, std::format("відмова {}", to_string(want)));
}

void scenario_loader()
{
    std::cout << "перевірка місії перед зльотом\n";
    static constexpr std::array<Instruction, 2> kBadOpcode{{
        {.opcode = static_cast<Opcode>(0x7F)},
        {.opcode = Opcode::Halt},
    }};
    static constexpr std::array<Instruction, 2> kBadJump{{
        {.opcode = Opcode::DoJump, .param1 = 99, .param2 = 2},
        {.opcode = Opcode::Halt},
    }};
    static constexpr std::array<Instruction, 2> kBadServo{{
        {.opcode = Opcode::DoSetServo, .param1 = 5, .param2 = 5000},
        {.opcode = Opcode::Halt},
    }};
    static constexpr std::array<Instruction, 1> kNoEnd{{
        {.opcode = Opcode::DoSetServo, .param1 = 5, .param2 = 1500},
    }};

    std::array<Instruction, kMaxLoopSlots + 2> too_many_loops{};
    for (std::size_t i = 0; i < kMaxLoopSlots + 1U; ++i) {
        too_many_loops[i] = {.opcode = Opcode::DoJump, .param1 = 0, .param2 = 1};
    }
    too_many_loops.back() = {.opcode = Opcode::Halt};

    expect_load(kPatrol, false, LoadError::NoHome);
    expect_load(std::span<const Instruction>{}, true, LoadError::Empty);
    expect_load(kBadOpcode, true, LoadError::BadOpcode);
    expect_load(kBadJump, true, LoadError::BadJump);
    expect_load(kBadServo, true, LoadError::BadParam);
    expect_load(kNoEnd, true, LoadError::NoTerminator);
    expect_load(too_many_loops, true, LoadError::TooManyLoops);
}

// Відмова GNSS: машина не має права ні летіти навмання, ні спинятися сама.
// Вона просто лишається в очікуванні, а лічильник простою росте — і саме за ним
// зовнішній супервізор колись вирішить сідати.
void scenario_no_position()
{
    std::cout << "відмова GNSS\n";
    static constexpr std::array<Instruction, 3> kProgram{{
        /* 0 */ {.opcode = Opcode::NavTakeoff, .alt_m = 10.0F},
        /* 1 */ {.opcode  = Opcode::NavWaypoint,
                 .lat_1e7 = 504'507'000,
                 .lon_1e7 = 305'212'000,
                 .alt_m   = 10.0F},
        /* 2 */ {.opcode = Opcode::NavRtl},
    }};
    Vm        vm;
    Simulator sim{50.45, 30.52};
    Actuators act{};
    Telemetry telem{};
    telem.dist_to_wp_m = std::numeric_limits<float>::quiet_NaN();

    sim.set_gnss(false); // позиції немає від самого початку
    vm.set_home(kHome);
    check(vm.load(kProgram).has_value(), "місію прийнято");

    Millis now{0};
    for (unsigned i = 0; i < 400; ++i) {
        vm.step(telem, act, now);
        telem = sim.update(act);
        now += kDtMs;
    }

    const Millis waiting = vm.wait_elapsed(now);
    std::cout << std::format("  {} на інструкції {}, чекає {} мс\n",
                             to_string(vm.status()), vm.pc(), waiting.count());

    // Зліт вимагає лише висоти й тому відпрацював; політ у точку — ні.
    check(vm.pc() == 1, "зліт виконано, машина стоїть на польоті в точку");
    check(vm.status() == Status::WaitingNav, "машина чекає, а не помиляється");
    check(waiting > 5s, "очікування триває й лічильник простою росте");
    check(!act.failsafe_request, "це стан світу, а не помилка машини");
}

} // namespace

int main()
{
    std::cout << std::format("розмір інструкції: {} байтів\n", sizeof(Instruction));
    scenario_patrol();
    scenario_low_battery();
    scenario_actions();
    scenario_loop_guard();
    scenario_loader();
    scenario_no_position();

    std::cout << (g_failures == 0 ? "усі сценарії пройдено\n"
                                  : std::format("збоїв: {}\n", g_failures));
    return g_failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}

// main.cpp — прогін наглядача крізь життя вхідної шини 24 В.
//
// Плати тут немає: профіль напруги на роз'ємі перетворює на код АЦП той самий
// об'єкт Divider, яким наглядач читає його назад. Наглядач не знає, що джерело
// вибірок — модель.
//
// Збірка: c++ -std=c++23 -O2 -Wall -Wextra src/main.cpp src/supervisor.cpp -o pwrsim
#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <string_view>
#include <vector>

#include "supervisor.hpp"

using namespace std::chrono_literals;
using namespace power::literals;  // суфікс _mV
using power::Millivolts;

namespace {

struct Segment {
    std::chrono::milliseconds until;
    Millivolts               from;
    Millivolts               to;
    std::string_view         what;
};

// Профіль напруги на вході: від холодного під'єднання до серії просідань.
const std::vector<Segment> kProfile{
    {   20ms,     0_mV,     0_mV, "плата знеструмлена" },
    {  120ms,     0_mV, 24000_mV, "гаряче під'єднання: плавний пуск заряджає C_bulk" },
    {  400ms, 24000_mV, 24000_mV, "штатний режим 24 В" },
    {  460ms, 15000_mV, 15000_mV, "просідання шини до 15 В (пуск сусіднього приводу)" },
    {  800ms, 24000_mV, 24000_mV, "шина відновилася" },
    {  900ms, 48000_mV, 48000_mV, "пробій регулятора БЖ: 48 В на вході" },
    { 1430ms, 24000_mV, 24000_mV, "БЖ замінено, шина 24 В" },
    { 1460ms, 15000_mV, 15000_mV, "просідання №2" },
    { 1590ms, 24000_mV, 24000_mV, "норма" },
    { 1620ms, 15000_mV, 15000_mV, "просідання №3" },
    { 1750ms, 24000_mV, 24000_mV, "норма" },
    { 1780ms, 15000_mV, 15000_mV, "просідання №4 — ліміт повторів вичерпано" },
    { 2100ms, 24000_mV, 24000_mV, "норма, але тримається засув" },
};

struct ProfilePoint {
    Millivolts bus;
    std::size_t segment;
};

ProfilePoint profile_at(std::chrono::milliseconds t)
{
    std::chrono::milliseconds from{0};
    for (std::size_t i = 0; i < kProfile.size(); ++i) {
        const Segment& seg = kProfile[i];
        if (t < seg.until) {
            const auto span = (seg.until - from).count();
            const auto done = (t - from).count();
            const auto delta = static_cast<std::int64_t>(seg.to.value) -
                               static_cast<std::int64_t>(seg.from.value);
            const auto value = static_cast<std::int64_t>(seg.from.value) + delta * done / span;
            return {Millivolts{static_cast<std::uint32_t>(value)}, i};
        }
        from = seg.until;
    }
    return {kProfile.back().to, kProfile.size() - 1};
}

}  // namespace

int main()
{
    // 110 кОм / 10 кОм, опорні 3.3 В, 12-бітний АЦП — як у розрахунку кроку 3.
    constexpr power::Divider divider{110'000, 10'000, 3300_mV, 4095};

    power::Config config{
        .divider = divider,
        .window = {},
        .retry = { .delay = 100ms, .window = 1500ms, .limit = 5 },
        .filter_shift = 3,
        .confirm_samples = 5,
        .settle_samples = 20,
    };

    bool     pin_pwr_enable = false;
    unsigned toggles = 0;

    try {
        power::Supervisor supervisor{config, [&](bool on) {
            pin_pwr_enable = on;
            ++toggles;
        }};

        std::cout << "  t, мс |  U шини |  U виміряна | стан        | PIN_PWR_ENABLE\n"
                  << "--------+---------+-------------+-------------+---------------\n";

        std::mt19937                       noise{20240829u};  // прогін мусить повторюватися
        std::uniform_int_distribution<int> lsb{-3, 3};

        auto        last_state = supervisor.state();
        std::size_t last_segment = kProfile.size();
        bool        efuse_fired = false;
        bool        lockout_cleared = false;

        for (auto t = 0ms; t <= 2200ms; t += 1ms) {
            const auto point = profile_at(t);

            if (point.segment != last_segment) {
                std::cout << "        · " << kProfile[point.segment].what << '\n';
                last_segment = point.segment;
            }

            if (!efuse_fired && t >= 830ms) {
                supervisor.on_efuse_fault();  // переривання EXTI від PIN_FAULT_IRQ
                efuse_fired = true;
            }
            if (!lockout_cleared && t >= 1900ms) {
                if (supervisor.clear_lockout(t)) std::cout << "        · оператор зняв засув\n";
                lockout_cleared = true;
            }

            // Модель АЦП: ідеальний код плюс кілька молодших розрядів шуму.
            const int raw = static_cast<int>(divider.code(point.bus)) + lsb(noise);
            const auto code = static_cast<std::uint16_t>(std::clamp(raw, 0, 4095));

            supervisor.on_sample(code, t);

            if (supervisor.state() != last_state) {
                std::cout << std::setw(7) << t.count() << " | "
                          << std::setw(5) << point.bus.value << " мВ | "
                          << std::setw(8) << supervisor.voltage().value << " мВ | "
                          << std::setw(11) << std::left << power::to_string(supervisor.state())
                          << std::right << " | " << (pin_pwr_enable ? 1 : 0) << '\n';
                last_state = supervisor.state();
            }
        }

        const auto& st = supervisor.stats();
        std::cout << "\nвибірок: " << st.samples << "   пусків: " << st.starts
                  << "   перемикань ключа: " << toggles << '\n'
                  << "аварії: UVLO " << st.uvlo_events << ", OVLO " << st.ovlo_events
                  << ", eFuse " << st.efuse_events << ", засувів " << st.lockouts << '\n'
                  << "напруга шини: від " << st.v_min.value << " мВ до " << st.v_max.value
                  << " мВ (стеля шкали дільника — " << divider.full_scale_bus().value << " мВ)\n";

        // Остання відповідь наглядача — або напруга, або причина відмови.
        if (const auto reading = supervisor.reading(); reading) {
            std::cout << "наприкінці прогону живлення дозволене: " << reading->value << " мВ\n";
        } else {
            std::cout << "наприкінці прогону живлення заборонене: "
                      << power::to_string(reading.error()) << '\n';
        }
    } catch (const std::invalid_argument& e) {
        std::cerr << "наглядач не піднявся: " << e.what() << '\n';
        return 1;
    }

    return 0;
}

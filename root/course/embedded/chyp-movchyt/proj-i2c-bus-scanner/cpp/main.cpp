/* Порядок дій, коли чіп мовчить: спершу дивимося на лінії у стані спокою,
   потім витягуємо шину із зависання і лише тоді щось скануємо. */
#include <cstdio>
#include <cstdlib>
#include <print>
#include <span>
#include <string_view>

#include "bit_bang_master.hpp"
#include "scanner.hpp"
#include "simulated_bus.hpp"

namespace {

/* Адреса акселерометра за даташитом (AD0 = 0) */
constexpr std::uint8_t expected_addr = 0x68;

SimulatedBus::Fault pick_scenario(std::span<char* const> args) {
    const std::string_view name = args.size() > 1 ? args[1] : "ok";

    if (name == "ok")       return SimulatedBus::Fault::none;
    if (name == "stuck")    return SimulatedBus::Fault::sda_stuck_low;
    if (name == "nopullup") return SimulatedBus::Fault::no_pullups;
    if (name == "nopower")  return SimulatedBus::Fault::no_power;

    std::println(stderr, "Невідомий сценарій '{}'. Є: ok, stuck, nopullup, nopower", name);
    std::exit(2);
}

} // namespace

int main(int argc, char** argv) {
    const std::span<char* const> args{argv, static_cast<std::size_t>(argc)};
    SimulatedBus bus{expected_addr, pick_scenario(args)};

    /* Виводи забирає конструктор і повертає деструктор — забути неможливо */
    BitBangMaster<SimulatedBus> master{bus};

    const auto idle = master.idle_state();
    std::println("Стан спокою: SCL={}, SDA={}", int{idle.scl_high}, int{idle.sda_high});

    if (!idle.scl_high && !idle.sda_high) {
        std::println("Обидві лінії в нулі — підтяжок немає або живлення відсутнє.\n"
                     "Скануємо все одно, щоб побачити, як це виглядає з боку ведучого.");
    } else if (!idle.sda_high) {
        std::println("SDA затиснута веденим. Виштовхуємо його байт дев'ятьма тактами SCL...");
        if (master.recover_bus()) {
            std::println("Лінію звільнено, шина знову придатна до транзакцій.");
        } else {
            std::println("Дев'ять тактів не допомогли — шукай замикання SDA на землю.");
        }
    } else if (!idle.scl_high) {
        std::println("SCL у нулі при вільній SDA — обрив підтяжки SCL або ведений тримає такт.");
    }

    const ScanReport report = scan_range(master);
    const Verdict verdict = classify(report, expected_addr);
    print_report(report, expected_addr, verdict);

    return verdict == Verdict::device_as_expected ? 0 : 1;
}

#include "latency/report.hpp"

#include <format>
#include <iostream>
#include <string>

namespace latency::report {
namespace {

constexpr std::size_t kNameColumn = 30;

// std::format рахує ширину поля в кодових ОДИНИЦЯХ, а кирилиця в UTF-8
// займає по дві на символ. Через це "{:<30}" з українськими назвами
// розвалює таблицю рівно на кількість не-ASCII літер. Тому доповнюємо
// самі, рахуючи кодові позиції: байти-продовження мають вигляд 10xxxxxx.
std::size_t code_points(std::string_view text) noexcept {
    std::size_t n = 0;
    for (const char c : text) {
        if ((static_cast<unsigned char>(c) & 0xC0u) != 0x80u) {
            ++n;
        }
    }
    return n;
}

std::string pad(std::string_view text, std::size_t width = kNameColumn) {
    std::string out{text};
    for (std::size_t n = code_points(text); n < width; ++n) {
        out.push_back(' ');
    }
    return out;
}

std::string_view kind_label(const Stage& stage) noexcept {
    switch (stage.kind) {
        case Kind::Fixed:    return "стала";
        case Kind::Periodic: return stage.phase_locked ? "такт+фаза" : "такт";
        case Kind::Band:     return "вилка";
    }
    return "?";
}

std::string rule(char c, std::size_t n = 72) { return std::string(n, c); }

}  // namespace

void print_track(const Track& track) {
    const Summary b = track.summary();

    std::cout << rule('=') << '\n'
              << std::format(" БЮДЖЕТ ЗАТРИМКИ: {}\n", track.title)
              << rule('-') << '\n'
              << pad("Ланка тракту")
              << std::format("  {:>9} {:>9} {:>9}  {}\n",
                             "min, мс", "typ, мс", "max, мс", "тип")
              << rule('-') << '\n';

    for (const Stage& stage : track.stages) {
        std::cout << pad(stage.name)
                  << std::format("  {:>9.3f} {:>9.3f} {:>9.3f}  {}{}\n",
                                 stage.min.count(), stage.typ.count(), stage.max.count(),
                                 kind_label(stage),
                                 stage.domain == Domain::Physical ? "  [фізика]" : "");
    }

    std::cout << rule('-') << '\n'
              << pad("РАЗОМ")
              << std::format("  {:>9.3f} {:>9.3f} {:>9.3f}\n",
                             b.min.count(), b.typ.count(), b.max.count())
              << pad("  з них електроніка (typ)")
              << std::format("  {:>9} {:>9.3f}\n", "", b.electronic.count())
              << pad("  з них фізика (typ)")
              << std::format("  {:>9} {:>9.3f}\n", "", b.physical.count())
              << pad("ДЖИТЕР (max - min)")
              << std::format("  {:>9} {:>9} {:>9.3f}\n", "", "", b.jitter.count());

    if (const auto worst = bottleneck(track.stages)) {
        std::cout << std::format(" Найтовща ланка: {} — {:.3f} мс, {:.0f}% найгіршого випадку\n",
                                 worst->name, worst->max.count(),
                                 bottleneck_share(track.stages) * 100.0);
    }
    if (const auto quantum = worst_quantum(track.stages)) {
        std::cout << std::format(" Найбільший такт: {} — T = {:.3f} мс{}\n",
                                 quantum->name, quantum->period.count(),
                                 quantum->phase_locked ? " (зведено за фазою, квант згорнуто)" : "");
    } else {
        std::cout << " Тактових ланок у тракті немає — квантування не додається\n";
    }
    std::cout << rule('=') << "\n\n";
}

void print_dynamics(std::string_view label, const Summary& budget,
                    double control_hz, double speed_mps) {
    const double phase_typ = phase_shift_deg(budget.typ, control_hz);
    const double phase_max = phase_shift_deg(budget.max, control_hz);

    std::cout << std::format(" ДИНАМІКА: {} (маневрування {:.1f} Гц, швидкість {:.0f} м/с)\n",
                             label, control_hz, speed_mps)
              << std::format("   затримка typ {:.1f} мс -> фаза {:6.1f}°  {}\n",
                             budget.typ.count(), phase_typ, to_string(pio_risk(phase_typ)))
              << std::format("   затримка max {:.1f} мс -> фаза {:6.1f}°  {}\n",
                             budget.max.count(), phase_max, to_string(pio_risk(phase_max)))
              << std::format("   сліпий шлях: {:.2f} м (typ), {:.2f} м (max)\n\n",
                             blind_distance_m(budget.typ, speed_mps),
                             blind_distance_m(budget.max, speed_mps));
}

void print_comparison(std::string_view heading, std::span<const Track> tracks) {
    std::cout << rule('=') << '\n'
              << std::format(" {}\n", heading)
              << rule('-') << '\n'
              << pad("Конфігурація")
              << std::format("  {:>9} {:>9} {:>9}  {}\n",
                             "typ, мс", "max, мс", "джитер", "пляшкове горло")
              << rule('-') << '\n';

    for (const Track& track : tracks) {
        const Summary b = track.summary();
        const auto worst = bottleneck(track.stages);
        std::cout << pad(track.title)
                  << std::format("  {:>9.2f} {:>9.2f} {:>9.2f}  {}\n",
                                 b.typ.count(), b.max.count(), b.jitter.count(),
                                 worst ? worst->name : std::string_view{"тракт порожній"});
    }
    std::cout << rule('=') << "\n\n";
}

}  // namespace latency::report

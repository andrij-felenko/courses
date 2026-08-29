// Аналізатор перехідної характеристики контуру кутової швидкості.
//
//   analyzer <лог.csv> [поріг_відсічки_В]
//
// Лог — CSV: t_us,setpoint,gyro,d_term,vbat.
// Збірка: c++ -std=c++20 -O2 -o analyzer src/*.cpp

#include "flight_log.hpp"
#include "step_finder.hpp"
#include "step_metrics.hpp"
#include "verdict.hpp"

#include <charconv>
#include <exception>
#include <format>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

void printHeader() {
    std::cout << "\n  №  ампл,°/с   τ,мс  t_нар,мс   M_p,%  t_вст,мс  D-шум  дзвін  примітка\n"
                 "  --------------------------------------------------------------------------\n";
}

void printRow(std::size_t idx, const pid::StepMetrics& m, const pid::StepWindow& w) {
    const std::string rise =
        m.riseTime ? std::format("{:8.1f}", m.riseTime->count()) : std::format("{:>8}", "<90%");
    const std::string noise =
        m.dNoiseRms ? std::format("{:5.1f}", *m.dNoiseRms) : std::format("{:>5}", "н/д");

    std::cout << std::format("  {:2}  {:8.1f}  {:5.1f}  {}  {:6.1f}  {:8.1f}{}  {}  {:5}  {}\n", idx,
                             m.amplitude, m.tau.count(), rise, m.overshootPct, m.settlingTime.count(),
                             m.settled ? ' ' : '+', noise, m.ringCrossings, pid::describe(w.distortion));
}

void printVerdict(const pid::StepMetrics& m, std::size_t used) {
    const auto bands = pid::classify(m);
    const auto advice = pid::adviceFor(pid::judge(m, bands));

    std::cout << std::format("\n  Медіана по {} чистих сходинках:\n", used);
    std::cout << std::format("    затримка τ .......... {:5.1f} мс   ({})\n", m.tau.count(),
                             pid::name(bands.tau));
    if (m.riseTime) {
        std::cout << std::format("    час наростання ...... {:5.1f} мс   ({})\n", m.riseTime->count(),
                                 pid::name(bands.rise));
    } else {
        std::cout << std::format("    час наростання ...... не досягнуто 90% завдання ({})\n",
                                 pid::name(bands.rise));
    }
    std::cout << std::format("    перерегулювання ..... {:5.1f} %    ({})\n", m.overshootPct,
                             pid::name(bands.overshoot));
    std::cout << std::format("    час встановлення .... {:5.1f} мс{}\n", m.settlingTime.count(),
                             m.settled ? "" : "   (у вікно не вклався)");
    if (m.dNoiseRms) {
        std::cout << std::format("    шум D-терма ......... {:5.1f}      ({})\n", *m.dNoiseRms,
                                 pid::name(bands.noise));
    } else {
        std::cout << "    шум D-терма ......... не виміряно: плато закоротке\n";
    }
    std::cout << std::format("    перетинів після піка  {:5}\n", m.ringCrossings);
    std::cout << std::format("\n  ВЕРДИКТ: {}\n  ДІЯ:     {}\n\n", advice.title, advice.action);
}

double parseCutoff(std::string_view text) {
    double value{};
    const auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
    if (ec != std::errc{} || ptr != text.data() + text.size() || value <= 0.0 || value > 60.0) {
        throw std::runtime_error(
            std::format("поріг відсічки «{}» безглуздий: чекали напругу в вольтах", text));
    }
    return value;
}

} // namespace

int main(int argc, char** argv) {
    const std::vector<std::string_view> args(argv, argv + argc);
    if (args.size() < 2 || args.size() > 3) {
        std::cerr << std::format("вжиток: {} <лог.csv> [поріг_відсічки_В]\n",
                                 args.empty() ? "analyzer" : args[0]);
        return 2;
    }

    try {
        pid::DetectConfig cfg;
        if (args.size() == 3) cfg.vbatCutoff = parseCutoff(args[2]);

        const auto log = pid::FlightLog::loadCsv(args[1]);
        const auto period = log.meanPeriod();
        std::cout << std::format("лог «{}»: {} відліків, крок {:.0f} мкс ({:.0f} Гц), поріг АКБ {:.1f} В\n",
                                 args[1], log.size(), period.count(),
                                 period.count() > 0.0 ? 1e6 / period.count() : 0.0, cfg.vbatCutoff);

        const auto search = pid::findSteps(log.samples(), cfg);
        const auto& r = search.rejected;
        std::cout << std::format("фронтів понад поріг: {}; відкинуто — повільних {}, дрібних {}, "
                                 "по неспокійній передісторії {}, без плато {}\n",
                                 r.edges, r.ramp, r.small, r.noisy, r.noPlateau);
        if (search.steps.empty()) {
            std::cout << "придатних сходинок не знайдено: політ або надто плавний, або надто рваний\n";
            return 1;
        }

        printHeader();
        std::vector<pid::StepMetrics> clean;
        std::size_t shown = 0;
        for (const auto& w : search.steps) {
            const auto m = pid::measure(log.samples(), w);
            if (!m) continue;                       // реакції немає — рядок нічого не скаже
            printRow(++shown, *m, w);
            if (w.clean()) clean.push_back(*m);
        }

        if (shown == 0) {
            std::cout << "\n  жодна сходинка не дала вимірної реакції\n\n";
            return 1;
        }
        if (clean.empty()) {
            std::cout << "\n  усі сходинки спотворені кліпінгом або просіданням АКБ:\n"
                         "  вердикту не буде, спершу приберіть причину\n\n";
            return 1;
        }

        printVerdict(pid::median(clean), clean.size());
        return 0;
    } catch (const std::exception& e) {
        std::cerr << std::format("аналіз перервано: {}\n", e.what());
        return 1;
    }
}

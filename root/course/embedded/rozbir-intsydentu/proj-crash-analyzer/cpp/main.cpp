#include "analyzer.hpp"
#include "log_reader.hpp"

#include <format>
#include <iostream>
#include <string>

namespace {

// Коди виходу для конвеєра обробки польотних даних.
constexpr int kExitClean = 0;
constexpr int kExitBadLog = 1;
constexpr int kExitUsage = 2;
constexpr int kExitFault = 3;

void print_mark(std::string_view label, std::optional<std::uint64_t> us)
{
    if (us) {
        std::cout << std::format("  {} T = {:.6f} с\n", label,
                                 static_cast<double>(*us) / 1e6);
    }
}

void print_report(const postmortem::Report& r)
{
    std::cout << std::format("Кадрів прийнято: {}, відкинуто: {}\n", r.frames_used,
                             r.frames_skipped);
    std::cout << std::format("Сигнатура: {}\n", postmortem::to_string(r.fault));
    if (r.fault != postmortem::Fault::None) {
        std::cout << std::format("Мітка: T = {:.6f} с ({} мкс)\n",
                                 static_cast<double>(r.timestamp_us) / 1e6,
                                 r.timestamp_us);
        std::cout << std::format("Впевненість: {:.2f}\n", r.confidence);
    }
    std::cout << std::format("Висновок: {}\n", r.description);

    if (r.impact_us || r.environment_us || r.depletion_us) {
        std::cout << "Контекст (події, відкинуті як не-першопричина):\n";
        print_mark("зіткнення, сплеск гіроскопа випередив мотори:", r.impact_us);
        print_mark("магнітна аномалія середовища без власного струму:", r.environment_us);
        print_mark("плавне вичерпання заряду батареї:", r.depletion_us);
    }
}

} // namespace

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::cerr << std::format(
            "Виклик: {} <журнал.csv>\n"
            "CSV — розпакований ULog/DataFlash із шапкою імен колонок.\n",
            argv[0]);
        return kExitUsage;
    }

    const auto log = postmortem::read_csv(argv[1]);
    if (!log) {
        const auto& e = log.error();
        if (e.line > 0) {
            std::cerr << std::format("Журнал {}, рядок {}: {}\n", argv[1], e.line,
                                     e.message);
        } else {
            std::cerr << std::format("Журнал {}: {}\n", argv[1], e.message);
        }
        return kExitBadLog;
    }

    const postmortem::Report report = postmortem::analyze_incident(*log);
    print_report(report);

    return report.fault == postmortem::Fault::None ? kExitClean : kExitFault;
}

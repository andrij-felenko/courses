#include <chrono>
#include <cstdint>
#include <format>
#include <fstream>
#include <iostream>
#include <span>
#include <string_view>

#include "analyzer.hpp"
#include "production_log.hpp"

namespace {

using genealogy::Board;
using genealogy::FeederWindow;
using genealogy::ProductionLog;
using genealogy::Timestamp;

constexpr int kMinGroup = 30;                    // менші групи статистики не витримують
constexpr std::string_view kQuarantinePath = "quarantine.csv";

// --------------------- синтетичний випуск для показу ----------------------

constexpr int kDemoBoards = 20000;
constexpr std::chrono::seconds kTakt{10};        // такт наскрізного потоку
constexpr Timestamp kStart{std::chrono::seconds{1772409600}};   // 2026-03-02 00:00 UTC

class Lcg {
public:
    double next() noexcept {
        state_ = state_ * 6364136223846793005ULL + 1442695040888963407ULL;
        return static_cast<double>((state_ >> 33) & 0x7FFFFFFFu) / 2147483648.0;
    }

private:
    std::uint64_t state_{20260302ULL};
};

Timestamp board_time(int index) { return kStart + kTakt * index; }

ProductionLog synthetic_run() {
    ProductionLog log;

    const auto end = board_time(kDemoBoards);
    const auto mcu_switch = board_time(10000);
    const auto bad_from = board_time(14000);
    const auto bad_to = board_time(15000);

    for (const std::string line : {"Line-1", "Line-2"}) {
        log.add_feeder({line, "U1", "R-501", "L-7001", "DC2130", kStart, mcu_switch, false});
        log.add_feeder({line, "U1", "R-502", "L-7002", "DC2134", mcu_switch, end, false});
        log.add_feeder({line, "U4", "R-101", "L-2201", "DC2129", kStart, bad_to, false});
        log.add_feeder({line, "U4", "R-102", "L-2202", "DC2133", bad_to, end, false});
        // Обидва стики котушок C12 зроблені склейкою стрічок на ходу.
        log.add_feeder({line, "C12", "R-901", "L-4410", "DC2125", kStart, bad_from, true});
        log.add_feeder({line, "C12", "R-902", "L-8921", "DC2133", bad_from, bad_to, true});
        log.add_feeder({line, "C12", "R-903", "L-4410", "DC2126", bad_to, end, false});
    }

    Lcg rng;
    for (int i = 0; i < kDemoBoards; ++i) {
        Board board;
        board.serial = std::format("SN{:05d}", i + 1);
        board.scanned = board_time(i);

        const bool in_bad_lot = i >= 14000 && i < 15000;
        // Дефектну котушку доїдали переважно на другій лінії — саме звідси
        // береться хибна кореляція «винна Line-2».
        board.line = rng.next() < (in_bad_lot ? 0.85 : 0.5) ? "Line-2" : "Line-1";
        board.reflow_profile = i < 12000 ? "P-7" : "P-9";

        board.failed = rng.next() < (in_bad_lot ? 0.040 : 0.0002);
        board.ttf_hours = board.failed ? 200.0 + rng.next() * 900.0 : 0.0;
        log.add_board(std::move(board));
    }
    return log;
}

void usage(std::string_view argv0) {
    std::cerr << std::format(
        "Використання:\n"
        "  {0} <mes.csv> <feeders.csv> <returns.csv>\n"
        "  {0} --demo\n\n"
        "  mes.csv      serial,smt_line,reflow_profile,scan_epoch\n"
        "  feeders.csv  smt_line,designator,reel_uid,lot_code,date_code,"
        "from_epoch,to_epoch,spliced\n"
        "  returns.csv  serial,ttf_hours,symptom\n",
        argv0);
}

int export_quarantine(const genealogy::Analyzer& analyzer, const genealogy::Finding& guilty,
                      std::ostream& log) {
    const auto entries = analyzer.quarantine(guilty);

    std::ofstream out{std::string{kQuarantinePath}};
    if (!out) {
        std::cerr << std::format("Не вдалося відкрити {} на запис\n", kQuarantinePath);
        return 1;
    }
    out << "serial,factor,confidence\n";
    std::size_t splice_zone = 0;
    for (const auto& entry : entries) {
        out << std::format("{},{},{}\n", entry.serial, guilty.factor,
                           entry.exact ? "exact" : "splice-zone");
        if (!entry.exact) ++splice_zone;
    }
    out.flush();
    if (!out) {
        std::cerr << std::format("Помилка запису {}\n", kQuarantinePath);
        return 1;
    }

    log << std::format("\n[КАРАНТИН] фактор {}\n", guilty.factor);
    log << std::format("  плат до вилучення: {} (з них {} із зони склейки стрічок)\n",
                       entries.size(), splice_zone);
    if (!entries.empty())
        log << std::format("  діапазон серійних номерів: {} .. {}\n",
                           entries.front().serial, entries.back().serial);
    log << std::format("  список збережено у {}\n", kQuarantinePath);
    return 0;
}

}  // namespace

int main(int argc, char** argv) try {
    const std::span<char*> args{argv, static_cast<std::size_t>(argc)};
    std::cout << "=== Аналізатор виробничої генеалогії PCBA ===\n";

    ProductionLog log;
    if (args.size() == 2 && std::string_view{args[1]} == "--demo") {
        std::cout << std::format("Джерело: синтетичний випуск на {} плат\n", kDemoBoards);
        log = synthetic_run();
    } else if (args.size() == 4) {
        log = ProductionLog::load(args[1], args[2], args[3]);
    } else {
        usage(args.empty() ? "analyzer" : args[0]);
        return 1;
    }

    if (log.boards().empty()) {
        std::cerr << "Журнал MES порожній — немає чого зіставляти\n";
        return 1;
    }
    if (log.feeder_count() == 0)
        std::cerr << "Попередження: логи живильників порожні, лишаються лише "
                     "фактори рівня плати\n";

    log.join();

    const genealogy::Analyzer analyzer{log.boards()};
    auto findings = analyzer.scan(kMinGroup);
    analyzer.check_confounders(findings, 0.05);
    genealogy::print_report(log.boards(), findings, 8, std::cout);

    const auto* guilty = analyzer.root_cause(findings, 1e-5, 10.0);
    if (guilty == nullptr) {
        std::cout << "\nЖоден фактор не перетнув поріг карантину (q<1e-5, OR>10).\n";
        return 0;
    }
    if (export_quarantine(analyzer, *guilty, std::cout) != 0) return 1;

    return 2;   // код 2 — гачок для нічного сервісу: відкрити аварійний тікет
} catch (const std::exception& e) {
    std::cerr << std::format("Помилка: {}\n", e.what());
    return 1;
}

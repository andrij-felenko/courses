#include <format>
#include <fstream>
#include <iostream>
#include <istream>
#include <string>
#include <string_view>
#include <vector>

#include "checks.hpp"
#include "snapshot.hpp"

namespace {

constexpr std::string_view RULE = "==========================================";

void print_report(const Verdict& verdict, std::ostream& out)
{
    out << RULE << '\n'
        << std::format(">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ {} ] <<<\n",
                       verdict.is_go() ? "GO" : "NO-GO");

    for (const auto& barrier : verdict.barriers()) {
        out << std::format("  [{}] {}\n", barrier.passed() ? " OK " : "FAIL", barrier.name);
        for (const auto& finding : barrier.findings) {
            out << std::format("        [!] {}\n", finding);
        }
    }

    if (verdict.is_go()) {
        out << "Усі шість бар'єрів пройдено. Дозвіл на ARM надано.\n";
    } else {
        out << std::format("Виявлено критичних блокувань: {}. Старт заборонено до усунення!\n",
                           verdict.finding_count());
    }
    out << RULE << '\n';
}

} // namespace

// Коди повернення — на них спирається пусковий скрипт польотної групи:
//   0 — GO, дозвіл на ARM;
//   1 — NO-GO, є щонайменше одне блокування;
//   2 — зліпок непридатний, вердикту немає взагалі.
// Третій код окремий навмисно: «не зміг перевірити» — це не «перевірив і
// дозволив», і плутати їх у скрипті означає злетіти наосліп.
int main(int argc, char** argv)
{
    const std::vector<std::string_view> args(argv + 1, argv + argc);
    if (args.size() > 1) {
        std::cerr << std::format("вжиток: {} [зліпок-телеметрії.txt]\n", argv[0]);
        return 2;
    }

    std::ifstream file;
    std::istream* in = &std::cin;
    if (args.size() == 1 && args.front() != "-") {
        file.open(std::string{args.front()});
        if (!file) {
            std::cerr << std::format("не вдалося відкрити «{}»\n", args.front());
            return 2;
        }
        in = &file;
    }

    const auto snapshot = parse_snapshot(*in);
    if (!snapshot) {
        std::cerr << std::format("зліпок телеметрії непридатний: {}\n", snapshot.error());
        std::cerr << "вердикт не винесено — армінг заборонено\n";
        return 2;
    }

    const Verdict verdict = evaluate(*snapshot);
    print_report(verdict, std::cout);

    return verdict.is_go() ? 0 : 1;
}

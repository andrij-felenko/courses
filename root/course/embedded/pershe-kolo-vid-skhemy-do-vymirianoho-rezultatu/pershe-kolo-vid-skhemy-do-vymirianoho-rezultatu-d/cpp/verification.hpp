#pragma once

#include <cstddef>
#include <iosfwd>
#include <string>
#include <string_view>
#include <vector>

// Протокол верифікації: судження про виміряне й таблиця для журналу.
namespace bench {

enum class Verdict {
    Pass = 0,  // у межах допуску
    Warn,      // пояснюється похибкою навантаження, потребує корекції
    Fail       // дефект
};

[[nodiscard]] std::string_view to_string(Verdict v) noexcept;

// Статус рядка за відносною похибкою й допуском рядка.
[[nodiscard]] Verdict verdict_of(double calc, double meas, double tol_pct) noexcept;

// «Золоте правило» вимірювання: R_m >= 100 * R_th.
[[nodiscard]] Verdict rule_of_hundred(double ratio) noexcept;

// Норми клем макетки: 0.05–0.3 Ом на новій платі, понад 0.5 Ом — брак.
[[nodiscard]] Verdict contact_verdict(double r_per_contact) noexcept;

// Вирівнювання написів: ширина поля у std::format рахується в БАЙТАХ,
// а українська літера в UTF-8 займає два — колонки б поїхали.
[[nodiscard]] std::string align_left(std::string_view s, std::size_t width);
[[nodiscard]] std::string align_right(std::string_view s, std::size_t width);

// Таблиця статичних параметрів (DC Table) інженерного журналу.
class VerificationLog {
public:
    void add(std::string_view name, std::string_view unit,
             double calc, double meas, double tol_pct);

    void note(Verdict v) noexcept;  // вердикт поза таблицею (контакти, монтаж)

    [[nodiscard]] Verdict overall() const noexcept;

    void render(std::ostream& os) const;

private:
    struct Row {
        std::string name;
        std::string unit;
        double calc{};
        double meas{};
        double tol_pct{};
    };

    std::vector<Row> rows_;
    Verdict extra_{Verdict::Pass};
};

}  // namespace bench

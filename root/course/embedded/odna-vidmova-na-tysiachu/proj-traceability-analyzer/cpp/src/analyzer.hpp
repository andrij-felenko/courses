#pragma once

#include <array>
#include <iosfwd>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include "production_log.hpp"
#include "statistics.hpp"

namespace genealogy {

// Один перевірений фактор: "C12.Lot=L-8921", "SMT_Line=Line-2", "Reflow=P-9".
struct Finding {
    std::string factor;
    stats::Table table;
    int unknown{0};              // плати зі стику котушок, виключені з таблиці
    stats::Effect effect;
    double p_value{1.0};
    double p_adj{1.0};

    std::string stratified_by;
    std::optional<stats::Stratified> stratified;
    bool confounded{false};      // сигнал зникає всередині страт
};

struct QuarantineEntry {
    std::string serial;
    bool exact{true};            // false — плата зі зони склейки стрічок
};

class Analyzer {
public:
    explicit Analyzer(std::span<const Board> boards) noexcept : boards_{boards} {}

    [[nodiscard]] std::vector<Finding> scan(int min_group) const;

    // Розділення спарених факторів за критерієм Мантеля — Гензеля.
    void check_confounders(std::vector<Finding>& findings, double alpha) const;

    [[nodiscard]] const Finding* root_cause(const std::vector<Finding>& findings,
                                            double max_p, double min_or) const;

    [[nodiscard]] std::vector<QuarantineEntry> quarantine(const Finding& guilty) const;

private:
    [[nodiscard]] std::array<stats::Table, 2> strata_tables(std::string_view factor,
                                                            std::string_view stratum) const;
    void stratify(Finding& finding, std::string_view stratum) const;

    std::span<const Board> boards_;
};

void print_report(std::span<const Board> boards, std::span<const Finding> findings,
                  std::size_t top, std::ostream& os);

}  // namespace genealogy

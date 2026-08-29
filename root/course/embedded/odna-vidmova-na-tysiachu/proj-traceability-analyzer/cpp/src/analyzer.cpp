#include "analyzer.hpp"

#include <algorithm>
#include <cmath>
#include <format>
#include <ostream>
#include <ranges>
#include <unordered_map>

namespace genealogy {
namespace {

struct KeyRef {
    std::string key;
    bool uncertain;
};

std::vector<KeyRef> board_keys(const Board& b) {
    std::vector<KeyRef> keys;
    keys.reserve(2 + b.parts.size() * 3);
    keys.push_back({std::format("SMT_Line={}", b.line), false});
    keys.push_back({std::format("Reflow={}", b.reflow_profile), false});
    for (const auto& p : b.parts) {
        keys.push_back({std::format("{}.Lot={}", p.designator, p.lot_code), p.uncertain});
        keys.push_back({std::format("{}.DateCode={}", p.designator, p.date_code), p.uncertain});
        keys.push_back({std::format("{}.Reel={}", p.designator, p.reel_uid), p.uncertain});
    }
    return keys;
}

// Витягує десігнатор із ключа "C12.Lot=L-8921"; для факторів рівня плати — порожньо.
std::string_view key_designator(std::string_view key) {
    const auto dot = key.find('.');
    const auto eq = key.find('=');
    if (dot == std::string_view::npos || (eq != std::string_view::npos && dot > eq)) return {};
    return key.substr(0, dot);
}

struct Membership {
    bool present{false};
    bool uncertain{false};
};

// Викликається лише для кількох кандидатів, тому перебудова ключів тут не дорога.
Membership membership(const Board& b, std::string_view key) {
    Membership m;
    if (const auto designator = key_designator(key); !designator.empty()) {
        const auto* part = b.part(designator);
        m.uncertain = part != nullptr && part->uncertain;
    }
    for (const auto& k : board_keys(b))
        if (k.key == key) { m.present = true; break; }
    return m;
}

std::string ratio_text(double value) {
    if (std::isnan(value)) return "-";
    if (std::isinf(value)) return "inf";
    return std::format("{:.1f}", value);
}

}  // namespace

std::vector<Finding> Analyzer::scan(int min_group) const {
    struct Counts { int a{}, b{}, ua{}, ub{}; };
    std::unordered_map<std::string, Counts> cells;

    int failed_total = 0, ok_total = 0;
    for (const auto& board : boards_) {
        (board.failed ? failed_total : ok_total)++;
        for (auto& key : board_keys(board)) {
            auto& cell = cells[std::move(key.key)];
            if (key.uncertain) (board.failed ? cell.ua : cell.ub)++;
            else               (board.failed ? cell.a : cell.b)++;
        }
    }

    std::vector<Finding> findings;
    for (const auto& [key, counts] : cells) {
        const int group = counts.a + counts.b;
        const int c = failed_total - counts.a - counts.ua;
        const int d = ok_total - counts.b - counts.ub;
        if (group < min_group || c < 0 || d < 0 || c + d < min_group) continue;

        Finding f;
        f.factor = key;
        f.table = stats::Table{counts.a, counts.b, c, d};
        f.unknown = counts.ua + counts.ub;
        f.effect = stats::effect_size(f.table);
        f.p_value = stats::fisher_exact(f.table);
        findings.push_back(std::move(f));
    }

    // Чим більше факторів перевірено, тим легше натрапити на випадковий сплеск.
    std::vector<double> raw;
    raw.reserve(findings.size());
    for (const auto& f : findings) raw.push_back(f.p_value);
    const auto adjusted = stats::benjamini_hochberg(raw);
    for (std::size_t i = 0; i < findings.size(); ++i) findings[i].p_adj = adjusted[i];

    std::ranges::sort(findings, [](const Finding& x, const Finding& y) {
        if (x.p_adj != y.p_adj) return x.p_adj < y.p_adj;
        if (x.effect.odds_ratio != y.effect.odds_ratio)
            return x.effect.odds_ratio > y.effect.odds_ratio;
        return x.factor < y.factor;
    });
    return findings;
}

std::array<stats::Table, 2> Analyzer::strata_tables(std::string_view factor,
                                                    std::string_view stratum) const {
    std::array<stats::Table, 2> tables{};
    for (const auto& board : boards_) {
        const auto f = membership(board, factor);
        if (f.uncertain) continue;               // непевні плати в таблицю не йдуть
        const auto s = membership(board, stratum);
        if (s.uncertain) continue;

        auto& t = tables[s.present ? 0 : 1];
        if (f.present && board.failed) ++t.a;
        else if (f.present)            ++t.b;
        else if (board.failed)         ++t.c;
        else                           ++t.d;
    }
    return tables;
}

void Analyzer::stratify(Finding& finding, std::string_view stratum) const {
    if (finding.factor == stratum) return;

    const auto tables = strata_tables(finding.factor, stratum);
    const auto mh = stats::mantel_haenszel(tables);

    finding.stratified_by = std::string{stratum};
    finding.stratified = mh;
    if (mh.strata < 2) return;                   // фактори збіглися — судити нема з чого

    // Сигнал, що зникає всередині страт, породжений не цим фактором.
    finding.confounded = mh.p_value > 0.01 ||
                         (finding.effect.odds_ratio > 3.0 &&
                          mh.odds_ratio < finding.effect.odds_ratio / 3.0);
}

void Analyzer::check_confounders(std::vector<Finding>& findings, double alpha) const {
    if (findings.size() < 2) return;

    // Решту факторів стратифікуємо за найсильнішим сигналом.
    const std::string leader = findings.front().factor;
    for (auto& f : findings | std::views::drop(1)) {
        if (f.p_adj > alpha) continue;
        stratify(f, leader);
    }
    // Самого лідера перевіряємо першим фактором, що дає дві змістовні страти.
    for (const auto& other : findings | std::views::drop(1)) {
        const std::string candidate = other.factor;
        stratify(findings.front(), candidate);
        const auto& mh = findings.front().stratified;
        if (mh && mh->strata >= 2) break;
        findings.front().stratified_by.clear();
        findings.front().stratified.reset();
    }
}

const Finding* Analyzer::root_cause(const std::vector<Finding>& findings,
                                    double max_p, double min_or) const {
    for (const auto& f : findings) {
        if (f.confounded) continue;
        if (f.p_adj < max_p && f.effect.odds_ratio > min_or) return &f;
    }
    return nullptr;
}

std::vector<QuarantineEntry> Analyzer::quarantine(const Finding& guilty) const {
    const auto designator = key_designator(guilty.factor);
    std::vector<QuarantineEntry> quarantined;

    for (const auto& board : boards_) {
        const auto m = membership(board, guilty.factor);
        // Плати зі стику котушок беремо теж: їхнє походження ми не знаємо,
        // а помилитися дешевше в бік карантину.
        if (!m.present && !(m.uncertain && !designator.empty())) continue;
        quarantined.push_back({board.serial, !m.uncertain});
    }
    std::ranges::sort(quarantined, {}, &QuarantineEntry::serial);
    return quarantined;
}

void print_report(std::span<const Board> boards, std::span<const Finding> findings,
                  std::size_t top, std::ostream& os) {
    const auto failed = std::ranges::count(boards, true, &Board::failed);
    const double rate = boards.empty()
                            ? 0.0
                            : 100.0 * static_cast<double>(failed) / static_cast<double>(boards.size());

    os << std::format("\nПлат у випуску: {}, польових відмов: {} ({:.3f}%)\n",
                      boards.size(), failed, rate);
    os << std::format("Перевірено факторів: {}\n\n", findings.size());
    os << std::format("{:<26} {:>5} {:>6} {:>5} {:>6} {:>9} {:>9} {:>9} {:>11}\n",
                      "фактор", "a", "b", "c", "d", "брак%", "фон%", "OR", "q(BH)");

    for (const auto& f : findings | std::views::take(top)) {
        const auto& t = f.table;
        const double in_group = (t.a + t.b) ? 100.0 * t.a / static_cast<double>(t.a + t.b) : 0.0;
        const double control = (t.c + t.d) ? 100.0 * t.c / static_cast<double>(t.c + t.d) : 0.0;

        os << std::format("{:<26} {:>5} {:>6} {:>5} {:>6} {:>8.3f}% {:>8.4f}% {:>9} {:>11.2e}\n",
                          f.factor, t.a, t.b, t.c, t.d, in_group, control,
                          ratio_text(f.effect.odds_ratio), f.p_adj);
        os << std::format("    95% CI [{:.1f} .. {:.1f}]{}, точний тест Фішера p={:.2e}",
                          f.effect.ci_low, f.effect.ci_high,
                          f.effect.haldane ? " (Холдейн-Енскомб)" : "", f.p_value);
        if (f.unknown > 0)
            os << std::format(", непевних плат зі стику котушок: {}", f.unknown);
        os << '\n';

        if (!f.stratified_by.empty() && f.stratified) {
            if (f.stratified->strata < 2) {
                os << std::format("    стратифікація за [{}] неможлива: фактори збігаються\n",
                                  f.stratified_by);
            } else {
                os << std::format("    Мантель-Гензель за [{}]: OR={} p={:.2e} -> {}\n",
                                  f.stratified_by, ratio_text(f.stratified->odds_ratio),
                                  f.stratified->p_value,
                                  f.confounded ? "спарений фактор, власного внеску немає"
                                               : "фактор витримує стратифікацію");
            }
        }
    }
}

}  // namespace genealogy

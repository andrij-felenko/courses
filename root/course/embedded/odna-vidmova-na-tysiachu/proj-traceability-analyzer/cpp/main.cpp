#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <cmath>
#include <iomanip>
#include <format>
#include <optional>
#include <span>

struct BoardRecord {
    std::string serial;
    std::string smt_line;
    std::string mcu_datecode;
    std::string ldo_reel;
    std::string mlcc_lot;
    bool is_failed{false};
};

struct ContingencyStats {
    int a{0}; // фактор є + відмова
    int b{0}; // фактор є + справний
    int c{0}; // фактора нема + відмова
    int d{0}; // фактора нема + справний
    double odds_ratio{0.0};
    double ci_low{0.0};
    double ci_high{0.0};
    double p_value{1.0};
};

class TraceabilityAnalyzer {
public:
    static double log_factorial(int n) noexcept {
        return std::lgamma(static_cast<double>(n + 1));
    }

    static double calculate_fisher_p_value(int a, int b, int c, int d) noexcept {
        const int n1 = a + b;
        const int n0 = c + d;
        const int m1 = a + c;
        const int m0 = b + d;
        const int total = n1 + n0;

        const double log_hyper_denom = log_factorial(n1) + log_factorial(n0) +
                                      log_factorial(m1) + log_factorial(m0) -
                                      log_factorial(total);

        const double log_p_obs = log_hyper_denom - (log_factorial(a) + log_factorial(b) +
                                                   log_factorial(c) + log_factorial(d));
        const double p_obs = std::exp(log_p_obs);

        const int min_a = std::max(0, m1 - n0);
        const int max_a = std::min(n1, m1);

        double p_total = 0.0;
        for (int x = min_a; x <= max_a; ++x) {
            const int cur_b = n1 - x;
            const int cur_c = m1 - x;
            const int cur_d = n0 - cur_c;

            const double log_p_cur = log_hyper_denom - (log_factorial(x) + log_factorial(cur_b) +
                                                       log_factorial(cur_c) + log_factorial(cur_d));
            const double p_cur = std::exp(log_p_cur);

            if (p_cur <= p_obs * (1.0 + 1e-9)) {
                p_total += p_cur;
            }
        }
        return std::min(1.0, p_total);
    }

    static ContingencyStats analyze_attribute(std::span<const BoardRecord> dataset,
                                             auto attribute_selector,
                                             std::string_view target_value) {
        ContingencyStats stats;

        for (const auto& record : dataset) {
            const bool match = (attribute_selector(record) == target_value);
            if (match && record.is_failed) ++stats.a;
            else if (match && !record.is_failed) ++stats.b;
            else if (!match && record.is_failed) ++stats.c;
            else if (!match && !record.is_failed) ++stats.d;
        }

        double a = stats.a, b = stats.b, c = stats.c, d = stats.d;
        if (a == 0 || b == 0 || c == 0 || d == 0) {
            a += 0.5; b += 0.5; c += 0.5; d += 0.5;
        }

        stats.odds_ratio = (a * d) / (b * c);
        const double se_ln_or = std::sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d);
        const double ln_or = std::log(stats.odds_ratio);

        stats.ci_low = std::exp(ln_or - 1.96 * se_ln_or);
        stats.ci_high = std::exp(ln_or + 1.96 * se_ln_or);
        stats.p_value = calculate_fisher_p_value(stats.a, stats.b, stats.c, stats.d);

        return stats;
    }
};

int main() {
    std::cout << "=== Аналізатор виробничої генеалогії PCBA (C++20) ===\n\n";

    constexpr int kTotalBoards = 20000;
    std::vector<BoardRecord> records;
    records.reserve(kTotalBoards);

    for (int i = 0; i < kTotalBoards; ++i) {
        BoardRecord rec{
            .serial = std::format("SN{:05d}", i + 1),
            .smt_line = (i % 2 == 0) ? "Line-1" : "Line-2",
            .mcu_datecode = (i < 10000) ? "DC2130" : "DC2134",
            .ldo_reel = (i < 15000) ? "R-101" : "R-102",
            .mlcc_lot = (i >= 14000 && i < 15000) ? "L-8921" : "L-4410",
            .is_failed = false
        };

        if (i >= 14000 && i < 15000) {
            rec.is_failed = (i % 55 == 0 && i < 14990); // 18 відмов
        } else {
            rec.is_failed = (i == 2500 || i == 8700);    // 2 відмови
        }
        records.push_back(std::move(rec));
    }

    const auto stats = TraceabilityAnalyzer::analyze_attribute(
        records,
        [](const BoardRecord& r) noexcept -> std::string_view { return r.mlcc_lot; },
        "L-8921"
    );

    std::cout << std::format("Результати аналізу для [MLCC Lot = L-8921]:\n");
    std::cout << std::format("  Клітинки таблиці 2x2: a={}, b={}, c={}, d={}\n",
                             stats.a, stats.b, stats.c, stats.d);
    std::cout << std::format("  Частота відмов у партії:   {:.3f}%\n",
                             (static_cast<double>(stats.a) / (stats.a + stats.b)) * 100.0);
    std::cout << std::format("  Частота відмов у контролі: {:.4f}%\n",
                             (static_cast<double>(stats.c) / (stats.c + stats.d)) * 100.0);
    std::cout << std::format("  Відношення шансів (OR):   {:.2f} (95% CI: [{:.2f} .. {:.2f}])\n",
                             stats.odds_ratio, stats.ci_low, stats.ci_high);
    std::cout << std::format("  Критерій Фішера (p-value): {:.4e}\n\n", stats.p_value);

    if (stats.p_value < 1e-5 && stats.odds_ratio > 10.0) {
        std::cout << "[УВАГА] Виявлено статистично значущий виробничий дефект!\n";
        std::cout << "Діапазон серійних номерів для карантину: SN14001 .. SN15000 (1000 плат)\n";
    }

    return 0;
}

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <cmath>
#include <algorithm>
#include <optional>
#include <span>

struct FpvChannel {
    std::string_view band;
    int channel;
    int freq_mhz;

    [[nodiscard]] std::string format() const {
        return std::string(band) + std::to_string(channel) + " (" + std::to_string(freq_mhz) + " МГц)";
    }
};

/* Глобальна база стандартних каналів 5.8 ГГц */
inline constexpr std::array<FpvChannel, 48> ALL_CHANNELS = {{
    {"A", 1, 5865}, {"A", 2, 5845}, {"A", 3, 5825}, {"A", 4, 5805},
    {"A", 5, 5785}, {"A", 6, 5765}, {"A", 7, 5745}, {"A", 8, 5725},
    {"B", 1, 5733}, {"B", 2, 5752}, {"B", 3, 5771}, {"B", 4, 5790},
    {"B", 5, 5809}, {"B", 6, 5828}, {"B", 7, 5847}, {"B", 8, 5866},
    {"E", 1, 5705}, {"E", 2, 5685}, {"E", 3, 5665}, {"E", 4, 5645},
    {"E", 5, 5885}, {"E", 6, 5905}, {"E", 7, 5925}, {"E", 8, 5945},
    {"F", 1, 5740}, {"F", 2, 5760}, {"F", 3, 5780}, {"F", 4, 5800},
    {"F", 5, 5820}, {"F", 6, 5840}, {"F", 7, 5860}, {"F", 8, 5880},
    {"R", 1, 5658}, {"R", 2, 5695}, {"R", 3, 5732}, {"R", 4, 5769},
    {"R", 5, 5806}, {"R", 6, 5843}, {"R", 7, 5880}, {"R", 8, 5917},
    {"L", 1, 5362}, {"L", 2, 5399}, {"L", 3, 5436}, {"L", 4, 5473},
    {"L", 5, 5510}, {"L", 6, 5547}, {"L", 7, 5584}, {"L", 8, 5621}
}};

struct ConflictSummary {
    int co_channel_count = 0;
    int adjacent_count = 0;
    int imd3_2tone_count = 0;
    int imd3_3tone_count = 0;
    int min_spacing_mhz = 9999;

    [[nodiscard]] bool is_clean() const noexcept {
        return co_channel_count == 0 && adjacent_count == 0 &&
               imd3_2tone_count == 0 && imd3_3tone_count == 0;
    }
};

class FrequencyPlanner {
public:
    static ConflictSummary evaluate(std::span<const FpvChannel> plan,
                                    int min_adjacent_mhz = 25,
                                    int imd_guard_mhz = 10,
                                    bool verbose = true) {
        ConflictSummary summary;
        const size_t n = plan.size();

        /* 1. Аналіз попарного рознесення */
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                const int diff = std::abs(plan[i].freq_mhz - plan[j].freq_mhz);
                summary.min_spacing_mhz = std::min(summary.min_spacing_mhz, diff);

                if (diff == 0) {
                    summary.co_channel_count++;
                    if (verbose) {
                        std::cout << "  [КОЛІЗІЯ] Прямий збіг: " << plan[i].format()
                                  << " та " << plan[j].format() << "\n";
                    }
                } else if (diff < min_adjacent_mhz) {
                    summary.adjacent_count++;
                    if (verbose) {
                        std::cout << "  [УВАГА] Недостатній інтервал: " << plan[i].format()
                                  << " та " << plan[j].format() << " (Δf = " << diff << " МГц)\n";
                    }
                }
            }
        }

        /* 2. Аналіз 2-тонового IMD3 */
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                if (i == j) continue;
                const int f_imd = 2 * plan[i].freq_mhz - plan[j].freq_mhz;
                for (size_t k = 0; k < n; ++k) {
                    if (k == i || k == j) continue;
                    const int diff = std::abs(f_imd - plan[k].freq_mhz);
                    if (diff < imd_guard_mhz) {
                        summary.imd3_2tone_count++;
                        if (verbose) {
                            std::cout << "  [IMD3 2-Tone] 2·" << plan[i].format() << " − "
                                      << plan[j].format() << " = " << f_imd << " МГц б'є в "
                                      << plan[k].format() << " (похибка " << diff << " МГц)\n";
                        }
                    }
                }
            }
        }

        /* 3. Аналіз 3-тонового IMD3 */
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                for (size_t k = 0; k < n; ++k) {
                    if (k == i || k == j) continue;
                    const int f_triple = plan[i].freq_mhz + plan[j].freq_mhz - plan[k].freq_mhz;
                    for (size_t m = 0; m < n; ++m) {
                        if (m == i || m == j || m == k) continue;
                        const int diff = std::abs(f_triple - plan[m].freq_mhz);
                        if (diff < imd_guard_mhz) {
                            summary.imd3_3tone_count++;
                            if (verbose) {
                                std::cout << "  [IMD3 3-Tone] " << plan[i].format() << " + "
                                          << plan[j].format() << " − " << plan[k].format()
                                          << " = " << f_triple << " МГц б'є в "
                                          << plan[m].format() << " (похибка " << diff << " МГц)\n";
                            }
                        }
                    }
                }
            }
        }

        return summary;
    }

    /* Пошук оптимального безконфліктного набору для N пілотів */
    static std::optional<std::vector<FpvChannel>> find_best_allocation(
            std::span<const FpvChannel> pool,
            size_t target_pilots,
            int min_adjacent_mhz = 30,
            int imd_guard_mhz = 12) {
        
        std::vector<FpvChannel> current;
        std::vector<FpvChannel> best_result;
        int best_spacing = 0;

        auto backtrack = [&](auto& self, size_t start_idx) -> void {
            if (current.size() == target_pilots) {
                auto report = evaluate(current, min_adjacent_mhz, imd_guard_mhz, false);
                if (report.is_clean() && report.min_spacing_mhz > best_spacing) {
                    best_spacing = report.min_spacing_mhz;
                    best_result = current;
                }
                return;
            }

            for (size_t i = start_idx; i < pool.size(); ++i) {
                current.push_back(pool[i]);
                self(self, i + 1);
                current.pop_back();
            }
        };

        backtrack(backtrack, 0);

        if (!best_result.empty()) {
            return best_result;
        }
        return std::nullopt;
    }
};

int main() {
    std::cout << "=== АНАЛІЗ ТА ОПТИМІЗАЦІЯ ЧАСТОТ FPV 5.8 ГГц (C++20) ===\n\n";

    // Тест 1: Конфліктна конфігурація
    const std::array<FpvChannel, 4> bad_setup = {{
        ALL_CHANNELS[24], // F1: 5740
        ALL_CHANNELS[25], // F2: 5760
        ALL_CHANNELS[26], // F3: 5780
        ALL_CHANNELS[27]  // F4: 5800
    }};

    std::cout << "1. Перевірка сітки Band F (20 МГц крок):\n";
    auto rep1 = FrequencyPlanner::evaluate(bad_setup, 25, 10, true);
    std::cout << "Чиста сітка: " << (rep1.is_clean() ? "ТАК" : "НІ")
              << " | Мінімальний крок: " << rep1.min_spacing_mhz << " МГц\n\n";

    // Тест 2: Оптимізована 4-канальна сітка Raceband
    const std::array<FpvChannel, 4> race_setup = {{
        ALL_CHANNELS[32], // R1: 5658
        ALL_CHANNELS[33], // R2: 5695
        ALL_CHANNELS[35], // R4: 5769
        ALL_CHANNELS[38]  // R7: 5880
    }};

    std::cout << "2. Перевірка сітки Raceband (R1, R2, R4, R7):\n";
    auto rep2 = FrequencyPlanner::evaluate(race_setup, 25, 10, true);
    std::cout << "Чиста сітка: " << (rep2.is_clean() ? "ТАК" : "НІ")
              << " | Мінімальний крок: " << rep2.min_spacing_mhz << " МГц\n\n";

    // Тест 3: Автоматичний пошук найкращої сітки для 6 пілотів
    std::cout << "3. Пошук оптимального розподілу для 6 пілотів серед Raceband:\n";
    std::span<const FpvChannel> race_pool(&ALL_CHANNELS[32], 8);
    auto opt6 = FrequencyPlanner::find_best_allocation(race_pool, 6, 25, 8);
    if (opt6) {
        std::cout << "Знайдено оптимальну конфігурацію:\n";
        for (const auto& ch : *opt6) {
            std::cout << "  - " << ch.format() << "\n";
        }
    } else {
        std::cout << "Для 6 пілотів у межах лише Raceband повністю чистої сітки без IMD3 не існує!\n"
                  << "Необхідно задіяти просторову розв'язку антенами RHCP/LHCP.\n";
    }

    return 0;
}

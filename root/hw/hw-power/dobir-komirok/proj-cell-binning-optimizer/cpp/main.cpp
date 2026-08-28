#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <iomanip>
#include <cstdint>
#include <cmath>
#include <span>

struct CellData {
    uint32_t id{0};           // Ідентифікатор
    uint32_t capacity_mah{0}; // Дійсна ємність, мА·год
    uint32_t ir_uohm{0};      // Внутрішній опір AC IR, мкОм
    uint16_t ocv_mv{0};       // Напруга відкритого кола, мВ
};

struct SeriesGroup {
    std::vector<CellData> cells;
    uint32_t total_capacity_mah{0};
    double eq_resistance_mohm{0.0};

    void update_metrics() noexcept {
        total_capacity_mah = 0;
        double conductance_sum = 0.0;

        for (const auto& cell : cells) {
            total_capacity_mah += cell.capacity_mah;
            const double r_mohm = static_cast<double>(cell.ir_uohm) / 1000.0;
            if (r_mohm > 0.001) {
                conductance_sum += 1.0 / r_mohm;
            }
        }
        eq_resistance_mohm = (conductance_sum > 0.0) ? (1.0 / conductance_sum) : 0.0;
    }
};

class BatteryPackOptimizer {
public:
    struct PackMetrics {
        uint32_t min_capacity_mah{0};
        uint32_t max_capacity_mah{0};
        double capacity_imbalance_pct{0.0};
        double max_ir_diff_mohm{0.0};
    };

    static std::vector<SeriesGroup> build_serpentine_pack(
        std::span<const CellData> input_cells,
        uint32_t series,
        uint32_t parallel) 
    {
        if (input_cells.size() < series * parallel) {
            throw std::invalid_argument("Недостатньо комірок для формування збірки");
        }
        if (series == 0 || parallel == 0) {
            throw std::invalid_argument("Кількість ланок та паралелей має бути більшою за нуль");
        }

        // Копіюємо та сортуємо комірки за спаданням ємності
        std::vector<CellData> sorted_cells(input_cells.begin(), input_cells.end());
        std::sort(sorted_cells.begin(), sorted_cells.end(), 
            [](const CellData& a, const CellData& b) noexcept {
                if (a.capacity_mah != b.capacity_mah) {
                    return a.capacity_mah > b.capacity_mah;
                }
                if (a.ir_uohm != b.ir_uohm) {
                    return a.ir_uohm < b.ir_uohm;
                }
                return a.id < b.id;
            });

        std::vector<SeriesGroup> groups(series);
        for (auto& g : groups) {
            g.cells.reserve(parallel);
        }

        // Розподіл змійкою (Serpentine)
        size_t cell_idx = 0;
        for (uint32_t p = 0; p < parallel; ++p) {
            const bool forward = (p % 2 == 0);
            for (uint32_t s = 0; s < series; ++s) {
                const uint32_t target_s = forward ? s : (series - 1 - s);
                groups[target_s].cells.push_back(sorted_cells[cell_idx++]);
            }
        }

        for (auto& g : groups) {
            g.update_metrics();
        }

        return groups;
    }

    static PackMetrics calculate_metrics(std::span<const SeriesGroup> groups) noexcept {
        if (groups.empty()) return {};

        uint32_t min_c = groups[0].total_capacity_mah;
        uint32_t max_c = groups[0].total_capacity_mah;
        double min_r = groups[0].eq_resistance_mohm;
        double max_r = groups[0].eq_resistance_mohm;

        for (const auto& g : groups) {
            min_c = std::min(min_c, g.total_capacity_mah);
            max_c = std::max(max_c, g.total_capacity_mah);
            min_r = std::min(min_r, g.eq_resistance_mohm);
            max_r = std::max(max_r, g.eq_resistance_mohm);
        }

        PackMetrics m;
        m.min_capacity_mah = min_c;
        m.max_capacity_mah = max_c;
        m.capacity_imbalance_pct = (max_c > 0) 
            ? (static_cast<double>(max_c - min_c) * 100.0 / static_cast<double>(max_c)) 
            : 0.0;
        m.max_ir_diff_mohm = max_r - min_r;
        return m;
    }

    static void print_report(std::span<const SeriesGroup> groups) {
        const auto metrics = calculate_metrics(groups);
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== ЗВІТ КОМПЛЕКТУВАННЯ БАТАРЕЇ (C++) ===\n";
        std::cout << "Послідовних ланок (S): " << groups.size() << "\n";
        std::cout << "Дисбаланс ємності: " << metrics.capacity_imbalance_pct << "% ("
                  << metrics.min_capacity_mah << " .. " << metrics.max_capacity_mah 
                  << " мА·год, різниця: " << (metrics.max_capacity_mah - metrics.min_capacity_mah) 
                  << " мА·год)\n";
        std::cout << "Розкид опору між ланками: " << metrics.max_ir_diff_mohm << " мОм\n\n";

        for (size_t s = 0; s < groups.size(); ++s) {
            const auto& g = groups[s];
            std::cout << "  Ланка S" << std::setw(2) << std::setfill('0') << (s + 1)
                      << ": Q = " << std::setw(5) << std::setfill(' ') << g.total_capacity_mah 
                      << " мА·год | R_eq = " << std::setw(6) << g.eq_resistance_mohm 
                      << " мОм | ID: [";
            for (size_t i = 0; i < g.cells.size(); ++i) {
                std::cout << g.cells[i].id << (i + 1 < g.cells.size() ? ", " : "");
            }
            std::cout << "]\n";
        }
    }
};

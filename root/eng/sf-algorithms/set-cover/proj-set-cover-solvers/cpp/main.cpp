#include <iostream>
#include <vector>
#include <bitset>
#include <numeric>
#include <algorithm>
#include <optional>
#include <span>
#include <memory>
#include <limits>

constexpr size_t MAX_ELEMENTS = 64;
using BitMask = std::bitset<MAX_ELEMENTS>;

struct Subset {
    int id;
    double cost;
    BitMask mask;
};

struct Solution {
    std::vector<int> selected_ids;
    double total_cost = 0.0;
};

class SetCoverSolver {
public:
    /* Ідіоматичний C++ жадібний розв'язувач */
    [[nodiscard]] static Solution solveGreedy(
        std::span<const Subset> subsets,
        const BitMask& universe
    ) {
        Solution sol;
        BitMask covered;

        while (covered != universe) {
            std::optional<size_t> best_idx;
            double best_ratio = std::numeric_limits<double>::infinity();

            for (size_t i = 0; i < subsets.size(); ++i) {
                BitMask newly_covered = subsets[i].mask & (~covered);
                size_t new_count = newly_covered.count();

                if (new_count > 0) {
                    double ratio = subsets[i].cost / static_cast<double>(new_count);
                    if (ratio < best_ratio) {
                        best_ratio = ratio;
                        best_idx = i;
                    }
                }
            }

            if (!best_idx.has_value()) {
                break; // Універсум неможливо покрити наявними множинами
            }

            const auto& best_set = subsets[*best_idx];
            sol.selected_ids.push_back(best_set.id);
            sol.total_cost += best_set.cost;
            covered |= best_set.mask;
        }

        return sol;
    }

    /* Точний метод гілок і меж із RAII та керуванням пам'яттю */
    [[nodiscard]] static Solution solveExact(
        std::span<const Subset> subsets,
        const BitMask& universe
    ) {
        Solution best_sol;
        best_sol.total_cost = std::numeric_limits<double>::infinity();
        std::vector<int> current_selected;
        current_selected.reserve(subsets.size());

        branchAndBound(subsets, universe, 0, BitMask{}, 0.0, current_selected, best_sol);
        return best_sol;
    }

private:
    static void branchAndBound(
        std::span<const Subset> subsets,
        const BitMask& universe,
        size_t idx,
        BitMask current_covered,
        double current_cost,
        std::vector<int>& current_selected,
        Solution& best_sol
    ) {
        // Відсікання гілки (Pruning за верхньою межею)
        if (current_cost >= best_sol.total_cost) {
            return;
        }

        // Базовий випадок: всі елементи закрито
        if (current_covered == universe) {
            best_sol.total_cost = current_cost;
            best_sol.selected_ids = current_selected;
            return;
        }

        if (idx >= subsets.size()) {
            return;
        }

        // Гілка 1: Включення поточної підмножини
        BitMask newly = subsets[idx].mask & (~current_covered);
        if (newly.any()) {
            current_selected.push_back(subsets[idx].id);
            branchAndBound(
                subsets, universe, idx + 1,
                current_covered | subsets[idx].mask,
                current_cost + subsets[idx].cost,
                current_selected,
                best_sol
            );
            current_selected.pop_back(); // Відкат стану (Backtrack)
        }

        // Гілка 2: Пропуск поточної підмножини
        branchAndBound(
            subsets, universe, idx + 1,
            current_covered,
            current_cost,
            current_selected,
            best_sol
        );
    }
};

int main() {
    BitMask universe;
    for (size_t i = 0; i < 10; ++i) {
        universe.set(i);
    }

    const std::vector<Subset> subsets = {
        { 1, 4.0, BitMask(0b0000011111) }, // e1..e5
        { 2, 5.0, BitMask(0b0000100101) }, // e1, e3, e6
        { 3, 6.0, BitMask(0b0011001010) }, // e2, e4, e7, e8
        { 4, 3.0, BitMask(0b0011101000) }, // e4, e6, e7, e8
        { 5, 4.0, BitMask(0b1100010010) }, // e2, e5, e9, e10
        { 6, 4.0, BitMask(0b0100010000) }  // e5, e9
    };

    auto greedy = SetCoverSolver::solveGreedy(subsets, universe);
    std::cout << "=== Жадібний розв'язок (C++) ===\n";
    std::cout << "Вартість: " << greedy.total_cost << ", Кількість: " << greedy.selected_ids.size() << "\nID: ";
    for (int id : greedy.selected_ids) {
        std::cout << "S" << id << " ";
    }
    std::cout << "\n\n";

    auto exact = SetCoverSolver::solveExact(subsets, universe);
    std::cout << "=== Точний розв'язок (C++) ===\n";
    std::cout << "Вартість: " << exact.total_cost << ", Кількість: " << exact.selected_ids.size() << "\nID: ";
    for (int id : exact.selected_ids) {
        std::cout << "S" << id << " ";
    }
    std::cout << "\n";

    return 0;
}

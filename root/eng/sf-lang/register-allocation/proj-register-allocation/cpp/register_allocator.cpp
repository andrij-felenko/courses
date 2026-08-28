// register_allocator.cpp — Ідіоматична реалізація мовою C++20 (RAII, Containers, Expected)
#include <iostream>
#include <vector>
#include <stack>
#include <unordered_set>
#include <optional>
#include <algorithm>
#include <limits>
#include <format>

struct LiveInterval {
    int id;
    int start;
    int end;
    double spill_cost;
    bool is_precolored{false};

    [[nodiscard]] constexpr bool overlaps_with(const LiveInterval& other) const noexcept {
        return !(end <= other.start || other.end <= start);
    }
};

enum class AllocationStatus {
    Success,
    SpillRequired
};

class RegisterAllocator {
public:
    explicit RegisterAllocator(size_t num_physical_registers)
        : k_registers_(num_physical_registers) {}

    void add_interval(int id, int start, int end, double cost, bool precolored = false) {
        intervals_.push_back({id, start, end, cost, precolored});
    }

    struct AllocationResult {
        AllocationStatus status;
        std::vector<int> node_colors; // >= 0: колір регістру, -1: Spill
    };

    AllocationResult allocate() {
        const size_t n = intervals_.size();
        std::vector<std::vector<bool>> adj(n, std::vector<bool>(n, false));
        std::vector<int> degree(n, 0);

        // 1. Побудова графа інтерференції
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                if (intervals_[i].overlaps_with(intervals_[j])) {
                    adj[i][j] = adj[j][i] = true;
                    degree[i]++;
                    degree[j]++;
                }
            }
        }

        // 2. Фаза спрощення (Simplify & Potential Spills)
        std::vector<bool> removed(n, false);
        std::stack<size_t> simplify_stack;
        size_t remaining = n;

        while (remaining > 0) {
            std::optional<size_t> candidate;

            // Шукаємо deg < K серед не-precolored
            for (size_t i = 0; i < n; ++i) {
                if (!removed[i] && !intervals_[i].is_precolored && static_cast<size_t>(degree[i]) < k_registers_) {
                    candidate = i;
                    break;
                }
            }

            // Якщо deg >= K, обираємо кандидат на Spill за відносним пріоритетом
            if (!candidate) {
                double min_priority = std::numeric_limits<double>::max();
                for (size_t i = 0; i < n; ++i) {
                    if (!removed[i] && !intervals_[i].is_precolored) {
                        double priority = intervals_[i].spill_cost / static_cast<double>(degree[i] + 1);
                        if (priority < min_priority) {
                            min_priority = priority;
                            candidate = i;
                        }
                    }
                }
            }

            if (!candidate) break;

            size_t idx = *candidate;
            removed[idx] = true;
            simplify_stack.push(idx);
            remaining--;

            for (size_t i = 0; i < n; ++i) {
                if (adj[idx][i] && !removed[i]) {
                    degree[i]--;
                }
            }
        }

        // 3. Фаза вибору кольорів (Select & Optimistic Coloring)
        std::vector<int> colors(n, -1);
        bool has_spill = false;

        while (!simplify_stack.empty()) {
            size_t node = simplify_stack.top();
            simplify_stack.pop();
            removed[node] = false;

            std::unordered_set<int> used_colors;
            for (size_t i = 0; i < n; ++i) {
                if (adj[node][i] && !removed[i] && colors[i] >= 0) {
                    used_colors.insert(colors[i]);
                }
            }

            int assigned_color = -1;
            for (size_t c = 0; c < k_registers_; ++c) {
                if (!used_colors.contains(static_cast<int>(c))) {
                    assigned_color = static_cast<int>(c);
                    break;
                }
            }

            if (assigned_color != -1) {
                colors[node] = assigned_color;
            } else {
                colors[node] = -1; // Spill
                has_spill = true;
            }
        }

        return AllocationResult{
            .status = has_spill ? AllocationStatus::SpillRequired : AllocationStatus::Success,
            .node_colors = std::move(colors)
        };
    }

private:
    size_t k_registers_;
    std::vector<LiveInterval> intervals_;
};

int main() {
    RegisterAllocator allocator(3); // K = 3
    allocator.add_interval(1, 1, 3, 10.0);
    allocator.add_interval(2, 2, 4, 15.0);
    allocator.add_interval(3, 1, 5, 25.0);
    allocator.add_interval(4, 4, 5, 5.0);
    allocator.add_interval(5, 3, 5, 12.0);

    auto result = allocator.allocate();

    std::cout << "=== Результат розподілу регістрів (C++20 Implementation) ===\n";
    std::cout << std::format("Успішність розподілу: {}\n", 
        result.status == AllocationStatus::Success ? "УСПІХ (без Spill)" : "ПОТРІБЕН SPILL");

    for (size_t i = 0; i < result.node_colors.size(); ++i) {
        if (result.node_colors[i] >= 0) {
            std::cout << std::format("Змінна v{} -> Регістр R{}\n", i + 1, result.node_colors[i]);
        } else {
            std::cout << std::format("Змінна v{} -> SPILL у стек [rsp + {}]\n", i + 1, i * 8);
        }
    }

    return 0;
}

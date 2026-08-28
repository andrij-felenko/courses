#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <algorithm>
#include <optional>
#include <iomanip>

enum class ResourceType : size_t {
    Mem = 0, // Порти пам'яті
    Alu = 1, // Цілочислові АЛП
    Mul = 2, // Блоки множення
    Count = 3
};

struct Edge {
    size_t src;
    size_t dst;
    int latency;
    int distance;
};

struct Node {
    std::string name;
    ResourceType res;
    int latency;
    int height{0};
    std::optional<int> schedTime{std::nullopt};
    int budget{64};
};

class ModuloScheduler {
public:
    ModuloScheduler(std::vector<Node> nodes, std::vector<Edge> edges, std::array<size_t, 3> resUnits)
        : nodes_(std::move(nodes)), edges_(std::move(edges)), resUnits_(resUnits) {}

    struct ScheduleResult {
        int ii;
        int scheduleLength;
        int stageCount;
        std::vector<std::pair<std::string, int>> timeline;
    };

    std::optional<ScheduleResult> computeSchedule() {
        const int resMii = computeResMII();
        const int recMii = computeRecMII();
        int ii = std::max(resMii, recMii);

        std::cout << "Розрахункові бар'єри: ResMII = " << resMii
                  << ", RecMII = " << recMii << " -> Старт із II = " << ii << "\n";

        constexpr int MaxII = 32;

        while (ii <= MaxII) {
            computeHeights(ii);
            for (auto& node : nodes_) {
                node.schedTime = std::nullopt;
                node.budget = 64;
            }

            // Модульна таблиця резервування: mrt[slot][resource_type] -> список зайнятих вузлів
            std::vector<std::array<std::vector<size_t>, 3>> mrt(ii);
            size_t unscheduledCount = nodes_.size();
            bool success = true;

            while (unscheduledCount > 0) {
                // Знаходимо нерозкладений вузол із найвищим пріоритетом Height
                std::optional<size_t> bestIdx;
                int maxHeight = -9999;
                for (size_t i = 0; i < nodes_.size(); ++i) {
                    if (!nodes_[i].schedTime.has_value() && nodes_[i].height > maxHeight) {
                        maxHeight = nodes_[i].height;
                        bestIdx = i;
                    }
                }

                if (!bestIdx.has_value()) break;
                const size_t u = *bestIdx;

                if (nodes_[u].budget <= 0) {
                    std::cout << "Бюджет спроб для '" << nodes_[u].name
                              << "' вичерпано. Збільшуємо II: " << ii << " -> " << ii + 1 << "\n";
                    success = false;
                    break;
                }
                --nodes_[u].budget;

                const int estart = computeEStart(u, ii);
                std::optional<int> scheduledTime;

                // Шукаємо вільний слот у вікні [EStart, EStart + II - 1]
                for (int t = estart; t < estart + ii; ++t) {
                    const size_t slot = static_cast<size_t>(t % ii);
                    const auto resIdx = static_cast<size_t>(nodes_[u].res);
                    if (mrt[slot][resIdx].size() < resUnits_[resIdx]) {
                        scheduledTime = t;
                        break;
                    }
                }

                const auto resIdx = static_cast<size_t>(nodes_[u].res);

                if (scheduledTime.has_value()) {
                    nodes_[u].schedTime = *scheduledTime;
                    const size_t slot = static_cast<size_t>(*scheduledTime % ii);
                    mrt[slot][resIdx].push_back(u);
                    --unscheduledCount;
                } else {
                    // Відкат (Backtracking): скидаємо першу операцію з конфліктного слота
                    const int forcedTime = estart;
                    const size_t slot = static_cast<size_t>(forcedTime % ii);

                    if (!mrt[slot][resIdx].empty()) {
                        const size_t victim = mrt[slot][resIdx].front();
                        mrt[slot][resIdx].erase(mrt[slot][resIdx].begin());
                        nodes_[victim].schedTime = std::nullopt;
                        ++unscheduledCount;
                    }

                    nodes_[u].schedTime = forcedTime;
                    mrt[slot][resIdx].push_back(u);
                    --unscheduledCount;
                }
            }

            if (success) {
                int maxEnd = 0;
                ScheduleResult res;
                res.ii = ii;
                for (const auto& node : nodes_) {
                    const int end = *node.schedTime + node.latency;
                    maxEnd = std::max(maxEnd, end);
                    res.timeline.emplace_back(node.name, *node.schedTime);
                }
                res.scheduleLength = maxEnd;
                res.stageCount = (maxEnd + ii - 1) / ii;
                return res;
            }

            ++ii;
        }

        return std::nullopt;
    }

private:
    [[nodiscard]] int computeResMII() const noexcept {
        int resMii = 1;
        for (size_t r = 0; r < 3; ++r) {
            int count = 0;
            for (const auto& node : nodes_) {
                if (static_cast<size_t>(node.res) == r) ++count;
            }
            const size_t units = resUnits_[r] > 0 ? resUnits_[r] : 1;
            const int miiR = static_cast<int>((count + units - 1) / units);
            resMii = std::max(resMii, miiR);
        }
        return resMii;
    }

    [[nodiscard]] int computeRecMII() const noexcept {
        int recMii = 1;
        for (const auto& edge : edges_) {
            if (edge.src == edge.dst && edge.distance > 0) {
                const int ratio = (edge.latency + edge.distance - 1) / edge.distance;
                recMii = std::max(recMii, ratio);
            }
        }
        return recMii;
    }

    void computeHeights(int ii) noexcept {
        for (auto& node : nodes_) {
            node.height = node.latency;
        }
        bool changed = true;
        while (changed) {
            changed = false;
            for (const auto& edge : edges_) {
                const int effD = edge.latency - edge.distance * ii;
                if (nodes_[edge.src].height < nodes_[edge.dst].height + effD) {
                    nodes_[edge.src].height = nodes_[edge.dst].height + effD;
                    changed = true;
                }
            }
        }
    }

    [[nodiscard]] int computeEStart(size_t nodeId, int ii) const noexcept {
        int estart = 0;
        for (const auto& edge : edges_) {
            if (edge.dst == nodeId && nodes_[edge.src].schedTime.has_value()) {
                const int minT = *nodes_[edge.src].schedTime + edge.latency - edge.distance * ii;
                estart = std::max(estart, minT);
            }
        }
        return estart;
    }

    std::vector<Node> nodes_;
    std::vector<Edge> edges_;
    std::array<size_t, 3> resUnits_;
};

int main() {
    std::vector<Node> nodes = {
        {"Load_A", ResourceType::Mem, 2},
        {"Load_B", ResourceType::Mem, 2},
        {"Multiply", ResourceType::Mul, 2},
        {"Accumulate", ResourceType::Alu, 1}
    };

    std::vector<Edge> edges = {
        {0, 2, 2, 0}, // Load_A -> Mul
        {1, 2, 2, 0}, // Load_B -> Mul
        {2, 3, 2, 0}, // Mul -> Acc
        {3, 3, 1, 1}  // Acc[i] -> Acc[i+1]
    };

    std::array<size_t, 3> units = {2, 1, 1}; // 2 Mem, 1 Alu, 1 Mul

    std::cout << "=== Планувальник Iterative Modulo Scheduling (C++) ===\n\n";

    ModuloScheduler scheduler(std::move(nodes), std::move(edges), units);
    auto result = scheduler.computeSchedule();

    if (result) {
        std::cout << "\nРозклад побудовано успішно!\n";
        std::cout << "Інтервал ініціалізації (II): " << result->ii << " такт(ів)\n";
        std::cout << "Загальна довжина розкладу:   " << result->scheduleLength << " тактів\n";
        std::cout << "Кількість стадій конвеєра:   " << result->stageCount << "\n\n";

        std::cout << std::left << std::setw(14) << "Операція" << " | "
                  << std::setw(8) << "Такт t" << " | Стадія\n";
        std::cout << "---------------+----------+-------------\n";
        for (const auto& [name, time] : result->timeline) {
            const int stage = time / result->ii;
            std::cout << std::left << std::setw(14) << name << " | "
                      << std::setw(8) << time << " | Стадія " << stage << "\n";
        }
    }

    return 0;
}

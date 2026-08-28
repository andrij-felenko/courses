#include <iostream>
#include <vector>
#include <unordered_map>
#include <limits>
#include <iomanip>

constexpr int INF = 9999;

struct RouteEntry {
    int cost{INF};
    int next_hop{-1};
};

class Router {
public:
    explicit Router(int id, int total_nodes) : id_(id) {
        table_.resize(total_nodes);
        table_[id_] = {0, id_};
    }

    void add_neighbor(int neighbor_id, int cost) {
        neighbors_[neighbor_id] = cost;
        table_[neighbor_id] = {cost, neighbor_id};
    }

    [[nodiscard]] int id() const { return id_; }
    [[nodiscard]] const std::unordered_map<int, int>& neighbors() const { return neighbors_; }

    // Формування вектора відстаней з отруйним реверсом (Poison Reverse)
    [[nodiscard]] std::vector<int> prepare_vector_for(int target_neighbor) const {
        std::vector<int> vec(table_.size());
        for (std::size_t d = 0; d < table_.size(); ++d) {
            if (static_cast<int>(d) != id_ && table_[d].next_hop == target_neighbor) {
                vec[d] = INF; // Отруюємо шлях, якщо він іде через цього сусіда
            } else {
                vec[d] = table_[d].cost;
            }
        }
        return vec;
    }

    // Оновлення за рівнянням Беллмана-Форда
    bool update_from(int neighbor_id, const std::vector<int>& received_vector) {
        auto it = neighbors_.find(neighbor_id);
        if (it == neighbors_.end()) return false;

        const int link_cost = it->second;
        bool changed = false;

        for (std::size_t d = 0; d < table_.size(); ++d) {
            if (static_cast<int>(d) == id_) continue;

            const int dist_via_neighbor = received_vector[d];
            const int new_cost = (dist_via_neighbor >= INF) ? INF : (link_cost + dist_via_neighbor);

            if (new_cost < table_[d].cost) {
                table_[d].cost = new_cost;
                table_[d].next_hop = neighbor_id;
                changed = true;
            }
        }
        return changed;
    }

    void print_table() const {
        std::cout << "--- Таблиця маршрутизації вузла " << id_ << " ---\n";
        std::cout << "Ціль\tДистанція\tНаступний хоп\n";
        for (std::size_t i = 0; i < table_.size(); ++i) {
            std::cout << i << "\t";
            if (table_[i].cost >= INF) {
                std::cout << "INF\t\t-\n";
            } else {
                std::cout << table_[i].cost << "\t\t" << table_[i].next_hop << "\n";
            }
        }
        std::cout << "\n";
    }

private:
    int id_;
    std::vector<RouteEntry> table_;
    std::unordered_map<int, int> neighbors_;
};

class NetworkSimulator {
public:
    explicit NetworkSimulator(int total_nodes) {
        routers_.reserve(total_nodes);
        for (int i = 0; i < total_nodes; ++i) {
            routers_.emplace_back(i, total_nodes);
        }
    }

    void add_link(int u, int v, int cost) {
        routers_[u].add_neighbor(v, cost);
        routers_[v].add_neighbor(u, cost);
    }

    void run_until_convergence() {
        int iteration = 0;
        bool any_changed = true;

        std::cout << "=== Старт симуляції (C++ RAII Engine) ===\n\n";

        while (any_changed && iteration < 15) {
            any_changed = false;
            ++iteration;
            std::cout << ">>> Ітерація " << iteration << " <<<\n";

            for (auto& sender : routers_) {
                for (const auto& [neighbor_id, _] : sender.neighbors()) {
                    auto vec = sender.prepare_vector_for(neighbor_id);
                    if (routers_[neighbor_id].update_from(sender.id(), vec)) {
                        any_changed = true;
                    }
                }
            }
        }

        std::cout << "Збіжність досягнута за " << iteration << " ітерацій.\n\n";
        for (const auto& r : routers_) {
            r.print_table();
        }
    }

private:
    std::vector<Router> routers_;
};

int main() {
    NetworkSimulator net(4);

    net.add_link(0, 1, 1);
    net.add_link(1, 2, 3);
    net.add_link(0, 2, 7);
    net.add_link(2, 3, 2);

    net.run_until_convergence();

    return 0;
}

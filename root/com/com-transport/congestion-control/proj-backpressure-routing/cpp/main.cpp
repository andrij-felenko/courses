#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>

struct Edge {
    int u;
    int v;
    int capacity;
};

class BackpressureNetwork {
private:
    int num_nodes_;
    int num_commodities_;
    std::vector<Edge> edges_;
    std::vector<std::vector<int>> queue_;

public:
    BackpressureNetwork(int n, int num_comm)
        : num_nodes_(n), num_commodities_(num_comm),
          queue_(n, std::vector<int>(num_comm, 0)) {}

    void add_edge(int u, int v, int cap) {
        edges_.push_back({u, v, cap});
    }

    void set_queue(int node, int commodity, int count) {
        queue_[node][commodity] = count;
    }

    int get_queue(int node, int commodity) const {
        return queue_[node][commodity];
    }

    void step() {
        std::vector<std::vector<int>> delta(num_nodes_, std::vector<int>(num_commodities_, 0));

        for (const auto& edge : edges_) {
            int u = edge.u;
            int v = edge.v;
            int cap = edge.capacity;

            int max_weight = 0;
            int best_commodity = -1;

            for (int c = 0; c < num_commodities_; ++c) {
                int weight = queue_[u][c] - queue_[v][c];
                if (weight > max_weight) {
                    max_weight = weight;
                    best_commodity = c;
                }
            }

            if (best_commodity != -1 && max_weight > 0) {
                int packets = std::min(queue_[u][best_commodity], cap);
                delta[u][best_commodity] -= packets;
                delta[v][best_commodity] += packets;

                std::cout << "  Ребро (" << u << "->" << v << "): переслано "
                          << packets << " пакетів товару " << best_commodity
                          << " (тиск = " << max_weight << ")\n";
            }
        }

        for (int i = 0; i < num_nodes_; ++i) {
            for (int c = 0; c < num_commodities_; ++c) {
                queue_[i][c] += delta[i][c];
                if (i == c) {
                    queue_[i][c] = 0; // Поглинання в точці призначення
                }
            }
        }
    }
};

int main() {
    BackpressureNetwork net(4, 2);

    net.add_edge(0, 1, 5);
    net.add_edge(0, 2, 5);
    net.add_edge(1, 3, 4);
    net.add_edge(2, 3, 4);

    net.set_queue(0, 3, 20);

    std::cout << "=== Початковий стан черги у вузлі 0: " << net.get_queue(0, 3) << " ===\n";

    for (int t = 1; t <= 4; ++t) {
        std::cout << "\nТакт " << t << ":\n";
        net.step();
        std::cout << "Стан черг: Node 0=" << net.get_queue(0, 3)
                  << ", Node 1=" << net.get_queue(1, 3)
                  << ", Node 2=" << net.get_queue(2, 3)
                  << ", Node 3=" << net.get_queue(3, 3) << "\n";
    }

    return 0;
}

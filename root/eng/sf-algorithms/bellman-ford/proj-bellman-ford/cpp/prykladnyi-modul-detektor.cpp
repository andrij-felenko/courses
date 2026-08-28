#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <unordered_map>
#include <optional>
#include <limits>
#include <algorithm>

struct CurrencyPair {
    std::string from;
    std::string to;
    double rate;
};

struct ArbitrageOpportunity {
    std::vector<std::string> path;
    double profit_multiplier;
};

class ArbitrageDetector {
public:
    static constexpr double EPSILON = 1e-9;

    static std::optional<ArbitrageOpportunity> find_opportunity(const std::vector<CurrencyPair>& pairs) {
        std::unordered_map<std::string, int> currency_to_id;
        std::vector<std::string> id_to_currency;

        auto get_id = [&](const std::string& name) {
            if (currency_to_id.find(name) == currency_to_id.end()) {
                currency_to_id[name] = id_to_currency.size();
                id_to_currency.push_back(name);
            }
            return currency_to_id[name];
        };

        struct GraphEdge {
            int src;
            int dest;
            double weight;
            double original_rate;
        };

        std::vector<GraphEdge> edges;
        for (const auto& pair : pairs) {
            int u = get_id(pair.from);
            int v = get_id(pair.to);
            edges.push_back({u, v, -std::log(pair.rate), pair.rate});
        }

        int V = id_to_currency.size();
        std::vector<double> dist(V, 0.0);
        std::vector<int> parent(V, -1);

        for (int iter = 0; iter < V - 1; ++iter) {
            bool updated = false;
            for (const auto& edge : edges) {
                if (dist[edge.src] + edge.weight < dist[edge.dest] - EPSILON) {
                    dist[edge.dest] = dist[edge.src] + edge.weight;
                    parent[edge.dest] = edge.src;
                    updated = true;
                }
            }
            if (!updated) break;
        }

        int cycle_node = -1;
        for (const auto& edge : edges) {
            if (dist[edge.src] + edge.weight < dist[edge.dest] - EPSILON) {
                cycle_node = edge.dest;
                parent[edge.dest] = edge.src;
                break;
            }
        }

        if (cycle_node == -1) {
            return std::nullopt;
        }

        for (int i = 0; i < V; ++i) {
            cycle_node = parent[cycle_node];
        }

        std::vector<int> cycle_ids;
        for (int curr = cycle_node;; curr = parent[curr]) {
            cycle_ids.push_back(curr);
            if (curr == cycle_node && cycle_ids.size() > 1) break;
        }
        std::reverse(cycle_ids.begin(), cycle_ids.end());

        std::vector<std::string> path;
        double multiplier = 1.0;
        for (size_t i = 0; i < cycle_ids.size() - 1; ++i) {
            path.push_back(id_to_currency[cycle_ids[i]]);
            int u = cycle_ids[i];
            int v = cycle_ids[i+1];
            for (const auto& edge : edges) {
                if (edge.src == u && edge.dest == v) {
                    multiplier *= edge.original_rate;
                    break;
                }
            }
        }
        path.push_back(id_to_currency[cycle_ids.back()]);

        return ArbitrageOpportunity{path, multiplier};
    }
};

int main() {
    std::vector<CurrencyPair> pairs = {
        {"USD", "EUR", 0.92},
        {"EUR", "GBP", 0.86},
        {"GBP", "USD", 1.28}
    };

    auto opp = ArbitrageDetector::find_opportunity(pairs);
    if (opp) {
        std::cout << "Знайдено арбітраж із множником " << opp->profit_multiplier << ": ";
        for (const auto& curr : opp->path) {
            std::cout << curr << " -> ";
        }
        std::cout << "\n";
    }
    return 0;
}

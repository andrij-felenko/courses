#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <algorithm>
#include <iomanip>
#include <numeric>

struct NodeLocation {
    int dc_id;
    int rack_id;
    int node_id;
};

enum class TopologyStrategy {
    FlatUniform,
    HierarchicalLocalityAware
};

struct SimulationConfig {
    int datacenters = 3;
    int racks_per_dc = 4;
    int nodes_per_rack = 50;  // Загалом: 3 * 4 * 50 = 600 вузлів
    int fanout = 3;
    double p_rack = 0.60;     // Ймовірність вибору у своїй стійці
    double p_dc = 0.35;       // Ймовірність вибору у своєму ДЦ (інша стійка)
    double p_wan = 0.05;      // Ймовірність міжрегіонального WAN-вибору
    double lat_rack_ms = 0.1;
    double lat_dc_ms = 0.8;
    double lat_wan_ms = 80.0;
};

struct SimulationResult {
    int total_rounds;
    double total_physical_time_ms;
    long long total_wan_packets;
};

class GossipSimulator {
public:
    explicit GossipSimulator(SimulationConfig config)
        : cfg_(config), rng_(1337) {
        init_nodes();
    }

    SimulationResult run(TopologyStrategy strategy) {
        std::vector<bool> infected(total_nodes_, false);
        std::vector<double> infection_time_ms(total_nodes_, 0.0);
        
        // Вузол 0 генерує оновлення на початку t = 0
        infected[0] = true;
        infection_time_ms[0] = 0.0;
        int infected_count = 1;

        int round = 0;
        long long wan_packets = 0;

        while (infected_count < total_nodes_ && round < 1000) {
            round++;
            std::vector<int> current_infected;
            current_infected.reserve(infected_count);
            for (int i = 0; i < total_nodes_; ++i) {
                if (infected[i]) {
                    current_infected.push_back(i);
                }
            }

            // Збираємо нові інфекції цього раунду
            std::vector<std::pair<int, double>> newly_infected;

            for (int src_id : current_infected) {
                for (int f = 0; f < cfg_.fanout; ++f) {
                    int target_id = (strategy == TopologyStrategy::FlatUniform)
                                    ? select_uniform_target(src_id)
                                    : select_hierarchical_target(src_id);

                    if (target_id == src_id || target_id < 0) continue;

                    const auto& src_loc = nodes_[src_id];
                    const auto& dst_loc = nodes_[target_id];

                    double delay_ms = 0.0;
                    if (src_loc.dc_id != dst_loc.dc_id) {
                        wan_packets++;
                        delay_ms = cfg_.lat_wan_ms;
                    } else if (src_loc.rack_id != dst_loc.rack_id) {
                        delay_ms = cfg_.lat_dc_ms;
                    } else {
                        delay_ms = cfg_.lat_rack_ms;
                    }

                    double arrival_time = infection_time_ms[src_id] + delay_ms;
                    if (!infected[target_id]) {
                        newly_infected.emplace_back(target_id, arrival_time);
                    }
                }
            }

            // Застосовуємо інфікування
            for (const auto& [target, time] : newly_infected) {
                if (!infected[target]) {
                    infected[target] = true;
                    infection_time_ms[target] = time;
                    infected_count++;
                } else {
                    infection_time_ms[target] = std::min(infection_time_ms[target], time);
                }
            }
        }

        double max_time = *std::max_element(infection_time_ms.begin(), infection_time_ms.end());
        return {round, max_time, wan_packets};
    }

private:
    void init_nodes() {
        nodes_.clear();
        dc_nodes_.assign(cfg_.datacenters, {});
        rack_nodes_.assign(cfg_.datacenters * cfg_.racks_per_dc, {});

        int id = 0;
        for (int d = 0; d < cfg_.datacenters; ++d) {
            for (int r = 0; r < cfg_.racks_per_dc; ++r) {
                int global_rack_idx = d * cfg_.racks_per_dc + r;
                for (int n = 0; n < cfg_.nodes_per_rack; ++n) {
                    nodes_.push_back({d, r, id});
                    dc_nodes_[d].push_back(id);
                    rack_nodes_[global_rack_idx].push_back(id);
                    id++;
                }
            }
        }
        total_nodes_ = id;
    }

    int select_uniform_target(int src_id) {
        std::uniform_int_distribution<int> dist(0, total_nodes_ - 2);
        int pick = dist(rng_);
        return (pick >= src_id) ? pick + 1 : pick;
    }

    int select_hierarchical_target(int src_id) {
        std::uniform_real_distribution<double> p_dist(0.0, 1.0);
        double roll = p_dist(rng_);

        const auto& src = nodes_[src_id];
        int global_rack = src.dc_id * cfg_.racks_per_dc + src.rack_id;

        if (roll < cfg_.p_rack) {
            // Вибір усередині тієї ж стійки
            const auto& pool = rack_nodes_[global_rack];
            if (pool.size() > 1) {
                std::uniform_int_distribution<size_t> dist(0, pool.size() - 1);
                int target = pool[dist(rng_)];
                return (target == src_id) ? select_uniform_target(src_id) : target;
            }
        } else if (roll < cfg_.p_rack + cfg_.p_dc) {
            // Вибір у тому ж ДЦ, але іншій стійці
            const auto& pool = dc_nodes_[src.dc_id];
            std::uniform_int_distribution<size_t> dist(0, pool.size() - 1);
            int target = pool[dist(rng_)];
            return (target == src_id) ? select_uniform_target(src_id) : target;
        } else {
            // Вибір у віддаленому ДЦ (WAN)
            std::uniform_int_distribution<int> dc_dist(0, cfg_.datacenters - 2);
            int remote_dc = dc_dist(rng_);
            if (remote_dc >= src.dc_id) remote_dc++;

            const auto& pool = dc_nodes_[remote_dc];
            std::uniform_int_distribution<size_t> dist(0, pool.size() - 1);
            return pool[dist(rng_)];
        }

        return select_uniform_target(src_id);
    }

    SimulationConfig cfg_;
    std::mt19937 rng_;
    int total_nodes_{0};
    std::vector<NodeLocation> nodes_;
    std::vector<std::vector<int>> dc_nodes_;
    std::vector<std::vector<int>> rack_nodes_;
};

int main() {
    SimulationConfig config;
    GossipSimulator sim(config);

    auto res_flat = sim.run(TopologyStrategy::FlatUniform);
    auto res_hier = sim.run(TopologyStrategy::HierarchicalLocalityAware);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "===============================================================\n";
    std::cout << " РЕЗУЛЬТАТИ ПОРІВНЯННЯ ТОПОЛОГІЙ GOSSIP (600 ВУЗЛІВ, 3 ДЦ)\n";
    std::cout << "===============================================================\n";
    std::cout << "Метрика                    | Flat Uniform       | Ієрархічний Gossip\n";
    std::cout << "---------------------------+--------------------+--------------------\n";
    std::cout << "Раундів до 100% збіжності  | " << std::setw(18) << res_flat.total_rounds
              << " | " << std::setw(18) << res_hier.total_rounds << "\n";
    std::cout << "Фізичний час (P99, мс)     | " << std::setw(15) << res_flat.total_physical_time_ms << " ms"
              << " | " << std::setw(15) << res_hier.total_physical_time_ms << " ms\n";
    std::cout << "Пакетів через WAN          | " << std::setw(18) << res_flat.total_wan_packets
              << " | " << std::setw(18) << res_hier.total_wan_packets << "\n";
    std::cout << "---------------------------+--------------------+--------------------\n";

    double wan_reduction = 100.0 * (1.0 - static_cast<double>(res_hier.total_wan_packets) / res_flat.total_wan_packets);
    std::cout << "Економія трафіку WAN: " << wan_reduction << "%\n";
    return 0;
}

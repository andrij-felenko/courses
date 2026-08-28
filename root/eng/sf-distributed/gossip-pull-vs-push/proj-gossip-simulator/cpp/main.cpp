#include <iostream>
#include <vector>
#include <span>
#include <random>
#include <memory>
#include <string_view>
#include <iomanip>

enum class GossipMode {
    Push,
    Pull,
    PushPull
};

struct Node {
    uint32_t id{0};
    uint64_t state_version{0};
};

struct SimMetrics {
    uint32_t total_messages{0};
    uint64_t total_payload_bytes{0};
    uint32_t rounds_to_converge{0};
};

class GossipSimulator {
public:
    GossipSimulator(uint32_t num_nodes, uint32_t fanout, double packet_loss)
        : num_nodes_(num_nodes),
          fanout_(fanout),
          packet_loss_(packet_loss),
          rng_(std::random_device{}()) {}

    SimMetrics simulate(GossipMode mode, uint64_t target_version) {
        std::vector<Node> current(num_nodes_);
        std::vector<Node> next(num_nodes_);

        for (uint32_t i = 0; i < num_nodes_; ++i) {
            current[i] = Node{.id = i, .state_version = (i == 0 ? target_version : 0)};
            next[i] = current[i];
        }

        SimMetrics metrics{};
        constexpr uint32_t max_rounds = 100;
        std::uniform_real_distribution<double> loss_dist(0.0, 1.0);
        std::uniform_int_distribution<uint32_t> peer_dist(0, num_nodes_ - 1);

        for (uint32_t r = 0; r < max_rounds; ++r) {
            uint32_t infected = 0;
            for (const auto& node : current) {
                if (node.state_version == target_version) {
                    infected++;
                }
            }

            if (infected == num_nodes_) {
                metrics.rounds_to_converge = r;
                return metrics;
            }

            for (uint32_t i = 0; i < num_nodes_; ++i) {
                for (uint32_t f = 0; f < fanout_; ++f) {
                    uint32_t peer = peer_dist(rng_);
                    while (peer == i) {
                        peer = peer_dist(rng_);
                    }

                    switch (mode) {
                        case GossipMode::Push:
                            if (current[i].state_version == target_version) {
                                metrics.total_messages++;
                                metrics.total_payload_bytes += 64;
                                if (loss_dist(rng_) >= packet_loss_) {
                                    next[peer].state_version = target_version;
                                }
                            }
                            break;

                        case GossipMode::Pull:
                            if (current[i].state_version < target_version) {
                                metrics.total_messages += 2;
                                metrics.total_payload_bytes += 8;
                                if (loss_dist(rng_) >= packet_loss_) {
                                    if (current[peer].state_version == target_version) {
                                        metrics.total_payload_bytes += 64;
                                        next[i].state_version = target_version;
                                    }
                                }
                            }
                            break;

                        case GossipMode::PushPull:
                            metrics.total_messages += 2;
                            metrics.total_payload_bytes += 16;
                            if (loss_dist(rng_) >= packet_loss_) {
                                if (current[i].state_version > current[peer].state_version) {
                                    metrics.total_payload_bytes += 64;
                                    next[peer].state_version = current[i].state_version;
                                }
                                if (current[peer].state_version > current[i].state_version) {
                                    metrics.total_payload_bytes += 64;
                                    next[i].state_version = current[peer].state_version;
                                }
                            }
                            break;
                    }
                }
            }
            current = next;
        }

        metrics.rounds_to_converge = max_rounds;
        return metrics;
    }

private:
    uint32_t num_nodes_;
    uint32_t fanout_;
    double packet_loss_;
    std::mt19937_64 rng_;
};

int main() {
    constexpr uint32_t cluster_size = 1000;
    constexpr uint32_t fanout = 2;
    constexpr double loss_rate = 0.05;
    constexpr uint64_t target_v = 42;

    GossipSimulator sim(cluster_size, fanout, loss_rate);

    std::cout << "=== Симуляція пліток (Кластер: " << cluster_size << " вузлів, Втрати: " << loss_rate * 100.0 << "%) ===\n\n";

    struct TestCase {
        std::string_view name;
        GossipMode mode;
    };

    const TestCase cases[] = {
        {"Pure Push", GossipMode::Push},
        {"Pure Pull", GossipMode::Pull},
        {"Hybrid Push-Pull", GossipMode::PushPull}
    };

    for (const auto& [name, mode] : cases) {
        const auto metrics = sim.simulate(mode, target_v);
        std::cout << "[" << name << "]\n";
        std::cout << "  • Раундів до 100% узгодженості: " << metrics.rounds_to_converge << "\n";
        std::cout << "  • Сумарно повідомлень:         " << metrics.total_messages << "\n";
        std::cout << "  • Сумарно трафіку:             " << std::fixed << std::setprecision(2)
                  << (metrics.total_payload_bytes / 1024.0) << " КБ\n\n";
    }

    return 0;
}

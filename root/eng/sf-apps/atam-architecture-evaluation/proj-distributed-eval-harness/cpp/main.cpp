#include <iostream>
#include <vector>
#include <array>
#include <random>
#include <algorithm>
#include <cmath>
#include <string_view>
#include <format>
#include <expected>

struct ArchConfig {
    int total_nodes{5};
    int write_quorum{3};
    int read_quorum{3};
    double net_latency_ms{1.5};
    double node_fail_prob{0.05};
};

struct EvaluationResult {
    double write_latency_p99_ms{0.0};
    double staleness_rate_pct{0.0};
    double write_availability_pct{0.0};
    bool is_latency_risk{false};
    bool is_consistency_risk{false};
    bool is_tradeoff_point{false};

    [[nodiscard]] std::string_view classification() const noexcept {
        if (is_consistency_risk && !is_latency_risk) {
            return "РИЗИК (Консистентність)";
        }
        if (is_latency_risk) {
            return "РИЗИК (Затримка SLA)";
        }
        if (is_tradeoff_point) {
            return "ТОЧКА КОМПРОМІСУ (NR)";
        }
        return "НЕ-РИЗИК";
    }
};

class ClusterEvaluator {
public:
    static constexpr std::size_t Trials = 50'000;

    explicit ClusterEvaluator(std::uint_fast32_t seed = 42)
        : rng_(seed) {}

    [[nodiscard]] EvaluationResult evaluate(const ArchConfig& cfg) {
        std::vector<double> latencies;
        latencies.reserve(Trials);

        std::size_t stale_reads = 0;
        std::size_t failed_writes = 0;

        std::uniform_real_distribution<double> uniform_dist(0.0, 1.0);
        std::normal_distribution<double> latency_dist(cfg.net_latency_ms, cfg.net_latency_ms * 0.35);

        std::vector<double> alive_latencies;
        alive_latencies.reserve(cfg.total_nodes);

        for (std::size_t t = 0; t < Trials; ++t) {
            alive_latencies.clear();

            for (int i = 0; i < cfg.total_nodes; ++i) {
                if (uniform_dist(rng_) >= cfg.node_fail_prob) {
                    double lat = std::max(0.1, latency_dist(rng_));
                    alive_latencies.push_back(lat);
                }
            }

            if (static_cast<int>(alive_latencies.size()) < cfg.write_quorum) {
                ++failed_writes;
                latencies.push_back(100.0); /* Штраф за таймаут операції */
                continue;
            }

            std::ranges::sort(alive_latencies);
            latencies.push_back(alive_latencies[static_cast<std::size_t>(cfg.write_quorum - 1)]);

            /* Перевірка умови перетину кворумів Гіффорда (W + R > N) */
            if (cfg.write_quorum + cfg.read_quorum <= cfg.total_nodes) {
                int non_updated = cfg.total_nodes - cfg.write_quorum;
                if (cfg.read_quorum <= non_updated) {
                    double p_stale = 1.0;
                    for (int step = 0; step < cfg.read_quorum; ++step) {
                        p_stale *= static_cast<double>(non_updated - step) / static_cast<double>(cfg.total_nodes - step);
                    }
                    if (uniform_dist(rng_) < p_stale) {
                        ++stale_reads;
                    }
                }
            }
        }

        std::ranges::sort(latencies);
        const auto p99_idx = static_cast<std::size_t>(Trials * 0.99);

        EvaluationResult result;
        result.write_latency_p99_ms = latencies[p99_idx];
        result.staleness_rate_pct = (static_cast<double>(stale_reads) / static_cast<double>(Trials)) * 100.0;
        result.write_availability_pct = (1.0 - static_cast<double>(failed_writes) / static_cast<double>(Trials)) * 100.0;

        result.is_latency_risk = (result.write_latency_p99_ms > 4.0);
        result.is_consistency_risk = (result.staleness_rate_pct > 0.0001);
        result.is_tradeoff_point = (cfg.write_quorum > 1 && cfg.write_quorum + cfg.read_quorum > cfg.total_nodes);

        return result;
    }

private:
    std::mt19937 rng_;
};

int main() {
    std::cout << "=== ATAM Architecture Evaluation Harness (C++20) ===\n\n";
    std::cout << "N=5 вузлів, Базова RTT = 1.5 мс, Ймовірність збою вузла = 5%\n";
    std::cout << "----------------------------------------------------------------------------------\n";
    std::cout << " Конфігурація (W, R) | Latency p99 | Stale Reads | Availability | ATAM Вердикт    \n";
    std::cout << "----------------------------------------------------------------------------------\n";

    ClusterEvaluator evaluator(42);

    constexpr std::array<std::pair<int, int>, 4> configurations{{
        {1, 1},
        {1, 3},
        {3, 3},
        {5, 1}
    }};

    for (const auto& [w, r] : configurations) {
        ArchConfig cfg{
            .total_nodes = 5,
            .write_quorum = w,
            .read_quorum = r,
            .net_latency_ms = 1.5,
            .node_fail_prob = 0.05
        };

        const auto res = evaluator.evaluate(cfg);

        std::cout << std::format(" W={:d}, R={:d}           |   {:5.2f} ms  |   {:5.2f} %   |   {:6.2f} %   | {}\n",
                                 cfg.write_quorum, cfg.read_quorum,
                                 res.write_latency_p99_ms, res.staleness_rate_pct, res.write_availability_pct,
                                 res.classification());
    }
    std::cout << "----------------------------------------------------------------------------------\n";
    return 0;
}

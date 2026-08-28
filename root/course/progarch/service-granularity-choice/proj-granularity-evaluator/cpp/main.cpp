#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iomanip>

// Структура для опису вузла сервісу в мережевому ланцюгу
struct ServiceNode {
    std::string name;
    double internal_compute_ms; // Чистий час обчислень у пам'яті
    double p50_net_ms;          // Медіанна затримка мережевого транспорту + SerDes
    double p99_net_ms;          // Хводова затримка мережі (P99)
    double failure_rate;        // Імовірність відмови (наприклад, 0.001 = 99.9% availability)
};

// Опис структури та технологічного стеку інженерної команди
struct TeamTopology {
    int num_engineers;
    int num_services;
    int num_repositories;
    int num_tech_stacks;
};

// Підсумкові метрики системи
struct GranularityMetrics {
    double total_p50_ms;
    double total_p99_ms;
    double tail_impact_probability;
    double system_availability;
    double cognitive_load_index;
    bool is_nano_service_danger;
};

class GranularityEvaluator {
public:
    static GranularityMetrics evaluate(const std::vector<ServiceNode>& chain, const TeamTopology& team) {
        GranularityMetrics m{};
        
        double sum_compute = 0.0;
        double sum_net_p50 = 0.0;
        double sum_net_p99_sq = 0.0;
        double avail_prod = 1.0;
        
        const std::size_t K = chain.size();

        for (const auto& node : chain) {
            sum_compute += node.internal_compute_ms;
            sum_net_p50 += node.p50_net_ms;
            
            // Затримка P99 для логнормальних затримок обчислюється квадратично
            double net_delta_p99 = node.p99_net_ms - node.p50_net_ms;
            sum_net_p99_sq += (net_delta_p99 * net_delta_p99);
            
            avail_prod *= (1.0 - node.failure_rate);
        }

        m.total_p50_ms = sum_compute + sum_net_p50;
        m.total_p99_ms = m.total_p50_ms + std::sqrt(sum_net_p99_sq);
        
        // Ймовірність зіткнення з P99 хвостом при K викликах
        m.tail_impact_probability = 1.0 - std::pow(0.99, static_cast<double>(K));
        m.system_availability = avail_prod;

        // Обчислення CLI (Cognitive Load Index) за методологією Team Topologies
        constexpr double alpha_repo = 1.5;
        constexpr double beta_pipe = 2.0;
        constexpr double gamma_stack = 3.5;
        constexpr double capacity_factor = 5.0;

        double raw_load = (team.num_services * alpha_repo) + 
                          (team.num_repositories * beta_pipe) + 
                          (team.num_tech_stacks * gamma_stack);
        
        m.cognitive_load_index = raw_load / (team.num_engineers * capacity_factor);
        
        // Детекція наносервісної небезпеки: частка мережі > 60% або CLI > 1.2 або K > 10
        double net_ratio = (m.total_p50_ms > 0) ? (sum_net_p50 / m.total_p50_ms) : 0.0;
        m.is_nano_service_danger = (net_ratio > 0.60) || (m.cognitive_load_index > 1.2) || (K > 10);

        return m;
    }
};

int main() {
    // Сценарій А: Наносервісна патологія (12 дрібних ланок)
    std::vector<ServiceNode> nano_chain = {
        {"Gateway", 2.0, 1.5, 8.0, 0.0005},
        {"AuthSvc", 1.0, 3.0, 15.0, 0.001},
        {"UserSvc", 1.5, 2.5, 12.0, 0.001},
        {"ProfileSvc", 1.0, 2.5, 14.0, 0.001},
        {"AddrSvc", 1.0, 3.0, 18.0, 0.001},
        {"OrderSvc", 2.0, 3.5, 20.0, 0.001},
        {"ItemSvc", 1.5, 2.5, 12.0, 0.001},
        {"PriceSvc", 1.0, 3.0, 16.0, 0.001},
        {"TaxSvc", 1.0, 4.0, 25.0, 0.002},
        {"StockSvc", 1.5, 3.0, 15.0, 0.001},
        {"PromoSvc", 1.0, 3.5, 18.0, 0.001},
        {"LogSvc", 0.5, 2.0, 10.0, 0.0005}
    };

    TeamTopology team_nano{ .num_engineers = 6, .num_services = 12, .num_repositories = 12, .num_tech_stacks = 3 };

    auto metrics_nano = GranularityEvaluator::evaluate(nano_chain, team_nano);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Сценарій А: Наносервіси (12 ланок) ===\n";
    std::cout << "Затримка P50: " << metrics_nano.total_p50_ms << " ms\n";
    std::cout << "Затримка P99: " << metrics_nano.total_p99_ms << " ms\n";
    std::cout << "Ризик P99 хвоста: " << metrics_nano.tail_impact_probability * 100.0 << " %\n";
    std::cout << "Доступність ланцюга: " << metrics_nano.system_availability * 100.0 << " %\n";
    std::cout << "Когнітивне навантаження CLI: " << metrics_nano.cognitive_load_index << " (Поріг > 1.0)\n";
    std::cout << "Статус системи: " << (metrics_nano.is_nano_service_danger ? "🔴 НАНОСЕРВІСНА ПАТОЛОГІЯ" : "🟢 НОРМА") << "\n\n";

    // Сценарій Б: Консолідовані предметні макросервіси (2 ланки)
    std::vector<ServiceNode> domain_chain = {
        {"CustomerDomainSvc", 5.0, 3.0, 12.0, 0.0005},
        {"OrderDomainSvc", 8.0, 3.5, 15.0, 0.0005}
    };

    TeamTopology team_domain{ .num_engineers = 6, .num_services = 2, .num_repositories = 2, .num_tech_stacks = 1 };

    auto metrics_domain = GranularityEvaluator::evaluate(domain_chain, team_domain);

    std::cout << "=== Сценарій Б: Консолідовані предметні сервіси (2 ланки) ===\n";
    std::cout << "Затримка P50: " << metrics_domain.total_p50_ms << " ms\n";
    std::cout << "Затримка P99: " << metrics_domain.total_p99_ms << " ms\n";
    std::cout << "Ризик P99 хвоста: " << metrics_domain.tail_impact_probability * 100.0 << " %\n";
    std::cout << "Доступність ланцюга: " << metrics_domain.system_availability * 100.0 << " %\n";
    std::cout << "Когнітивне навантаження CLI: " << metrics_domain.cognitive_load_index << " (Поріг > 1.0)\n";
    std::cout << "Статус системи: " << (metrics_domain.is_nano_service_danger ? "🔴 НАНОСЕРВІСНА ПАТОЛОГІЯ" : "🟢 НОРМА") << "\n";

    return 0;
}

#include <cmath>
#include <format>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

struct WorkloadProfile {
    double base_rps;          // Середній денний трафік (RPS)
    double diurnal_factor;    // Коефіцієнт вечірнього піку
    double burst_factor;      // Коефіцієнт непередбачених сплесків
    double growth_rate_pct;   // Очікуваний ріст на місяць у %
    int months_ahead;         // Горизонт планування в місяцях
};

struct NodeProfile {
    double capacity_rps;      // Максимальна продуктивність одного вузла (RPS)
    double service_time_ms;   // Чистий час виконання запиту на CPU (мс)
    double max_safe_util;     // Гранично допустима безпечна утилізація
};

struct ResilienceConfig {
    int availability_zones;   // Кількість зон доступності (AZ)
    int extra_nodes_per_az;   // Локальний резерв на зону (N+1)
};

struct CapacityPlan {
    double forecast_peak_rps;
    int total_nodes;
    int nodes_per_az;
    double steady_state_util;
    double steady_state_headroom;
    double disaster_util;
    double disaster_headroom;
    double steady_p99_latency_ms;
    double disaster_p99_latency_ms;
    bool is_slo_safe;
};

// Обчислює 99-й перцентиль затримки очікування в черзі за моделлю M/M/1
[[nodiscard]] double calculate_p99_queue_delay(double service_time_ms, double util) noexcept {
    if (util >= 0.999) {
        return std::numeric_limits<double>::infinity();
    }
    if (util <= 0.001) {
        return 0.0;
    }
    // t_99 = S * ln(util / (1 - 0.99)) / (1 - util)
    return service_time_ms * (std::log(util / 0.01) / (1.0 - util));
}

[[nodiscard]] CapacityPlan plan_capacity(
    const WorkloadProfile& workload,
    const NodeProfile& node,
    const ResilienceConfig& resilience
) {
    if (resilience.availability_zones < 2) {
        throw std::invalid_argument("Для Multi-AZ планування потрібно щонайменше 2 зони.");
    }

    // 1. Прогноз пікового навантаження з урахуванням складного відсотка росту
    const double growth_multiplier = std::pow(1.0 + workload.growth_rate_pct / 100.0, workload.months_ahead);
    const double peak_rps = workload.base_rps * workload.diurnal_factor * workload.burst_factor * growth_multiplier;

    // 2. Розрахунок штатної потреби для Multi-AZ схеми
    const int m = resilience.availability_zones;
    const double disaster_usable_node_rps = node.capacity_rps * node.max_safe_util;
    const int min_working_nodes_disaster = static_cast<int>(std::ceil(peak_rps / disaster_usable_node_rps));
    const int nodes_per_az_work = static_cast<int>(std::ceil(static_cast<double>(min_working_nodes_disaster) / (m - 1)));

    // Повний розмір зони з локальним резервом (N+k)
    const int nodes_per_az_total = nodes_per_az_work + resilience.extra_nodes_per_az;
    const int total_nodes = nodes_per_az_total * m;

    // 3. Аналіз штатного стану (Normal State)
    const double total_cluster_capacity_rps = total_nodes * node.capacity_rps;
    const double steady_util = peak_rps / total_cluster_capacity_rps;
    const double steady_headroom = 1.0 - steady_util;

    // 4. Аналіз катастрофічного стану (1 AZ Outage)
    const int surviving_nodes = nodes_per_az_total * (m - 1);
    const double disaster_capacity_rps = surviving_nodes * node.capacity_rps;
    const double disaster_util = peak_rps / disaster_capacity_rps;
    const double disaster_headroom = 1.0 - disaster_util;

    // 5. Розрахунок затримок черг
    const double steady_p99 = calculate_p99_queue_delay(node.service_time_ms, steady_util);
    const double disaster_p99 = calculate_p99_queue_delay(node.service_time_ms, disaster_util);
    const bool is_safe = disaster_util <= node.max_safe_util;

    return CapacityPlan{
        .forecast_peak_rps = peak_rps,
        .total_nodes = total_nodes,
        .nodes_per_az = nodes_per_az_total,
        .steady_state_util = steady_util,
        .steady_state_headroom = steady_headroom,
        .disaster_util = disaster_util,
        .disaster_headroom = disaster_headroom,
        .steady_p99_latency_ms = steady_p99,
        .disaster_p99_latency_ms = disaster_p99,
        .is_slo_safe = is_safe
    };
}

void print_report(const CapacityPlan& plan) {
    std::cout << "====================================================================\n";
    std::cout << "           ЗВІТ ПЛАНУВАННЯ ПОТУЖНОСТЕЙ ТА HEADROOM (C++20)\n";
    std::cout << "====================================================================\n";
    std::cout << "Прогнозований піковий трафік : " << plan.forecast_peak_rps << " RPS\n";
    std::cout << "Загальна кількість вузлів     : " << plan.total_nodes 
              << " (по " << plan.nodes_per_az << " у кожній з зон)\n";
    std::cout << "--------------------------------------------------------------------\n";
    std::cout << "ШТАТНИЙ РЕЖИМ (УСІ ЗОНИ ПРАЦЮЮТЬ):\n";
    std::cout << "  • Утилізація кластера       : " << (plan.steady_state_util * 100.0) << "%\n";
    std::cout << "  • Запас міцності (Headroom) : " << (plan.steady_state_headroom * 100.0) << "%\n";
    std::cout << "  • Оцінка p99 затримки черги : " << plan.steady_p99_latency_ms << " мс\n";
    std::cout << "--------------------------------------------------------------------\n";
    std::cout << "СТРЕС-СЦЕНАРІЙ (АВАРІЯ 1 ЗОНИ ДОСТУПНОСТІ):\n";
    std::cout << "  • Утилізація вцілілих зон   : " << (plan.disaster_util * 100.0) << "%\n";
    std::cout << "  • Залишковий Headroom       : " << (plan.disaster_headroom * 100.0) << "%\n";
    std::cout << "  • Оцінка p99 затримки черги : " << plan.disaster_p99_latency_ms << " мс\n";
    std::cout << "--------------------------------------------------------------------\n";
    const std::string_view status_str = plan.is_slo_safe ? "✓ БЕЗПЕЧНО (SLO ДОТРИМАНО)" : "✖ НЕБЕЗПЕКА (РИЗИК КОЛАПСУ)";
    std::cout << "ПІДСУМКОВИЙ СТАТУС НАДІЙНОСТІ : " << status_str << "\n";
    std::cout << "====================================================================\n";
}

int main() {
    const WorkloadProfile workload{
        .base_rps = 5000.0,
        .diurnal_factor = 1.6,
        .burst_factor = 1.2,
        .growth_rate_pct = 8.0,
        .months_ahead = 3
    };

    const NodeProfile node{
        .capacity_rps = 350.0,
        .service_time_ms = 2.8,
        .max_safe_util = 0.75
    };

    const ResilienceConfig resilience{
        .availability_zones = 3,
        .extra_nodes_per_az = 1
    };

    const CapacityPlan plan = plan_capacity(workload, node, resilience);
    print_report(plan);

    return 0;
}

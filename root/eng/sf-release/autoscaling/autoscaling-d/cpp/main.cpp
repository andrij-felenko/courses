#include <iostream>
#include <cmath>
#include <algorithm>

// Розрахунок горизонтального масштабування HTTP-сервісу
int calculate_http_replicas(int current_replicas,
                           double current_metric,
                           double target_metric,
                           double tolerance,
                           int min_rep,
                           int max_rep) {
    double ratio = current_metric / target_metric;
    if (std::abs(ratio - 1.0) <= tolerance) {
        return current_replicas; // Усередині зони нечутливості
    }
    int desired = static_cast<int>(std::ceil(current_replicas * ratio));
    return std::clamp(desired, min_rep, max_rep);
}

// Розрахунок пулу воркерів для черги за дедлайном
int calculate_queue_workers(long long queue_lag,
                            double arrival_rate_rps,
                            double task_duration_sec,
                            double target_drain_time_sec,
                            int max_workers) {
    if (queue_lag <= 0 && arrival_rate_rps <= 0.0) {
        return 0; // Масштабування до нуля (Scale-to-Zero)
    }
    double total_tasks = static_cast<double>(queue_lag) + arrival_rate_rps * target_drain_time_sec;
    double tasks_per_worker = target_drain_time_sec / task_duration_sec;
    int desired = static_cast<int>(std::ceil(total_tasks / tasks_per_worker));
    return std::min(desired, max_workers);
}

int main() {
    int http_pool = calculate_http_replicas(8, 88.0, 65.0, 0.10, 4, 20);
    int worker_pool = calculate_queue_workers(45000, 250.0, 0.12, 60.0, 200);

    std::cout << "HTTP API target replicas: " << http_pool << " (очікується 11)\n";
    std::cout << "Queue Workers target pool: " << worker_pool << " (очікується 120)\n";
    return 0;
}

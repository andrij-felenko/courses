#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cmath>
#include <algorithm>
#include <optional>
#include <array>

enum class ComputePlatform {
    ServerlessFargate,
    ManagedKubernetes,
    BareMetalVM
};

std::string_view to_string(ComputePlatform platform) noexcept {
    switch (platform) {
        case ComputePlatform::ServerlessFargate: return "Serverless / Fargate";
        case ComputePlatform::ManagedKubernetes: return "Managed Kubernetes (EKS/GKE)";
        case ComputePlatform::BareMetalVM:       return "Bare Metal / Dedicated VM";
    }
    return "Unknown";
}

struct WorkloadMetrics {
    std::string name;
    double p99_max_latency_ms{100.0};
    double avg_utilization_pct{20.0};
    bool is_stateful_grpc{false};
    double max_execution_minutes{5.0};
    bool requires_custom_kernel_gpu{false};
    int team_ops_capacity_score{5}; // 1 (no ops) to 10 (dedicated platform team)
};

struct PlatformScore {
    ComputePlatform platform;
    double score{0.0};
    std::vector<std::string> rationale;
};

class ComputeDecisionEngine {
public:
    [[nodiscard]] static PlatformScore evaluate(const WorkloadMetrics& w) {
        double serverless_score = 50.0;
        double k8s_score        = 50.0;
        double baremetal_score  = 50.0;

        std::vector<std::string> serverless_notes;
        std::vector<std::string> k8s_notes;
        std::vector<std::string> baremetal_notes;

        // 1. Оцінка чутливості до затримки (Cold Start penalty)
        if (w.p99_max_latency_ms < 10.0) {
            serverless_score -= 45.0;
            serverless_notes.push_back("Штраф: Сувора вимоглавість p99 < 10ms несумісна з Cold Start");
            baremetal_score += 25.0;
            baremetal_notes.push_back("Бонус: Прямий запуск на залізі дає мінімальний p99 jitter");
        } else if (w.p99_max_latency_ms < 50.0) {
            serverless_score -= 20.0;
            serverless_notes.push_back("Застереження: Cold start може перевищувати поріг 50ms");
            k8s_score += 15.0;
        }

        // 2. Оцінка утилізації та профілю навантаження
        if (w.avg_utilization_pct < 15.0) {
            serverless_score += 35.0;
            serverless_notes.push_back("Бонус: Низька утилізація (<15%) економічно ідеальна для Pay-per-use");
            baremetal_score -= 30.0;
            baremetal_notes.push_back("Штраф: Простій заліза спалює бюджет (Idle Penalty)");
        } else if (w.avg_utilization_pct > 65.0) {
            baremetal_score += 35.0;
            baremetal_notes.push_back("Бонус: Висока утилізація (>65%) робить Bare Metal найдешевшим за 1 core");
            k8s_score += 20.0;
            serverless_score -= 35.0;
            serverless_notes.push_back("Штраф: 24/7 висока утилізація в Serverless перетворюється на астрономічні рахунки");
        } else {
            k8s_score += 30.0;
            k8s_notes.push_back("Бонус: Помірне навантаження (15-65%) ідеально покривається HPA/KEDA");
        }

        // 3. Stateful gRPC та довжини виконання
        if (w.is_stateful_grpc) {
            serverless_score -= 50.0;
            serverless_notes.push_back("Дискваліфікація: Довгоживучі TCP/gRPC стрими не підтримуються функціями");
            k8s_score += 20.0;
            baremetal_score += 20.0;
        }

        if (w.max_execution_minutes > 15.0) {
            serverless_score -= 50.0;
            serverless_notes.push_back("Дискваліфікація: Перевищено ліміт часу виконання ефемерних функцій (15 хв)");
        }

        // 4. Кастомні ядра, DPDK, GPU
        if (w.requires_custom_kernel_gpu) {
            serverless_score -= 40.0;
            serverless_notes.push_back("Штраф: Відсутній доступ до фізичного GPU/eBPF/DPDK");
            baremetal_score += 30.0;
            baremetal_notes.push_back("Бонус: Прямий доступ до PCIe пристроїв та ядерних модулів");
        }

        // 5. Операційне навантаження команди (Ops Capacity)
        if (w.team_ops_capacity_score < 4) {
            baremetal_score -= 40.0;
            baremetal_notes.push_back("Штраф: Відсутній Ops-ресурс для підтримки заліза та мереж");
            k8s_score -= 15.0;
            serverless_score += 25.0;
            serverless_notes.push_back("Бонус: Нульове обслуговування інфраструктури (NoOps)");
        } else if (w.team_ops_capacity_score >= 8) {
            k8s_score += 15.0;
            baremetal_score += 15.0;
        }

        // Знаходження переможця
        std::array<PlatformScore, 3> results{{
            {ComputePlatform::ServerlessFargate, serverless_score, std::move(serverless_notes)},
            {ComputePlatform::ManagedKubernetes, k8s_score, std::move(k8s_notes)},
            {ComputePlatform::BareMetalVM, baremetal_score, std::move(baremetal_notes)}
        }};

        auto best = std::max_element(results.begin(), results.end(),
            [](const PlatformScore& a, const PlatformScore& b) {
                return a.score < b.score;
            });

        return *best;
    }
};

int main() {
    WorkloadMetrics ingest_stream{
        "IoT Telemetry Ingestion",
        2.0,   // p99 < 2ms
        80.0,  // util 80%
        true,  // stateful gRPC
        1440.0,// 24h streams
        true,  // eBPF custom driver
        8      // strong ops team
    };

    auto choice = ComputeDecisionEngine::evaluate(ingest_stream);
    std::cout << "Workload: " << ingest_stream.name << "\n";
    std::cout << "Recommended Platform: " << to_string(choice.platform) << " (Score: " << choice.score << ")\n";
    std::cout << "Rationale:\n";
    for (const auto& note : choice.rationale) {
        std::cout << " - " << note << "\n";
    }
    return 0;
}

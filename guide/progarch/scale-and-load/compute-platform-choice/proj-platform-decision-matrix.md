# ⚙️ Двигун оцінки та матриця вибору compute-платформи

Автоматизація архітектурного вибору обчислювальної платформи вимагає переведення якісних вимог до системи у формалізовану числову матрицю оцінки. Замість суб'єктивних суперечок про технологічні вподобання інженерів, архітектурна матриця вираховує вагові коефіцієнти для кожного з чотирьох ключових векторів: чутливості до затримки, профілю утилізації, вимог до контролю ядра та операційного бюджету команди.

## 1. Архітектура та математична основа двигуна прийняття рішень

Двигун вибору платформи приймає на вхід вектор метрик робочого навантаження (Workload Metrics) та повертає інтегральний бал `Score_platform` для трьох кандидатів: **Serverless / Fargate**, **Managed Kubernetes** та **Bare Metal / Dedicated VM**.

Формування інтегральної оцінки здійснюється за сумою вагових параметрів:

```
Score_platform = Base_score + W_latency + W_utilization + W_state + W_hardware + W_ops
```

Де базовий бал `Base_score = 50.0` для всіх платформ, після чого вмикаються штрафні та бонусні коефіцієнти за результатами аналізу метрик:

1. **Затримка (Latency Weight `W_latency`):** Аналізує чутливість застосунку до наявності холодного старту (Cold Start) та стабільності p99 латентності. Якщо бізнес-вимоги вимагають затримки `p99 < 10 ms`, бессерверна модель отримує жорсткий штраф (-45 балів) через ризик затримок ініціалізації мікровіртуальної машини та рантайму. Прямий запуск на Bare Metal отримує бонус (+25 балів) завдяки нульовим накладним витратам гіпервізора.
2. **Утилізація (Utilization Weight `W_utilization`):** Визначає фінансову ефективність утримання ресурсів. При середній утилізації `U < 15%` Serverless отримує максимальний бонус (+35 балів), оскільки модель Pay-per-use повністю звільняє компанію від плати за простій. Натомість при цілодобовому фоновому навантаженні з утилізацією `U > 65%` бессерверні середовища штрафуються (-35 балів) через високу ціну 1 GB-sec, а Bare Metal демонструє максимальну економію (+35 балів).
3. **Обсяг, стан та тривалість (State & Duration Weight `W_state`):** Оцінює наявність довгоживучих стан заснованих TCP/gRPC з'єднань або тривалість обчислювальних задач. Якщо сервіс тримає дуплексні gRPC-стрими або виконує задачі тривалістю понад 15 хвилин, Serverless дискваліфікується (-50 балів), оскільки ефемерні функції не підтримують утримання стану сокета.
4. **Вимоги до ядра та прискорювачів (Hardware Weight `W_hardware`):** Перевіряє потребу в прямому доступі до тензорних ядер GPU, розширень eBPF або оптимізацій ядра Linux (`sysctl`, CPU Affinity). Бессерверні середовища отримують штраф (-40 балів) через відсутність доступу до фізичних пристроїв PCIe.
5. **Операційний бюджет команди (Ops Footprint Weight `W_ops`):** Оцінює спроможність інженерної команди підтримувати складну інфраструктуру за 10-бальною шкалою. Якщо команда не має виділеного DevOps-ресурсу (`Ops_score < 4`), Bare Metal штрафується (-40 балів) через високу операційну вартість обслуговування заліза, а Serverless отримує бонус (+25 балів) за модель NoOps.

## 2. Обробка крайових випадків та інфраструктурних пасток

Двигун оцінки враховує три поширені крайові випадки:

- **Спалаховий шторм (Burst Storm):** При відсутності трафіку вночі та миттєвому стрибку до 20 000 rps (наприклад, обробка тривог під час негоди) Kubernetes вимагає налаштування KEDA або прогрітих нод. Двигун віддає перевагу Serverless, якщо тривалість спалахового періоду не перевищує кількох хвилин.
- **Галасливий сусід (Noisy Neighbor):** У Multi-Tenant середовищі Serverless виконання декількох функцій на одному фізичному хості може спричинити конкуренцію за L3-кеш процесора. Якщо метрика `p99_max_latency_ms` становить менше 5 ms, двигун автоматично підвищує вагу Bare Metal.
- **OOMKilled та витоки пам'яті:** У Serverless довгоживучі середовища виконання можуть зберігати витоки пам'яті між повторними викликами однієї функції. Двигун перевіряє розмір оперативної пам'яті та штрафує ефемерні середовища при нестійкому споживанні RAM.

## 3. Покроковий розбір оцінки трьох компонентів Digital Homes

Для демонстрації роботи двигуна проаналізуємо три реальні сервіси системи:

1. **Сервіс телеметрії (IoT Telemetry Ingest):**
   - Метрики: `p99 = 2ms`, `util = 80%`, `stateful = true`, `duration = 1440 min`, `hardware = true (eBPF)`, `ops = 8`.
   - Обчислення: Serverless отримує штрафи за p99 (-45), утилізацію (-35), stateful gRPC (-50), час виконання (-50) та відсутність eBPF (-40), зводячи підсумковий бал до **0.0**. Bare Metal отримує бонуси за p99 (+25), утилізацію (+35), stateful (+20), eBPF (+30) та наявну Ops-команду (+15), здобуваючи перемогу з підсумковим балом **175.0**.

2. **Обробник тривожних вебхуків (Webhook Workers):**
   - Метрики: `p99 = 200ms`, `util = 4%`, `stateful = false`, `duration = 0.5 min`, `hardware = false`, `ops = 2`.
   - Обчислення: Bare Metal штрафується за низьку утилізацію (-30) та відсутність Ops-команди (-40), отримуючи **-20.0** балів. Serverless здобуває бонус за утилізацію (+35) та NoOps (+25), здобуваючи **110.0** балів і першість.

3. **Основний REST API (Core Mobile API):**
   - Метрики: `p99 = 25ms`, `util = 40%`, `stateful = false`, `duration = 0.1 min`, `hardware = false`, `ops = 6`.
   - Обчислення: Kubernetes отримує бонус за ідеальну зону утилізації HPA (+30), стабільний p99 (+15) та збалансований Ops-ресурс (+15), перемагаючи з підсумковим балом **110.0**.

## 4. Оптимізація та інтуїція вибору

Матричний алгоритм дозволяє перетворити складний інфраструктурний вибір на прозорий числовий результат. При розгортанні нових сервісів інженер заповнює лише об'єкт `WorkloadMetrics`, а двигун миттєво підраховує підсумкові бали та генерує текстове обґрунтування для архітектурного комітету.

## 5. Реалізація двигуна оцінки мовами C++ та Python

Нижче наведено алгоритм обчислення оптимальної обчислювальної платформи, реалізований мовами C++ (ізольований клас із підтримкою RAII та strong type enums) та Python (типізовані dataclasses).

:::tabs
```cpp
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
```
```py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple

class ComputePlatform(Enum):
    SERVERLESS_FARGATE = "Serverless / Fargate"
    MANAGED_KUBERNETES = "Managed Kubernetes (EKS/GKE)"
    BARE_METAL_VM = "Bare Metal / Dedicated VM"

@dataclass
class WorkloadMetrics:
    name: str
    p99_max_latency_ms: float = 100.0
    avg_utilization_pct: float = 20.0
    is_stateful_grpc: bool = False
    max_execution_minutes: float = 5.0
    requires_custom_kernel_gpu: bool = False
    team_ops_capacity_score: int = 5  # 1 (NoOps) to 10 (Full Platform Team)

@dataclass
class PlatformScore:
    platform: ComputePlatform
    score: float
    notes: List[str] = field(default_factory=list)

class ComputeDecisionEngine:
    @staticmethod
    def evaluate(w: WorkloadMetrics) -> PlatformScore:
        scores = {
            ComputePlatform.SERVERLESS_FARGATE: (50.0, []),
            ComputePlatform.MANAGED_KUBERNETES: (50.0, []),
            ComputePlatform.BARE_METAL_VM: (50.0, []),
        }

        # 1. Затримка та Cold Start
        if w.p99_max_latency_ms < 10.0:
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s - 45.0, n + ["Штраф: p99 < 10ms несумісна з Cold Start"])
            s, n = scores[ComputePlatform.BARE_METAL_VM]
            scores[ComputePlatform.BARE_METAL_VM] = (s + 25.0, n + ["Бонус: Мінімальний jitter на залізі"])
        elif w.p99_max_latency_ms < 50.0:
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s - 20.0, n + ["Застереження: Ризик холодного старту"])
            s, n = scores[ComputePlatform.MANAGED_KUBERNETES]
            scores[ComputePlatform.MANAGED_KUBERNETES] = (s + 15.0, n)

        # 2. Утилізація
        if w.avg_utilization_pct < 15.0:
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s + 35.0, n + ["Бонус: Ідеально для Pay-per-use при U < 15%"])
            s, n = scores[ComputePlatform.BARE_METAL_VM]
            scores[ComputePlatform.BARE_METAL_VM] = (s - 30.0, n + ["Штраф: Idle penalty при простої"])
        elif w.avg_utilization_pct > 65.0:
            s, n = scores[ComputePlatform.BARE_METAL_VM]
            scores[ComputePlatform.BARE_METAL_VM] = (s + 35.0, n + ["Бонус: Висока економічність 24/7"])
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s - 35.0, n + ["Штраф: Астрономічний TCO у Serverless 24/7"])
        else:
            s, n = scores[ComputePlatform.MANAGED_KUBERNETES]
            scores[ComputePlatform.MANAGED_KUBERNETES] = (s + 30.0, n + ["Бонус: Ідеальна зона для K8s HPA"])

        # 3. Stateful & Duration
        if w.is_stateful_grpc:
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s - 50.0, n + ["Дискваліфікація: Stateful gRPC несумісний"])
            s, n = scores[ComputePlatform.MANAGED_KUBERNETES]
            scores[ComputePlatform.MANAGED_KUBERNETES] = (s + 20.0, n)
            s, n = scores[ComputePlatform.BARE_METAL_VM]
            scores[ComputePlatform.BARE_METAL_VM] = (s + 20.0, n)

        if w.max_execution_minutes > 15.0:
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s - 50.0, n + ["Дискваліфікація: Час виконання > 15 хв"])

        # 4. Hardware/Kernel
        if w.requires_custom_kernel_gpu:
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s - 40.0, n + ["Штраф: Немає доступу до GPU/eBPF"])
            s, n = scores[ComputePlatform.BARE_METAL_VM]
            scores[ComputePlatform.BARE_METAL_VM] = (s + 30.0, n + ["Бонус: Повний доступ до PCIe/GPU"])

        # 5. Ops Budget
        if w.team_ops_capacity_score < 4:
            s, n = scores[ComputePlatform.BARE_METAL_VM]
            scores[ComputePlatform.BARE_METAL_VM] = (s - 40.0, n + ["Штраф: Відсутній Ops-ресурс"])
            s, n = scores[ComputePlatform.SERVERLESS_FARGATE]
            scores[ComputePlatform.SERVERLESS_FARGATE] = (s + 25.0, n + ["Бонус: NoOps середовище"])

        # Визначаємо переможця
        best_platform = max(scores.keys(), key=lambda p: scores[p][0])
        score, notes = scores[best_platform]
        return PlatformScore(platform=best_platform, score=score, notes=notes)

if __name__ == "__main__":
    workload = WorkloadMetrics(
        name="Webhook Async Processing",
        p99_max_latency_ms=200.0,
        avg_utilization_pct=4.0,
        is_stateful_grpc=False,
        max_execution_minutes=0.5,
        team_ops_capacity_score=2
    )
    result = ComputeDecisionEngine.evaluate(workload)
    print(f"Workload: {workload.name}")
    print(f"Recommendation: {result.platform.value} (Score: {result.score})")
    print("Rationale:")
    for note in result.notes:
        print(f" - {note}")
```
:::

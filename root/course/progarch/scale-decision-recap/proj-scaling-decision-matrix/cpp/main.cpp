#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <optional>
#include <algorithm>
#include <iomanip>

// Перелік стратегій масштабування
enum class ScaleStrategy {
    ProfileAndOptimizeCode,  // Важіль 1: Профілювання та індекси
    EnableCachingAndReplicas, // Важіль 2: Кешування та Read Replicas
    VerticalScaleUp,         // Важіль 3: Вертикальний Scale-Up вузла
    HorizontalSharding,      // Важіль 4: Горизонтальний шардинг даних
    CellBasedMultiRegion     // Важіль 5: Коміркова топологія та мультирегіон
};

// Метрики поточного стану системи
struct SystemMetrics {
    double qps{0.0};                 // Запитів на секунду (QPS)
    double read_ratio{0.8};          // Частка читання (0.0 ... 1.0)
    double p99_latency_ms{0.0};      // Перцентиль p99 затримки (ms)
    std::size_t cpu_cores{4};        // Кількість ядер CPU на вузол
    std::size_t ram_gb{16};          // Оперативна пам'ять (GB)
    double disk_write_iops{0.0};     // Операцій запису на диск за секунду
    std::size_t sre_team_size{2};    // Кількість SRE / DevOps інженерів
    bool has_profiling_done{false};  // Чи проводилося профілювання коду
    bool strict_blast_radius{false}; // Вимога до мінімізації радіуса ураження
};

// Результат оцінки та обґрунтування
struct AssessmentResult {
    ScaleStrategy recommended_strategy;
    std::string strategy_name;
    std::string primary_rationale;
    double estimated_tco_monthly_usd{0.0};
    double expected_throughput_gain_x{1.0};
    std::vector<std::string> action_plan_steps;
};

class ScalingDecisionEngine {
public:
    [[nodiscard]] AssessmentResult evaluate(const SystemMetrics& metrics) const {
        AssessmentResult result;

        // Фільтр 1: Перевірка потреби у профілюванні коду
        if (!metrics.has_profiling_done && (metrics.qps < 10'000.0 || metrics.p99_latency_ms > 100.0)) {
            result.recommended_strategy = ScaleStrategy::ProfileAndOptimizeCode;
            result.strategy_name = "Важіль 1: Профілювання коду та оптимізація SQL";
            result.primary_rationale = "Низький QPS або висока затримка без проведеного профілювання свідчить про наявність N+1 запитів, відсутність індексів або витоки пам'яті.";
            result.estimated_tco_monthly_usd = 0.0;
            result.expected_throughput_gain_x = 10.0;
            result.action_plan_steps = {
                "Підключити eBPF / pprof профайлер для аналізу CPU allocation hot-paths.",
                "Провести EXPLAIN ANALYZE для усіх SQL-запитів із тривалістю понад 10 ms.",
                "Додати пропущені складені індекси та усунути N+1 виклики в ORM."
            };
            return result;
        }

        // Фільтр 2: Read-Heavy навантаження та кешування
        if (metrics.read_ratio >= 0.75 && metrics.qps >= 5'000.0 && metrics.disk_write_iops < 15'000.0) {
            result.recommended_strategy = ScaleStrategy::EnableCachingAndReplicas;
            result.strategy_name = "Важіль 2: Багатоярусне кешування та Read Replicas";
            result.primary_rationale = "Переважання читання (> 75%) дозволяє зняти до 95% навантаження з баз даних шляхом впровадження L1 in-memory кешу та L2 Redis cluster.";
            result.estimated_tco_monthly_usd = 800.0;
            result.expected_throughput_gain_x = 8.0;
            result.action_plan_steps = {
                "Впровадити L1 Process Memory cache (LRU) для гарячих словників та конфігів.",
                "Розгорнути кластер Redis L2 для об'єктів із TTL та публікації інвалідацій.",
                "Налаштувати Read Replicas для бази даних та винести read-only транзакції."
            };
            return result;
        }

        // Фільтр 3: Запас вертикального масштабування (Scale-Up)
        if (metrics.cpu_cores < 128 && metrics.ram_gb < 512 && metrics.sre_team_size <= 4) {
            result.recommended_strategy = ScaleStrategy::VerticalScaleUp;
            result.strategy_name = "Важіль 3: Вертикальне розширення вузлів (Scale-Up)";
            result.primary_rationale = "Система не досягла межі заліза (128 cores / 512GB RAM), а мала команда SRE робить горизонтальне розбиття економічно недоцільним.";
            result.estimated_tco_monthly_usd = 2'200.0;
            result.expected_throughput_gain_x = 4.0;
            result.action_plan_steps = {
                "Оновити специфікацію екземпляра до 64-128 vCPU та 256-512GB RAM.",
                "Мігрувати дисковий масив на NVMe з гарантованими 60,000+ Write IOPS.",
                "Збільшити розміри сокетних буферів ядра та pool_size бази даних."
            };
            return result;
        }

        // Фільтр 5: Вимоги до суворого blast radius або мультирегіону
        if (metrics.strict_blast_radius || metrics.qps > 200'000.0) {
            result.recommended_strategy = ScaleStrategy::CellBasedMultiRegion;
            result.strategy_name = "Важіль 5: Коміркова архітектура (Cells) та Мультирегіон";
            result.primary_rationale = "Обмеження радіуса ураження до < 1% або ультра-високе навантаження вимагають розбиття інфраструктури на автономні штампи (Cells).";
            result.estimated_tco_monthly_usd = 25'000.0;
            result.expected_throughput_gain_x = 20.0;
            result.action_plan_steps = {
                "Спроектувати Cell-Router для маршрутизації трафіку на основі Tenant ID.",
                "Розбити базу даних та обчислення на автономні штампи інфраструктури.",
                "Впровадити асинхронну репліку між регіонами для Disaster Recovery."
            };
            return result;
        }

        // Фільтр 4: За замовчуванням — Горизонтальний шардинг даних
        result.recommended_strategy = ScaleStrategy::HorizontalSharding;
        result.strategy_name = "Важіль 4: Горизонтальний шардинг баз даних (Scale-Out)";
        result.primary_rationale = "Високий потік записів та насичення ресурсів одного вузла вимагають партиціонування бази даних за ключем шардування.";
        result.estimated_tco_monthly_usd = 12'000.0;
        result.expected_throughput_gain_x = 6.0;
        result.action_plan_steps = {
            "Обрати стабільний ключ шардування (Tenant ID / User ID) з рівномірним розподілом.",
            "Розгорнути sharding proxy (Vitess, Citus або власне хеш-кільце).",
            "Забезпечити відсутність крос-шардових ACID-транзакцій у гарячих шляхах."
        };

        return result;
    }
};

int main() {
    SystemMetrics metrics;
    metrics.qps = 25'000.0;
    metrics.read_ratio = 0.85;
    metrics.p99_latency_ms = 45.0;
    metrics.cpu_cores = 16;
    metrics.ram_gb = 64;
    metrics.disk_write_iops = 8'000.0;
    metrics.sre_team_size = 2;
    metrics.has_profiling_done = true;
    metrics.strict_blast_radius = false;

    ScalingDecisionEngine engine;
    AssessmentResult assessment = engine.evaluate(metrics);

    std::cout << "========================================================\n";
    std::cout << "    ЗВІТ ДІАГНОСТИЧНОГО КАЛЬКУЛЯТОРА МАСШТАБУВАННЯ      \n";
    std::cout << "========================================================\n";
    std::cout << "Рекомендована стратегія: " << assessment.strategy_name << "\n\n";
    std::cout << "Обґрунтування: " << assessment.primary_rationale << "\n\n";
    std::cout << "Оціночна вартість TCO: $" << std::fixed << std::setprecision(2) 
              << assessment.estimated_tco_monthly_usd << " / місяць\n";
    std::cout << "Очікуваний прирост пропускної здатності: " 
              << assessment.expected_throughput_gain_x << "x\n\n";
    std::cout << "План дій:\n";
    for (std::size_t i = 0; i < assessment.action_plan_steps.size(); ++i) {
        std::cout << "  " << (i + 1) << ". " << assessment.action_plan_steps[i] << "\n";
    }
    std::cout << "========================================================\n";

    return 0;
}

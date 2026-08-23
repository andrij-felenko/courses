# ⚙️ Практичний калькулятор та матриця прийняття рішень щодо масштабування

Ця вставка містить практичну реалізацію інструментарію автоматизованої діагностики та матриці прийняття рішень щодо стратегії масштабування. Програма приймає поточні телеметричні метрики системи (QPS, співвідношення читань і записів, перцентиль p99 затримки, утилізацію RAM та дискових IOPS, а також розмір команди розробки) і будує кількісний вектор рекомендацій: від оптимізації коду та розгортання кешу до вертикального Scale-Up або комірчастого шардингу.

## Архітектурний дизайн діагностичного калькулятора

Розробка системного калькулятора масштабування базується на суворому послідовному аналізі п'яти фундаментальних важелів продуктивності. Замість того, щоб спиратися на суб'єктивні оцінки розробників чи маркетингові обіцянки постачальників хмарних рішень, калькулятор формалізує діагностичний процес у вигляді дерева розгалужених правил. Кожен рівень дерева перевіряє конкретні фізичні метрики системи та оцінює граничну вартість (TCO) і складність впровадження відповідних архітектурних змін.

Діагностичний рушій оцінює систему за п'ятьма послідовними фільтрами:

1. **Фільтр 1 (Code & Query Profiling — Профілювання та локальна оптимізація):** Перший рівень діагностики перевіряє, чи не є деградація продуктивності наслідком банальних неоптимальностей у коді або базі даних. Якщо засунуті метрики свідчать про високе навантаження на CPU при відносно низькому QPS (< 10,000 QPS) або якщо профілювання не проводилося зовсім, будь-які спроби додавати сервери є марнотратством. На даному етапі виявляються проблеми N+1 запитів у ORM, відсутні складені індекси, перевитрати пам'яті під час серіалізації JSON та аномальна контенція блокувань у гарячих секціях коду. Оптимізація на цьому рівні надає виграш у 10x–100x при нульових витратах на нове обладнання.

2. **Фільтр 2 (Caching & Read Offloading — Кешування та зняття читального навантаження):** Другий фільтр аналізує структуру трафіку. Для більшості інформаційних систем співвідношення запитів читання до запису (Read/Write Ratio) становить від 80/20 до 99/1. Якщо дискова система або первинна база даних зазнають високої утилізації, але потік записів є відносно низьким (< 15,000 write IOPS), калькулятор рекомендує впровадження багатоярусного кешування. Створення локального кешу процесів (L1 RAM cache) та кластера Redis/Memcached (L2 cache) разом із винесенням read-only запитів на Read Replicas дозволяє зняти до 95% трафіку з Origin DB.

3. **Фільтр 3 (Vertical Scale-Up — Вертикальне розширення вузлів):** Третій фільтр оцінює фізичний запас масштабування поточного сервера. Сучасні фізичні сервери (Bare-Metal) та великі хмарні екземпляри підтримують до 128–256 обчислювальних ядер CPU, 1–4 Терабайти оперативної пам'яті та дискові масиви NVMe PCIe Gen5 із продуктивністю понад 100,000–500,000 IOPS. Якщо поточні ресурси сервера далекі від цих меж (наприклад, 16 ядер та 64 Гігабайти RAM), а команда розробки й SRE є малою (до 4–5 осіб), вертикальний Scale-Up є найшвидшим, найдешевшим та найбезпечнішим шляхом. Він надає 2x–8x прирост продуктивності без зміни жодного рядка коду та без ризику втрати ACID-консистентності.

4. **Фільтр 4 (Data Sharding & Partitioning — Шардинг та партиціонування):** Четвертий рівень включається лише тоді, коли система досягає фізичних меж одного вузла: потік записів перевищує граничну спроможність послідовного запису у WAL-журнал (> 30,000–50,000 write IOPS), а оперативна пам'ять не може вмістити гарячий індекс бази даних. У цьому разі калькулятор рекомендує горизонтальний шардинг даних за ключем шардування (Tenant ID або User ID). Це вимагає відмови від крос-шардових ACID-транзакцій та впровадження шардувального проксі (Vitess, Citus) або хеш-кільця на рівні додатка.

5. **Фільтр 5 (Cell-Based & Multi-Region Topology — Коміркова архітектура та мультирегіон):** П'ятий фільтр призначений для систем планетарного масштабу або проєктів із найсуворішими вимогами до надійності. Якщо вимагається обмеження радіуса ураження збоїв (Blast Radius < 1% користувачів під час аварії) або надання глобальної затримки < 20 мілісекунд для клієнтів на різних континентах, калькулятор рекомендує розбиття інфраструктури на автономні штампи-комірки (Cells). Кожна комірка містить повний стек застосунку та власну базу даних для підмножини клієнтів.

## Метрики та фізичний підтекст порогів калькулятора

Кожен поріг у калькуляторі виправданий реальними фізичними характеристиками сучасного обладнання:

*   **Поріг QPS < 10,000:** Одне ядро сучасного x86 CPU здатне виконувати понад 100,000 простих операцій в секунду. Якщо сервіс на 16 ядрах просідає при 5,000 QPS, проблему спричинено не недостачею ядер, а неоптимальним кодом або блокуваннями.
*   **Співвідношення Read/Write >= 75%:** Операції читання є фундаментально ідемпотентними та безпечними для кешування, тоді як операції запису вимагають змагання за дисковий WAL-журнал та консенсус.
*   **Дискові IOPS > 30,000:** Порогове значення, при якому послідовний флаш WAL-буферів на одиночний NVMe накопичувач починає створювати контенцію на дисковому контролері.
*   **Розмір SRE команди <= 4 осіб:** Кількісне обмеження, що відображає операційну спроможність організації. Команда з 2–4 інженерів фізично не здатна обслуговувати кластер із 50+ мікросервісів, service mesh та розподілених баз даних без високого ризику вигорання та тривалих аварій (MTTR > 4 години).

## Послідовність підключення телеметричних метрик

Діагностичний рушій призначений для інтеграції у системні скрипти CI/CD та системи моніторингу (Prometheus, Grafana, OpenTelemetry). Збір вхідних метрик здійснюється з трьох джерел:

*   **Prometheus / OpenTelemetry:** Збір показників `qps` (через `rate(http_requests_total[5m])`), `read_ratio` (зіставлення `GET` проти `POST/PUT/DELETE` методів) та `p99_latency_ms` (через `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`).
*   **Linux System Telemetry (`/proc` та `sysfs`):** Збір утилізації CPU та пам'яті через `/proc/stat` та `/proc/meminfo`, а також аналіз затримок та IOPS дискової підсистеми через `/proc/diskstats`.
*   **Database Internal Stats:** Отримання показників `disk_write_iops` та тривалості транзакцій з системних представлень бази даних (наприклад, `pg_stat_database`, `pg_stat_bgwriter` у PostgreSQL або `SHOW GLOBAL STATUS` у MySQL).

## Реалізація калькулятора прийняття рішень

Нижче наведено робочу реалізацію діагностичного калькулятора мовами C++20 та Python.

:::tabs
```cpp
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
```
```py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List

class ScaleStrategy(Enum):
    PROFILE_AND_OPTIMIZE = auto()
    ENABLE_CACHING = auto()
    VERTICAL_SCALE_UP = auto()
    HORIZONTAL_SHARDING = auto()
    CELL_BASED_MULTI_REGION = auto()

@dataclass
class SystemMetrics:
    qps: float = 0.0
    read_ratio: float = 0.8
    p99_latency_ms: float = 0.0
    cpu_cores: int = 4
    ram_gb: int = 16
    disk_write_iops: float = 0.0
    sre_team_size: int = 2
    has_profiling_done: bool = False
    strict_blast_radius: bool = False

@dataclass
class AssessmentResult:
    recommended_strategy: ScaleStrategy
    strategy_name: str
    primary_rationale: str
    estimated_tco_monthly_usd: float
    expected_throughput_gain_x: float
    action_plan_steps: List[str] = field(default_factory=list)

class ScalingDecisionEngine:
    def evaluate(self, metrics: SystemMetrics) -> AssessmentResult:
        if not metrics.has_profiling_done and (metrics.qps < 10000.0 or metrics.p99_latency_ms > 100.0):
            return AssessmentResult(
                recommended_strategy=ScaleStrategy.PROFILE_AND_OPTIMIZE,
                strategy_name="Важіль 1: Профілювання коду та оптимізація SQL",
                primary_rationale="Низький QPS або висока затримка без профілювання свідчать про N+1 запити або пропущені індекси.",
                estimated_tco_monthly_usd=0.0,
                expected_throughput_gain_x=10.0,
                action_plan_steps=[
                    "Підключити eBPF/pprof профайлер для аналізу CPU allocation hot-paths.",
                    "Провести EXPLAIN ANALYZE для усіх SQL-запитів тривалістю понад 10 ms.",
                    "Усунути N+1 виклики в ORM та додати складені індекси."
                ]
            )

        if metrics.read_ratio >= 0.75 and metrics.qps >= 5000.0 and metrics.disk_write_iops < 15000.0:
            return AssessmentResult(
                recommended_strategy=ScaleStrategy.ENABLE_CACHING,
                strategy_name="Важіль 2: Багатоярусне кешування та Read Replicas",
                primary_rationale="Переважання читання (> 75%) дозволяє зняти до 95% навантаження з БД через L1/L2 кеш.",
                estimated_tco_monthly_usd=800.0,
                expected_throughput_gain_x=8.0,
                action_plan_steps=[
                    "Впровадити L1 Process Memory cache (LRU) для гарячих даних.",
                    "Розгорнути L2 Redis cluster для об'єктів з TTL.",
                    "Винести read-only транзакції на Read Replicas."
                ]
            )

        if metrics.cpu_cores < 128 and metrics.ram_gb < 512 and metrics.sre_team_size <= 4:
            return AssessmentResult(
                recommended_strategy=ScaleStrategy.VERTICAL_SCALE_UP,
                strategy_name="Важіль 3: Вертикальне розширення вузлів (Scale-Up)",
                primary_rationale="Система не досягла межі заліза (128 cores / 512GB RAM), а мала SRE команда робить Scale-Out недоцільним.",
                estimated_tco_monthly_usd=2200.0,
                expected_throughput_gain_x=4.0,
                action_plan_steps=[
                    "Оновити специфікацію вузла до 64-128 vCPU та 256-512GB RAM.",
                    "Мігрувати дисковий масив на high-iops NVMe накопичувачі.",
                    "Оптимізувати параметри ядра Linux та pool_size бази даних."
                ]
            )

        if metrics.strict_blast_radius or metrics.qps > 200000.0:
            return AssessmentResult(
                recommended_strategy=ScaleStrategy.CELL_BASED_MULTI_REGION,
                strategy_name="Важіль 5: Коміркова архітектура (Cells) та Мультирегіон",
                primary_rationale="Обмеження радіуса ураження до < 1% вимагає розбиття інфраструктури на автономні штампи (Cells).",
                estimated_tco_monthly_usd=25000.0,
                expected_throughput_gain_x=20.0,
                action_plan_steps=[
                    "Спроектувати Cell-Router на основі Tenant ID.",
                    "Розбити бази даних на автономні штампи інфраструктури.",
                    "Налаштувати асинхронну реплікацію для Disaster Recovery."
                ]
            )

        return AssessmentResult(
            recommended_strategy=ScaleStrategy.HORIZONTAL_SHARDING,
            strategy_name="Важіль 4: Горизонтальний шардинг баз даних (Scale-Out)",
            primary_rationale="Високий потік записів та насичення ресурсу одного вузла вимагають шардування бази даних.",
            estimated_tco_monthly_usd=12000.0,
            expected_throughput_gain_x=6.0,
            action_plan_steps=[
                "Обрати стабільний ключ шардування (Tenant ID).",
                "Розгорнути sharded proxy або distributed SQL engine.",
                "Усунути крос-шардові ACID-транзакції у гарячих шляхах."
            ]
        )

if __name__ == "__main__":
    metrics = SystemMetrics(
        qps=25000.0,
        read_ratio=0.85,
        p99_latency_ms=45.0,
        cpu_cores=16,
        ram_gb=64,
        disk_write_iops=8000.0,
        sre_team_size=2,
        has_profiling_done=True
    )
    engine = ScalingDecisionEngine()
    result = engine.evaluate(metrics)
    print(f"Стратегія: {result.strategy_name}")
    print(f"Обґрунтування: {result.primary_rationale}")
    print(f"Оцінка TCO: ${result.estimated_tco_monthly_usd:.2f}/mo")
```
:::

## Аналіз матриці прийняття рішень

Для закріплення алгоритму калькулятора, у наведеній нижче матриці зіставлено ключові інфраструктурні вектори із відповідними важелями масштабування.

| Вектор метрики | Важіль 1 (Профіль) | Важіль 2 (Кеш) | Важіль 3 (Scale-Up) | Важіль 4 (Шардинг) | Важіль 5 (Cells) |
|---|---|---|---|---|---|
| **Межа QPS** | < 10,000 | 10k – 100k | 20k – 100k | 100k – 500k | > 500k |
| **Співвідношення R/W** | Будь-яке | > 80/20 | Будь-яке | < 60/40 (Write-heavy) | Будь-яке |
| **Мінімальна SRE команда** | 0 осіб | 1 особа | 1–2 особи | 3–5 осіб | > 5 осіб |
| **Оцінка TCO у місяць** | $0 | $500 – $2,000 | $1,500 – $4,000 | $8,000 – $20,000 | > $25,000 |
| **Період окупності (ROI)** | Миттєво (дні) | Дні/тижні | Дні | Місяці | 6–12 місяців |

Справжньою практичною цінністю даного інструменту є усунення емоційного фактору під час вибору архітектури. Системна діагностика гарантує, що рішення про масштабування базується на математичному розрахунку TCO та фізичних межах накопичувачів, а не на сліпому наслідуванні трендів.

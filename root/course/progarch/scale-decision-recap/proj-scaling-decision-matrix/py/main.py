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

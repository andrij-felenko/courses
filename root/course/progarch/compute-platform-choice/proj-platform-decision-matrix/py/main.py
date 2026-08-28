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

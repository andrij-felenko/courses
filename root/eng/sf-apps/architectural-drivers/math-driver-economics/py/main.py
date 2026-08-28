from dataclasses import dataclass

@dataclass
class Tactic:
    name: str
    du: dict[str, float]           # приріст корисності ΔU по сценаріях
    cost: float                    # зусилля + податок-складності + експлуатація

def benefit(t: Tactic, weight: dict[str, float], mu: float) -> float:
    # вигода = (Σ ΔUⱼ · вагаⱼ) · ціна-корисності
    utility = sum(t.du.get(s, 0.0) * w for s, w in weight.items())
    return utility * mu

def roi(t: Tactic, weight: dict[str, float], mu: float) -> float:
    b = benefit(t, weight, mu)
    return (b - t.cost) / t.cost

def pick_under_budget(tactics, weight, mu, budget):
    # сортуємо за ROI спадно, беремо жадібно, доки вистачає бюджету
    ranked = sorted(tactics, key=lambda t: roi(t, weight, mu), reverse=True)
    chosen, spent = [], 0.0
    for t in ranked:
        if roi(t, weight, mu) <= 0:          # збиткову — ніколи
            continue
        if spent + t.cost <= budget:
            chosen.append(t.name)
            spent += t.cost
    return chosen, spent

weight = {"пік": 0.40, "відмова": 0.35, "провайдер": 0.25}
tactics = [
    Tactic("кеш+репліки", {"пік": 60, "відмова": 20}, cost=30),
    Tactic("синхронне",   {"пік": -6, "відмова": 60}, cost=40),
    Tactic("шар-провайдер", {"провайдер": 50},        cost=12),
    Tactic("мікросервіси", {"пік": 50, "відмова": 10, "провайдер": 35}, cost=150),
]
print(pick_under_budget(tactics, weight, mu=3.0, budget=45))
# (['шар-провайдер', 'кеш+репліки'], 42.0)

from dataclasses import dataclass
from collections.abc import Callable

@dataclass(frozen=True)
class Option:
    name: str
    max_throughput: int    # повідомлень/с без болю
    ops_cost_week: int     # людино-годин експлуатації на тиждень
    exactly_once: bool     # чи дає доставку «точно раз»

# Набір кандидатів — тримаємо ЖИВИМИ, поки факт не спростує
CANDIDATES = [
    Option("in-process",    max_throughput=2_000,     ops_cost_week=1,  exactly_once=False),
    Option("managed-queue", max_throughput=50_000,    ops_cost_week=3,  exactly_once=False),
    Option("kafka",         max_throughput=1_000_000, ops_cost_week=12, exactly_once=True),
]

Constraint = Callable[[Option], bool]  # факт = предикат: лишаємо тих, хто ВИТРИМАВ

def survivors(options: list[Option], facts: list[Constraint]) -> list[Option]:
    return [o for o in options if all(f(o) for f in facts)]

facts: list[Constraint] = []

facts.append(lambda o: o.max_throughput >= 20_000)   # виміряний пік навантаження
# лишились: managed-queue, kafka   (in-process відпав — доведено, не вгадано)

facts.append(lambda o: o.ops_cost_week <= 5)          # реальний бюджет експлуатації
# лишився: managed-queue          (kafka відпав — зайві витрати не окупились)

alive = survivors(CANDIDATES, facts)
assert [o.name for o in alive] == ["managed-queue"]
# один живий → рішення визріло саме, без ранньої ставки й переробки

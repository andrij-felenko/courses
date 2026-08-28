# dh_coupling_analyzer.py — Python версія аналізатора зчеплення
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

@dataclass
class ContextMetrics:
    resource_asymmetry: float
    deploy_autonomy: float
    fault_isolation: float
    compliance_wall: float

class BoundedContext:
    def __init__(self, name: str, metrics: ContextMetrics, tables: List[str]):
        self.name = name
        self.metrics = metrics
        self.tables = set(tables)

class CouplingAnalyzer:
    def __init__(self):
        self.contexts: Dict[str, BoundedContext] = {}
        self.table_map: Dict[str, str] = {}
        self.cross_joins: Dict[Tuple[str, str], int] = {}

    def register_context(self, ctx: BoundedContext):
        self.contexts[ctx.name] = ctx
        for table in ctx.tables:
            self.table_map[table] = ctx.name

    def process_sql(self, sql: str):
        if "JOIN" not in sql.upper():
            return
        
        # Спрощений парсинг таблиць
        words = sql.replace(",", " ").split()
        tables_found = [w for w in words if w in self.table_map]
        
        if len(tables_found) >= 2:
            ctx_a = self.table_map[tables_found[0]]
            ctx_b = self.table_map[tables_found[1]]
            
            if ctx_a != ctx_b:
                pair = tuple(sorted([ctx_a, ctx_b]))
                self.cross_joins[pair] = self.cross_joins.get(pair, 0) + 1

    def calculate_score(self, name: str) -> float:
        ctx = self.contexts[name]
        m = ctx.metrics
        
        total_joins = sum(count for pair, count in self.cross_joins.items() if name in pair)
        penalty = total_joins * 1.5
        
        return (2.5 * m.resource_asymmetry) + \
               (2.0 * m.deploy_autonomy) + \
               (3.0 * m.fault_isolation) + \
               (3.5 * m.compliance_wall) - \
               penalty

    def print_report(self):
        print("=== Результати сервіс-аудиту Digital Homes (Python) ===")
        for name in self.contexts:
            score = self.calculate_score(name)
            verdict = "🟢 ВИДІЛЯТИ СЕРВІС" if score >= 15.0 else "🔴 ЗАЛИШИТИ В МОНОЛІТІ"
            print(f"Домен: {name:<18} | Score: {score:6.1f} | Вердикт: {verdict}")

if __name__ == "__main__":
    analyzer = CouplingAnalyzer()
    analyzer.register_context(BoundedContext("dh-telemetry", ContextMetrics(9.5, 8.0, 4.0, 0.0), ["telemetry_events"]))
    analyzer.register_context(BoundedContext("dh-video", ContextMetrics(9.0, 6.0, 9.5, 0.0), ["video_feeds"]))
    analyzer.register_context(BoundedContext("dh-device-mgmt", ContextMetrics(3.0, 3.0, 2.0, 0.0), ["devices"]))
    analyzer.register_context(BoundedContext("dh-digital-twin", ContextMetrics(4.0, 4.0, 2.0, 0.0), ["device_states"]))

    analyzer.process_sql("SELECT * FROM device_states JOIN devices ON device_states.id = devices.id")
    analyzer.process_sql("SELECT * FROM device_states JOIN devices ON device_states.id = devices.id")

    analyzer.print_report()

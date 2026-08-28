# scripts/check_team_boundaries.py — Повний автоматичний інспектор меж топології
import sys
import os
import yaml
import json
from typing import Dict, List, Any

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def audit_sociotechnical_boundaries(topology_path: str, arch_graph_path: str) -> None:
    """
    Автоматична перевірка соціотехнічних меж у CI/CD.
    Перевіряє заборонені прямі доступ до баз даних, тривалість Collaboration 
    та когнітивне перевантаження команд.
    """
    if not os.path.exists(topology_path) or not os.path.exists(arch_graph_path):
        print(f"⚠️ Файли топології ({topology_path}) або графа ({arch_graph_path}) не знайдені!")
        sys.exit(1)

    topology = load_yaml(topology_path)
    graph = load_json(arch_graph_path)

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Мапування контекст -> команда
    context_to_team: Dict[str, str] = {}
    team_cognitive_limits: Dict[str, int] = {}
    team_context_counts: Dict[str, int] = {}

    for team in topology.get('teams', []):
        team_id = team['id']
        max_services = team.get('max_cognitive_capacity_services', 3)
        team_cognitive_limits[team_id] = max_services
        team_context_counts[team_id] = 0

        for ctx in team.get('domain_contexts', []):
            context_to_team[ctx] = team_id
            team_context_counts[team_id] += 1

    # 2. Перевірка когнітивного ліміту володіння контекстами
    for team_id, count in team_context_counts.items():
        limit = team_cognitive_limits.get(team_id, 3)
        if count > limit:
            errors.append(
                f"КОГНІТИВНЕ ПЕРЕВАНТАЖЕННЯ: Команда '{team_id}' володіє {count} контекстами "
                f"(встановлений суворий ліміт: {limit}). Необхідно розділити домен!"
            )

    # 3. Перевірка ребер графа залежностей
    for edge in graph.get('edges', []):
        source_ctx = edge.get('source_context')
        target_ctx = edge.get('target_context')
        edge_type = edge.get('type') # "api", "db_direct", "event"
        mode = edge.get('interaction_mode', 'x-as-a-service')
        duration_days = edge.get('collaboration_duration_days', 0)

        source_team = context_to_team.get(source_ctx, 'UNKNOWN_TEAM')
        target_team = context_to_team.get(target_ctx, 'UNKNOWN_TEAM')

        # Заборонено: прямий доступ до БД чужої команди
        if source_team != target_team and edge_type == 'db_direct':
            errors.append(
                f"КРИТИЧНА ЕРОЗІЯ: Контекст '{source_ctx}' (команда {source_team}) має прямий "
                f"доступ до БД контексту '{target_ctx}' (команда {target_team})! "
                f"Дозволено лише через API або Події."
            )

        # Заборонено: перевищення терміну Collaboration
        if mode == 'collaboration' and duration_days > 21:
            warnings.append(
                f"ТРИВАЛИЙ COLLABORATION: Взаємодія між {source_team} та {target_team} "
                f"триває {duration_days} днів (ліміт 21 день). Час фіксувати контракт X-as-a-Service!"
            )

    # Друк результатів
    print("=" * 60)
    print("РЕЗУЛЬТАТИ АУДИТУ СОЦІОТЕХНІЧНОЇ ТОПОЛОГІЇ КОМАНД")
    print("=" * 60)

    if warnings:
        print("\n⚠️ ПОПЕРЕДЖЕННЯ:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ ПОРУШЕННЯ СУВОРИХ ПРАВИЛ ТА ЕРОЗІЯ:")
        for e in errors:
            print(f"  - {e}")
        print("\nЗбірку валиться через порушення соціотехнічних меж!")
        sys.exit(1)

    print("\n✅ Соціотехнічні межі топології команд дотримано успішно!")

if __name__ == "__main__":
    audit_sociotechnical_boundaries("org-topology-dh.yaml", "architecture-graph.json")

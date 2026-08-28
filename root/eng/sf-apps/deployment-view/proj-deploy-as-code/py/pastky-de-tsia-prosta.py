from collections import defaultdict

def by_logical(entries: list[dict]) -> dict[str, dict]:
    groups: dict[str, dict] = defaultdict(lambda: {"copies": 0, "zones": set()})
    for e in entries:
        app = e["labels"]["app"]              # логічний контейнер, а не ім'я запису
        groups[app]["copies"] += e["replicas"]      # копії ДОДАЮТЬСЯ по записах
        groups[app]["zones"]  |= e["zones"]         # зони ОБ'ЄДНУЮТЬСЯ по записах
    return groups
# тепер {"api": {"copies": 4, "zones": {"eu-central-1a", "eu-central-1b"}}} → OK

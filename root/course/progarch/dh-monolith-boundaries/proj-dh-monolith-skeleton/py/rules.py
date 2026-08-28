# arch/rules.py — єдине джерело правди: дозволені РЕБРА графа
ALLOWED = {
    "control":       {"ids", "identity"},
    "twin":          {"ids", "identity"},
    "telemetry":     {"ids", "identity"},        # control знають лише через подію, не імпортом
    "automations":   {"ids", "identity", "twin"},
    "notifications": {"ids", "identity"},
    "billing":       {"ids", "identity"},        # НЕ control!
    "video":         {"ids", "identity"},
    "identity":      {"ids"},
    "ids":           set(),                       # ядро не залежить ні від кого
}
def forbidden_edges(graph):
    return [(mod, d) for mod, deps in graph.items() for d in deps - ALLOWED[mod]]

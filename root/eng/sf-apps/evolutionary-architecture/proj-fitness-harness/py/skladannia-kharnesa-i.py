import sys

def main() -> int:
    g = build_graph(Path("src"))                                # спільна основа для двох осей

    allowed = {("ui", "domain"), ("domain", "ports"), ("db", "ports")}
    b = Budget(max_p95_ms=200, max_artifact_kb=250)             # бюджети зі сценаріїв

    ffs = [
        layer_rule(g, allowed),    # вісь структури  (атомарна)
        acyclic(g),                # вісь форми графа (атомарна)
        budget(measure_live, b),   # осі швидкодії й постачання (цілісна)
    ]
    return run_harness(ffs)        # 0 пропускає, 1 валить конвеєр

if __name__ == "__main__":
    sys.exit(main())

def run_benchmark():
    # Перелік модулів різного розміру та складності
    target_modules = [
        "json",
        "urllib.request",
        "email",
        "xml.etree.ElementTree",
        "http.client",
        "zipfile",
        "difflib",
        "csv"
    ]

    print("=== 1. Жадібний (eager) імпорт модулів ===")
    t_start_eager = time.perf_counter_ns()
    eager_registry: Dict[str, Any] = {}
    for mod in target_modules:
        sys.modules.pop(mod, None)
        eager_registry[mod] = importlib.import_module(mod)
    t_end_eager = time.perf_counter_ns()
    eager_time_ms = (t_end_eager - t_start_eager) / 1_000_000.0
    print(f"Час синхронного завантаження {len(target_modules)} модулів: {eager_time_ms:.3f} мс")

    print("\n=== 2. Відкладений (lazy) імпорт ===")
    t_start_lazy = time.perf_counter_ns()
    lazy_registry: Dict[str, Any] = {}
    for mod in target_modules:
        sys.modules.pop(mod, None)
        lazy_registry[mod] = lazy_import(mod)
    t_end_lazy = time.perf_counter_ns()
    lazy_time_ms = (t_end_lazy - t_start_lazy) / 1_000_000.0
    print(f"Час створення {len(target_modules)} проксі-об'єктів: {lazy_time_ms:.3f} мс")

    speedup = eager_time_ms / max(lazy_time_ms, 0.001)
    print(f"\nПрискорення ініціалізації середовища: у {speedup:.1f} раза")

    print("\n=== 3. Перший виклик функції (фактичне завантаження) ===")
    print("Стан проксі до виклику:", lazy_registry["json"])
    t_call_start = time.perf_counter_ns()
    
    # Перше звернення до dumps ініціює реальний імпорт json
    serialized = lazy_registry["json"].dumps({"metric": "startup_latency", "optimized": True})
    t_call_end = time.perf_counter_ns()
    call_time_ms = (t_call_end - t_call_start) / 1_000_000.0

    print("Стан проксі після виклику:", lazy_registry["json"])
    print(f"Результат виконання: {serialized}")
    print(f"Час виконання першого звернення: {call_time_ms:.3f} мс")


if __name__ == "__main__":
    run_benchmark()

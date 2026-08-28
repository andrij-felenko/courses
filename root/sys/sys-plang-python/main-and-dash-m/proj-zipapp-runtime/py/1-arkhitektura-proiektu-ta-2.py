def format_text(metrics: dict[str, str | int]) -> str:
    """Перетворює словник метрик у читабельний текстовий звіт."""
    lines = [
        "=== ЗВІТ СИСТЕМНОГО МОНІТОРИНГУ ===",
        f"Платформа:       {metrics['platform']}",
        f"Версія Python:   {metrics['python_version']}",
        f"PID процесу:     {metrics['pid']}",
        f"Навантаження:    1хв={metrics['load_1m']:.2f}, 5хв={metrics['load_5m']:.2f}, 15хв={metrics['load_15m']:.2f}",
        "==================================",
    ]
    return "\n".join(lines)

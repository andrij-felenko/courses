def validate(cfg):
    problems = []
    if not cfg.get("db_url"):
        problems.append("DB_URL не задано")
    if not (1 <= cfg["port"] <= 65535):
        problems.append(f"port={cfg['port']} поза діапазоном 1..65535")
    if cfg["log_level"] not in ("debug", "info", "warn", "error"):
        problems.append(f"невідомий log_level={cfg['log_level']}")
    if problems:
        # усі помилки разом, а не по одній за запуск
        raise SystemExit("Конфіг непридатний:\n  " + "\n  ".join(problems))

import json

# ЯДРО, яке доводиться відкривати на КОЖЕН новий формат
def export_report(fmt: str, rows: list[dict]) -> str:
    if fmt == "csv":
        return to_csv(rows)
    if fmt == "json":
        return json.dumps(rows, ensure_ascii=False, indent=2)
    # ← новий формат = нова гілка ТУТ, у вже робочому ядрі
    raise ValueError(f"невідомий формат: {fmt}")

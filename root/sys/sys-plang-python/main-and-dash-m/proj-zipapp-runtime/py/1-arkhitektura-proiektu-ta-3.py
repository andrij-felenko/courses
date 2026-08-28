import sys
from monitor.collector import collect_metrics
from monitor.formatter import format_text


def main() -> int:
    """Точка входу автономного пакунка."""
    try:
        metrics = collect_metrics()
        output = format_text(metrics)
        print(output)
        return 0
    except Exception as err:
        sys.stderr.write(f"Помилка виконання монітора: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

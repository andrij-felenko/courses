# ПРАВИЛЬНО: повна ізоляція логіки виконання
import sys
import argparse


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Парсить параметри командного рядка."""
    parser = argparse.ArgumentParser(description="Мережевий мікросервіс")
    parser.add_argument("--port", type=int, default=8080, help="Порт сервера")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Головна точка входу: повертає числовий код завершення."""
    args = parse_arguments(argv)
    try:
        server = start_server(args.port)
        server.serve_forever()
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as err:
        sys.stderr.write(f"Фатальна помилка: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

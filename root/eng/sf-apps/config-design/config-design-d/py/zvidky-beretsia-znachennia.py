import os

def load_config():
    # 1. Найслабший пласт: типові значення просто в коді
    cfg = {"port": 3000, "log_level": "info", "db_url": "localhost:5432"}

    # 2. Спільний файл — те, що однакове скрізь
    cfg.update(read_yaml("config.yaml"))

    # 3. Файл конкретного середовища перекриває спільний
    env = os.environ.get("APP_ENV", "dev")
    cfg.update(read_yaml(f"config.{env}.yaml"))

    # 4. Змінні середовища сильніші за файли (сюди хмара кладе секрети)
    if "PORT" in os.environ:
        cfg["port"] = int(os.environ["PORT"])
    if "DB_URL" in os.environ:
        cfg["db_url"] = os.environ["DB_URL"]

    # 5. Аргумент рядка перебиває все — разове ручне втручання
    cfg.update(parse_cli_overrides())
    return cfg

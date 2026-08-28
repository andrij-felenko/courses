import base64
import csv
import hashlib
from pathlib import Path


def calculate_sha256_base64url(data: bytes) -> str:
    """Обчислити SHA-256 дайджест у форматі base64url без вирівнювання '='."""
    digest = hashlib.sha256(data).digest()
    # RFC 4648 urlsafe base64 з видаленням кінцевих '='
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def generate_record_for_wheel(root_dir: Path, dist_info_dirname: str) -> None:
    """Згенерувати валідний файл RECORD для вмісту каталогу колеса."""
    record_rel_path = f"{dist_info_dirname}/RECORD"
    rows: list[tuple[str, str, str | int]] = []

    # Обхід усіх файлів у дереві розпакованого пакета
    for file_path in sorted(root_dir.rglob("*")):
        if file_path.is_file():
            rel_path = file_path.relative_to(root_dir).as_posix()
            
            # Файл RECORD не фіксує власний хеш
            if rel_path == record_rel_path:
                continue

            file_bytes = file_path.read_bytes()
            hash_str = calculate_sha256_base64url(file_bytes)
            rows.append((rel_path, f"sha256={hash_str}", len(file_bytes)))

    # Додавання обов'язкового порожнього запису для самого RECORD
    rows.append((record_rel_path, "", ""))

    output_record_path = root_dir / dist_info_dirname / "RECORD"
    with open(output_record_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def verify_installed_record(root_dir: Path, dist_info_dirname: str) -> bool:
    """Перевірити цілісність встановленого пакета за даними файлу RECORD."""
    record_path = root_dir / dist_info_dirname / "RECORD"
    if not record_path.exists():
        raise FileNotFoundError(f"Файл маніфесту не знайдено: {record_path}")

    with open(record_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            rel_path, expected_hash, expected_size = row
            target_file = root_dir / rel_path

            # Пропуск запису самого RECORD
            if not expected_hash:
                continue

            if not target_file.exists():
                print(f"Помилка: відсутній файл {rel_path}")
                return False

            data = target_file.read_bytes()
            actual_size = str(len(data))
            algo, hash_val = expected_hash.split("=", 1)

            if algo != "sha256":
                print(f"Помилка: невідомий алгоритм хешування {algo}")
                return False

            actual_hash = calculate_sha256_base64url(data)
            if actual_hash != hash_val or actual_size != expected_size:
                print(f"Помилка цілісності: файл {rel_path} змінено на диску!")
                return False

    return True

#!/usr/bin/env python3
import os
import stat
import zipapp
from pathlib import Path


def build_standalone_zipapp(
    source_dir: str | Path,
    output_file: str | Path,
    shebang: str = "/usr/bin/env python3",
) -> None:
    """Збирає автономний zipapp-архів із каталогу source_dir."""
    src = Path(source_dir).resolve()
    out = Path(output_file).resolve()

    if not (src / "__main__.py").exists():
        raise FileNotFoundError(
            f"Каталог {src} не містить обов'язкового файлу точки входу __main__.py"
        )

    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Збирання zipapp: {src} -> {out}...")
    zipapp.create_archive(
        source=src,
        target=out,
        interpreter=shebang,
        main=None,  # Використовувати наявний файл __main__.py у корені каталогу
        compressed=True,
    )

    # Встановлюємо права виконання rwxr-xr-x для систем Unix/Linux/macOS
    current_mode = os.stat(out).st_mode
    os.chmod(out, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Архів створено успішно (розмір: {out.stat().st_size} байтів).")


if __name__ == "__main__":
    build_standalone_zipapp("system_monitor", "bin/sysmon.pyz")

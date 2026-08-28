# scripts/generate_version.py
import subprocess
import os
from datetime import datetime

# Отримання середовища SCons з контексту PlatformIO
Import("env")

def get_git_revision():
    """Витягування короткого хешу та стану репозиторію."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=env.get("PROJECT_DIR")
        ).strip().decode("utf-8")
        
        # Перевірка наявності незакомічених змін у робочому дереві
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=env.get("PROJECT_DIR")
        ).strip().decode("utf-8")
        
        dirty_flag = "-dirty" if len(status) > 0 else ""
        return f"{commit}{dirty_flag}"
    except Exception:
        return "v1.0.0-release"

def generate_header():
    """Створення C/C++ заголовка з метаданими збірки."""
    project_dir = env.get("PROJECT_DIR")
    include_dir = os.path.join(project_dir, "include")
    os.makedirs(include_dir, exist_ok=True)
    
    header_path = os.path.join(include_dir, "generated_version.h")
    git_hash = get_git_revision()
    build_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    env_name = env.get("PIOENV", "unknown_env")
    mcu = env.get("BOARD_MCU", "unknown_mcu")
    
    content = f"""#pragma once
// Цей файл згенеровано автоматично скриптом scripts/generate_version.py.
// Будь-які ручні правки буде перезаписано під час наступної збірки.

#define BUILD_GIT_HASH "{git_hash}"
#define BUILD_TIMESTAMP "{build_time}"
#define BUILD_ENVIRONMENT "{env_name}"
#define BUILD_TARGET_MCU "{mcu}"
"""
    
    # Критична перевірка: запобігаємо зміні mtime, якщо зміст не змінився
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as f:
            if f.read() == content:
                return
                
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[PRE-BUILD] Оновлено файл заголовка: {header_path} (git: {git_hash})")

# Запуск генерації метаданих
generate_header()

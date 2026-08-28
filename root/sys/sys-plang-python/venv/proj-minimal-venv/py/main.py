#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def create_manual_venv(target_path: Path) -> None:
    """Створює мінімальне віртуальне середовище PEP 405 без модуля venv."""
    target_path = target_path.resolve()
    
    # 1. Визначення параметрів базового інтерпретатора
    base_executable = Path(sys.executable).resolve()
    base_bin_dir = base_executable.parent
    py_version_major = sys.version_info.major
    py_version_minor = sys.version_info.minor
    py_ver_str = f"python{py_version_major}.{py_version_minor}"
    
    # 2. Формування структури каталогів залежно від платформи
    if os.name == "nt":
        bin_dir = target_path / "Scripts"
        include_dir = target_path / "Include"
        site_packages_dir = target_path / "Lib" / "site-packages"
    else:
        bin_dir = target_path / "bin"
        include_dir = target_path / "include"
        site_packages_dir = target_path / "lib" / py_ver_str / "site-packages"
    
    for directory in (bin_dir, include_dir, site_packages_dir):
        directory.mkdir(parents=True, exist_ok=True)
    
    # 3. Створення маркерного файлу pyvenv.cfg
    cfg_path = target_path / "pyvenv.cfg"
    cfg_content = (
        f"home = {base_bin_dir}\n"
        f"include-system-site-packages = false\n"
        f"version = {py_version_major}.{py_version_minor}.{sys.version_info.micro}\n"
        f"executable = {base_executable}\n"
        f"command = manual_venv_bootstrap {target_path}\n"
    )
    cfg_path.write_text(cfg_content, encoding="utf-8")
    
    # 4. Створення символічного посилання на бінарний інтерпретатор
    venv_python = bin_dir / ("python.exe" if os.name == "nt" else "python3")
    if venv_python.exists() or venv_python.is_symlink():
        venv_python.unlink()
    
    try:
        venv_python.symlink_to(base_executable)
    except (OSError, NotImplementedError):
        # На Windows без прав адміністратора копіюємо бінарник
        import shutil
        shutil.copy2(base_executable, venv_python)
        
    # Додатковий симлінк python -> python3 для зручності у POSIX
    if os.name != "nt":
        venv_python_alias = bin_dir / "python"
        if not venv_python_alias.exists():
            try:
                venv_python_alias.symlink_to(venv_python.name)
            except OSError:
                pass

    # 5. Створення базового POSIX-скрипта активації
    if os.name != "nt":
        activate_script = bin_dir / "activate"
        activate_content = f"""# Скрипт активації для POSIX shell
deactivate () {{
    if [ -n "${{_OLD_VIRTUAL_PATH:-}}" ] ; then
        PATH="${{_OLD_VIRTUAL_PATH:-}}"
        export PATH
        unset _OLD_VIRTUAL_PATH
    fi
    if [ -n "${{_OLD_VIRTUAL_PS1:-}}" ] ; then
        PS1="${{_OLD_VIRTUAL_PS1:-}}"
        export PS1
        unset _OLD_VIRTUAL_PS1
    fi
    unset VIRTUAL_ENV
    unset VIRTUAL_ENV_PROMPT
    if [ "${{1-}}" != "nondestructive" ] ; then
        unset -f deactivate
    fi
}}

deactivate nondestructive

VIRTUAL_ENV="{target_path}"
export VIRTUAL_ENV
VIRTUAL_ENV_PROMPT="({target_path.name}) "
export VIRTUAL_ENV_PROMPT

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

_OLD_VIRTUAL_PS1="${{PS1:-}}"
PS1="({target_path.name}) ${{PS1:-}}"
export PS1
"""
        activate_script.write_text(activate_content, encoding="utf-8")
        activate_script.chmod(0o755)
    
    print(f"Віртуальне середовище успішно розгорнуто у: {target_path}")

if __name__ == "__main__":
    venv_dir = Path("./test_custom_env")
    create_manual_venv(venv_dir)

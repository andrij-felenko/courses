# ⚙️ Створення віртуального середовища без модуля venv

Віртуальне середовище Python часто сприймають як складний монолітний механізм, нерозривно прив'язаний до стандартного модуля `venv` або зовнішньої утиліти `virtualenv`. На практиці архітектура стандарту PEP 405 є надзвичайно компактною та прозорою: для повноцінної ізоляції сторонніх бібліотек достатньо створити чітку структуру підкаталогів, одне символічне посилання на бінарний файл інтерпретатора та текстовий конфігураційний файл `pyvenv.cfg`.

Розбір процесу ручного створення віртуального середовища без залучення модуля `venv` дозволяє наочно простежити, як низькорівневий алгоритм розрахунку шляхів у CPython підміняє системні префікси, як динамічно завантажуються скомпільовані C-розширення та куди менеджер `pip` спрямовує інстальовані файли.

## 1. Архітектурні вимоги стандарту PEP 405

Щоб ядро CPython під час запуску розпізнало довільний каталог файлової системи як валідне віртуальне середовище, необхідно виконати чотири фундаментальні інваріанти:

1. **Структура каталогів виконання:** у цільовому каталозі має бути створено підкаталог бінарних файлів `bin` (для POSIX-сумісних систем) або `Scripts` (для середовища Windows).
2. **Символічне посилання на інтерпретатор:** усередині бінарного каталогу розміщується символічне посилання (symlink) із назвою `python3` (або `python`), яке вказує на системний бінарний образ `sys.executable`.
3. **Маркерний конфігураційний файл `pyvenv.cfg`:** файл розміщується безпосередньо в корені цільового каталогу середовища або всередині бінарного каталогу. Він зобов'язаний містити рядок `home = <каталог_базового_інтерпретатора>`.
4. **Каталог ізольованих пакунків:** у структурі `lib/pythonX.Y/site-packages/` (де `X.Y` — мажорна та мінорна версії Python) або `Lib/site-packages/` на Windows створюється каталог, куди підсистема `site.py` спрямовуватиме імпорти сторонніх модулів.

Скрипти активації командного рядка (`activate`, `activate.csh`, `activate.fish`, `activate.ps1`) не є частиною вимог CPython до виявлення оточення. Вони слугують суто оболонками для модифікації змінних сесії користувача.

## 2. Реалізація генератора venv на чистому Python

Нижче наведено повний самодостатній скрипт, який створює функціональне віртуальне середовище без виклику `import venv` та перевіряє коректність ізоляції системних шляхів:

```py
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
```

## 3. Фазовий аналіз розрахунку шляхів під час запуску

Коли згенерований інтерпретатор запускається командою `./test_custom_env/bin/python3`, операційна система викликає `execve` за шляхом символічного посилання. CPython проходить кілька етапів визначення контексту виконання:

1. **Отримання точки входу:** функція `_PyConfig_Read` зчитує системний аргумент `argv[0]` та обчислює абсолютний шлях до бінарника інтерпретатора.
2. **Перевірка орієнтирів (Landmarks):** алгоритм модуля `getpath.py` аналізує каталог виконуваного файлу (`test_custom_env/bin/`) та піднімається на один рівень угору (`test_custom_env/`).
3. **Парсинг маркерного файлу:** інтерпретатор виявляє файл `pyvenv.cfg` у каталозі `test_custom_env/` і перемикається в режим PEP 405. З файлу зчитується ключ `home = /usr/bin`.
4. **Розділення префіксів:** 
   - `sys.base_prefix` встановлюється на базовий системний каталог (`/usr`), звідки імпортуються модулі стандартної бібліотеки (`os`, `sys`, `json`, `math`).
   - `sys.prefix` та `sys.exec_prefix` спрямовуються на `/home/user/project/test_custom_env`.
5. **Ініціалізація підсистеми `site.py`:** стандартний модуль `site` перевіряє значення `sys.prefix`, будує шлях до локального каталогу `site-packages` і додає його до списку пошуку `sys.path`. Оскільки параметр `include-system-site-packages` встановлено у `false`, глобальні каталоги `/usr/lib/python3/dist-packages` взагалі не додаються до шляхів пошуку.

Перевіримо роботу створеного середовища через прямий виклик інтерпретатора:

```bash
$ ./test_custom_env/bin/python3 -c "
import sys
print(f'sys.executable:  {sys.executable}')
print(f'sys.prefix:      {sys.prefix}')
print(f'sys.base_prefix: {sys.base_prefix}')
print(f'site-packages:   {[p for p in sys.path if \"site-packages\" in p]}')
"
```

Результат виконання наочно демонструє успішне розділення просторів:

```
sys.executable:  /home/user/project/test_custom_env/bin/python3
sys.prefix:      /home/user/project/test_custom_env
sys.base_prefix: /usr
site-packages:   ['/home/user/project/test_custom_env/lib/python3.12/site-packages']
```

## 4. Розгортання pip та перевірка повної ізоляції

Створене вручну середовище є абсолютно чистим і не містить сторонніх інструментів. Щоб інтегрувати менеджер пакунків `pip`, не звертаючись до модуля `venv`, скористаємося стандартним механізмом `ensurepip`:

```bash
$ ./test_custom_env/bin/python3 -m ensurepip --default-pip
Looking in links: /tmp/tmp_wheel_cache...
Processing /usr/share/python-wheels/pip-24.0-py3-none-any.whl
Installing collected packages: pip
Successfully installed pip-24.0
```

Модуль `ensurepip` автоматично створив виконуваний скрипт `test_custom_env/bin/pip` із шебангом `#!/home/user/project/test_custom_env/bin/python3`. Тепер виконаємо тестову інсталяцію бібліотеки `requests`:

```bash
$ ./test_custom_env/bin/pip install requests
Collecting requests
  Downloading requests-2.31.0-py3-none-any.whl (62 kB)
Collecting urllib3<3,>=1.21.1
  Downloading urllib3-2.2.1-py2.py3-none-any.whl (121 kB)
Successfully installed certifi-2024.2.2 charset-normalizer-3.3.2 idna-3.6 requests-2.31.0 urllib3-2.2.1
```

Перевіримо фізичне розташування встановлених файлів:

```bash
$ ls test_custom_env/lib/python3.12/site-packages/
certifi  charset_normalizer  idna  pip  requests  urllib3
```

Якщо викликати системний інтерпретатор `/usr/bin/python3 -c "import requests"`, процес завершиться помилкою `ModuleNotFoundError: No module named 'requests'`. Це доводить, що бібліотека встановлена виключно в ізольованому дереві каталогів.

## 5. Обробка файлів конфігурації шляхів (.pth)

Усередині каталогу `site-packages` віртуального середовища модуль `site.py` під час кожного старту сканує файли з розширенням `.pth`. Цей механізм дозволяє додавати локальні шляхи розробки або виконувати початковий код ініціалізації:

1. Якщо рядок у `.pth` файлі є звичайним шляхом (абсолютним або відносним щодо розташування файлу `.pth`), `site.py` автоматично додає цей шлях до `sys.path`.
2. Якщо рядок починається з префікса `import `, інтерпретатор виконує цей рядок як код Python (саме так працюють інструменти покриття коду на кшталт `coverage` та розширювачі налагоджувачів).

Створимо файл `local_dev.pth` всередині нашого віртуального середовища:

```bash
$ echo "/home/user/shared_libs" > test_custom_env/lib/python3.12/site-packages/local_dev.pth
```

При наступному виклику `./test_custom_env/bin/python3` каталог `/home/user/shared_libs` автоматично з'явиться в списку `sys.path`.

## 6. Типові пастки та крайові випадки ручного розгортання

Під час ручного чи програмного формування віртуальних середовищ розробники найчастіше стикаються з трьома критичними проблемами:

1. **Неправильний параметр `home` у `pyvenv.cfg`:** якщо вказати шлях до кореня інсталяції замість каталогу бінарника (наприклад, `home = /usr` замість `home = /usr/bin`), CPython не зможе знайти базову стандартну бібліотеку (`os.py`) і впаде з фатальною помилкою `Could not find platform independent libraries <prefix>`.
2. **Переміщення або перейменування каталогу середовища:** оскільки згенеровані файли консольних утиліт (`pip`, `pytest`, `uvicorn`) записують жорсткий абсолютний шлях у свій шебанг (`#!/home/user/old_path/.venv/bin/python3`), після перенесення каталогу запуск цих утиліт зламається з повідомленням `bad interpreter: No such file or directory`. Виправленням є перегенерація шебангів або використання прямого запуску `python3 -m pip`.
3. **Оновлення мінорної версії базового Python в ОС:** якщо системний пакет оновлюється з Python 3.12 на Python 3.13, старе віртуальне середовище продовжуватиме шукати каталог `lib/python3.12/site-packages/`, тоді як базовий інтерпретатор очікує стандартну бібліотеку версії 3.13. Для відновлення працездатності середовище необхідно перестворити під нову версію інтерпретатора.

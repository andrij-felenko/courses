# ⚙️ Низькорівневий аудит системного Python та діагностика конфліктів середовища

Для надійної експлуатації виробничих серверів під керуванням Linux системному інженеру та архітектору платформи необхідний інструментарій автоматизованого аудиту. Такий інструментарій повинен своєчасно виявляти несанкціоноване втручання в системний інтерпретатор, стан затінення системних модулів пакунками з каталогу `/usr/local` та невідповідність бінарного ABI скомпільованих C-розширень.

У цьому практичному проєкті розглядаються дві комплементарні реалізації діагностичного аудитора: глибокий скрипт мовою Python для детального аналізу метаданих та високоефективний сканер мовами C і C++ для інтеграції в низькорівневі системні демони моніторингу.

## 1. Завдання, діагностичні критерії та алгоритм аналізу

Головна мета аудиту полягає у виявленні прихованих дефектів середовища виконання до того, як вони спричинять аварійну зупинку системних служб або користувацьких сервісів.

У реальній практиці системного адміністрування інженери стикаються з ситуаціями, коли сервер функціонує місяцями, але перша ж планова спроба перезавантаження або оновлення безпеки призводить до фатального краху. Це трапляється через те, що хтось із розробників колись виконав `sudo pip install` для швидкого тестування, непомітно підмінивши базові системні модулі.

Діагностичний конвеєр реалізує чотири послідовні фази перевірки:

1. **Ідентифікація контексту виконання (Runtime Context Discovery):**
   Утиліта аналізує параметри `sys.prefix`, `sys.base_prefix` та `sys.real_prefix`, щоб однозначно встановити, чи запущено процес у межах віртуального середовища (`venv`/`virtualenv`), чи в глобальному системному просторі.
2. **Верифікація стандарту захисту PEP 668:**
   Сканер опитує шляхи стандартної бібліотеки через модуль `sysconfig`, перевіряє наявність файлу-маркера `EXTERNALLY-MANAGED`, здійснює синтаксичний аналіз конфігурації INI та витягує офіційні інструкції дистрибутива.
3. **Детекція затінення пакунків (Shadowing Detection):**
   Алгоритм порівнює вміст каталогів вищого пріоритету (`/usr/local/lib/pythonX.Y/dist-packages` або `site-packages`) із каталогами дистрибутива (`/usr/lib/python3/dist-packages`). Будь-який модуль, присутній в обох деревах одночасно, позначається як потенційне джерело системного збою.
4. **Контроль цілісності двійкових C-розширень (.so):**
   Перевіряється коректність тегів ABI (наприклад, `.cpython-312-x86_64-linux-gnu.so`), відповідність прапорців сумісності `sys.abiflags` та відсутність втрачених залежностей динамічного лінкувальника.

## 2. Реалізація діагностичного сканера мовою Python

Нижче наведено повнофункціональний скрипт аудиту, який поєднує стандартні бібліотеки `sysconfig`, `configparser` та `pathlib` для глибокого аналізу файлової системи.

Скрипт розроблено з урахуванням того, що він повинен безпечно виконуватися навіть на частково пошкоджених системах, тому він не спирається на жодні зовнішні сторонні бібліотеки (як-от `requests` чи `click`), використовуючи виключно модулі стандартного постачання CPython:

```python
#!/usr/bin/env python3
"""Утиліта аудиту системного оточення Python та перевірки маркерів PEP 668."""

from __future__ import annotations
import configparser
import os
import sys
import sysconfig
from pathlib import Path


def check_virtual_environment() -> dict[str, str | bool]:
    """Перевіряє, чи активне віртуальне середовище venv."""
    is_venv = (
        hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix
    ) or (
        hasattr(sys, "real_prefix") and sys.prefix != sys.real_prefix
    )
    
    return {
        "is_venv": is_venv,
        "prefix": sys.prefix,
        "base_prefix": getattr(sys, "base_prefix", sys.prefix),
        "executable": sys.executable,
    }


def check_pep668_marker() -> dict[str, str | bool | None]:
    """Перевіряє наявність та зміст файлу EXTERNALLY-MANAGED."""
    paths_to_check = [
        sysconfig.get_path("stdlib"),
        sysconfig.get_path("platstdlib"),
    ]
    
    for base_dir in dict.fromkeys(paths_to_check):
        if not base_dir:
            continue
        marker_path = Path(base_dir) / "EXTERNALLY-MANAGED"
        if marker_path.is_file():
            parser = configparser.RawConfigParser()
            try:
                parser.read(marker_path, encoding="utf-8")
                msg = parser.get("externally-managed", "Error", fallback=None)
                if msg is None:
                    msg = parser.get("externally-managed", "error", fallback="[Повідомлення за замовчуванням]")
            except Exception:
                msg = "[Помилка парсингу INI файлу EXTERNALLY-MANAGED]"
                
            return {
                "present": True,
                "path": str(marker_path),
                "error_message": msg.strip(),
            }
            
    return {
        "present": False,
        "path": None,
        "error_message": None,
    }


def audit_shadowed_packages() -> list[dict[str, str]]:
    """Виявляє модулі в /usr/local, які затіняють системні пакети в /usr/lib."""
    local_site = None
    system_site = None
    
    for p in sys.path:
        p_path = Path(p)
        if not p_path.is_dir():
            continue
        if "/usr/local/" in p and ("dist-packages" in p or "site-packages" in p):
            local_site = p_path
        elif "/usr/lib/" in p and ("dist-packages" in p or "site-packages" in p):
            if system_site is None:
                system_site = p_path

    if not local_site or not system_site or not local_site.exists() or not system_site.exists():
        return []

    def get_top_level_names(directory: Path) -> set[str]:
        names = set()
        for item in directory.iterdir():
            if item.name.startswith((".", "_")) or item.name.endswith(".dist-info"):
                continue
            if item.is_dir():
                names.add(item.name)
            elif item.suffix in (".py", ".so"):
                names.add(item.stem)
        return names

    local_names = get_top_level_names(local_site)
    system_names = get_top_level_names(system_site)
    conflicts = local_names.intersection(system_names)

    result = []
    for name in sorted(conflicts):
        result.append({
            "package": name,
            "shadow_path": str(local_site / name),
            "system_path": str(system_site / name),
        })
    return result


def main() -> int:
    print("=== АУДИТ СИСТЕМНОГО ОТОЧЕННЯ PYTHON ===")
    venv_info = check_virtual_environment()
    if venv_info["is_venv"]:
        print("Статус: [ВІРТУАЛЬНЕ СЕРЕДОВИЩЕ]")
        print(f"Префікс venv : {venv_info['prefix']}")
        print(f"Базовий CPython: {venv_info['base_prefix']}")
    else:
        print("Статус: [СИСТЕМНИЙ ІНТЕРПРЕТАТОР]")
        print(f"Шлях префікса: {venv_info['prefix']}")

    print("\n--- Перевірка стандарту PEP 668 ---")
    pep668 = check_pep668_marker()
    if pep668["present"]:
        print("Маркер EXTERNALLY-MANAGED : ЗНАЙДЕНО (Захист активний)")
        print(f"Файл: {pep668['path']}")
        print(f"Текст дистрибутива:\n>>> {pep668['error_message']}")
    else:
        print("Маркер EXTERNALLY-MANAGED : ВІДСУТНІЙ (Прямий pip install не блокується)")

    print("\n--- Перевірка затінення системних модулів ---")
    shadows = audit_shadowed_packages()
    if shadows:
        print(f"УВАГА: Виявлено {len(shadows)} затінених системних пакетів!")
        for s in shadows:
            print(f" [!] Модуль '{s['package']}':")
            print(f"     Локальний (активний): {s['shadow_path']}")
            print(f"     Системний (затінений): {s['system_path']}")
    else:
        print("Конфліктів затінення між /usr/local та /usr/lib не виявлено.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## 3. Системний C/C++ сканер середовища

Для вбудовування в низькорівневі системні агенти нагляду та бекенди моніторингу (де запуск важкого процесу Python на кожну перевірку є надто ресурсомістким) розроблено нативний сканер мовами C та C++.

Він працює виключно на рівні прямих POSIX системних викликів або стандартних абстракцій файлової системи C++20 `std::filesystem`, що гарантує мінімальне споживання оперативної пам'яті та нульовий оверхед запуску інтерпретатора.

Реалізація мовою C спирається на класичні функції `stat`, `fopen`, `fgets` та системні константи `sys/stat.h`. Реалізація мовою C++ демонструє сучасний ідіоматичний підхід: контейнер `std::expected` для безпечної обробки можливих помилок введення-виведення без винятків, автоматичне керування ресурсами через RAII та роботу з шляхами файлової системи через `std::filesystem::path`.

:::tabs
```c
/* scanner.c — Аудит маркерів PEP 668 та каталогів dist-packages */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>

#define MAX_PATH 4096
#define BUFFER_SIZE 2048

static int check_file_exists(const char *path) {
    struct stat st;
    return (stat(path, &st) == 0 && S_ISREG(st.st_mode));
}

static void read_pep668_message(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return;
    
    char line[BUFFER_SIZE];
    printf("Файл маркер: %s\n", path);
    printf("--- Вміст EXTERNALLY-MANAGED ---\n");
    while (fgets(line, sizeof(line), f)) {
        fputs(line, stdout);
    }
    printf("--------------------------------\n");
    fclose(f);
}

int main(int argc, char *argv[]) {
    const char *candidates[] = {
        "/usr/lib/python3.12/EXTERNALLY-MANAGED",
        "/usr/lib64/python3.12/EXTERNALLY-MANAGED",
        "/usr/lib/python3.11/EXTERNALLY-MANAGED",
        "/usr/lib64/python3.11/EXTERNALLY-MANAGED",
        "/usr/lib/python3/EXTERNALLY-MANAGED",
        NULL
    };

    printf("=== POSIX C АУДИТОР PEP 668 ===\n");
    int found = 0;
    for (int i = 0; candidates[i] != NULL; ++i) {
        if (check_file_exists(candidates[i])) {
            printf("[ЗНАЙДЕНО] Системне оточення заблоковано PEP 668.\n");
            read_pep668_message(candidates[i]);
            found = 1;
            break;
        }
    }

    if (!found) {
        printf("[ВІДСУТНІЙ] Маркер EXTERNALLY-MANAGED не знайдено за стандартними шляхами.\n");
    }

    return 0;
}
```
```cpp
// scanner.cpp — Ідіоматичний C++20 аудит середовища CPython
#include <iostream>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
#include <string_view>
#include <expected>

namespace fs = std::filesystem;

class EnvironmentAuditor {
public:
    struct MarkerInfo {
        fs::path path;
        std::string content;
    };

    static std::expected<MarkerInfo, std::string> find_pep668_marker() {
        const std::vector<fs::path> candidate_paths = {
            "/usr/lib/python3.12/EXTERNALLY-MANAGED",
            "/usr/lib64/python3.12/EXTERNALLY-MANAGED",
            "/usr/lib/python3.11/EXTERNALLY-MANAGED",
            "/usr/lib64/python3.11/EXTERNALLY-MANAGED",
            "/usr/lib/python3/EXTERNALLY-MANAGED"
        };

        for (const auto& path : candidate_paths) {
            std::error_code ec;
            if (fs::is_regular_file(path, ec)) {
                std::ifstream file(path);
                if (!file.is_open()) {
                    return std::unexpected("Не вдалося відкрити знайдений файл: " + path.string());
                }
                std::string content((std::istreambuf_iterator<char>(file)),
                                     std::istreambuf_iterator<char>());
                return MarkerInfo{path, std::move(content)};
            }
        }

        return std::unexpected("Маркер EXTERNALLY-MANAGED не знайдено");
    }

    static void report_status() {
        std::cout << "=== C++20 АУДИТОР СИСТЕМНОГО PYTHON ===\n";
        auto marker_result = find_pep668_marker();
        if (marker_result.has_value()) {
            const auto& [path, content] = marker_result.value();
            std::cout << "[ЗНАЙДЕНО] Маркер захисту PEP 668: " << path << "\n";
            std::cout << "--- Повідомлення дистрибутива ---\n"
                      << content
                      << "---------------------------------\n";
        } else {
            std::cout << "[УВАГА] " << marker_result.error() << "\n";
        }
    }
};

int main() {
    EnvironmentAuditor::report_status();
    return 0;
}
```
:::

## 4. Пастки реальної експлуатації та регламент відновлення

Під час практичного аудиту системної інфраструктури інженери стикаються з типовими прихованими станами пошкодження:

1. **Невидимі метадані видалених пакунків (Orphaned .dist-info):**
   Коли адміністратор вручну видаляє каталог модуля з `/usr/local/lib/pythonX.Y/dist-packages`, але забуває видалити відповідний каталог метаданих `.dist-info`, інструменти діагностики (на кшталт `pip list` або `importlib.metadata`) продовжують повідомляти, що пакунок встановлено. Будь-який скрипт, який перевіряє наявність залежності через `importlib.metadata.version('requests')`, отримає позитивну відповідь, проте подальший виклик `import requests` зазнає краху з винятком `ModuleNotFoundError`.
2. **Невідповідність прапорців ABI у назвах двійкових розширень:**
   Суфікс скомпільованих `.so` файлів містить закодовані прапорці конфігурації CPython. Якщо розширення було скомпільовано під налагоджувальний інтерпретатор (`--with-pydebug`, суфікс `d`), стандартний релізний інтерпретатор проігнорує цей файл під час динамічного імпорту, що призведе до неочевидних помилок завантаження бібліотеки.
3. **Несанкціоноване додавання шляхів через .pth файли:**
   Файли з розширенням `.pth`, залишені в `/usr/local/lib/pythonX.Y/dist-packages`, зчитуються модулем `site.py` на найбільш ранньому етапі ініціалізації середовища. Якщо `.pth` файл містить виклики імпорту (`import sys; sys.path.insert(...)`), це може докорінно спотворити порядок завантаження модулів без відображення в стандартних змінних оточення `PYTHONPATH`.

### Процедура безпечного відновлення системи

Якщо аудит виявив критичні конфлікти затінення, відновлення працездатності здійснюється за таким регламентом:

1. **Створення резервної копії:**
   Перед будь-якими маніпуляціями обов'язково зберігається знімок поточного стану каталогу `/usr/local`:
   ```bash
   sudo tar -czf /root/usr-local-python-backup.tar.gz /usr/local/lib/python3.*
   ```
2. **Очищення сторонніх пакунків:**
   Видаляються всі сторонні модулі, що затіняють системні шляхи:
   ```bash
   sudo rm -rf /usr/local/lib/python3.*/dist-packages/*
   sudo rm -rf /usr/local/lib/python3.*/site-packages/*
   ```
3. **Верифікація та відновлення системних пакетів через пакетний менеджер:**
   Виконується примусова перевстановлення пошкоджених пакетів дистрибутива для відновлення оригінальних файлів:
   ```bash
   # Debian / Ubuntu
   sudo apt-get install --reinstall $(dpkg -S /usr/lib/python3/dist-packages | cut -d: -f1 | sort -u)

   # RHEL / Fedora
   sudo dnf reinstall $(rpm -qf /usr/lib/python3.*/site-packages/* | sort -u)
   ```
4. **Контрольний запуск сканера:**
   Виконується повторний аудит для підтвердження того, що список `sys.path` чистий і захист PEP 668 активний.

## 5. Інтеграція в моніторинг інфраструктури

На рівні корпоративного парку серверів сканер оформлюється як періодичний юніт `systemd.timer` або плагін моніторингу Nagios/Zabbix.

Утиліта підтримує генерацію стандартизованого коду повернення:
- `0` — середовище повністю чисте, маркер `EXTERNALLY-MANAGED` активний, затінення відсутнє.
- `1` — виявлено затінення системних модулів у `/usr/local` (вимагає втручання адміністратора).
- `2` — відсутній захисний маркер PEP 668 на виробничій системі.

Такий підхід дозволяє перехоплювати несанкціоноване виконання `sudo pip install` до того, як наступне системне оновлення призведе до незворотного краху операційної системи.

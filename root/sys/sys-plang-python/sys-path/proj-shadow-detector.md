# ⚙️ Аудит sys.path та автоматичне виявлення затінення модулів

Помилки затінення модулів (Module Shadowing) та небезпечні відносні шляхи в списку `sys.path` є поширеною причиною прихованих аварій у виробничих середовищах. Якщо розробник створює в корені проєкту допоміжний файл з іменем `math.py`, `random.py`, `json.py` або `test.py`, стандартна підсистема імпорту CPython знаходить цей локальний файл раніше за системну бібліотеку, що ламає не лише прямі виклики, але й внутрішні залежності сторонніх пакетів.

Нижче наведено архітектуру та реалізацію виробничого діагностичного інструменту `syspath_audit`, який виконує статичний та динамічний аналіз `sys.path`, виявляє потенційні колізії імен зі стандартною бібліотекою та сторонніми пакунками, перевіряє права доступу і генерує структурований звіт про безпеку середовища.

## 1. Архітектура діагностичного інструменту

Коли інтерпретатор обробляє інструкцію імпорту, об'єкт `sys.meta_path` делегує пошук стандартному файловому шукачу `PathFinder`. Цей шукач послідовно проходить список `sys.path` зліва направо і зупиняється на першому каталозі, який містить файл із відповідним ім'ям модуля. Через це будь-який файл у каталозі з нижчим індексом повністю блокує доступ до файлів з таким самим ім'ям у каталогах з вищими індексами.

Діагностика виконується у три послідовні фази:

1. **Фаза 1: Санітарний аналіз шляхів (`PathSanitizer`):**
   - Перевірка наявності порожніх рядків `""` або явного поточного каталогу `.` у `sys.path`.
   - Виявлення дублікатів шляхів та розіменування символічних посилань (`realpath`).
   - Перевірка прав доступу на запис (World-writable directories у багатокористувацьких Unix-системах).
2. **Фаза 2: Сканування простору імен та пошук затінень (`ShadowDetector`):**
   - Побудова еталонного індексу модулів стандартної бібліотеки через `sys.stdlib_module_names` (впровадженого в Python 3.10 для усунення потреби сканувати диск) та `sys.builtin_module_names`.
   - Сканування файлів `.py`, `.pyc` та компільованих розширень `.so`/`.pyd` у кожному каталозі з `sys.path` відповідно до їхнього пріоритету.
   - Фіксація випадків, коли модуль із каталогу з вищим пріоритетом перекриває однойменний модуль із каталогу з нижчим пріоритетом.
3. **Фаза 3: Генерація звіту (`AuditReporter`):**
   - Форматування результатів у вигляді консольної таблиці або експорт у форматі JSON для інтеграції в автоматизовані CI/CD пайплайни та Git pre-commit хуки.

```
sys.path entries: ['/project', '/usr/lib/python3.12', '/usr/lib/.../site-packages']
       │
       ▼
[PathSanitizer] ──→ Перевірка небезпечних відносних шляхів, прав доступу, дублів
       │
       ▼
[ShadowDetector] ──→ Сканування *.py/*.so в кожному каталозі за пріоритетом
       │            Порівняння з sys.stdlib_module_names та site-packages
       ▼
[AuditReporter] ──→ CLI звіт / JSON артефакт
```

## 2. Реалізація утиліти на мові Python

Програмна реалізація сканера спирається на стандартну бібліотеку Python і не потребує встановлення сторонніх залежностей. Клас `SysPathAuditor` інкапсулює логіку обходу файлової системи, обробки помилок доступу `PermissionError` та зіставлення імен модулів.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""syspath_audit.py — інструмент діагностики безпеки sys.path та затінення модулів."""

from __future__ import annotations

import os
import sys
import stat
from pathlib import Path
from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class PathIssue:
    path: str
    severity: str  # "CRITICAL", "WARNING", "INFO"
    message: str


@dataclass
class ShadowConflict:
    module_name: str
    shadowing_path: Path
    shadowed_path: Path
    conflict_type: str  # "STDLIB_SHADOW", "SITE_SHADOW"


@dataclass
class AuditReport:
    path_issues: list[PathIssue] = field(default_factory=list)
    conflicts: list[ShadowConflict] = field(default_factory=list)
    scanned_paths: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.path_issues and not self.conflicts


class SysPathAuditor:
    def __init__(self, target_paths: list[str] | None = None) -> None:
        self.paths = target_paths if target_paths is not None else list(sys.path)
        # Отримання офіційного множинного індексу модулів стандартної бібліотеки
        if hasattr(sys, "stdlib_module_names"):
            self.stdlib_names = sys.stdlib_module_names
        else:
            # Fallback для версій Python < 3.10
            import distutils.sysconfig
            self.stdlib_names = set(sys.builtin_module_names)

    def audit_path_structure(self) -> list[PathIssue]:
        issues: list[PathIssue] = []
        seen_realpaths: set[str] = set()

        for idx, raw_path in enumerate(self.paths):
            # 1. Перевірка на небезпечний порожній рядок або відносний шлях
            if raw_path == "" or raw_path == ".":
                issues.append(PathIssue(
                    path=raw_path,
                    severity="CRITICAL",
                    message=f"Позиція [{idx}]: Порожній або відносний шлях відкриває вразливість локального затінення (CWD injection)."
                ))
                continue

            p = Path(raw_path)
            if not p.is_absolute():
                issues.append(PathIssue(
                    path=raw_path,
                    severity="WARNING",
                    message=f"Позиція [{idx}]: Відносний шлях '{raw_path}' залежить від поточного каталогу виклику процесу."
                ))

            if not p.exists():
                issues.append(PathIssue(
                    path=raw_path,
                    severity="INFO",
                    message=f"Позиція [{idx}]: Каталог не існує на диску."
                ))
                continue

            # 2. Перевірка дублікатів шляхів через розіменування symlink
            try:
                resolved = str(p.resolve())
                if resolved in seen_realpaths:
                    issues.append(PathIssue(
                        path=raw_path,
                        severity="WARNING",
                        message=f"Позиція [{idx}]: Дублікат шляху (канонічний шлях: '{resolved}')."
                    ))
                seen_realpaths.add(resolved)
            except OSError as err:
                issues.append(PathIssue(path=raw_path, severity="WARNING", message=f"Помилка доступу: {err}"))
                continue

            # 3. Перевірка небезпечних прав доступу на запис у POSIX системах
            if os.name == "posix":
                try:
                    st = p.stat()
                    if bool(st.st_mode & stat.S_IWOTH):
                        issues.append(PathIssue(
                            path=raw_path,
                            severity="CRITICAL",
                            message=f"Позиція [{idx}]: Каталог доступний для запису всім користувачам (World-writable)."
                        ))
                except OSError:
                    pass

        return issues

    def _discover_modules_in_dir(self, directory: Path) -> Iterator[tuple[str, Path]]:
        """Сканує каталог на наявність кореневих модулів та пакетів."""
        valid_extensions = {".py", ".pyc", ".so", ".pyd"}
        try:
            for entry in directory.iterdir():
                if entry.is_file():
                    ext = entry.suffix.lower()
                    if ext in valid_extensions:
                        # Відкидаємо суфікси компіляції на зразок .cpython-312-x86_64-linux-gnu
                        stem = entry.name.split(".")[0]
                        if stem != "__init__":
                            yield stem, entry
                elif entry.is_dir():
                    # Каталог є пакетом, якщо містить __init__.py або є namespace-пакетом
                    if (entry / "__init__.py").is_file():
                        yield entry.name, entry
        except (PermissionError, OSError):
            return

    def audit_shadowing(self) -> list[ShadowConflict]:
        conflicts: list[ShadowConflict] = []
        # Словник першого знайденого екземпляра кожного імені модуля: name -> (index, path)
        first_seen: dict[str, tuple[int, Path]] = {}

        for idx, raw_path in enumerate(self.paths):
            if not raw_path:
                raw_path = "."
            p = Path(raw_path)
            if not p.is_dir():
                continue

            for mod_name, file_path in self._discover_modules_in_dir(p):
                # 1. Перевірка затінення стандартної бібліотеки користувацькими каталогами
                # Якщо каталог скрипту містить файл зі списку stdlib (наприклад, math.py)
                is_stdlib = mod_name in self.stdlib_names
                is_user_dir = "site-packages" not in str(p) and "lib/python" not in str(p)

                if is_stdlib and is_user_dir:
                    conflicts.append(ShadowConflict(
                        module_name=mod_name,
                        shadowing_path=file_path,
                        shadowed_path=Path(f"<Standard Library Module: {mod_name}>"),
                        conflict_type="STDLIB_SHADOW"
                    ))

                # 2. Перевірка колізій між елементами sys.path різного пріоритету
                if mod_name in first_seen:
                    prev_idx, prev_path = first_seen[mod_name]
                    # Фіксуємо конфлікт, якщо модуль знайдено в двох різних фізичних місцях
                    if prev_path.resolve() != file_path.resolve():
                        conflicts.append(ShadowConflict(
                            module_name=mod_name,
                            shadowing_path=prev_path,
                            shadowed_path=file_path,
                            conflict_type="SITE_SHADOW"
                        ))
                else:
                    first_seen[mod_name] = (idx, file_path)

        return conflicts

    def run_full_audit(self) -> AuditReport:
        report = AuditReport(scanned_paths=self.paths)
        report.path_issues = self.audit_path_structure()
        report.conflicts = self.audit_shadowing()
        return report


def print_cli_report(report: AuditReport) -> None:
    print("=" * 70)
    print("                 ЗВІТ АУДИТУ БЕЗПЕКИ SYS.PATH")
    print("=" * 70)

    print(f"\n[+] Проскановано {len(report.scanned_paths)} записів у sys.path.")

    if report.path_issues:
        print(f"\n[!] Виявлено структурні дефекти шляхів ({len(report.path_issues)}):")
        for issue in report.path_issues:
            color_mark = "CRITICAL: " if issue.severity == "CRITICAL" else "WARNING:  "
            print(f"  • [{color_mark}] {issue.message}")
            print(f"    Шлях: '{issue.path}'")
    else:
        print("\n[✓] Структурних проблем у записах sys.path не знайдено.")

    if report.conflicts:
        print(f"\n[!] Виявлено колізії імен та затінення модулів ({len(report.conflicts)}):")
        for conf in report.conflicts:
            if conf.conflict_type == "STDLIB_SHADOW":
                print(f"  • [STDLIB SHADOW] Модуль '{conf.module_name}' затіняє стандартну бібліотеку!")
                print(f"    Файл затінення: {conf.shadowing_path}")
            else:
                print(f"  • [PATH COLLISION] Модуль '{conf.module_name}' продубльовано на різних рівнях:")
                print(f"    Пріоритетний:  {conf.shadowing_path}")
                print(f"    Затінений:    {conf.shadowed_path}")
    else:
        print("\n[✓] Небезпечних затінень модулів не виявлено.")

    print("\n" + "=" * 70)
    if report.is_clean:
        print("РЕЗУЛЬТАТ: СЕРЕДОВИЩЕ ЧИСТЕ. Затінень та вразливих шляхів немає.")
    else:
        print("РЕЗУЛЬТАТ: ВИЯВЛЕНО РИЗИКИ. Перевірте локальні файли та налаштування CWD.")
    print("=" * 70)


if __name__ == "__main__":
    auditor = SysPathAuditor()
    report = auditor.run_full_audit()
    print_cli_report(report)
    if not report.is_clean:
        sys.exit(1)
```

## 3. Низькорівневий аналіз шляхів у C/C++ (PyConfig Embedding)

При вбудовуванні інтерпретатора CPython у нативні застосунки C або C++ конфігурація шляхів повинна перевірятися до виклику функції `Py_InitializeFromConfig()`. Якщо хостовий застосунок запускається користувачем із підвищеними системними привілеями (наприклад, як системна служба чи демон), наявність відносного шляху або поточного каталогу в `config.module_search_paths` створює пряму загрозу ін'єкції довільного скомпільованого C-розширення через маніпуляцію робочим каталогом процесу.

Стандарт PEP 587 надає структуру `PyConfig`, де поле `module_search_paths_set` дозволяє повністю заблокувати евристичний розрахунок орієнтирів `_PyPathConfig` та зафіксувати детермінований список дозволених каталогів у пам'яті C.

Нижче наведено парні ідіоматичні реалізації попередньої валідації та безпечної ініціалізації середовища мовами C та C++:

:::tabs
```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <wchar.h>

/* Безпечна ініціалізація та аудит шляхів пошуку модулів CPython */
int init_safe_embedded_python(const wchar_t* program_name, const wchar_t* custom_lib_path) {
    PyStatus status;
    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    config.program_name = Py_DecodeLocale("secure_app", NULL);
    config.isolated = 1;         /* Вмикає повну ізоляцію від середовища */
    config.safe_path = 1;        /* Забороняє додавання CWD до sys.path[0] */
    config.use_environment = 0;  /* Блокує змінні PYTHONPATH та PYTHONHOME */

    status = PyConfig_SetString(&config, &config.program_name, program_name);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return -1;
    }

    /* Явне завдання безпечного списку каталогів пошуку */
    config.module_search_paths_set = 1;
    status = PyWideStringList_Append(&config.module_search_paths, custom_lib_path);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return -1;
    }

    /* Валідація: перевірка, чи не потрапив відносний шлях у список */
    for (size_t i = 0; i < config.module_search_paths.length; i++) {
        const wchar_t* p = config.module_search_paths.items[i];
        if (p[0] != L'/' && p[0] != L'\\' && !(p[0] != L'\0' && p[1] == L':')) {
            fprintf(stderr, "Помилка безпеки: відносний шлях у module_search_paths заборонено!\n");
            PyConfig_Clear(&config);
            return -2;
        }
    }

    status = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);

    if (PyStatus_Exception(status)) {
        return -3;
    }
    return 0;
}
```
```cpp
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <filesystem>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>
#include <expected>

namespace py_embed {

namespace fs = std::filesystem;

class ScopedPyConfig {
public:
    ScopedPyConfig() {
        PyConfig_InitPythonConfig(&config_);
    }

    ~ScopedPyConfig() {
        PyConfig_Clear(&config_);
    }

    ScopedPyConfig(const ScopedPyConfig&) = delete;
    ScopedPyConfig& operator=(const ScopedPyConfig&) = delete;

    PyConfig& get() noexcept { return config_; }
    const PyConfig& get() const noexcept { return config_; }

private:
    PyConfig config_;
};

enum class InitError {
    ConfigError,
    InsecureRelativePath,
    BootstrapFailed
};

class SafePythonRuntime {
public:
    static std::expected<SafePythonRuntime, InitError> create(
        std::wstring_view program_name,
        std::span<const fs::path> allowed_library_paths) 
    {
        ScopedPyConfig scoped_cfg;
        PyConfig& cfg = scoped_cfg.get();

        cfg.isolated = 1;
        cfg.safe_path = 1;
        cfg.use_environment = 0;

        PyStatus status = PyConfig_SetString(&cfg, &cfg.program_name, program_name.data());
        if (PyStatus_Exception(status)) {
            return std::unexpected(InitError::ConfigError);
        }

        cfg.module_search_paths_set = 1;
        for (const auto& dir_path : allowed_library_paths) {
            // Сувора C++ перевірка: шлях повинен бути абсолютним
            if (!dir_path.is_absolute()) {
                std::cerr << "Безпековий дефект: заборонено неабсолютний шлях: " 
                          << dir_path << '\n';
                return std::unexpected(InitError::InsecureRelativePath);
            }

            status = PyWideStringList_Append(&cfg.module_search_paths, dir_path.c_str());
            if (PyStatus_Exception(status)) {
                return std::unexpected(InitError::ConfigError);
            }
        }

        status = Py_InitializeFromConfig(&cfg);
        if (PyStatus_Exception(status)) {
            return std::unexpected(InitError::BootstrapFailed);
        }

        return SafePythonRuntime{};
    }

    ~SafePythonRuntime() {
        if (Py_IsInitialized()) {
            Py_FinalizeEx();
        }
    }

    SafePythonRuntime(SafePythonRuntime&&) noexcept = default;
    SafePythonRuntime& operator=(SafePythonRuntime&&) noexcept = default;

private:
    SafePythonRuntime() = default;
};

} // namespace py_embed
```
:::

## 4. Граничні випадки та особливості файлових систем

Під час проєктування та експлуатації засобів аудиту шляхів необхідно враховувати три системні крайові випадки, які часто виникають на різних платформах:

1. **Нечутливість до регістру символів (Case-Insensitive Filesystems):**
   На операційних системах Windows (файлова система NTFS) та macOS (APFS за замовчуванням) файли `MATH.py`, `Math.py` та `math.py` є фізично одним і тим самим файлом. Якщо розробник на macOS створить файл `Math.py`, підсистема імпорту на Linux успішно імпортує системний модуль `math` (ігноруючи `Math.py` через розрізнення регістру символів), але на macOS або Windows цей локальний файл перехопить інструкцію `import math`. Це породжує важковідтворювані збої, які проявляються лише при зміні операційної системи розробника чи CI-сервера.
2. **Пакети просторів імен без `__init__.py` (PEP 420 Namespace Packages):**
   Починаючи з Python 3.3, каталоги без файлу `__init__.py` можуть бути валідними пакетами просторів імен. Сканер не повинен відкидати каталоги без `__init__.py`, якщо вони містять внутрішні вкладені модулі, оскільки вони також можуть затіняти сторонні простори імен, розподілені між різними каталогами `site-packages`.
3. **Динамічна модифікація через `.pth` файли:**
   Оскільки рядки з директивою `import` у файлах `.pth` виконуються під час старту, сторонній пакет може модифікувати `sys.path` вже після завершення початкової ініціалізації. Тому для 100% гарантії аудит повинен виконуватися як статично (аналізом конфігурацій перед запуском), так і динамічно у вже запущеному екземплярі процесу перед виконанням бізнес-логіки застосунку.

## 5. Інтеграція аудиту в процес розробки та CI/CD

Для запобігання потраплянню шкідливих або конфліктних файлів у кодову базу перевірку шляхів доцільно автоматизувати на рівні системи контролю версій:

- **Git Pre-commit Hook:** Скрипт перевіряє додані до коміту файли на збіг з іменами з `sys.stdlib_module_names` та блокує коміт, якщо розробник створив у корені проєкту файл на зразок `test.py` або `csv.py`.
- **Контейнеризація (Dockerfile):** Під час побудови виробничих образів на базі Docker прапорець `PYTHONSAFEPATH=1` або `-P` повинен бути встановлений за замовчуванням через директиву `ENV PYTHONSAFEPATH=1`. Це гарантує, що запуск застосунку у випадковому робочому каталозі контейнера не призведе до виконання неперевірених файлів.

# Практичний конвеєр автоматизованої модернізації та валідації C++ кодової бази

Модернізація великої промислової кодової бази обсягом у сотні тисяч або мільйони рядків не може здійснюватися ручним редагуванням файлів або примітивними скриптами на базі регулярних виразів. Ручне внесення змін неминуче породжує випадкові друкарські помилки, викликає масові конфлікти злиття гілок (merge conflicts) у команді та створює приховані регресії у багатопотоковому коді. Для безпечного переходу необхідний повністю автоматизований конвеєр, що поетапно трансформує абстрактне синтаксичне дерево (AST), фіксує проміжні результати в системі контролю версій Git та автоматично валідує збереження поведінки системи за допомогою розширеного тестового набору під контролем динамічних санітайзерів пам'яті та невизначеної поведінки.

Нижче наведено повну реалізацію інженерного конвеєра: покроковий алгоритм трансформації, скрипт автоматичної оркестрації на Python, механізм запобігання гонкам запису у спільні заголовні файли, методологію диференційного тестування, архітектурний шаблон повної ізоляції застарілих сторонніх бібліотек через C-сумісний інтерфейсний бар'єр, динамічне завантаження бібліотек через системні виклики `dlopen`, керування графом залежностей (DAG) у багатостандартних проєктах, а також протокол локалізації дефектів через автоматизований бісекційний аналіз.

## Архітектура та послідовність кроків конвеєра

Конвеєр модернізації базується на концепції атомарних транзакцій. Будь-яка комплексна зміна (наприклад, одночасне оновлення покажчиків, циклів і псевдонімів типів) розбивається на послідовність окремих ізольованих кроків за конкретними правилами AST.

Повний цикл обробки складається з шести послідовних етапів:

1. **Генерація та верифікація бази компіляції (`compile_commands.json`):**
   Система збірки CMake під час конфігурації генерує точний опис прапорців трансляції для кожної одиниці вихідного коду. База компіляції містить абсолютні шляхи до вихідних файлів, повні списки каталогів пошуку заголовків (`-I`, `-isystem`), препроцесорні визначення (`-D`) та поточний діалект стандарту мови. Компілятори й інструменти аналізу використовують цей файл як єдине джерело істини про те, як саме збирається кожен вихідний файл.

2. **Фіксація вихідного стану та створення контрольної точки Git:**
   Перед початком кожної операції скрипт перевіряє чистоту робочого дерева Git. Для модернізації створюється окрема ізольована гілка, а перед застосуванням кожного окремого правила фіксується внутрішній хеш коміту (англ. *checkpoint*), що гарантує миттєве повернення до працездатного стану в разі збою.

3. **Пакетна трансформація AST за допомогою Clang-Tidy:**
   Утиліта `clang-tidy` виконує семантичний розбір сирців і формує список структур `FixItHint`. Щоб уникнути пошкодження коду під час паралельної обробки кількох `.cpp` файлів, які підключають спільні `.hpp` заголовки, застосовується двофазний підхід: генерація файлів виправлень у форматі YAML з їхнім подальшим детермінованим злиттям через утиліту `clang-apply-replacements`. Це усуває стан гонитви, коли два паралельні процеси одночасно записують правки в один файл заголовка.

4. **Автоматична компіляція проєкту новим компілятором:**
   Після внесення правок виконується паралельна збірка всіх цільових об'єктів проєкту з увімкненими прапорцями суворої діагностики (`-Wall -Wextra -Werror -Wdeprecated-declarations`). Якщо компілятор фіксує синтаксичну помилку або неоднозначність типів, транзакція вважається невдалою.

5. **Запуск тестового набору під контролем санітайзерів:**
   Успішна компіляція не гарантує збереження семантики. Скрипт ініціює виконання модульних та системних тестів під контролем AddressSanitizer (ASan) для виявлення порушень меж пам'яті, UndefinedBehaviorSanitizer (UBSan) для перехоплення некоректних операцій та ThreadSanitizer (TSan) для моніторингу гонок даних.

6. **Ухвалення рішення (Commit або Rollback):**
   - У разі успішного проходження збірки та всіх тестів зміни автоматично фіксуються в Git з детальним повідомленням про назву перевірки та модифіковані компоненти.
   - Якщо збірка впала або хоча б один тест повернув ненульовий код, скрипт виконує команду `git reset --hard HEAD`, очищає невідстежувані тимчасові файли та заносить проблемне правило до звіту для ручного аудиту розробниками.

---

## Реалізація скрипта оркестрації модернізації (migrate_runner.py)

Скрипт автоматизує виконання конвеєра, контролює чергу перевірок від найпростіших синтаксичних до глибоких семантичних і забезпечує транзакційну безпеку кожної операції.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скрипт транзакційної модернізації C++ кодової бази на основі Clang-Tidy."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class MigrationPipeline:
    def __init__(self, build_dir: str, source_dir: str):
        self.build_dir = Path(build_dir).resolve()
        self.source_dir = Path(source_dir).resolve()
        self.compilation_db = self.build_dir / "compile_commands.json"
        self.fixes_dir = self.build_dir / "clang_tidy_fixes"

        if not self.compilation_db.exists():
            raise FileNotFoundError(
                f"Не знайдено базу компіляції: {self.compilation_db}\n"
                "Згенеруйте її командою: cmake -B <build_dir> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
            )

        # Черга правил: послідовність від безпечних до глибоких семантичних
        self.rules_queue = [
            ("modernize-use-nullptr", "Заміна літералів 0 та макросів NULL на nullptr"),
            ("modernize-use-override", "Додавання специфікатора override до віртуальних методів"),
            ("modernize-use-using", "Заміна конструкцій typedef на синтаксис using"),
            ("modernize-redundant-void-arg", "Видалення надлишкових параметрів void у функціях"),
            ("modernize-deprecated-headers", "Міграція застарілих C-заголовків на префіксні <c*>"),
            ("modernize-replace-auto-ptr", "Заміна забороненого std::auto_ptr на std::unique_ptr"),
            ("modernize-make-unique", "Заміна явних викликів new на std::make_unique"),
            ("modernize-make-shared", "Заміна явних викликів new на std::make_shared"),
            ("modernize-loop-convert", "Трансформація індексних та ітераторних циклів у range-based for"),
            ("modernize-use-nodiscard", "Додавання атрибута [[nodiscard]] для функцій без побічних ефектів"),
            ("modernize-use-starts-ends-with", "Заміна s.find()==0 на виклики s.starts_with (C++20)"),
        ]

    def _execute(self, cmd: list[str], cwd: Path = None) -> tuple[int, str, str]:
        """Виконує команду оболонки та повертає статус, stdout і stderr."""
        work_dir = cwd if cwd else self.source_dir
        proc = subprocess.run(
            cmd,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return proc.returncode, proc.stdout, proc.stderr

    def get_project_sources(self) -> list[str]:
        """Отримує перелік файлів власного коду проєкту з бази компіляції."""
        with open(self.compilation_db, "r", encoding="utf-8") as f:
            data = json.load(f)

        sources = []
        for entry in data:
            fpath = Path(entry["file"]).resolve()
            # Обробляємо лише файли нашого репозиторію, виключаючи сторонні залежності
            if fpath.is_relative_to(self.source_dir):
                ignored_subdirs = ["third_party", "extern", "build", "vendor", "submodules"]
                if not any(part in fpath.parts for part in ignored_subdirs):
                    if fpath.suffix in [".cpp", ".cc", ".cxx"]:
                        sources.append(str(fpath))

        return sorted(list(set(sources)))

    def apply_clang_tidy_rule(self, rule_name: str, sources: list[str]) -> bool:
        """Виконує аналіз Clang-Tidy та експортує виправлення у тимчасовий каталог."""
        if self.fixes_dir.exists():
            shutil.rmtree(self.fixes_dir)
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        print(f"[*] Запуск AST-аналізу для правила: {rule_name} ({len(sources)} файлів)...")

        # Використовуємо run-clang-tidy для безпечного збереження заміщень у YAML
        cmd = [
            "clang-tidy",
            f"-checks=-*,{rule_name}",
            f"--export-fixes={self.fixes_dir}/fixes.yaml",
            f"-p={self.build_dir}",
            f"-header-filter=^{self.source_dir}/.*",
        ] + sources

        # Clang-Tidy може повертати ненульовий статус, якщо знайдено зауваження
        self._execute(cmd)

        fixes_file = self.fixes_dir / "fixes.yaml"
        if not fixes_file.exists() or fixes_file.stat().st_size == 0:
            print(f"[-] Правило {rule_name} не знайшло шаблонів для заміни.")
            return False

        # Детерміноване застосування виправлень без ризику гонок запису у заголовки
        print("[*] Застосування згенерованих виправлень до кодової бази...")
        apply_cmd = ["clang-apply-replacements", str(self.fixes_dir)]
        ret, out, err = self._execute(apply_cmd)
        if ret != 0:
            print(f"[!] Помилка застосування виправлень: {err}")
            return False

        return True

    def validate_build_and_tests(self) -> bool:
        """Перевіряє успішність компіляції та виконання тестів під санітайзерами."""
        print("[*] Компіляція проєкту...")
        build_cmd = ["cmake", "--build", str(self.build_dir), "--parallel"]
        ret, stdout, stderr = self._execute(build_cmd)
        if ret != 0:
            print(f"[x] Помилка збірки після модернізації:\n{stderr}")
            return False

        print("[*] Виконання тестового набору через CTest...")
        test_cmd = [
            "ctest",
            "--test-dir", str(self.build_dir),
            "--output-on-failure",
            "--parallel", str(os.cpu_count() or 4)
        ]
        ret, stdout, stderr = self._execute(test_cmd)
        if ret != 0:
            print(f"[x] Тести провалилися:\n{stdout}\n{stderr}")
            return False

        print("[✓] Компіляція та тести пройшли без зауважень.")
        return True

    def run_pipeline(self):
        """Головний цикл виконання конвеєра модернізації."""
        sources = self.get_project_sources()
        print(f"Знайдено {len(sources)} файлів вихідного коду для перевірки.")

        for rule, desc in self.rules_queue:
            print(f"\n{'='*75}\n[ФАЗА МОДЕРНІЗАЦІЇ] Правило: {rule}\nОпис: {desc}\n{'='*75}")

            has_changes = self.apply_clang_tidy_rule(rule, sources)
            if not has_changes:
                continue

            # Перевіряємо статус робочої копії Git
            ret, status_out, _ = self._execute(["git", "status", "--porcelain"])
            if not status_out.strip():
                print(f"[-] Змін у робочому дереві Git не виявлено.")
                continue

            # Верифікація поведінки кодової бази
            if self.validate_build_and_tests():
                self._execute(["git", "add", "."])
                commit_msg = f"refactor(modernize): застосовано правило {rule}\n\n{desc}"
                self._execute(["git", "commit", "-m", commit_msg])
                print(f"[✓] Успішно зафіксовано транзакцію: {rule}")
            else:
                print(f"[!] Відкат робочого дерева через збій валідації правила: {rule}")
                self._execute(["git", "reset", "--hard", "HEAD"])
                self._execute(["git", "clean", "-fd"])
                print(f"[!] Правило {rule} потребує ручного втручання.")

        print("\n[✓] Конвеєр завершив роботу. Перегляньте історію комітів Git.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Використання: python migrate_runner.py <шлях_до_build> <шлях_до_source>")
        sys.exit(1)

    pipeline = MigrationPipeline(sys.argv[1], sys.argv[2])
    pipeline.run_pipeline()
```

---

## Методологія диференційного тестування та налаштування санітайзерів

Звичайної перевірки тверджень у модульних тестах часто недостатньо для виявлення тонких змін семантики мови. Наприклад, зміна порядку обчислення аргументів функції або зміна часу життя тимчасових об'єктів у C++17 може не викликати падіння простого тесту, але призведе до спотворення даних у виробничому середовищі.

Для виявлення таких дефектів застосовується **диференційне тестування** (англ. *Differential Testing*):

```
                       ┌────────────────────────┐
                       │  Набір тестових даних  │
                       │     (Golden Inputs)    │
                       └───────────┬────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
      ┌─────────────────────┐             ┌─────────────────────┐
      │   Бінарник C++03    │             │   Бінарник C++20    │
      │  (Еталонна версія)  │             │ (Модернізований код)│
      └──────────┬──────────┘             └──────────┬──────────┘
                 │                                   │
                 ▼                                   ▼
      ┌─────────────────────┐             ┌─────────────────────┐
      │ Еталонний результат │             │ Модернізований вивід│
      │   (Golden Output)   │             │   (Target Output)   │
      └──────────┬──────────┘             └──────────┬──────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │ Побайтове порівняння (diff)  │
                    │  та перевірка інваріантів    │
                    └──────────────────────────────┘
```

Якщо результати виконання не збігаються до останнього байта або логу, інженерна команда отримує точний сценарій регресії.

### Конфігурація CMake для складання тестів під санітайзерами

Для роботи з конвеєром збірка має бути зібрана з інструментальними прапорцями санітайзерів. Нижче наведено фрагмент конфігурації CMake:

```cmake
# Опція увімкнення санітайзерів
option(ENABLE_SANITIZERS "Увімкнути ASan, UBSan та LSan" OFF)

if(ENABLE_SANITIZERS)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        message(STATUS "Увімкнено санітайзери: AddressSanitizer, UndefinedBehaviorSanitizer")
        
        # Прапорці компіляції для точного відстеження стека
        set(SANITIZER_FLAGS "-fsanitize=address,undefined -fno-omit-frame-pointer -g -O1")
        
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${SANITIZER_FLAGS}")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${SANITIZER_FLAGS}")
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${SANITIZER_FLAGS}")
        set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${SANITIZER_FLAGS}")
    else()
        message(WARNING "Санітайзери підтримуються лише на компіляторах GCC та Clang")
    endif()
endif()
```

---

## Ізоляція застарілих бібліотек: C-сумісний інтерфейсний бар'єр та dlopen

Однією з найскладніших проблем при переході великого проєкту на C++17 або C++20 є наявність сторонніх пропрієтарних бібліотек без вихідного коду (Closed-source Precompiled Binaries). Такі бібліотеки скомпільовані під старий стандарт (наприклад, C++03 на GCC 4.8) і експортують заголовні файли з використанням заборонених типів, таких як `std::auto_ptr`, старих прив'язок STL чи несумісної реалізації `std::string` (Copy-On-Write).

Якщо спробувати підключити такий заголовок безпосередньо у новий модуль проєкту з прапорцем `-std=c++20`, компілятор негайно зупинить збірку через синтаксичну несумісність або згенерує бінарно пошкоджений виклик (ABI Mismatch).

Єдиним надійним архітектурним шаблоном розв'язання цієї проблеми є повна ізоляція застарілого коду за непрозорим інтерфейсним бар'єром (Adapter / PIMPL Pattern) або динамічне завантаження через системні виклики `dlopen` / `dlsym`.

### 1. Чистий заголовок інтерфейсу для сучасного C++20 коду (legacy_adapter.hpp)

Цей файл включається у всі нові модулі проєкту. Він не містить жодного застарілого типу, не підключає чужих заголовків і оперує виключно безпечними типами `std::unique_ptr` та `std::string_view`:

```cpp
#pragma once

#include <memory>
#include <string>
#include <string_view>

namespace modern_system {

// Непрозорий клас-адаптер для роботи із застарілим рушієм
class LegacyEngineAdapter {
public:
    LegacyEngineAdapter();
    ~LegacyEngineAdapter();

    // Заборона копіювання через небезпеку дублювання вказівників (Rule of 5)
    LegacyEngineAdapter(const LegacyEngineAdapter&) = delete;
    LegacyEngineAdapter& operator=(const LegacyEngineAdapter&) = delete;

    // Дозвіл безпечного переміщення ресурсу
    LegacyEngineAdapter(LegacyEngineAdapter&&) noexcept;
    LegacyEngineAdapter& operator=(LegacyEngineAdapter&&) noexcept;

    // Публічний API для решти кодової бази
    [[nodiscard]] bool configure(std::string_view config_path);
    [[nodiscard]] std::string execute_query(std::string_view query);

private:
    // Структура реалізації ховається у файлі .cpp (PIMPL)
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace modern_system
```

### 2. Реалізація адаптера в окремій одиниці трансляції (legacy_adapter.cpp)

Цей файл компілюється в ізольованому режимі, де дозволено включення старих заголовків або де застарілі інтерфейси транслюються у сучасну семантику з обов'язковим очищенням ресурсів:

```cpp
#include "legacy_adapter.hpp"
#include <cstdlib>
#include <cstring>

// Симуляція сторонньої бібліотеки епохи C++03
namespace vendor_cxx03 {
    struct VendorDatabaseEngine {
        bool init(const char* path) {
            return path != nullptr;
        }

        // Старий API повертає динамічно виділений C-рядок, який треба звільняти вручну
        char* process(const char* sql, int len) {
            if (!sql || len <= 0) return nullptr;
            const char* response_prefix = "SUCCESS_RESULT: ";
            std::size_t total_len = std::strlen(response_prefix) + static_cast<std::size_t>(len) + 1;
            char* buffer = static_cast<char*>(std::malloc(total_len));
            if (!buffer) return nullptr;
            std::strcpy(buffer, response_prefix);
            std::strncat(buffer, sql, static_cast<std::size_t>(len));
            return buffer;
        }

        void free_result(char* ptr) {
            std::free(ptr);
        }
    };
}

namespace modern_system {

struct LegacyEngineAdapter::Impl {
    vendor_cxx03::VendorDatabaseEngine engine;
};

LegacyEngineAdapter::LegacyEngineAdapter()
    : pimpl_(std::make_unique<Impl>()) {}

LegacyEngineAdapter::~LegacyEngineAdapter() = default;
LegacyEngineAdapter::LegacyEngineAdapter(LegacyEngineAdapter&&) noexcept = default;
LegacyEngineAdapter& LegacyEngineAdapter::operator=(LegacyEngineAdapter&&) noexcept = default;

bool LegacyEngineAdapter::configure(std::string_view config_path) {
    // Безпечне перетворення рядкового перегляду в сумісний null-terminated рядок
    std::string safe_path(config_path);
    return pimpl_->engine.init(safe_path.c_str());
}

std::string LegacyEngineAdapter::execute_query(std::string_view query) {
    std::string safe_query(query);
    char* raw_data = pimpl_->engine.process(
        safe_query.c_str(),
        static_cast<int>(safe_query.size())
    );

    if (!raw_data) {
        return {};
    }

    // Захоплення сирого вказівника у стандартний рядок C++ та негайне звільнення буфера
    std::string result(raw_data);
    pimpl_->engine.free_result(raw_data);
    return result;
}

} // namespace modern_system
```

### 3. Динамічна ізоляція застарілого бінарника через dlopen

Якщо стороння бібліотека скомпільована із зовсім іншою стандартною бібліотекою (наприклад, застаріла версія `libstdc++.so.5` проти системної `libstdc++.so.6`), статичне лінкування неможливе. У такому разі створюється C-сумісний плагін, завантажуваний через системний виклик `dlopen`:

```cpp
#include <dlfcn.h>
#include <stdexcept>
#include <string>

// Сигнатури чистих C-функцій без витоку STL-типів
using InitFunc = int (*)(const char*);
using ProcessFunc = int (*)(const char*, char*, int);

class DynamicPluginLoader {
    void* handle_{nullptr};
    InitFunc init_fn_{nullptr};
    ProcessFunc process_fn_{nullptr};

public:
    explicit DynamicPluginLoader(const char* lib_path) {
        // Завантаження бібліотеки в ізольованому просторі імен
        handle_ = dlopen(lib_path, RTLD_NOW | RTLD_LOCAL);
        if (!handle_) {
            throw std::runtime_error(std::string("Не вдалося завантажити бібліотеку: ") + dlerror());
        }

        // Отримання адрес чистих C-функцій
        init_fn_ = reinterpret_cast<InitFunc>(dlsym(handle_, "plugin_init"));
        process_fn_ = reinterpret_cast<ProcessFunc>(dlsym(handle_, "plugin_process"));

        if (!init_fn_ || !process_fn_) {
            dlclose(handle_);
            throw std::runtime_error("Символи інтерфейсу не знайдено в завантаженій бібліотеці");
        }
    }

    ~DynamicPluginLoader() {
        if (handle_) {
            dlclose(handle_);
        }
    }
};
```

Такий підхід повністю запобігає конфліктам таблиць символів лінкера та гарантує стабільну роботу навіть при взаємодії C++20 коду з модулями тридцятирічної давнини.

---

## Керування графом залежностей (DAG) у змішаних кодових базах

У масштабних корпоративних проєктах переведення всіх підсистем на новий стандарт за один крок є неможливим через розподіл відповідальності між різними командами. У такому разі дерево залежностей проєкту (Directed Acyclic Graph, DAG) модернізується знизу вгору.

Фундаментальне інженерне правило змішаних збірок полягає в наступному: **бібліотека вищого рівня може використовувати новіший або такий самий стандарт, ніж бібліотеки нижчого рівня, але ніколи не старіший**, за умови, що типи стандартної бібліотеки не перетинають бінарні межі модулів.

```
       ┌────────────────────────────────────────────────────────┐
       │             Клієнтський застосунок (C++20)             │
       └───────────────────────────┬────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
  ┌─────────────────────────────┐     ┌─────────────────────────────┐
  │   Мережевий модуль (C++17)  │     │    Графічний рушій (C++17)  │
  └──────────────┬──────────────┘     └──────────────┬──────────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                  ┌─────────────────────────────────┐
                  │    Базова математика (C++11)    │
                  └─────────────────────────────────┘
```

Для реалізації цієї схеми в CMake використовуються цільові властивості `target_compile_features` із модифікатором `PRIVATE` для внутрішнього коду та `INTERFACE` для експортованих заголовків:

```cmake
# Базова бібліотека зі стандартом C++11
add_library(math_core src/math.cpp)
target_compile_features(math_core PUBLIC cxx_std_11)

# Проміжний модуль, що використовує C++17 для внутрішньої оптимізації
add_library(network_engine src/net.cpp)
target_compile_features(network_engine PRIVATE cxx_std_17)
target_compile_features(network_engine INTERFACE cxx_std_11)
target_link_libraries(network_engine PRIVATE math_core)

# Головний бінарник на C++20
add_executable(app main.cpp)
target_compile_features(app PRIVATE cxx_std_20)
target_link_libraries(app PRIVATE network_engine)
```

Такий підхід гарантує, що внутрішня модернізація окремого підмодуля до C++17 не змушує всі залежні проєкти негайно оновлювати свої прапорці компіляції.

---

## Автоматизований бісекційний аналіз регресій (Git Bisect Integration)

Якщо після виконання серії модернізаційних комітів виникає рідкісна регресія продуктивності або приховане пошкодження пам'яті, локалізація дефектного правила вручну займає години. Для автоматизації цього процесу створюється скрипт-валідатор для команди `git bisect run`.

```bash
#!/usr/bin/env bash
# bisect_validator.sh — скрипт автоматичної локалізації регресії

set -e

# 1. Швидка збірка проєкту
cmake --build build --target test_suite --parallel $(nproc) > /dev/null 2>&1

# 2. Запуск цільового тесту під AddressSanitizer
export ASAN_OPTIONS="abort_on_error=1:detect_leaks=1"
./build/bin/test_suite --gtest_filter=PerformanceRegressionTest.* > /dev/null 2>&1

# Код виходу 0 — коміт хороший, код > 0 — коміт зламано
exit $?
```

Інженер запускає команду `git bisect start HEAD v1.0.0` та передає валідатор `git bisect run ./bisect_validator.sh`. Git автоматично за логарифмічний час знаходить точний коміт модернізації, який вніс дефект, дозволяючи точково виправити правило трансформації.

---

## Інженерні крайові випадки та аналіз дефектів авторефакторингу

Під час практичного використання конвеєра команда обов'язково зіткнеться з крайовими випадками, де автоматичні інструменти можуть пошкодити код:

1. **Конфлікти паралельного запису у заголовні файли:**
   Якщо `clang-tidy` запускається у кілька потоків на різних вихідних файлах, які підключають один спільний заголовок `types.hpp`, обидва процеси можуть спробувати внести зміни в той самий рядок (наприклад, додати `override`). Це призводить до появи конструкцій `override override` або розриву синтаксису.
   *Рішення:* Використання опції `--export-fixes` та утиліти `clang-apply-replacements`, яка збирає виправлення з усіх одиниць трансляції в пам'яті, усуває дублікати та детерміновано застосовує їх до файлів на диску в один потік.

2. **Неявне видалення або блокування конструктора переміщення (Rule of 5):**
   У старих кодових базах часто зустрічаються класи з явно оголошеним деструктором, але без конструктора копіювання чи переміщення (`~MyClass() { delete ptr_; }`). У C++98 такий клас неявно копіювався. У C++11/17 наявність деструктора пригнічує автоматичну генерацію конструктора переміщення. Коли `modernize-pass-by-value` замінює передачу на `std::move(param)`, компілятор тихо відкочується до дорогого глибокого копіювання замість переміщення.
   *Рішення:* Додатковий запуск правила `cppcoreguidelines-special-member-functions` для явного визначення або заборони всіх п'яти спеціальних функцій-членів.

3. **Інвалідація ітераторів у range-based for циклах:**
   Якщо старий індексний цикл викликав методи додавання або видалення елементів вектора (`v.push_back(x)` або `v.erase(it)`), перетворення на `for (auto& item : v)` призводить до миттєвого інвалідування внутрішніх ітераторів діапазону.
   *Рішення:* Попередній статичний аналіз коду на предмет викликів модифікуючих методів контейнера всередині тіла циклу та обов'язковий запуск тестів під AddressSanitizer.

4. **Зміна порядку обчислення аргументів та виразів присвоєння у C++17:**
   До стандарту C++17 порядок обчислення операндів у виразах на кшталт `f(a(), b())` або `v[i] = i++` був повністю невизначеним (англ. *unsequenced / unspecified*). У C++17 стандарт чітко зафіксував порядок: лівий операнд у присвоєнні та виборі елемента обчислюється раніше правого. Якщо старий код неявно покладався на порядок обчислень конкретного компілятора, оновлення стандарту може змінити значення виразу.
   *Рішення:* Виявлення конструкцій із множинними модифікаціями однієї змінної в одному виразі за допомогою правила `clang-tidy` `bugprone-unhandled-self-assignment` та прапорця компілятора `-Wsequence-point`.

5. **Розбіжність SFINAE-виразів та концептів C++20:**
   При модернізації шаблонних бібліотек заміна `std::enable_if_t` на концептуальні вирази `requires` може змінити правила перевантаження функцій. Концепти беруть участь у впорядкуванні за ступенем специфічності (англ. *subsumption rules*), тоді як SFINAE працювало через видалення невідповідних кандидатів. Якщо концепт перекриває кілька варіантів перевантаження, компілятор вимагатиме суворого впорядкування обмежень, генеруючи помилку неоднозначності (Ambiguous Overload).
   *Рішення:* Поетапна заміна SFINAE на `if constexpr` всередині тіл функцій перед введенням повноцінних концептів на рівні сигнатур.

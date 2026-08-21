# ⚙️ Конфігураційний пайплайн: версіонування з Git та перемикачі функцій

У промисловій розробці програмного забезпечення на C та C++ вихідний бінарний файл повинен містити дві взаємодоповнюючі категорії інформації про збірку: статичні метадані версії релізу (семантична версія `MAJOR.MINOR.PATCH`, назва проєкту, ліцензія) та динамічний стан оточення розробника (короткий геш коміту Git, наявність локальних незакомічених правок, прапорці апаратних і програмних модулів). Нижче наведено завершений, самодостатній інженерний проєкт, який реалізує наскрізний конфігураційний конвеєр із повною ізоляцією артефактів збірки.

## Архітектурні вимоги та структура файлів

Проєкт будується навколо наступних ключових принципів:

1. **Недоторканність дерева джерел:** Репозиторій Git розглядається як доступний виключно для читання. Усі згенеровані заголовки `config.h` та `version.hpp` створюються в ізольованому каталозі збірки всередині `${CMAKE_CURRENT_BINARY_DIR}`. Це унеможливлює випадкове потрапляння згенерованих файлів у коміти системи контролю версій та дозволяє виконувати паралельні збірки з різними налаштуваннями з одного вихідного дерева.
2. **Захист від відсутності Git:** Якщо збірка виконується з розпакованого tar-архіву дистрибутива Linux (де каталог `.git` відсутній) або в ізольованому контейнері CI без встановленої утиліти Git, процес конфігурації не повинен завершуватися аварійно. Для таких випадків передбачено надійні резервні значення за замовчуванням.
3. **Строга типізація у C++ та сумісність із чистим C:** Код на C отримує традиційні числові макроси препроцесора через заголовок `config.h`, а код на C++20 використовує безпечні константи `std::string_view` та `inline constexpr` у власному просторі імен через заголовок `version.hpp`.
4. **Уникнення лавинних перекомпіляцій:** Завдяки вбудованому побайтовому порівнянню в `configure_file` зміна непов'язаних файлів `CMakeLists.txt` не змінює дату модифікації (`mtime`) заголовків, якщо значення змінних залишилися попередніми. Система збірки Ninja відстежує залежності через dep-файли компілятора та перекомпільовує лише ті файли, які безпосередньо залежать від змінених заголовків.

Файлова ієрархія проєкту організована наступним чином:

```text
diagnostics-app/
├── CMakeLists.txt
├── cmake/
│   └── GetGitRevision.cmake
├── include/
│   └── diag/
│       ├── config.h.in
│       └── version.hpp.in
└── src/
    ├── main.c
    └── main.cpp
```

## Крок 1. Вилучення динамічних метаданих із Git (cmake/GetGitRevision.cmake)

Модуль `GetGitRevision.cmake` інкапсулює всю логіку взаємодії з системою контролю версій. Він шукає виконуваний файл `git` за допомогою штатної команди `find_package(Git QUIET)`, перевіряє наявність каталогу `.git` у корені проєкту та виконує опитування репозиторію через команду `execute_process`.

Ми вилучаємо три ключові параметри: скорочений SHA-1 геш поточного коміту (7 символів), поточну робочу гілку (або стан `HEAD` при від'єднаному покажчику) та ознаку наявності незакомічених локальних модифікацій (брудне робоче дерево, *dirty working tree*).

```cmake
# cmake/GetGitRevision.cmake
# Модуль безпечного вилучення інформації про Git-ревізію

find_package(Git QUIET)

# Резервні значення на випадок збірки поза репозиторієм або без встановленого Git
set(DIAG_GIT_HASH "unknown")
set(DIAG_GIT_BRANCH "unknown")
set(DIAG_GIT_DIRTY_FLAG 0)

if(GIT_FOUND AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.git")
    # 1. Отримання 7-символьного скороченого SHA-1 поточного коміту
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" rev-parse --short=7 HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_hash_out
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _git_hash_res
    )
    if(_git_hash_res EQUAL 0 AND NOT "${_git_hash_out}" STREQUAL "")
        set(DIAG_GIT_HASH "${_git_hash_out}")
    endif()

    # 2. Отримання імені поточної гілки (або HEAD у разі detached state)
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" rev-parse --abbrev-ref HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_branch_out
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _git_branch_res
    )
    if(_git_branch_res EQUAL 0 AND NOT "${_git_branch_out}" STREQUAL "")
        set(DIAG_GIT_BRANCH "${_git_branch_out}")
    endif()

    # 3. Перевірка статусу робочого дерева на наявність незакомічених змін
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" status --porcelain
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_status_out
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _git_status_res
    )
    if(_git_status_res EQUAL 0 AND NOT "${_git_status_out}" STREQUAL "")
        # Якщо вивід не порожній, у дереві є змінені або додані файли
        set(DIAG_GIT_DIRTY_FLAG 1)
    endif()
else()
    # Якщо Git відсутній або папки .git немає (наприклад, збірка з tar.gz)
    set(DIAG_GIT_HASH "release-tarball")
    set(DIAG_GIT_BRANCH "release")
endif()
```

## Крок 2. Проєктування шаблонів заголовків

### Заголовок для перемикачів функцій (include/diag/config.h.in)

Цей заголовок проєктується так, щоб його можна було безперешкодно підключати як у чистий код C11, так і в сучасний C++20. Для всіх логічних прапорців використовується директива `#cmakedefine01`, яка усуває небезпеку помилкової поведінки при забутому `#include`.

```text
/* include/diag/config.h.in — шаблон препроцесорної конфігурації */
#ifndef DIAG_CONFIG_H
#define DIAG_CONFIG_H

/* Ознака активації модуля стиснення даних Zstandard (1 або 0) */
#cmakedefine01 DIAG_ENABLE_ZSTD

/* Ознака активації діагностичного мережевого трасування (1 або 0) */
#cmakedefine01 DIAG_ENABLE_TRACING

/* Ознака підтримки розширеного апаратного набору інструкцій AVX-512 */
#cmakedefine01 DIAG_ENABLE_AVX512

/* Розмір кільцевого буфера для запису системних журналів */
#cmakedefine DIAG_BUFFER_SIZE @DIAG_BUFFER_SIZE@

#endif /* DIAG_CONFIG_H */
```

### Заголовок статичних та динамічних метаданих (include/diag/version.hpp.in)

Цей заголовок демонструє сучасний ідіоматичний підхід у мові C++: повну відмову від нетипізованих макросів на користь константних виразів часу компіляції (`inline constexpr`), суворої типізації `std::uint32_t` та незмінних рядкових представлень `std::string_view`. Усі змінні CMake обрамлені маркерами `@VAR@`, а виклик `configure_file` захищений опцією `@ONLY`.

```cpp
// include/diag/version.hpp.in — шаблон типізованих метаданих версії C++
#pragma once

#include <cstdint>
#include <string_view>

namespace diag::version {

// Текстова назва проєкту, отримана з директиви project(...)
inline constexpr std::string_view project_name{"@PROJECT_NAME@"};

// Повний семантичний рядок версії (наприклад "2.4.1")
inline constexpr std::string_view version_string{"@PROJECT_VERSION@"};

// Коротка ревізія коміту Git
inline constexpr std::string_view git_commit_hash{"@DIAG_GIT_HASH@"};

// Ім'я активної гілки Git
inline constexpr std::string_view git_branch{"@DIAG_GIT_BRANCH@"};

// Числові складові версії для програмного порівняння в if constexpr
inline constexpr std::uint32_t major{@PROJECT_VERSION_MAJOR@};
inline constexpr std::uint32_t minor{@PROJECT_VERSION_MINOR@};
inline constexpr std::uint32_t patch{@PROJECT_VERSION_PATCH@};

// Ознака того, що бінарний файл зібрано з модифікованого робочого дерева
inline constexpr bool is_dirty_tree{@DIAG_GIT_DIRTY_FLAG@};

} // namespace diag::version
```

## Крок 3. Головний сценарій збірки (CMakeLists.txt)

Сценарій зв'язує систему опцій користувача, виклик генерації шаблонів та експорт вимог вжитку заголовків для цілей збірки.

Зверніть особливу увагу на використання генераторних виразів `$<BUILD_INTERFACE:...>` та `$<INSTALL_INTERFACE:...>`. Під час розробки всередині репозиторію компілятор шукатиме згенеровані файли у каталозі збірки `build/generated/include`. Проте після інсталяції бібліотеки в систему командою `cmake --install` ці шляхи будуть замінені на стандартний відносний каталог `include`, що гарантує переносність експортованих пакетів.

```cmake
cmake_minimum_required(VERSION 3.20)
project(DiagnosticsTool VERSION 2.4.1 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Оголошення опцій користувача, які потрапляють у кеш збірки
option(DIAG_ENABLE_ZSTD "Увімкнути підтримку стиснення Zstandard" ON)
option(DIAG_ENABLE_TRACING "Увімкнути детальне діагностичне трасування" OFF)
option(DIAG_ENABLE_AVX512 "Активація апаратних інструкцій AVX-512" OFF)

set(DIAG_BUFFER_SIZE 8192 CACHE STRING "Розмір внутрішнього буфера журналів")

# Підключення модуля вилучення даних Git
include(cmake/GetGitRevision.cmake)

# Визначення шляху до ізольованого каталогу згенерованих заголовків
set(GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated/include")

# Генерація файлу препроцесорних директив (config.h)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/include/diag/config.h.in"
    "${GENERATED_INCLUDE_DIR}/diag/config.h"
    @ONLY
)

# Генерація файлу типізованих констант C++ (version.hpp)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/include/diag/version.hpp.in"
    "${GENERATED_INCLUDE_DIR}/diag/version.hpp"
    @ONLY
)

# Створення бібліотеки ядра
add_library(diag_core STATIC)

# Експорт шляхів до заголовків через генераторні вирази вимог вжитку
target_include_directories(diag_core PUBLIC
    $<BUILD_INTERFACE:${GENERATED_INCLUDE_DIR}>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Створення демонстраційних утиліт на C та C++
add_executable(diag_cli_c src/main.c)
target_link_libraries(diag_cli_c PRIVATE diag_core)

add_executable(diag_cli_cpp src/main.cpp)
target_link_libraries(diag_cli_cpp PRIVATE diag_core)
```

## Крок 4. Реалізація клієнтських програм

Клієнтський код демонструє два принципово різних підходи до споживання згенерованих даних: класичний C11 на базі `#if` та сучасний C++20 на базі `if constexpr` і `std::string_view`.

:::tabs
```c
/* src/main.c — реалізація утиліти на чистій мові C11 */
#include <stdio.h>
#include <stdint.h>
#include "diag/config.h"

int main(void) {
    printf("========================================\n");
    printf("Діагностична утиліта ядра (C11 клієнт)\n");
    printf("========================================\n");
    printf("Розмір виділеного буфера: %d байтів\n", (int)DIAG_BUFFER_SIZE);

#if DIAG_ENABLE_ZSTD
    printf("Підсистема стиснення: модуль Zstandard [УВІМКНЕНО]\n");
#else
    printf("Підсистема стиснення: raw stream [ВИМКНЕНО]\n");
#endif

#if DIAG_ENABLE_TRACING
    printf("Мережеве трасування: розширений журнал [АКТИВНИЙ]\n");
#else
    printf("Мережеве трасування: вимкнено для економії CPU\n");
#endif

#if DIAG_ENABLE_AVX512
    printf("Векторні операції: векторні регістри ZMM 512-біт\n");
#else
    printf("Векторні операції: базовий набір SSE/AVX2\n");
#endif

    return 0;
}
```
```cpp
// src/main.cpp — сучасна реалізація утиліти на мові C++20
#include <iostream>
#include <span>
#include <vector>
#include "diag/config.h"
#include "diag/version.hpp"

int main() {
    std::cout << "========================================\n";
    std::cout << diag::version::project_name << " (C++20 клієнт)\n";
    std::cout << "========================================\n";
    std::cout << "Версія продукту: " << diag::version::version_string
              << " (компоненти: " << diag::version::major << "."
              << diag::version::minor << "." << diag::version::patch << ")\n";
    std::cout << "Git ревізія:     " << diag::version::git_commit_hash
              << " [гілка: " << diag::version::git_branch << "]";

    if constexpr (diag::version::is_dirty_tree) {
        std::cout << " [УВАГА: незакомічені локальні зміни!]";
    }
    std::cout << "\n----------------------------------------\n";

    // Безпечне розгалуження часу компіляції за допомогою if constexpr
    if constexpr (DIAG_ENABLE_ZSTD) {
        std::cout << "Стиснення даних: Zstandard скомпільовано в бінарний файл\n";
    } else {
        std::cout << "Стиснення даних: пряма передача без пакування\n";
    }

    if constexpr (DIAG_ENABLE_TRACING) {
        std::cout << "Діагностика: активовано високоточні лічильники подій\n";
    }

    std::cout << "Розмір внутрішнього буфера: " << DIAG_BUFFER_SIZE << " байтів\n";
    return 0;
}
```
:::

## Аналіз поведінки та верифікація збірки

Перевіримо роботу конфігураційного конвеєра в реальних виробничих сценаріях:

1. **Перший запуск збірки:**
   Команда `cmake -B build -G Ninja` створює каталог `build/`, виконує модуль `GetGitRevision.cmake` та генерує два файли у каталозі `build/generated/include/diag/`. Компілятор збирає обидві утиліти, успішно знаходячи згенеровані заголовки за правилом `target_include_directories`.
2. **Повторний запуск без зміни стану:**
   Виклик `ninja -C build` миттєво повертає `ninja: no work to do`. Побайтове порівняння у `configure_file` залишило атрибути `mtime` незмінними, тому жоден об'єктний файл не перекомпільовується.
3. **Створення нового коміту в Git:**
   Після виклику `git commit` та запуску `ninja -C build`, система збірки виявляє необхідність повторної конфігурації CMake. Скрипт вилучає новий геш коміту. `configure_file` фіксує зміну байтів у `version.hpp` і перезаписує його, але залишає файл `config.h` незмінним. У результаті Ninja перекомпільовує **виключно** файл `main.cpp` (який підключає `version.hpp`), тоді як файл `main.c` (який залежить лише від `config.h`) не перекомпільовується взагалі.
4. **Робота у неглибоких клонах CI (Shallow Clones):**
   Під час виконання задач у CI/CD системах (наприклад, GitHub Actions чи GitLab CI) репозиторій зазвичай клонується з параметром `--depth 1`. Команда `git rev-parse --short=7 HEAD` коректно повертає геш верхнього коміту навіть за відсутності повної історії тегів, запобігаючи збоям автоматизованих конвеєрів.

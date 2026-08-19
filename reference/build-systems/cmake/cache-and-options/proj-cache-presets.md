# ⚙️ Практика: модульна система опцій, валідація та скрипти попереднього кешування

Ця вставка розбирає практичну архітектуру конфігурації промислового кросплатформового C/C++ проєкту з розгалуженим деревом функціональних модулів, залежними опціями, суворою перевіркою коректності введених значень та автоматизованим завантаженням конфігураційних профілів для систем неперервної інтеграції (CI/CD).

## 1. Постановка інженерної задачі

Розробка масштабних системного рівня бібліотек та служб вимагає вирішення суперечливих завдань: з одного боку, система збірки повинна надавати розробникам та інтеграторам максимальну гнучкість у виборі підтримуваних протоколів, форматів та апаратних бекендів; з іншого боку, конфігуратор зобов'язаний гарантувати, що отримана комбінація параметрів є коректною, несуперечливою і фізично підтримується цільовою платформою.

У цьому практичному проекті ми реалізуємо систему конфігурації для високопродуктивної бібліотеки синхронізації мультимедійних потоків `mediasync`. Бібліотека проектується для роботи на широкому спектрі платформ — від високонавантажених серверів під керуванням Linux до робочих станцій Windows та портативних вбудованих пристроїв.

### Архітектурні вимоги до системи конфігурації

1. **Модульність та ізоляція**: ядро бібліотеки має збиратися за мінімальних залежностей (виключно стандартні системні потоки), тоді як додаткові можливості (мережевий транспорт, апаратне кодування, графічний моніторинг) мають вмикатися за допомогою незалежних перемикачів.
2. **Умовні апаратні залежності**: модуль апаратного прискорення відео (VA-API) повинен бути доступним для активації лише на операційній системі Linux і лише за умови фізичної наявності системної бібліотеки `libva`. На інших платформах або за відсутності бібліотеки опція не повинна з'являтися у списку доступних налаштувань.
3. **Строга типізація та валідація переліків**: вибір мережевого бекенду (QUIC, TCP, UNIX-сокети) та рівня деталізації журналювання (DEBUG, INFO, WARN, ERROR) має бути обмежений фіксованим списком варіантів. Будь-які друкарські помилки користувача в командному рядку повинні перехоплюватися на ранньому етапі конфігурації з генерацією вичерпного діагностичного повідомлення.
4. **Ієрархія та фільтрація складності**: параметри внутрішнього тюнінгу (розміри кільцевих буферів, порти системної телеметрії) мають бути приховані від звичайного користувача через механізм `ADVANCED`, щоб не перевантажувати графічні інтерфейси.
5. **Профілі попереднього завантаження (Initial Cache)**: створення стандартизованих наборів налаштувань для серверів тестування (Release-збірки на базі Clang) та робочих місць розробників (Debug-збірки з інтегрованими динамічними санітайзерами пам'яті ASan/UBSan).

---

## 2. Структура файлового дерева проєкту

Організація файлів проєкту чітко розмежовує сценарії конфігурації, системні профілі, заголовки, реалізації різними мовами програмування та тести:

```text
mediasync/
├── CMakeLists.txt
├── cmake/
│   ├── ConfigValidation.cmake
│   └── profiles/
│       ├── ci-linux-release.cmake
│       └── dev-debug-asan.cmake
├── include/
│   └── mediasync/
│       └── mediasync.h
├── src/
│   ├── mediasync.c
│   ├── mediasync.cpp
│   ├── config.h.in
│   └── main.cpp
└── tests/
    └── test_sync.cpp
```

Каталог `cmake/profiles/` містить незалежні сценарії попереднього кешування, які завантажуються через прапорець `-C`. Каталог `src/` містить файл шаблону `config.h.in`, який перетворюється на згенерований C/C++ заголовок `mediasync_config.h` у каталозі збірки.

---

## 3. Проєктування кореневого CMakeLists.txt

Кореневий файл описує інтерфейс проєкту. Нижче наведено детальний текст сценарію з детальними коментарями щодо кожного кроку конфігурації:

```cmake
cmake_minimum_required(VERSION 3.24)
project(mediasync VERSION 2.4.0 LANGUAGES C CXX)

# Встановлення обов'язкових стандартів мов програмування
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Підключення вбудованих та власних модулів розширення
include(CMakeDependentOption)
include(FeatureSummary)
include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/ConfigValidation.cmake")

# ── 1. Оголошення базових прапорців конфігурації ──────────────────────────────
option(MEDIASYNC_BUILD_TOOLS "Збирати утиліти командного рядка та діагностики" ON)
option(MEDIASYNC_ENABLE_TESTS "Збирати модульні та інтеграційні тести" ON)
option(MEDIASYNC_ENABLE_LOGGING "Увімкнути детальне журналювання подій" ON)

# ── 2. Рядкові переліки з випадаючими списками (STRINGS) ───────────────────────
set(MEDIASYNC_NETWORK_BACKEND "QUIC" CACHE STRING "Мережевий протокол передачі потоків")
set_property(CACHE MEDIASYNC_NETWORK_BACKEND PROPERTY STRINGS "QUIC" "TCP" "UNIX_SOCKET")

set(MEDIASYNC_LOG_LEVEL "INFO" CACHE STRING "Мінімальний рівень деталізації журналювання")
set_property(CACHE MEDIASYNC_LOG_LEVEL PROPERTY STRINGS "DEBUG" "INFO" "WARN" "ERROR")

# ── 3. Інтроспекція системи та пошук зовнішніх залежностей ─────────────────────
find_package(Threads REQUIRED)

# Пошук бібліотеки апаратного кодування VA-API (лише для цільової платформи Linux)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(LIBVA QUIET libva)
    endif()
endif()

# Пошук фреймворку Qt6 для компіляції графічного інтерфейсу моніторингу
find_package(Qt6 QUIET COMPONENTS Core Widgets)

# ── 4. Декларація залежних опцій (CMakeDependentOption) ───────────────────────
# Апаратне прискорення через VA-API доступне лише на Linux і за наявності libva
cmake_dependent_option(
    MEDIASYNC_USE_VAAPI
    "Використовувати апаратне прискорення кодування через VA-API" ON
    "CMAKE_SYSTEM_NAME STREQUAL \"Linux\";LIBVA_FOUND" OFF
)

# Графічний монітор синхронізації активний лише якщо увімкнено утиліти і знайдено Qt6
cmake_dependent_option(
    MEDIASYNC_BUILD_GUI_MONITOR
    "Збирати графічний монітор синхронізації на базі Qt6" ON
    "MEDIASYNC_BUILD_TOOLS;Qt6_FOUND" OFF
)

# ── 5. Налаштування просунутих інженерних параметрів (ADVANCED) ───────────────
set(MEDIASYNC_RING_BUFFER_CAPACITY 65536 CACHE STRING "Розмір кільцевого буфера кадрів (у байтах)")
set(MEDIASYNC_METRICS_PORT 9090 CACHE STRING "Порт експорту телеметрії Prometheus")

mark_as_advanced(
    MEDIASYNC_RING_BUFFER_CAPACITY
    MEDIASYNC_METRICS_PORT
    LIBVA_INCLUDE_DIRS
    LIBVA_LIBRARIES
)

# ── 6. Валідація кешу перед створенням цілей збірки ────────────────────────────
mediasync_validate_cache_configuration()

# ── 7. Генерація заголовка конфігурації ────────────────────────────────────────
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/src/config.h.in"
    "${CMAKE_CURRENT_BINARY_DIR}/include/mediasync_config.h"
    @ONLY
)

# ── 8. Створення цілей збірки та налаштування властивостей ────────────────────
add_library(mediasync_core
    src/mediasync.c
    src/mediasync.cpp
)

target_include_directories(mediasync_core
    PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>"
        "$<INSTALL_INTERFACE:include>"
)

target_link_libraries(mediasync_core
    PUBLIC
        Threads::Threads
)

if(MEDIASYNC_USE_VAAPI)
    target_include_directories(mediasync_core PRIVATE ${LIBVA_INCLUDE_DIRS})
    target_link_libraries(mediasync_core PRIVATE ${LIBVA_LIBRARIES})
endif()

# Генерація підсумкового звіту про стан усіх модулів
feature_summary(
    WHAT ALL 
    INCLUDE_QUIET_PACKAGES 
    DESCRIPTION "=== Підсумковий звіт конфігурації mediasync ==="
)
```

---

## 4. Логіка валідації параметрів кешу: cmake/ConfigValidation.cmake

Однією з найпоширеніших проблем у проектах на CMake є передача користувачами нечинних значень через прапорці командного рядка `-D`. Оскільки CMake розглядає значення змінних кешу як довільні текстові рядки, виклик команди `cmake -B build -DMEDIASYNC_NETWORK_BACKEND=quic` (у нижньому регістрі) або `cmake -B build -DMEDIASYNC_NETWORK_BACKEND=WEBSOCKET` буде прийнятий інтерпретатором без попереджень.

Якщо конфігуратор не містить явної перевірки, нечинний рядок потрапить у згенерований заголовок `config.h`. Це призведе або до помилки компіляції десь у глибині коду, або, що значно гірше, до прихованого падіння програми під час виконання через невиконання блоків умовного макропроцесингу.

Функція валідації `mediasync_validate_cache_configuration` виконує строгу верифікацію всіх параметрів за трьома критеріями:
1. Перевірка відповідності рядкових опцій списку дозволених значень з властивості `STRINGS`.
2. Перевірка числових діапазонів для запобігання переповненню пам'яті або виділенню буферів нульового розміру.
3. Перевірка логічної сумісності активованих компонентів.

```cmake
function(mediasync_validate_cache_configuration)
    # 1. Валідація вибору мережевого транспорту
    get_property(allowed_backends CACHE MEDIASYNC_NETWORK_BACKEND PROPERTY STRINGS)
    if(NOT MEDIASYNC_NETWORK_BACKEND IN_LIST allowed_backends)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: нечинне значення MEDIASYNC_NETWORK_BACKEND='${MEDIASYNC_NETWORK_BACKEND}'.\n"
            "Дозволені варіанти: ${allowed_backends}\n"
            "Зверніть увагу, що значення чутливі до регістру символів.")
    endif()

    # 2. Валідація рівня журналювання
    get_property(allowed_levels CACHE MEDIASYNC_LOG_LEVEL PROPERTY STRINGS)
    if(NOT MEDIASYNC_LOG_LEVEL IN_LIST allowed_levels)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: нечинне значення MEDIASYNC_LOG_LEVEL='${MEDIASYNC_LOG_LEVEL}'.\n"
            "Дозволені варіанти: ${allowed_levels}")
    endif()

    # 3. Перевірка числового діапазону для розміру кільцевого буфера
    # Буфер не може бути меншим за розмір одного мережевого MTU (1024 байти)
    # та більшим за 10 мегабайтів для запобігання вичерпанню RAM
    if(MEDIASYNC_RING_BUFFER_CAPACITY LESS 1024 OR MEDIASYNC_RING_BUFFER_CAPACITY GREATER 10485760)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: MEDIASYNC_RING_BUFFER_CAPACITY встановлено у ${MEDIASYNC_RING_BUFFER_CAPACITY}.\n"
            "Допустимий діапазон становить від 1024 до 10485760 байтів (1 КБ – 10 МБ).")
    endif()

    # 4. Перевірка мережевого порту метрик
    if(MEDIASYNC_METRICS_PORT LESS 1024 OR MEDIASYNC_METRICS_PORT GREATER 65535)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: MEDIASYNC_METRICS_PORT (${MEDIASYNC_METRICS_PORT}) "
            "має бути непривілейованим портом у діапазоні 1024–65535.")
    endif()

    message(STATUS "[mediasync] Усі параметри кешу пройшли успішну валідацію.")
endfunction()
```

---

## 5. Шаблон конфігураційного заголовка: src/config.h.in

Шаблон заголовка транслює змінні інтерпретатора CMake у директиви мов C та C++. Директива `#cmakedefine` є спеціалізованою інструкцією CMake: якщо однойменна змінна у сценарії збірки обчислюється як істинна (`TRUE`, `ON`, `1`), рядок перетворюється на `#define VAR 1`; якщо змінна хибна (`FALSE`, `OFF`, `0`), рядок замінюється на коментар `/* #undef VAR */`.

Синтаксис `@VARIABLE@` здійснює пряму підстановку текстового або числового значення змінної CMake:

```text
#ifndef MEDIASYNC_CONFIG_H
#define MEDIASYNC_CONFIG_H

/* Метадані версії бібліотеки */
#define MEDIASYNC_VERSION_MAJOR @mediasync_VERSION_MAJOR@
#define MEDIASYNC_VERSION_MINOR @mediasync_VERSION_MINOR@
#define MEDIASYNC_VERSION_PATCH @mediasync_VERSION_PATCH@
#define MEDIASYNC_VERSION_STRING "@mediasync_VERSION@"

/* Булеві перемикачі функціоналу */
#cmakedefine MEDIASYNC_ENABLE_LOGGING
#cmakedefine MEDIASYNC_USE_VAAPI
#cmakedefine MEDIASYNC_BUILD_GUI_MONITOR

/* Текстові конфігураційні параметри */
#define MEDIASYNC_NETWORK_BACKEND "@MEDIASYNC_NETWORK_BACKEND@"
#define MEDIASYNC_LOG_LEVEL_STRING "@MEDIASYNC_LOG_LEVEL@"

/* Числові конфігураційні параметри */
#define MEDIASYNC_BUFFER_SIZE @MEDIASYNC_RING_BUFFER_CAPACITY@
#define MEDIASYNC_DEFAULT_PORT @MEDIASYNC_METRICS_PORT@

#endif /* MEDIASYNC_CONFIG_H */
```

---

## 6. Використання конфігурації у вихідному коді: C та C++

Згенерований заголовок підключається до вихідних файлів бібліотеки. Нижче наведено приклад взаємодії коду з параметрами конфігурації: мовою C показано пряму роботу зі структурами та ручним керуванням пам'яттю, а мовою C++20 — ідіоматичний підхід з використанням незмінних типів (`std::string_view`), строгих переліків та концепції RAII (Resource Acquisition Is Initialization).

:::tabs
```c
/* src/mediasync.c — чиста реалізація мовою C11 */
#include "mediasync_config.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    size_t buffer_capacity;
    char network_backend[32];
    int vaapi_enabled;
    int metrics_port;
} MediaSyncCore;

MediaSyncCore* mediasync_create_instance(void) {
    MediaSyncCore* core = (MediaSyncCore*)malloc(sizeof(MediaSyncCore));
    if (!core) {
        return NULL;
    }

    core->buffer_capacity = MEDIASYNC_BUFFER_SIZE;
    core->metrics_port = MEDIASYNC_DEFAULT_PORT;
    
    strncpy(core->network_backend, MEDIASYNC_NETWORK_BACKEND, sizeof(core->network_backend) - 1);
    core->network_backend[sizeof(core->network_backend) - 1] = '\0';

#ifdef MEDIASYNC_USE_VAAPI
    core->vaapi_enabled = 1;
#else
    core->vaapi_enabled = 0;
#endif

#ifdef MEDIASYNC_ENABLE_LOGGING
    printf("[mediasync-C] Ініціалізація v%s | Бекенд: %s | Буфер: %zu байт | VA-API: %s\n",
           MEDIASYNC_VERSION_STRING,
           core->network_backend,
           core->buffer_capacity,
           core->vaapi_enabled ? "АКТИВНО" : "ВИМКНЕНО");
#endif

    return core;
}

void mediasync_destroy_instance(MediaSyncCore* core) {
    if (core) {
        free(core);
    }
}
```
```cpp
// src/mediasync.cpp — ідіоматична реалізація мовою C++20
#include "mediasync_config.h"
#include <iostream>
#include <memory>
#include <string_view>
#include <concepts>
#include <span>

namespace mediasync {

enum class TransportProtocol {
    Quic,
    Tcp,
    UnixSocket
};

[[nodiscard]] constexpr TransportProtocol parse_backend_string(std::string_view name) noexcept {
    if (name == "TCP") return TransportProtocol::Tcp;
    if (name == "UNIX_SOCKET") return TransportProtocol::UnixSocket;
    return TransportProtocol::Quic;
}

struct EngineSettings {
    std::size_t buffer_capacity{MEDIASYNC_BUFFER_SIZE};
    int metrics_port{MEDIASYNC_DEFAULT_PORT};
    std::string_view backend_raw{MEDIASYNC_NETWORK_BACKEND};
    TransportProtocol protocol{parse_backend_string(MEDIASYNC_NETWORK_BACKEND)};
    bool vaapi_active{
#ifdef MEDIASYNC_USE_VAAPI
        true
#else
        false
#endif
    };
};

class MediaSyncPipeline {
public:
    explicit MediaSyncPipeline(EngineSettings settings = {}) 
        : settings_{settings} {
#ifdef MEDIASYNC_ENABLE_LOGGING
        std::cout << "[mediasync-C++] Ініціалізація ядра v" << MEDIASYNC_VERSION_STRING
                  << "\n  • Мережевий бекенд : " << settings_.backend_raw
                  << "\n  • Ємність буфера   : " << settings_.buffer_capacity << " байтів"
                  << "\n  • Порт телеметрії  : " << settings_.metrics_port
                  << "\n  • Апаратний кодек  : " << (settings_.vaapi_active ? "VA-API (активовано)" : "Програмний")
                  << std::endl;
#endif
    }

    [[nodiscard]] std::string_view backend_name() const noexcept {
        return settings_.backend_raw;
    }

    [[nodiscard]] bool is_hardware_accelerated() const noexcept {
        return settings_.vaapi_active;
    }

private:
    EngineSettings settings_;
};

} // namespace mediasync
```
:::

---

## 7. Скрипти попереднього завантаження кешу (Initial Cache)

Під час налаштування автоматизованих конвеєрів збірки (CI/CD) ручне передавання довгих ланцюжків аргументів `-D` є джерелом невідтворюваних помилок. Набагато надійнішим інженерним рішенням є версіонування конфігураційних профілів у вигляді окремих скриптів попереднього кешування, які завантажуються командою `cmake -C <шлях-до-файлу>`.

### Профіль сервісної збірки для Linux CI: cmake/profiles/ci-linux-release.cmake

Цей сценарій фіксує всі параметри продуктивної оптимізованої збірки для сервера неперервної інтеграції на базі компілятора Clang. Зверніть увагу на використання ключового слова `FORCE`: воно гарантує, що значення скрипта перекриють будь-які системні налаштування середовища.

```cmake
# Фіксація компіляторів для відтворюваності оточення
set(CMAKE_C_COMPILER "clang" CACHE FILEPATH "Компілятор C для серверів CI" FORCE)
set(CMAKE_CXX_COMPILER "clang++" CACHE FILEPATH "Компілятор C++ для серверів CI" FORCE)

# Фіксація типу збірки та оптимізацій
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Оптимізована продуктивна збірка" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Експорт компіляційної бази" FORCE)

# Конфігурація модулів проєкту
set(MEDIASYNC_BUILD_TOOLS ON CACHE BOOL "Збирати утиліти" FORCE)
set(MEDIASYNC_ENABLE_TESTS ON CACHE BOOL "Збирати модульні тести" FORCE)
set(MEDIASYNC_ENABLE_LOGGING ON CACHE BOOL "Журналювання увімкнено" FORCE)
set(MEDIASYNC_LOG_LEVEL "INFO" CACHE STRING "Рівень журналювання" FORCE)
set(MEDIASYNC_NETWORK_BACKEND "QUIC" CACHE STRING "Протокол за замовчуванням" FORCE)
set(MEDIASYNC_RING_BUFFER_CAPACITY 262144 CACHE STRING "Буфер 256 КБ для високошвидкісних каналів" FORCE)
```

### Профіль локального налагодження із санітайзерами: cmake/profiles/dev-debug-asan.cmake

Цей профіль призначений для розробників, які проводять динамічний аналіз пам'яті на локальних комп'ютерах. Він вмикає символи налагодження, знижує оптимізацію до рівня `-O1` для збереження читабельності стек-трейсів та додає компіляторні прапорці AddressSanitizer і UndefinedBehaviorSanitizer:

```cmake
# Базовий налагоджувальний режим
set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Налагоджувальна збірка" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Експорт бази компіляції для інтеграції з clangd" FORCE)

# Ін'єкція прапорців динамічних санітайзерів пам'яті
set(CMAKE_C_FLAGS_DEBUG "-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer" CACHE STRING "Прапорці C для ASan" FORCE)
set(CMAKE_CXX_FLAGS_DEBUG "-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer" CACHE STRING "Прапорці C++ для ASan" FORCE)

# Налаштування модулів для локальної розробки
set(MEDIASYNC_BUILD_TOOLS ON CACHE BOOL "Збирати утиліти тестування" FORCE)
set(MEDIASYNC_ENABLE_TESTS ON CACHE BOOL "Збирати тестовий набір" FORCE)
set(MEDIASYNC_ENABLE_LOGGING ON CACHE BOOL "Детальне журналювання" FORCE)
set(MEDIASYNC_LOG_LEVEL "DEBUG" CACHE STRING "Максимальна деталізація подій" FORCE)
set(MEDIASYNC_NETWORK_BACKEND "UNIX_SOCKET" CACHE STRING "Локальний транспорт сокетів" FORCE)
set(MEDIASYNC_RING_BUFFER_CAPACITY 4096 CACHE STRING "Мінімальний буфер для провокування швидкого переповнення в тестах" FORCE)
```

---

## 8. Покроковий життєвий цикл виконання та практичні команди

### 1. Запуск конфігурації у конвеєрі CI

Під час запуску в системі CI агент виконує конфігурацію, компіляцію та запуск тестів за три стандартні команди:

```bash
# 1. Попередня ініціалізація кешу з файлу профілю
cmake -B build-ci -S . -C cmake/profiles/ci-linux-release.cmake -G Ninja

# 2. Паралельна компіляція всіх артефактів
cmake --build build-ci --parallel

# 3. Автоматизований прогін тестів через CTest
ctest --test-dir build-ci --output-on-failure
```

Під час першого виклику інтерпретатор послідовно виконує такі кроки:
1. Завантажує файл `cmake/profiles/ci-linux-release.cmake` і записує всі значення `set(... CACHE ... FORCE)` у свіжу таблицю пам'яті кешу.
2. Завантажує кореневий `CMakeLists.txt`. Команда `project()` ініціалізує компілятор Clang, який було вказано в кеші.
3. Команди `option()` та `set(CACHE)` бачать, що однойменні змінні вже визначені в кеші скриптом попереднього завантаження, і не перетирають їхні значення значеннями за замовчуванням.
4. Виконується модуль валідації `ConfigValidation.cmake`, який підтверджує коректність параметрів.
5. Генератор створює файл `build-ci/build.ninja` та фіксує підсумковий стан у `build-ci/CMakeCache.txt`.

### 2. Локальне налагодження розробником

Розробник на своїй машині ініціалізує робоче середовище командою:

```bash
cmake -B build-dev -S . -C cmake/profiles/dev-debug-asan.cmake -G Ninja
cmake --build build-dev
```

### 3. Перевірка роботи захисту від помилок валідації

Спробуємо передати нечинне значення мережевого протоколу через командний рядок:

```bash
cmake -B build-test -S . -DMEDIASYNC_NETWORK_BACKEND=BLUETOOTH
```

Конфігурація негайно зупиниться з повідомленням:

```text
CMake Error at cmake/ConfigValidation.cmake:6 (message):
  ПОМИЛКА КОНФІГУРАЦІЇ: нечинне значення MEDIASYNC_NETWORK_BACKEND='BLUETOOTH'.
  Дозволені варіанти: QUIC;TCP;UNIX_SOCKET
  Зверніть увагу, що значення чутливі до регістру символів.
Call Stack (most recent call first):
  CMakeLists.txt:58 (mediasync_validate_cache_configuration)
```

### 4. Повне оновлення середовища через --fresh

Якщо в систему було встановлено оновлену версію драйвера `libva` або змінено набір бібліотек, гарантоване скидання застарілого стану без ручного видалення файлів виконується командою:

```bash
cmake -B build-ci --fresh
```

---

## 9. Порівняння підходів до конфігурації у промислових середовищах

Під час проектування конфігураційної архітектури команди розробників обирають між чотирма основними механізмами передачі параметрів: прямими прапорцями `-D`, скриптами попередньої ініціалізації `-C`, декларативними схемами `CMakePresets.json` та системними змінними оточення `ENV`. Кожен підхід має чітко окреслені межі ефективності та приховані ризики.

### 1. Прямі аргументи командного рядка: cmake -DVAR=VAL

Передача параметрів через `-D` є найпростішим і найгнучкішим способом для швидких локальних експериментів. Інженер може на льоту змінити значення одного прапорця без редагування файлів проєкту. Проте цей підхід стає небезпечним у разі масштабування: якщо проєкт містить 20–30 налаштувань, командний рядок перетворюється на нечитабельний монолітний рядок у bash-скрипті. Друкарська помилка в назві прапорця не викликає помилки від інтерпретатора: CMake мовчки створить у кеші новий невідомий ключ, який жодним чином не вплине на хід збірки, залишаючи розробника в омані щодо активності опції.

### 2. Скрипти попереднього кешування: cmake -C script.cmake

Сценарії попереднього кешування зберігають повну потужність мови CMake: у них можна використовувати логічні умови `if()`, отримувати шляхи через функції файлової системи або динамічно обчислювати прапорці оптимізації залежно від версії ядра ОС. Головна перевага полягає у повторному використанні: один і той самий файл `ci-linux-release.cmake` версіонується в Git разом із кодом і підключається однаково як на машині розробника, так і всередині Docker-контейнера в Kubernetes. Ризик цього підходу полягає у надмірному використанні модифікатора `FORCE`: якщо скрипт примусово перезаписує системні змінні без необхідності, користувач втрачає можливість точкового перевизначення параметрів через додаткові прапорці `-D`.

### 3. Декларативні пресети: CMakePresets.json

Формат `CMakePresets.json` є сучасним промисловим стандартом, підтримуваним усіма популярними середовищами розробки (Visual Studio, CLion, VS Code). Він дозволяє описати матрицю збірок (генератор, каталог виводу, набір кеш-змінних, змінні оточення) у вигляді структурованого JSON-файлу. Це усуває людський фактор, оскільки IDE автоматично зчитує доступні конфігурації з пресетів. Обмеженням JSON є його статичність: на відміну від скриптів `-C`, у ньому не можна виконати довільний код чи динамічну перевірку апаратних можливостей машини.

### 4. Змінні середовища: export VAR=VAL / $ENV{VAR}

Використання змінних оточення операційної системи є найменш надійним методом керування збіркою. Змінні середовища не зберігаються у файлі `CMakeCache.txt`. Якщо розробник виконав первинну конфігурацію із встановленою змінною `export CXXFLAGS="-O3"`, а наступного дня запустив `cmake --build` у новому терміналі, де ця змінна відсутня, поведінка збірки може розійтися з очікуваннями. Системні змінні оточення рекомендується використовувати виключно для вказівки шляхів до глобальних інструментів та ліцензійних ключів, але не для керування логікою самого проєкту.

---

## 10. Інтеграція підпроєктів: затінення та політика CMP0077

Коли бібліотека `mediasync` інтегрується як підпроєкт у більший монорепозиторій через `add_subdirectory()` або модуль `FetchContent`, виникає питання пріоритету налаштувань. Якщо батьківський проєкт бажає вимкнути збірку тестів у `mediasync`, він встановлює локальну змінну:

```cmake
# Батьківський CMakeLists.txt
set(MEDIASYNC_ENABLE_TESTS OFF)
add_subdirectory(third_party/mediasync)
```

Завдяки політиці **CMP0077** команда `option(MEDIASYNC_ENABLE_TESTS ... ON)` усередині дочірнього проєкту бачить наявну нормальну змінну і не створює нового запису в кеші з типовим значенням `ON`. Це забезпечує передбачувану композицію модулів без конфліктів у глобальному кеші.

---

## 11. Інструменти діагностики та трасування стану кешу

Коли поведінка конфігуратора відрізняється від очікуваної, для локалізації проблеми застосовують вбудовані діагностичні режими інтерпретатора:

### Повний режим трасування викликів

```bash
cmake -B build-debug -S . --trace-expand
```

Прапорець `--trace-expand` виводить у термінал кожен виконаний рядок усіх сценаріїв `CMakeLists.txt` та модулів `include()` з повним розіменуванням значень змінних. Це дозволяє побачити, в якому саме місці змінна отримала небажане значення або де саме відбулося затінення кешу локальною змінною.

### Програмне спостереження за ключем кешу

Усередині коду `CMakeLists.txt` можна активувати точку спостереження (Watchpoint) для конкретного запису:

```cmake
variable_watch(MEDIASYNC_NETWORK_BACKEND)
```

Щойно інтерпретатор здійснить читання, модифікацію або спробу видалення змінної `MEDIASYNC_NETWORK_BACKEND`, у консоль буде виведено докладний стек викликів із зазначенням файлу та номера рядка, який ініціював дію.

---

## 12. Глобальні компіляторні прапорці CMAKE_CXX_FLAGS та їхнє кешування

Частою помилкою початківців є маніпуляція глобальними прапорцями оптимізації `CMAKE_CXX_FLAGS` замість цільових властивостей. Під час першого виклику `project()` CMake зчитує системну змінну оточення `CXXFLAGS` і записує її значення у кешовану змінну `CMAKE_CXX_FLAGS:STRING`.

Якщо згодом розробник напише в коді:

```cmake
# Антипатерн: модифікація глобального кешу прапорців
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra" CACHE STRING "Прапорці C++" FORCE)
```

Це призведе до того, що під час кожного повторного запуску рядок `-Wall -Wextra` буде повторно дублюватися в кінці значення, якщо скрипт написаний некоректно, або зафіксує прапорці назавжди, позбавляючи розробника можливості додати специфічні прапорці через CLI.

Правильним сучасним підходом є повна відмова від прямого редагування `CMAKE_CXX_FLAGS` у коді на користь команд цілей:

```cmake
# Сучасна практика: інкапсуляція прапорців на рівні цілі
target_compile_options(mediasync_core PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)
```

У цьому випадку прапорці компілятора не зберігаються в кеші `CMakeCache.txt`, а генеруються динамічно на основі типу цілі та обраного компілятора, забезпечуючи максимальну портативність та чистоту кешу.

---

## 13. Особливості кешування у мультиконфігураційних генераторах

Під час роботи з одноконфігураційними генераторами (наприклад, Ninja або Unix Makefiles) тип поточної оптимізації фіксується у змінній `CMAKE_BUILD_TYPE` (`Debug`, `Release` тощо) на етапі конфігурації. У мультиконфігураційних генераторах (таких як Visual Studio, Xcode або Ninja Multi-Config) один каталог збірки містить правила для всіх режимів одночасно.

У таких середовищах `CMAKE_BUILD_TYPE` повністю ігнорується, а список доступних конфігурацій зберігається у кеш-змінній `CMAKE_CONFIGURATION_TYPES`:

```cmake
# Налаштування переліку конфігурацій для мультиконфігураційних генераторів
set(CMAKE_CONFIGURATION_TYPES "Debug;Release;RelWithDebInfo" CACHE STRING 
    "Список доступних конфігурацій у Visual Studio/Xcode" FORCE)
```

Вибір активного режиму відбувається вже під час виклику компіляції (`cmake --build build --config Release`), що вимагає від архітектора збірки використання генераторних виразів `$<CONFIG:Debug>` замість перевірок `if(CMAKE_BUILD_TYPE STREQUAL "Debug")` під час аналізу кешу.

---

## 14. Автоматизація тестування через CTest та змінну BUILD_TESTING

Стандартний модуль `include(CTest)` автоматично реєструє в кеші булеву опцію `BUILD_TESTING` зі значенням за замовчуванням `ON`. Це загальноприйнятий стандарт в екосистемі C++, який дозволяє стороннім менеджерам пакетів (таким як vcpkg або Conan) автоматично вимикати збірку тестів для бібліотек-залежностей за допомогою одного прапорця `-DBUILD_TESTING=OFF`.

Якщо проєкт створює власний перемикач (наприклад, `MEDIASYNC_ENABLE_TESTS`), рекомендується узгоджувати його зі стандартною змінною кешу:

```cmake
include(CTest)
if(DEFINED BUILD_TESTING)
    set(MEDIASYNC_ENABLE_TESTS ${BUILD_TESTING} CACHE BOOL "Синхронізація з CTest" FORCE)
endif()
```

---

## 15. Гігієна версіонування та командної розробки

1. **Ізоляція каталогу збірки**: `CMakeCache.txt` містить абсолютні шляхи до файлів та компіляторів конкретної машини. Файли `CMakeCache.txt`, `CMakeFiles/` та каталоги збірки **ніколи не додаються до Git**. Файл `.gitignore` проєкту завжди повинен містити правила `build/`, `bin/` та `*.cache`.
2. **Заборона копіювання кешу**: копіювання каталогу `build/` на інший комп'ютер або перейменування батьківського каталогу гарантовано призводить до збоїв збірки, оскільки внутрішні шляхи в кеші стають недійсними. Єдиним коректним способом перенесення збірки є генерація дерева з нуля.
3. **Атомарне оновлення профілів**: будь-які зміни в архітектурі опцій проєкту мають супроводжуватися відповідними правками у файлах `cmake/profiles/*.cmake` та оновленням документації конфігурації.
4. **Незмінність протоколів збірки у CI**: на серверах автоматизованого тестування рекомендується зберігати згенерований `CMakeCache.txt` як незмінний артефакт діагностики після завершення прогону, що дозволяє швидко відтворити точний стан середовища у разі виявлення помилок.

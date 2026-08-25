# ⚙️ Створення власного оверлей-порту та інтеграція через маніфестний режим

У промислових проєктах часто виникає потреба підключити C++-бібліотеку, якої ще немає в офіційному репозиторії `microsoft/vcpkg`, або яка потребує внутрішніх корпоративних латок (патчів), специфічних прапорців компіляції чи спеціального крос-тулчейна під цільову вбудовану платформу.

Спроба модифікувати глобальний каталог портів vcpkg безпосередньо в підмодулі чи системній інсталяції руйнує відтворюваність збірки й ускладнює оновлення менеджера пакетів. Натомість vcpkg надає ізольований механізм **оверлеїв (overlays)**:
1. **Оверлей-порти (Overlay Ports)** — локальні каталоги з файлами `vcpkg.json` та `portfile.cmake`, які мають пріоритет над офіційним каталогом портів або доповнюють його.
2. **Оверлей-тріплети (Overlay Triplets)** — локальні CMake-описи цільової платформи, які налаштовують специфічні крос-компілятори, системні корені (sysroot) та прапорці оптимізації.

Нижче наведено практичний процес створення повноцінного оверлей-порту для високопродуктивної бібліотеки обробки телеметрії `fast_telemetry`, підключення накладання патчів для сумісності з POSIX-потоками на ARM64 Linux, налаштування власного оверлей-тріплета та інтеграції зі споживчим проєктом у маніфестному режимі.

## Архітектура каталогу споживчого проєкту

Організуємо репозиторій споживчого сервісу таким чином, щоб оверлей-порти та оверлей-тріплети зберігалися поруч із кодом програми в системі контролю версій Git. Це забезпечує повну автономність репозиторію: будь-який розробник або сервер CI/CD після клонування коду отримує всі необхідні інструкції збірки без додаткових ручних конфігурацій.

```text
telemetry_service/
├── CMakeLists.txt
├── vcpkg.json
├── vcpkg-configuration.json
├── custom-ports/
│   └── fast_telemetry/
│       ├── vcpkg.json
│       ├── portfile.cmake
│       └── patches/
│           └── 0001-fix-arm-affinity.patch
├── custom-triplets/
│   └── arm64-linux-embedded.cmake
└── src/
    ├── main.cpp
    ├── telemetry_c_api.h
    └── telemetry_consumer.hpp
```

Така ієрархія чітко розмежовує метадані стороннього порту (`custom-ports/`), опис апаратного середовища (`custom-triplets/`) та безпосередній бізнес-код сервісу (`src/`).

## Крок 1. Декларація маніфесту порту (vcpkg.json)

Файл `custom-ports/fast_telemetry/vcpkg.json` описує метадані сторонньої бібліотеки, її ліцензію, версію, залежності від інших портів vcpkg та опціональні можливості (features). Рушій vcpkg аналізує цей файл першим для побудови графа залежностей.

```json
{
  "name": "fast-telemetry",
  "version-semver": "2.1.0",
  "port-version": 1,
  "description": "Високопродуктивний асинхронний агрегатор телеметрії для вбудованих систем",
  "homepage": "https://github.com/example-org/fast-telemetry",
  "license": "Apache-2.0",
  "dependencies": [
    "fmt",
    "nlohmann-json"
  ],
  "features": {
    "compression": {
      "description": "Підтримка стиснення телеметричних кадрів через zlib",
      "dependencies": [
        "zlib"
      ]
    }
  },
  "default-features": [
    "compression"
  ]
}
```

Зверніть увагу на поле `port-version: 1`: якщо вихідний код бібліотеки має версію `2.1.0`, але в інструкції збірки чи патчі порту внесено виправлення, `port-version` інкрементується без зміни базової версії сирців. Це сигналізує рушію кешування про зміну інструкцій та необхідність інвалідації попередніх бінарних пакетів.

## Крок 2. Розробка скрипта збірки порту (portfile.cmake)

Скрипт `custom-ports/fast_telemetry/portfile.cmake` виконує повний життєвий цикл: завантаження вихідного коду, перевірку цілісності за криптографічним хешем SHA-512, накладання латок, запуск генератора CMake, компіляцію для Release і Debug, перенесення файлів експорту та очищення дублікатів.

```cmake
# 1. Завантаження вихідного коду з репозиторію GitHub із перевіркою SHA-512
vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO example-org/fast-telemetry
    REF "v${VERSION}"
    SHA512 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    HEAD_REF main
    PATCHES
        patches/0001-fix-arm-affinity.patch
)

# 2. Перевірка обраних опцій (features)
vcpkg_check_features(
    OUT_FEATURE_OPTIONS FEATURE_OPTIONS
    FEATURES
        compression ENABLE_ZLIB_COMPRESSION
)

# 3. Конфігурація системи збірки CMake через хелпери vcpkg
vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        -DFAST_TELEMETRY_BUILD_TESTS=OFF
        -DFAST_TELEMETRY_BUILD_EXAMPLES=OFF
        ${FEATURE_OPTIONS}
)

# 4. Компіляція та встановлення в буфер packages/fast-telemetry_<triplet>/
vcpkg_cmake_install()

# 5. Нормалізація структури CMake-конфігурацій
# Переносить fast-telemetryConfig.cmake з lib/cmake/ у share/fast-telemetry/
vcpkg_cmake_config_fixup(
    PACKAGE_NAME fast-telemetry
    CONFIG_PATH lib/cmake/fast-telemetry
)

# 6. Очищення дубльованих файлів заголовків у налагоджувальній конфігурації
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

# 7. Збереження ліцензійного файлу (обов'язкова вимога vcpkg)
vcpkg_install_copyright(
    FILE_LIST "${SOURCE_PATH}/LICENSE"
)
```

Кожен крок скрипта відповідає за суворий інваріант: `vcpkg_from_github` гарантує незмінність вхідного коду, `vcpkg_cmake_config_fixup` усуває некоректні відносні шляхи в конфігураційних файлах, а видалення `debug/include` унеможливлює розбіжності в оголошеннях структур між різними конфігураціями.

### Вміст латки (patches/0001-fix-arm-affinity.patch)

Латка виправляє специфічну поведінку прив'язки потоків `pthread_setaffinity_np` для цільових процесорів ARM64 у середовищі з нестандартною бібліотекою C, де заголовок `<sched.h>` не підключається автоматично:

```diff
--- a/src/thread_pool.cpp
+++ b/src/thread_pool.cpp
@@ -14,6 +14,8 @@
 #include <pthread.h>
+#if defined(__linux__) && defined(__aarch64__)
+#include <sched.h>
+#endif
 
 void bind_worker_core(int core_id) {
 #if defined(__linux__) && !defined(__ANDROID__)
```

## Крок 3. Налаштування власного оверлей-тріплета

Створимо файл `custom-triplets/arm64-linux-embedded.cmake`, який задає налаштування для крос-компіляції під цільову плату на базі ARM Cortex-A53. Цей тріплет налаштовує статичне лінкування бібліотек, що спрощує розгортання прошивки на цільовому пристрої:

```cmake
set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Linux)

# Підключення зовнішнього тулчейна компілятора
set(VCPKG_CHAINLOAD_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/../../cmake/toolchains/aarch64-linux-gnu.cmake")

# Оптимізаційні прапорці збірки
set(VCPKG_C_FLAGS "-O3 -march=armv8-a+crc -pipe")
set(VCPKG_CXX_FLAGS "-O3 -march=armv8-a+crc -pipe -fno-rtti")
```

Використання `VCPKG_CHAINLOAD_TOOLCHAIN_FILE` дозволяє зберегти всі стандартні механізми vcpkg (пошук пакетів, генерація шляхів `CMAKE_PREFIX_PATH`), передаючи контроль над вибором компіляторів `aarch64-linux-gnu-gcc` та шляхів до системного кореня (sysroot) зовнішньому тулчейну.

## Крок 4. Підключення оверлеїв у проєкті споживача

Щоб розробникам та серверам безперервної інтеграції не потрібно було передавати довгі аргументи командного рядка (`--overlay-ports` та `--overlay-triplets`), налаштуємо файл `vcpkg-configuration.json` у корені споживчого репозиторію:

```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/vcpkg-tool/main/docs/vcpkg-configuration.schema.json",
  "default-registry": {
    "kind": "builtin",
    "baseline": "d3509a2d326f59fa05f4e1f7a1f59265f24ec4d9"
  },
  "overlay-ports": [
    "./custom-ports"
  ],
  "overlay-triplets": [
    "./custom-triplets"
  ]
}
```

А в маніфесті проєкту `vcpkg.json` оголосимо необхідні бібліотеки та зафіксуємо точну версію бібліотеки форматування:

```json
{
  "name": "telemetry-service",
  "version-semver": "1.0.0",
  "dependencies": [
    "fast-telemetry",
    "fmt"
  ],
  "overrides": [
    {
      "name": "fmt",
      "version": "10.1.1"
    }
  ]
}
```

## Крок 5. Складання споживчого CMakeLists.txt та C++ коду

Файл `CMakeLists.txt` сервісу підключає залежності через звичайні імпортовані цілі, оскільки vcpkg повністю нормалізував конфігураційні файли:

```cmake
cmake_minimum_required(VERSION 3.24)
project(telemetry_service CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(fast-telemetry CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)

add_executable(telemetry_service src/main.cpp)
target_link_libraries(telemetry_service PRIVATE fast-telemetry::fast-telemetry fmt::fmt)
```

Реалізація інтерфейсу споживача мовами C та C++ демонструє роботу зі створеними структурами даних:

:::tabs
```c
/* src/telemetry_c_api.h */
#ifndef TELEMETRY_C_API_H
#define TELEMETRY_C_API_H

#include <stdint.h>

struct TelemetryRecord {
    uint64_t timestamp_ns;
    uint32_t sensor_id;
    double metric_value;
};

int dispatch_telemetry_c(const struct TelemetryRecord *rec);

#endif
```
```cpp
// src/telemetry_consumer.hpp
#pragma once
#include <cstdint>
#include <span>
#include <string_view>

namespace telemetry {
    struct Record {
        std::uint64_t timestamp_ns{0};
        std::uint32_t sensor_id{0};
        double metric_value{0.0};
    };

    [[nodiscard]] bool dispatch_records(std::span<const Record> batch) noexcept;
}
```
:::

Основна програма використовує безпечні C++ ідіоми:

```cpp
// src/main.cpp
#include "telemetry_consumer.hpp"
#include <fmt/core.h>
#include <vector>
#include <chrono>

int main() {
    std::vector<telemetry::Record> batch{
        {1700000000000ULL, 101, 23.85},
        {1700000001000ULL, 102, 101.32}
    };

    fmt::print("Ініціалізація відправлення {} записів телеметрії...\n", batch.size());
    
    if (telemetry::dispatch_records(batch)) {
        fmt::print("Телеметрію успішно передано до агрегатора fast-telemetry.\n");
        return 0;
    }

    fmt::print(stderr, "Помилка передавання кадру телеметрії!\n");
    return 1;
}
```

## Крок 6. Запуск і перевірка збірки

Для збірки проєкту достатньо викликати CMake із зазначенням файлу тулчейна vcpkg та нашого цільового тріплета:

```bash
# Конфігурація (автоматично розпакує порти, застосує латки та збере оверлей-пакет)
cmake -B build -S . \
  -DCMAKE_TOOLCHAIN_FILE="$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" \
  -DVCPKG_TARGET_TRIPLET=arm64-linux-embedded

# Компіляція бінарного виконуваного файлу
cmake --build build
```

Під час виконання конфігурації vcpkg знайде `custom-ports/fast_telemetry`, виконає компіляцію порту в каталозі `build/vcpkg_installed/arm64-linux-embedded/` та експортує ціль `fast-telemetry::fast-telemetry` у простір CMake без втручання в загальносистемні бібліотеки.

## Аналіз типових помилок при розробці оверлеїв

Під час створення власних портів розробники найчастіше стикаються з трьома категоріями проблем:

1. **Помилка контрольної суми (SHA512 mismatch):** виникає, якщо вихідний архів було перезалито на сервері розробника або тег Git було зміщено. vcpkg зупиняє виконання і друкує фактичний хеш файлу. Якщо зміна була легітимною, новий хеш копіюється у виклик `vcpkg_from_github()`.
2. **Незнайдена імпортована ціль у find_package:** трапляється, якщо `vcpkg_cmake_config_fixup()` не було викликано або передано некоректний шлях `CONFIG_PATH`. Якщо оригінальний проєкт встановив конфіги в `lib/cmake/FastTelemetry/`, vcpkg не зможе знайти їх за стандартним іменем без виклику фіксації.
3. **Конфлікт шляхів інсталяції ліцензії:** забутий виклик `vcpkg_install_copyright()` викликає фатальну зупинку вбудованого валідатора пакетів. Завжди передавайте шлях до файлу `LICENSE` або `COPYING` у фінальній частині `portfile.cmake`.

Дотримання цієї структури гарантує, що ваші власні бібліотеки працюватимуть у конвеєрі vcpkg з тією самою надійністю та детермінізмом, що й офіційні пакети екосистеми.

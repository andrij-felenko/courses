# ⚙️ Практикум: компонентне пакування сервісу телеметрії

Цей практикум демонструє повний інженерний цикл побудови системи компонентного пакування для системного сервісу збору метрик `telemetryd`. Типова проблема промислової розробки полягає в тому, що один проєкт породжує артефакти різного призначення: виконуваний серверний демон, спільну динамічну бібліотеку з публічним ABI, заголовочні файли для розробки сторонніх плагінів, конфігурації компілятора CMake, файли юнітів системного менеджера `systemd` та документацію.

Якщо запакувати всі ці артефакти в єдиний монолітний пакет, користувачі на серверах будуть змушені встановлювати непотрібні заголовки й документацію, а розробники бібліотек отримають конфлікти версій. Мета цього практикуму — створити єдиний сценарій CMake та CPack, який автоматично розділяє артефакти на три ізольовані пакети:
1. `telemetry-runtime` — скомпільований демон `telemetryd`, спільна бібліотека `libtelemetry.so.1`, юніт-файл `systemd` та скрипти постінсталяційного перезавантаження.
2. `telemetry-devel` — заголовки C/C++, символічне посилання `libtelemetry.so` для лінкування та файли експорту цілей CMake (`TelemetryConfig.cmake`).
3. `telemetry-docs` — документація API та системні man-сторінки.

## 1. Архітектура та вихідний код компонентів

Проєкт спроєктовано за модульним принципом: логіка обчислення метрик винесена в окрему спільну бібліотеку з чистим C-сумісним ABI, що дозволяє викликати її з програм будь-якими мовами програмування. Демон `telemetryd` є тонким клієнтом над бібліотекою, який періодично опитує показники та виводить їх у форматі JSON.

### Заголовочний файл бібліотеки (`include/telemetry/metrics.h` / `include/telemetry/metrics.hpp`)

Публічний заголовок визначає структуру знімка метрик та сигнатури функцій збору й форматування.

:::tabs
```c
#ifndef TELEMETRY_METRICS_H
#define TELEMETRY_METRICS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint64_t uptime_seconds;
    uint64_t memory_used_bytes;
    double cpu_load_percent;
} telemetry_snapshot_t;

int telemetry_collect_metrics(telemetry_snapshot_t* out_snapshot);
void telemetry_format_json(const telemetry_snapshot_t* snapshot, char* buffer, size_t max_len);

#ifdef __cplusplus
}
#endif

#endif /* TELEMETRY_METRICS_H */
```
```cpp
#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>

namespace telemetry {

struct Snapshot {
    std::uint64_t uptime_seconds{0};
    std::uint64_t memory_used_bytes{0};
    double cpu_load_percent{0.0};
};

bool collect_metrics(Snapshot& out_snapshot);
std::string format_json(const Snapshot& snapshot);

} // namespace telemetry
```
:::

### Реалізація бібліотеки (`src/metrics.c` / `src/metrics.cpp`)

Реалізація бібліотеки розраховує час безперервної роботи процесу від моменту першого виклику та формує серіалізований рядок JSON. Нижче наведено варіанти реалізації мовами C та сучасним C++ (C++20).

:::tabs
```c
#include "telemetry/metrics.h"
#include <stdio.h>
#include <time.h>

static uint64_t g_start_time = 0;

int telemetry_collect_metrics(telemetry_snapshot_t* out_snapshot) {
    if (!out_snapshot) {
        return -1;
    }
    if (g_start_time == 0) {
        g_start_time = (uint64_t)time(NULL);
    }

    out_snapshot->uptime_seconds = (uint64_t)time(NULL) - g_start_time;
    out_snapshot->memory_used_bytes = 1048576 * 42; // Фіксоване тестове значення
    out_snapshot->cpu_load_percent = 12.5;

    return 0;
}

void telemetry_format_json(const telemetry_snapshot_t* snapshot, char* buffer, size_t max_len) {
    if (!snapshot || !buffer || max_len == 0) {
        return;
    }
    snprintf(buffer, max_len,
             "{\"uptime\": %llu, \"memory_bytes\": %llu, \"cpu_load\": %.2f}\n",
             (unsigned long long)snapshot->uptime_seconds,
             (unsigned long long)snapshot->memory_used_bytes,
             snapshot->cpu_load_percent);
}
```
```cpp
#include "telemetry/metrics.h"
#include <chrono>
#include <format>
#include <string_view>
#include <cstring>

namespace {
    const auto g_start_time = std::chrono::steady_clock::now();
}

extern "C" int telemetry_collect_metrics(telemetry_snapshot_t* out_snapshot) {
    if (!out_snapshot) {
        return -1;
    }

    const auto now = std::chrono::steady_clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - g_start_time).count();

    out_snapshot->uptime_seconds = static_cast<uint64_t>(elapsed);
    out_snapshot->memory_used_bytes = 1048576ULL * 42ULL;
    out_snapshot->cpu_load_percent = 12.5;

    return 0;
}

extern "C" void telemetry_format_json(const telemetry_snapshot_t* snapshot, char* buffer, size_t max_len) {
    if (!snapshot || !buffer || max_len == 0) {
        return;
    }
    const std::string json = std::format(
        "{{\"uptime\": {}, \"memory_bytes\": {}, \"cpu_load\": {:.2f}}}\n",
        snapshot->uptime_seconds,
        snapshot->memory_used_bytes,
        snapshot->cpu_load_percent
    );
    const size_t copy_len = (json.size() < max_len - 1) ? json.size() : max_len - 1;
    std::memcpy(buffer, json.data(), copy_len);
    buffer[copy_len] = '\0';
}
```
:::

### Виконуваний демон (`src/daemon.c` / `src/daemon.cpp`)

Демон запускається як системна служба, ініціалізує буфери пам'яті, опитує бібліотеку метрик і передає результати у стандартний потік виводу (який перехоплюється журналом `systemd-journald`).

:::tabs
```c
#include "telemetry/metrics.h"
#include <stdio.h>
#include <unistd.h>

int main(void) {
    printf("Starting Telemetry Daemon v1.4.2...\n");
    telemetry_snapshot_t snapshot;
    char buffer[256];

    for (int i = 0; i < 3; ++i) {
        if (telemetry_collect_metrics(&snapshot) == 0) {
            telemetry_format_json(&snapshot, buffer, sizeof(buffer));
            fputs(buffer, stdout);
        }
        sleep(1);
    }
    return 0;
}
```
```cpp
#include "telemetry/metrics.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <array>

int main() {
    std::cout << "Starting Telemetry Daemon v1.4.2...\n";
    telemetry_snapshot_t snapshot{};
    std::array<char, 256> buffer{};

    for (int i = 0; i < 3; ++i) {
        if (telemetry_collect_metrics(&snapshot) == 0) {
            telemetry_format_json(&snapshot, buffer.data(), buffer.size());
            std::cout << buffer.data();
        }
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return 0;
}
```
:::

## 2. Системна інтеграція та сценарії життєвого циклу

Системний пакунок Linux повинен не просто розпакувати бінарники на диск, а й зареєструвати службу в підсистемі ініціалізації та оновити кеш динамічного лінкера.

### Юніт-файл systemd (`packaging/telemetryd.service`)

Юніт описує правила запуску демона операційною системою: тип процесу `simple`, автоматичний перезапуск при аварійному завершенні та залежність від мережевого стека.

```ini
[Unit]
Description=Telemetry Monitoring Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/telemetryd
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Сценарій постінсталяції (`packaging/postinst.sh`)

Скрипт викликається пакетним менеджером (`dpkg` або `rpm`) після запису всіх файлів на диск. Він виконує дві критичні задачі: викликає `ldconfig` для реєстрації нової бібліотеки `/usr/lib/libtelemetry.so.1` та сповіщає `systemd` про появу нового юніт-файлу через команду `systemctl daemon-reload`.

Для забезпечення ідемпотентності скрипт перевіряє наявність сокета `systemd` у `/run/systemd/system`. Якщо пакунок встановлюється всередині контейнера Docker чи ізольованого середовища `chroot`, де демон `systemd` не запущений як PID 1, скрипт не аварійно перериває інсталяцію, а тихо завершує роботу.

```bash
#!/bin/sh
set -e

# 1. Оновлення кешу завантажувача динамічних бібліотек
if [ -x "$(command -v ldconfig)" ]; then
    ldconfig
fi

# 2. Оновлення конфігурації systemd, якщо сервіс встановлюється у працюючій системі
if [ -d /run/systemd/system ]; then
    systemctl --system daemon-reload >/dev/null 2>&1 || true
fi

exit 0
```

## 3. Повна конфігурація `CMakeLists.txt`

Файл проєкту організовує збірку цілей, пов'язує їх із компонентами інсталяції та конфігурує параметри CPack для генерації DEB, RPM та архівних дистрибутивів.

Зверніть увагу на використання генераторних виразів `$<BUILD_INTERFACE:...>` та `$<INSTALL_INTERFACE:...>` у команді `target_include_directories`. Це гарантує, що під час локальної збірки компілятор шукатиме заголовки у вихідному каталозі `include/`, а при експорті цілей для сторонніх проєктів у згенерований `TelemetryTargets.cmake` буде записано правильний відносний шлях `${_IMPORT_PREFIX}/include`.

```cmake
cmake_minimum_required(VERSION 3.22)
project(telemetry
    VERSION 1.4.2
    DESCRIPTION "High-performance telemetry aggregation service"
    HOMEPAGE_URL "https://github.com/example/telemetry"
    LANGUAGES C CXX
)

include(GNUInstallDirs)

# ── 1. Збірка спільної динамічної бібліотеки ─────────────────────────────────
add_library(telemetry_lib SHARED
    src/metrics.c
)
set_target_properties(telemetry_lib PROPERTIES
    OUTPUT_NAME "telemetry"
    SOVERSION 1
    VERSION 1.4.2
)
target_include_directories(telemetry_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# ── 2. Збірка демона ──────────────────────────────────────────────────────────
add_executable(telemetryd src/daemon.c)
target_link_libraries(telemetryd PRIVATE telemetry_lib)

# ── 3. Правила інсталяції з розподілом за компонентами ────────────────────────

# Компонент Runtime: бінарник демона та версіонована бібліотека
install(TARGETS telemetryd telemetry_lib
    EXPORT TelemetryTargets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT Runtime
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT Runtime
    NAMELINK_COMPONENT Development
)

# Системний юніт systemd також належить компоненту Runtime
install(FILES packaging/telemetryd.service
    DESTINATION /lib/systemd/system
    COMPONENT Runtime
)

# Компонент Development: публічні заголовки
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    COMPONENT Development
)

# Експорт цілей CMake для зовнішніх розробників (find_package(Telemetry))
install(EXPORT TelemetryTargets
    NAMESPACE Telemetry::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Telemetry
    COMPONENT Development
)

# Компонент Documentation: документація
install(FILES README.md
    DESTINATION ${CMAKE_INSTALL_DOCDIR}
    COMPONENT Documentation
)

# ── 4. Налаштування CPack ────────────────────────────────────────────────────
set(CPACK_PACKAGE_NAME "telemetry")
set(CPACK_PACKAGE_VENDOR "Acme Telemetry Systems")
set(CPACK_PACKAGE_CONTACT "ops@telemetry.example.com")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Lightweight system telemetry daemon")
set(CPACK_PACKAGING_INSTALL_PREFIX "/usr")

# Активація покомпонентної генерації для DEB та RPM
set(CPACK_DEBIAN_COMPONENT_INSTALL ON)
set(CPACK_RPM_COMPONENT_INSTALL ON)

# Специфікація DEB генератора
set(CPACK_DEBIAN_PACKAGE_SECTION "utils")
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON) # Автоматичний аналіз DT_NEEDED через dpkg-shlibdeps
set(CPACK_DEBIAN_RUNTIME_PACKAGE_CONTROL_EXTRA "${CMAKE_CURRENT_SOURCE_DIR}/packaging/postinst.sh")
set(CPACK_COMPONENT_DEVELOPMENT_DEPENDS "Runtime") # Пакет dev залежить від runtime

# Специфікація RPM генератора
set(CPACK_RPM_PACKAGE_LICENSE "Apache-2.0")
set(CPACK_RPM_PACKAGE_GROUP "Applications/System")
set(CPACK_RPM_PACKAGE_AUTOREQ YES)
set(CPACK_RPM_RUNTIME_POST_INSTALL_SCRIPT_FILE "${CMAKE_CURRENT_SOURCE_DIR}/packaging/postinst.sh")

# Підключення модуля CPack
include(CPack)
include(CPackComponent)

# Декларація метаданих компонентів для графічних інсталяторів
cpack_add_component(Runtime
    DISPLAY_NAME "Telemetry Service & Daemon"
    DESCRIPTION "Contains the executable daemon, shared library, and systemd service"
    REQUIRED
)

cpack_add_component(Development
    DISPLAY_NAME "C/C++ SDK & CMake Configs"
    DESCRIPTION "Header files and CMake target exports for building applications"
    DEPENDS Runtime
)

cpack_add_component(Documentation
    DISPLAY_NAME "User Documentation"
    DESCRIPTION "Manuals and quick-start guides"
    DISABLED
)
```

## 4. Збірка проєкту та створення пакетів

Процес збірки та пакування здійснюється у два етапи: спочатку CMake збирає бінарники у каталозі `build/`, після чого утиліта `cpack` монтує дерево інсталяції та викликає відповідні бекенди генераторів.

```bash
# Крок 1. Конфігурація та компіляція
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Крок 2. Генерація пакетів Debian (DEB)
cd build
cpack -G DEB

# Крок 3. Генерація пакетів Red Hat (RPM)
cpack -G RPM

# Крок 4. Генерація автономного архіву (TGZ)
cpack -G TGZ
```

## 5. Інспекція та верифікація згенерованих пакетів

Після успішного виконання CPack у каталозі `build/` з'являються готові артефакти:

```text
build/
├── telemetry-1.4.2-Linux-Runtime.deb
├── telemetry-1.4.2-Linux-Development.deb
├── telemetry-1.4.2-Linux-Documentation.deb
├── telemetry-1.4.2-1.x86_64-Runtime.rpm
├── telemetry-1.4.2-1.x86_64-Development.rpm
└── telemetry-1.4.2-Linux.tar.gz
```

### Перевірка метаданих пакета `telemetry-Runtime.deb`

Виконаємо інспекцію файлу `control` всередині згенерованого DEB-пакета за допомогою утиліти `dpkg-deb`:

```bash
dpkg-deb -I telemetry-1.4.2-Linux-Runtime.deb
```

У виводі утиліти видно, що CPack успішно інтегрував параметри з `CMakeLists.txt`, а увімкнений прапорець `CPACK_DEBIAN_PACKAGE_SHLIBDEPS` автоматично визначив системну залежність від версії бібліотеки `libc6` на основі аналізу секції `DT_NEEDED` бінарника `telemetryd`:

```text
 Package: telemetry-runtime
 Version: 1.4.2
 Section: utils
 Priority: optional
 Architecture: amd64
 Maintainer: ops@telemetry.example.com
 Depends: libc6 (>= 2.34)
 Description: Lightweight system telemetry daemon
```

### Перевірка вмісту файлової системи пакета

Переглянемо перелік файлів, запакованих у `telemetry-Runtime.deb`:

```bash
dpkg-deb -c telemetry-1.4.2-Linux-Runtime.deb
```

```text
-rwxr-xr-x root/root     18424 2026-08-21 12:00 ./usr/bin/telemetryd
-rwxr-xr-x root/root     15680 2026-08-21 12:00 ./usr/lib/libtelemetry.so.1.4.2
lrwxrwxrwx root/root         0 2026-08-21 12:00 ./usr/lib/libtelemetry.so.1 -> libtelemetry.so.1.4.2
-rw-r--r-- root/root       210 2026-08-21 12:00 ./lib/systemd/system/telemetryd.service
```

Як видно зі списку, завдяки директиві `NAMELINK_COMPONENT Development`, символічне посилання без версії `libtelemetry.so` та заголовочні файли `include/` потрапили виключно до пакета `telemetry-Development.deb`. Таким чином досягається повна ізоляція середовища виконання від інструментів розробника.

### Інспекція експортованих конфігурацій CMake

Перевіримо вміст пакета розробника `telemetry-Development.deb`:

```bash
dpkg-deb -c telemetry-1.4.2-Linux-Development.deb
```

```text
-rw-r--r-- root/root       730 2026-08-21 12:00 ./usr/include/telemetry/metrics.h
lrwxrwxrwx root/root         0 2026-08-21 12:00 ./usr/lib/libtelemetry.so -> libtelemetry.so.1
-rw-r--r-- root/root      4512 2026-08-21 12:00 ./usr/lib/cmake/Telemetry/TelemetryTargets.cmake
-rw-r--r-- root/root      1280 2026-08-21 12:00 ./usr/lib/cmake/Telemetry/TelemetryTargets-release.cmake
```

Сторонній проєкт, встановивши цей пакет, може безпосередньо підключити бібліотеку у своєму `CMakeLists.txt` за допомогою стандартної команди:

```cmake
find_package(Telemetry REQUIRED)
target_link_libraries(my_plugin PRIVATE Telemetry::telemetry_lib)
```

При цьому CMake автоматично отримає коректні шляхи до заголовочних файлів (`/usr/include`) та прапорці компонування (`-ltelemetry`), гарантуючи повну переносимість і стабільність збірки у системі.

## 6. Порівняння поведінки життєвого циклу в DEB та RPM

Особливу увагу при написанні сценаріїв супроводу слід звертати на аргументи, які передаються операційними менеджерами під час інсталяції та оновлення:

- **У системі Debian (dpkg):** Перший позиційний аргумент `$1` у `postinst` приймає значення `configure` під час початкової інсталяції, або `configure <попередня-версія>` під час оновлення. Сценарій `prerm` викликається з аргументом `remove` або `upgrade <нова-версія>`.
- **У системі Red Hat (RPM):** Перший позиційний аргумент `$1` у секціях `%post` та `%preun` позначає кількість встановлених копій пакета в системі після завершення поточної транзакції. При первинному встановленні `$1 == 1`. При оновленні пакета новою версією `$1 == 2`. При повному видаленні пакета із системи в скрипті `%preun` змінна `$1 == 0`.

Врахування цих аргументів дозволяє писати надійні скрипти, які перезапускають системні служби під час оновлення, але не запускають їх передчасно при розгортанні образу диска під час складання контейнера.

# ⚙️ Практикум ізольованого пакування з DESTDIR та перевіркою RPATH

Створення дистрибутивного пакета (.deb для Debian/Ubuntu, .rpm для Red Hat/Fedora або автономного архіву .tar.gz) вимагає суворого дотримання ізоляції: файли програми мають бути скомпільовані під цільовий системний префікс (наприклад `PREFIX=/usr` або `PREFIX=/opt/calcapp`), але фізично встановлені у тимчасовий каталог пісочниці (**Staging Root** / **Fake Root**) без привілеїв суперкористувача `root`.

У цьому практичному розборі реалізовано повний виробничий конвеєр для C/C++ проєкту `calcapp`. Проєкт складається зі спільної динамічної бібліотеки `libcalc`, виконуваного файлу `calc_cli`, файлу статичних ресурсів `operations.json` та системного опису конфігурації. Конвеєр демонструє компіляцію, ізольоване встановлення через `DESTDIR`, вилучення налагоджувальних символів у `.debug`-файли, валідацію заголовків ELF утилітою `readelf` та фінальне формування пакетного архіву.

## 1. Архітектура та конфігурація проєкту

Структура каталогів вихідного коду проєкту:

```
calcapp/
 ├── CMakeLists.txt
 ├── include/
 │    └── calc/
 │         └── math_ops.h
 ├── src/
 │    ├── math_ops.cpp
 │    └── main.cpp
 └── assets/
      └── operations.json
```

У кореневому `CMakeLists.txt` налаштовано стандартизовані шляхи через модуль `GNUInstallDirs`, задано динамічний пошук бібліотек через `$ORIGIN` у властивості `INSTALL_RPATH` та визначено правила встановлення для всіх компонентів:

```cmake
cmake_minimum_required(VERSION 3.20)
project(CalcApp VERSION 1.0.0 LANGUAGES CXX)

# Встановлюємо сучасний стандарт C++
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Підключаємо стандартні конвенції розміщення каталогів
include(GNUInstallDirs)

# 1. Спільна динамічна бібліотека обчислень
add_library(calc SHARED src/math_ops.cpp)
target_include_directories(calc PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
set_target_properties(calc PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
)

# 2. Виконуваний файл консольного клієнта
add_executable(calc_cli src/main.cpp)
target_link_libraries(calc_cli PRIVATE calc)

# Передаємо цільовий абсолютний шлях до ресурсів у константи компілятора
target_compile_definitions(calc_cli PRIVATE
    APP_DATADIR="${CMAKE_INSTALL_FULL_DATADIR}/calcapp"
)

# 3. Налаштування RPATH для встановленого двійкового файлу
# Використовуємо $ORIGIN для відносного пошуку lib/ відносно bin/
set_target_properties(calc_cli PROPERTIES
    INSTALL_RPATH "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}"
    BUILD_WITH_INSTALL_RPATH FALSE
)

# 4. Правила встановлення цілей та заголовків
install(TARGETS calc calc_cli
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(DIRECTORY include/calc
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(FILES assets/operations.json
    DESTINATION ${CMAKE_INSTALL_DATADIR}/calcapp
)
```

## 2. Реалізація компонентів програми

Бібліотека надає інтерфейс обчислень:

```cpp
// include/calc/math_ops.h
#pragma once

#if defined(_WIN32)
  #if defined(calc_EXPORTS)
    #define CALC_API __declspec(dllexport)
  #else
    #define CALC_API __declspec(dllimport)
  #endif
#else
  #define CALC_API __attribute__((visibility("default")))
#endif

extern "C" {
    CALC_API int calc_add(int a, int b);
    CALC_API int calc_mul(int a, int b);
}
```

Виконуваний файл завантажує статичні ресурси за вшитим скомпільованим шляхом `APP_DATADIR`:

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include "calc/math_ops.h"

#ifndef APP_DATADIR
#define APP_DATADIR "/usr/local/share/calcapp"
#endif

int main(int argc, char* argv[]) {
    char asset_path[512];
    snprintf(asset_path, sizeof(asset_path), "%s/operations.json", APP_DATADIR);

    FILE* f = fopen(asset_path, "r");
    if (!f) {
        fprintf(stderr, "Помилка: не знайдено файл конфігурації: %s\n", asset_path);
        return 1;
    }
    printf("Конфігурацію завантажено з: %s\n", asset_path);
    fclose(f);

    printf("Розрахунок: 12 + 30 = %d\n", calc_add(12, 30));
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include "calc/math_ops.h"

#ifndef APP_DATADIR
#define APP_DATADIR "/usr/local/share/calcapp"
#endif

int main(int argc, char* argv[]) {
    namespace fs = std::filesystem;
    const fs::path asset_path = fs::path(APP_DATADIR) / "operations.json";

    std::ifstream file(asset_path);
    if (!file.is_open()) {
        std::cerr << "Помилка: не знайдено файл конфігурації за шляхом: " 
                  << asset_path << '\n';
        return 1;
    }

    std::cout << "Конфігурацію успішно завантажено з: " << asset_path << '\n';
    std::cout << "Розрахунок: 12 + 30 = " << calc_add(12, 30) << '\n';
    return 0;
}
```
:::

## 3. Сценарій складання, валідації та пакування

Автоматизований сценарій `package_build.sh` виконує повний виробничий цикл розгортання:
1. Конфігурація проєкту під цільовий системний префікс `TARGET_PREFIX=/usr`.
2. Компіляція оптимізованих бінарних цілей із генерацією налагоджувальної інформації DWARF у режимі `RelWithDebInfo`.
3. Ізольоване встановлення у тимчасовий каталог Staging Root за допомогою змінної `DESTDIR=${STAGING_DIR}`.
4. Відокремлення налагоджувальних символів у зовнішні файли `.debug` через утиліти `objcopy` та `strip` із формуванням лінків `.gnu_debuglink`.
5. Автоматизована діагностика двійкових заголовків ELF утилітою `readelf` для перевірки відсутності витоку шляхів Staging у секцію `DT_RUNPATH`.
6. Глибоке сканування рядкових літералів секції `.rodata` утилітою `strings` для підтвердження того, що константи ресурсів зашиті відносно цільового префікса, а не тимчасового середовища збірки.
7. Нормалізація прав доступу згідно зі стандартами FHS (каталоги й бінарники 0755, дані 0644) та формування кінцевого двійкового архіву tar.gz із закріпленням власника `root:root` (UID 0, GID 0).

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"
STAGING_DIR="${PROJECT_ROOT}/staging_root"
DIST_DIR="${PROJECT_ROOT}/dist"
TARGET_PREFIX="/usr"
PKG_NAME="calcapp-1.0.0-linux-x86_64"

echo "=== 1. Очищення робочих просторів ==="
rm -rf "${BUILD_DIR}" "${STAGING_DIR}" "${DIST_DIR}"
mkdir -p "${STAGING_DIR}" "${DIST_DIR}"

echo "=== 2. Конфігурація проєкту для цільового префікса ${TARGET_PREFIX} ==="
cmake -S "${PROJECT_ROOT}" -B "${BUILD_DIR}" \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_PREFIX="${TARGET_PREFIX}" \
    -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_INSTALL_LOCALSTATEDIR=/var

echo "=== 3. Компіляція вихідного коду ==="
cmake --build "${BUILD_DIR}" --parallel "$(nproc)"

echo "=== 4. Ізольоване встановлення у Staging Root (DESTDIR) ==="
# Викликаємо cmake --install із передачею DESTDIR
DESTDIR="${STAGING_DIR}" cmake --install "${BUILD_DIR}"

echo "=== 5. Відокремлення налагоджувальних символів (Split Debug) ==="
BIN_FILE="${STAGING_DIR}${TARGET_PREFIX}/bin/calc_cli"
LIB_FILE="${STAGING_DIR}${TARGET_PREFIX}/lib/libcalc.so.1.0.0"
DEBUG_DIR="${STAGING_DIR}${TARGET_PREFIX}/lib/debug"
mkdir -p "${DEBUG_DIR}"

# Обробка виконуваного файлу
objcopy --only-keep-debug "${BIN_FILE}" "${DEBUG_DIR}/calc_cli.debug"
strip --strip-unneeded "${BIN_FILE}"
objcopy --add-gnu-debuglink="${DEBUG_DIR}/calc_cli.debug" "${BIN_FILE}"

# Обробка спільної бібліотеки
objcopy --only-keep-debug "${LIB_FILE}" "${DEBUG_DIR}/libcalc.so.debug"
strip --strip-unneeded "${LIB_FILE}"
objcopy --add-gnu-debuglink="${DEBUG_DIR}/libcalc.so.debug" "${LIB_FILE}"

echo "=== 6. Автоматизована валідація артефактів у Staging ==="

# Перевірка 1: Фізична присутність файлів
test -f "${BIN_FILE}" || { echo "ПОМИЛКА: calc_cli відсутній!"; exit 1; }
test -f "${LIB_FILE}" || { echo "ПОМИЛКА: libcalc.so відсутня!"; exit 1; }
test -f "${STAGING_DIR}${TARGET_PREFIX}/share/calcapp/operations.json" || \
    { echo "ПОМИЛКА: operations.json відсутній!"; exit 1; }

# Перевірка 2: Контроль RUNPATH у бінарнику через readelf
echo "--- Перевірка RUNPATH у виконуваному файлі ---"
RUNPATH_ENTRY=$(readelf -d "${BIN_FILE}" | grep -E '(RUNPATH|RPATH)' || true)
echo "Знайдено: ${RUNPATH_ENTRY}"

# Перевіряємо, чи містить бінарник очікуваний відносний шлях
if ! echo "${RUNPATH_ENTRY}" | grep -q '\$ORIGIN/../lib'; then
    echo "ПОМИЛКА: RUNPATH не містить \$ORIGIN/../lib!"
    exit 1
fi

# Сувора перевірка: чи не потрапив шлях staging у заголовок ELF
if echo "${RUNPATH_ENTRY}" | grep -q "${STAGING_DIR}"; then
    echo "КРИТИЧНИЙ ДЕФЕКТ: Шлях Staging (${STAGING_DIR}) витік у заголовок ELF!"
    exit 1
fi

# Перевірка 3: Сканування скомпільованих констант утилітою strings
echo "--- Сканування зашитих рядків у секції .rodata ---"
if strings "${BIN_FILE}" | grep -q "${STAGING_DIR}"; then
    echo "КРИТИЧНИЙ ДЕФЕКТ: Тимчасовий каталог збірки зашитий у двійковий код!"
    exit 1
fi

if strings "${BIN_FILE}" | grep -q "${TARGET_PREFIX}/share/calcapp"; then
    echo "OK: Вшитий шлях відповідає цільовому префіксу (${TARGET_PREFIX}/share/calcapp)"
else
    echo "ПОМИЛКА: Цільовий префікс відсутній у бінарнику!"
    exit 1
fi

echo "=== 7. Нормалізація прав доступу та створення пакетного архіву ==="
# Встановлюємо стандартні права FHS: 0755 для каталогів та бінарників, 0644 для даних
find "${STAGING_DIR}" -type d -exec chmod 0755 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/bin" -type f -exec chmod 0755 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/lib" -type f -name "*.so*" -exec chmod 0755 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/share" -type f -exec chmod 0644 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/include" -type f -exec chmod 0644 {} +

# Формуємо стиснений tarball із закріпленням власника root:root (UID=0, GID=0)
tar --create --gzip --verbose \
    --owner=0 --group=0 --numeric-owner \
    --directory="${STAGING_DIR}" \
    --file="${DIST_DIR}/${PKG_NAME}.tar.gz" .

# Генеруємо контрольну суму SHA-256 для верифікації дистрибутива
(cd "${DIST_DIR}" && sha256sum "${PKG_NAME}.tar.gz" > "${PKG_NAME}.tar.gz.sha256")

echo "=== Пакування успішно завершено ==="
echo "Пакет: ${DIST_DIR}/${PKG_NAME}.tar.gz"
cat "${DIST_DIR}/${PKG_NAME}.tar.gz.sha256"
```

## Механізм розділення налагоджувальних символів (Split DWARF)

У виробничих середовищах кінцеві користувачі завантажують бінарні файли без важкої таблиці налагоджувальних символів DWARF, оскільки символи можуть збільшувати розмір бінарника у 5–10 разів. Проте в разі виникнення системного збою або зняття дампу пам'яті (*core dump*) інженерам необхідні точні назви функцій і номери рядків вихідного коду.

Конвеєр розв'язує цю проблему за допомогою трикрокової обробки:
1. Команда `objcopy --only-keep-debug` створює файл `calc_cli.debug`, копіюючи в нього лише налагоджувальні секції (`.debug_info`, `.debug_line`, `.debug_str`, `.debug_abbrev`), залишаючи структуру заголовків ELF недоторканою.
2. Команда `strip --strip-unneeded` видаляє всі необов'язкові секції з основного бінарника `calc_cli`, зменшуючи його розмір до мінімуму.
3. Команда `objcopy --add-gnu-debuglink` записує в основний бінарник спеціальну секцію `.gnu_debuglink`. Ця секція містить відносне ім'я файлу налагодження та 32-бітну контрольну суму CRC32. Коли налагоджувач `gdb` або профайлер `perf` відкриває бінарник, він зчитує `.gnu_debuglink`, знаходить файл у стандартному каталозі `/usr/lib/debug` і автоматично зіставляє символи з виконуваним кодом.

У системних пакетах Linux налагоджувальні файли з каталогу `/usr/lib/debug` виділяються в окремий супутній пакет (наприклад `calcapp-dbgsym` у Debian або `calcapp-debuginfo` у Fedora), який встановлюється лише за потреби глибокого налагодження.

## Особливості поведінки символьних посилань у Staging

Під час встановлення бібліотек система CMake створює ланцюжок символьних посилань для сумісності з механізмом версіонування SONAME:
- Фізичний файл бібліотеки: `libcalc.so.1.0.0`
- Символьне посилання для завантажувача часу виконання: `libcalc.so.1 -> libcalc.so.1.0.0`
- Символьне посилання для компілятора часу збірки: `libcalc.so -> libcalc.so.1`

Якщо система збірки помилково згенерує абсолютні символьні посилання всередині каталогу Staging:
```bash
# АНТИПАТЕРН: Абсолютне посилання всередині Staging Root
ln -s /tmp/staging_root/usr/lib/libcalc.so.1.0.0 /tmp/staging_root/usr/lib/libcalc.so
```
то після пакування в архів і розпакування на цільовому сервері клієнта посилання `libcalc.so` вказуватиме на неіснуючий шлях `/tmp/staging_root/...`.

Правильний підхід, реалізований у CMake, полягає у створенні суто **відносних** символьних посилань (`libcalc.so -> libcalc.so.1`), які залишаються цілісними як усередині тимчасового каталогу `DESTDIR`, так і після розгортання в цільову файлову систему операційної системи.

## Інженерні пастки під час роботи з DESTDIR

1. **Жорстке кодування `DESTDIR` у макросах компіляції:**
   Якщо передати `-DDATADIR="${DESTDIR}${CMAKE_INSTALL_DATADIR}"`, бінарник отримає шлях `/tmp/staging_root/usr/share/calcapp`. На комп'ютері розробника це працюватиме, але у кінцевого користувача каталог `/tmp/staging_root` відсутній, і програма зазнає аварії під час спроби відкрити файл.
2. **Абсолютні шляхи у правилах `install(DESTINATION)`:**
   Якщо в CMake вказати абсолютний шлях без прив'язки до змінних, наприклад `install(FILES config.conf DESTINATION /etc)`, CMake все одно підставить `DESTDIR` на початку під час `make install` (`${DESTDIR}/etc`), але такий проєкт втратить можливість встановлення в довільний префікс користувача через `--prefix`. Правильний підхід — використовувати `CMAKE_INSTALL_SYSCONFDIR` (`etc`).
3. **Переповнення буфера конкатенації шляхів у Makefile:**
   У сценаріях Makefile запис `mkdir -p $(DESTDIR)/$(bindir)` створює подвійний слеш, якщо `bindir` уже починається зі слеша (`//usr/bin`). Хоча стандарт POSIX допускає подвійний початковий слеш, у деяких середовищах (наприклад Cygwin або мережеві ФС) подвійний слеш на початку шляху інтерпретується як мережевий ресурс UNC (`//server/share`), що призводить до несподіваних збоїв доступу. Завжди використовуйте конкатенацію без проміжного слеша: `$(DESTDIR)$(bindir)`.
4. **Витік метаданих користувача хоста:**
   Якщо створювати архів без прапорців `--owner=0 --group=0 --numeric-owner`, архів збереже UID та GID розробника або користувача сервера CI (наприклад `1001:1001`). Під час розпакування такого архіву на цільовому сервері файли можуть отримати випадкових системних власників.

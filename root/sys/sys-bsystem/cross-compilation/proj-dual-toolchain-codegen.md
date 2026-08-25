# ⚙️ Подвійний тулчейн у CMake: генерація вихідного коду під час крос-компіляції

Під час крос-компіляції програмного забезпечення для вбудованих систем, одноплатних комп'ютерів (Raspberry Pi, BeagleBone) чи мікроконтролерів (STM32, ESP32) розробники регулярно стикаються з потребою згенерувати частину вихідного коду безпосередньо під час складання проєкту. Типовими прикладами є попередній розрахунок математичних таблиць сталих значень (тригонометрія, контрольні суми CRC, геш-таблиці), компіляція схем серіалізації структурованих даних (Protocol Buffers, FlatBuffers, ASN.1), генерація лексичних і синтаксичних аналізаторів (`flex`, `bison`), конвертація растрових шрифтів або перетворення текстових файлів конфігурації у скомпільовані структури мови C чи C++.

Якщо розробник напише таку допоміжну утиліту-генератор мовою C або C++ усередині основного цільового проєкту за допомогою стандартної команди `add_executable(my_generator ...)`, система збірки за наявності файлу тулчейна збере її за допомогою цільового крос-компілятора (наприклад, `arm-none-eabi-gcc` або `aarch64-linux-gnu-gcc`). Отриманий двійковий файл матиме машинний формат цільової архітектури (ARM Cortex-M або AArch64). Коли система складання (Ninja або Make) на наступному кроці спробує запустити цей бінарник через команду `add_custom_command()` на робочій станції розробника (x86_64), операційна система Linux негайно поверне фатальну помилку ядра:

```text
ninja: error: 'bin/table_generator': cannot execute binary file: Exec format error
[12/45] Generating lookup_table.c FAILED
```

Ядро хостової системи не може виконати інструкції чужої архітектури. Виникає класична проблема подвійного тулчейну: проєкт потребує одночасного використання двох різних компіляторів — нативного компілятора хоста для допоміжних утиліт генерації коду та крос-компілятора цільової платформи для кінцевої прошивки чи застосунку.

Цей практичний практикум демонструє повну архітектуру розв'язання проблеми через створення ізольованого підпроєкту інструментів хоста (`Host Tools`) за допомогою модуля CMake `ExternalProject_Add`, організацію залежностей між цілями та верифікацію зібраних бінарників.

---

## Архітектура та життєвий цикл збірки

Щоб розв'язати конфлікт компіляторів, структура проєкту розділяється на два незалежні контури конфігурації:

1. **Контур хоста (`Host Tools`)**: збирається нативним компілятором хостової робочої станції (`/usr/bin/c++` або `clang++` під x86_64). Отриманий виконуваний файл інсталюється у внутрішній тимчасовий каталог складання хоста й негайно виконується для генерації сирцевих файлів C/C++.
2. **Цільовий контур (`Target Application`)**: збирається цільовим крос-компілятором із використанням `CMAKE_TOOLCHAIN_FILE`. Він підхоплює згенеровані файли з каталогу `CMAKE_CURRENT_BINARY_DIR`, компілює основний код і лінкує кінцевий бінарний образ цільової платформи (`firmware_app`) під архітектуру ARM.

```text
Конфігурація CMake (з -DCMAKE_TOOLCHAIN_FILE)
 │
 ├── [Контур 1: Host Tools (ExternalProject)]
 │    ├── Виклик нативного хостового компілятора (x86_64 GCC/Clang)
 │    ├── Збірка виконуваного файлу: build-arm64/host_tools-build/bin/table_gen
 │    └── Запуск: table_gen -> створює build-arm64/generated/crc32_table.cpp
 │
 └── [Контур 2: Target Firmware (Крос-тулчейн)]
      ├── Крос-компілятор: aarch64-linux-gnu-g++
      ├── Компіляція: src/main.cpp + generated/crc32_table.cpp
      └── Лінкування: кінцевий бінарник build-arm64/firmware_app (AArch64 ELF)
```

Головна перевага модуля `ExternalProject_Add` полягає в тому, що він створює повністю ізольоване середовище конфігурації CMake. Внутрішній підпроєкт має власне дерево кешу `CMakeCache.txt`, де глобальні змінні цільового тулчейна (наприклад, `CMAKE_SYSTEM_NAME` або `CMAKE_C_COMPILER`) не впливають на процес компіляції хостового інструмента.

---

## 1. Вихідний код кодогенератора (таблиця CRC-32)

Як практичний приклад реалізуємо утиліту `table_gen`, яка обчислює 256 значень таблиці швидкого розрахунку контрольної суми CRC-32 (поліном IEEE 802.3 `0xEDB88320`) і форматує їх у вихідний код C/C++.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static uint32_t generate_crc32_entry(uint32_t byte, uint32_t polynomial) {
    uint32_t crc = byte;
    for (int bit = 0; bit < 8; ++bit) {
        if (crc & 1U) {
            crc = (crc >> 1U) ^ polynomial;
        } else {
            crc = crc >> 1U;
        }
    }
    return crc;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_вихідного_файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *out = fopen(argv[1], "w");
    if (!out) {
        perror("Не вдалося відкрити вихідний файл для запису");
        return EXIT_FAILURE;
    }

    const uint32_t polynomial = 0xEDB88320U; // Стандартний поліном IEEE 802.3

    fprintf(out, "/* Автоматично згенеровано утилітою table_gen на хості. Не редагувати! */\n");
    fprintf(out, "#include <stdint.h>\n\n");
    fprintf(out, "const uint32_t g_crc32_lookup[256] = {\n");

    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t entry = generate_crc32_entry(i, polynomial);
        fprintf(out, "    0x%08XU%s%s", entry, (i < 255) ? "," : "", (i % 8 == 7) ? "\n" : " ");
    }

    fprintf(out, "};\n");
    fclose(out);
    return EXIT_SUCCESS;
}
```
@tab C++
```cpp
#include <iostream>
#include <fstream>
#include <iomanip>
#include <array>
#include <cstdint>
#include <string_view>
#include <span>

namespace {

constexpr uint32_t generate_crc32_entry(uint32_t byte_val, uint32_t polynomial) noexcept {
    uint32_t crc = byte_val;
    for (int bit = 0; bit < 8; ++bit) {
        crc = (crc & 1U) ? ((crc >> 1U) ^ polynomial) : (crc >> 1U);
    }
    return crc;
}

constexpr auto make_crc_table(uint32_t polynomial) noexcept {
    std::array<uint32_t, 256> table{};
    for (uint32_t i = 0; i < 256; ++i) {
        table[i] = generate_crc32_entry(i, polynomial);
    }
    return table;
}

} // namespace

int main(int argc, char* argv[]) {
    const std::span<char*> args(argv, static_cast<size_t>(argc));
    if (args.size() < 2) {
        std::cerr << "Використання: " << args[0] << " <шлях_до_вихідного_файлу>\n";
        return 1;
    }

    std::ofstream out(args[1], std::ios::trunc);
    if (!out.is_open()) {
        std::cerr << "Помилка відкриття файлу для запису: " << args[1] << '\n';
        return 1;
    }

    constexpr uint32_t ieee_poly = 0xEDB88320U;
    constexpr auto table = make_crc_table(ieee_poly);

    out << "/* Автоматично згенеровано утилітою table_gen на хості. Не редагувати! */\n";
    out << "#include <stdint.h>\n\n";
    out << "extern const uint32_t g_crc32_lookup[256] = {\n";

    for (size_t i = 0; i < table.size(); ++i) {
        if (i % 8 == 0) out << "    ";
        out << "0x" << std::hex << std::uppercase << std::setfill('0') << std::setw(8) << table[i] << "U";
        if (i + 1 < table.size()) out << ", ";
        if (i % 8 == 7) out << '\n';
    }

    out << "};\n";
    return 0;
}
```
:::

---

## 2. Вихідний код цільового застосунку

Цільовий застосунок використовує згенеровану масивну таблицю `g_crc32_lookup` для швидкого побайтового розрахунку контрольної суми буфера повідомлення.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

extern const uint32_t g_crc32_lookup[256];

uint32_t calculate_buffer_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        uint8_t table_index = (uint8_t)((crc ^ data[i]) & 0xFFU);
        crc = (crc >> 8U) ^ g_crc32_lookup[table_index];
    }
    return crc ^ 0xFFFFFFFFU;
}

int main(void) {
    const uint8_t payload[] = "Firmware telemetry packet payload";
    uint32_t checksum = calculate_buffer_crc32(payload, sizeof(payload) - 1);
    printf("Обчислена контрольна сума CRC-32: 0x%08X\n", checksum);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <iomanip>
#include <cstdint>
#include <span>
#include <string_view>

extern "C" const uint32_t g_crc32_lookup[256];

namespace telemetry {

[[nodiscard]] uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte_val : data) {
        const uint8_t table_idx = static_cast<uint8_t>((crc ^ byte_val) & 0xFFU);
        crc = (crc >> 8U) ^ g_crc32_lookup[table_idx];
    }
    return crc ^ 0xFFFFFFFFU;
}

} // namespace telemetry

int main() {
    constexpr std::string_view msg = "Firmware telemetry packet payload";
    const std::span<const uint8_t> payload_bytes{
        reinterpret_cast<const uint8_t*>(msg.data()), msg.size()
    };

    const uint32_t checksum = telemetry::calculate_crc32(payload_bytes);
    std::cout << "Обчислена контрольна сума CRC-32: 0x"
              << std::hex << std::uppercase << std::setfill('0') << std::setw(8)
              << checksum << '\n';
    return 0;
}
```
:::

---

## 3. Організація дерев каталогів та файлів CMake

Для ізоляції інструментів хоста створимо структуру з окремою підпапкою `host_tools/`:

```text
cross_dual_toolchain/
├── CMakeLists.txt              # Головний сценарій складання
├── cmake/
│   └── aarch64-toolchain.cmake # Файл опису цільового тулчейна
├── host_tools/
│   ├── CMakeLists.txt          # Ізольований CMakeLists для хоста
│   └── table_gen.cpp           # Вихідний код кодогенератора
└── src/
    └── main.cpp                # Цільовий код прошивки
```

### Вкладений `host_tools/CMakeLists.txt`

Цей сценарій нічого не знає про крос-компіляцію й завжди конфігурується з нативними компіляторами хоста:

```cmake
cmake_minimum_required(VERSION 3.20)
project(HostTools LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(table_gen table_gen.cpp)

# Встановлюємо виконуваний файл у каталог bin
install(TARGETS table_gen DESTINATION bin)
```

### Головний кореневий `CMakeLists.txt`

Головний сценарій перевіряє значення змінної `CMAKE_CROSSCOMPILING`. Якщо активна крос-компіляція, він використовує `ExternalProject_Add` для автономного виклику CMake під нативний хост зі скиданням файлу тулчейна (`-DCMAKE_TOOLCHAIN_FILE=`):

```cmake
cmake_minimum_required(VERSION 3.20)
project(FirmwareProject LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(GENERATED_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(GENERATED_CRC_SRC "${GENERATED_DIR}/crc32_table.cpp")
file(MAKE_DIRECTORY "${GENERATED_DIR}")

if(CMAKE_CROSSCOMPILING)
    # Крос-компіляція: збираємо автономний нативний підпроєкт для хоста
    include(ExternalProject)

    set(HOST_TOOLS_DIR "${CMAKE_CURRENT_BINARY_DIR}/host_tools-build")
    set(HOST_TABLE_GEN_EXE "${HOST_TOOLS_DIR}/bin/table_gen")

    ExternalProject_Add(host_tools_subproject
        SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/host_tools"
        BINARY_DIR "${HOST_TOOLS_DIR}"
        INSTALL_DIR "${HOST_TOOLS_DIR}"
        CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${HOST_TOOLS_DIR}
            # Критично: скидаємо файл тулчейна для нативного складання хостом
            -DCMAKE_TOOLCHAIN_FILE=
            -DCMAKE_BUILD_TYPE=Release
        BUILD_BYPRODUCTS "${HOST_TABLE_GEN_EXE}"
    )

    # Оголошуємо імпортовану виконувану ціль
    add_executable(generator_tool IMPORTED GLOBAL)
    set_target_properties(generator_tool PROPERTIES
        IMPORTED_LOCATION "${HOST_TABLE_GEN_EXE}"
    )
    add_dependencies(generator_tool host_tools_subproject)
else()
    # Нативна збірка (хост і ціль однакові): збираємо напряму
    add_subdirectory(host_tools)
    add_executable(generator_tool ALIAS table_gen)
endif()

# Команда запуску хостового генератора
add_custom_command(
    OUTPUT "${GENERATED_CRC_SRC}"
    COMMAND generator_tool "${GENERATED_CRC_SRC}"
    DEPENDS generator_tool
    COMMENT "Генерація CRC-32 таблиці нативною утилітою хоста..."
    VERBATIM
)

# Цільовий бінарник прошивки під цільову архітектуру
add_executable(firmware_app
    src/main.cpp
    "${GENERATED_CRC_SRC}"
)

target_include_directories(firmware_app PRIVATE "${GENERATED_DIR}")
```

---

## 4. Покрокове трасування процесу збірки та перевірка

Для верифікації налаштуємо файл тулчейна `cmake/aarch64-toolchain.cmake`:

```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

Запустимо конфігурацію та збірку:

```bash
# 1. Конфігурація крос-збірки
cmake -B build-arm64 -S . -DCMAKE_TOOLCHAIN_FILE=cmake/aarch64-toolchain.cmake -G Ninja

# 2. Виконання компіляції
cmake --build build-arm64 --verbose
```

### Аналіз послідовності викликів у журналі Ninja

Під час виконання команди `cmake --build` утиліта Ninja будує коректний ациклічний граф залежностей і виконує команди у такій суворій послідовності:

1. **Крок 1 (Ініціалізація хостового інструмента)**:
   Ninja запускає внутрішній крок `host_tools_subproject`. Викликається системний компілятор хоста `/usr/bin/c++` без прапорців крос-компіляції:
   ```text
   /usr/bin/c++ -O3 -std=c++20 host_tools/table_gen.cpp -o host_tools-build/bin/table_gen
   ```
2. **Крок 2 (Генерація коду на хості)**:
   Виконується скомпільований бінарник хоста:
   ```text
   build-arm64/host_tools-build/bin/table_gen build-arm64/generated/crc32_table.cpp
   ```
3. **Крок 3 (Цільова крос-компіляція)**:
   Крос-компілятор `aarch64-linux-gnu-g++` компілює згенерований файл разом із джерельними кодами застосунку:
   ```text
   aarch64-linux-gnu-g++ -std=c++20 -Ibuild-arm64/generated -c build-arm64/generated/crc32_table.cpp
   aarch64-linux-gnu-g++ -std=c++20 -Ibuild-arm64/generated -c src/main.cpp
   aarch64-linux-gnu-g++ main.o crc32_table.o -o build-arm64/firmware_app
   ```

### Верифікація отриманих артефактів через утиліту `file`

Перевірка заголовків ELF підтверджує, що в одному проєкті було створено бінарники для двох абсолютно різних процесорних архітектур:

```bash
# 1. Перевірка хостової утиліти
file build-arm64/host_tools-build/bin/table_gen
# Вивід: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked...

# 2. Перевірка цільової прошивки
file build-arm64/firmware_app
# Вивід: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), dynamically linked...
```

---

## 5. Крайові випадки та промислові рекомендації

Під час розгортання конвеєрів подвійного тулчейну в промислових системах неперервної інтеграції (CI/CD) слід враховувати такі інженерні нюанси:

1. **Крос-компіляція з Windows-хоста на Linux-ціль**:
   Виконуваний файл хоста у Windows має розширення `.exe` (`table_gen.exe`). Використання генераторного виразу `$<TARGET_FILE:generator_tool>` замість жорстко прописаного шляху автоматично підставляє правильне розширення двійкового файлу хоста на будь-якій ОС.
2. **Інкрементальність та відстеження змін у генераторі**:
   Директива `DEPENDS generator_tool` у команді `add_custom_command()` гарантує, що якщо розробник змінить алгоритм у `host_tools/table_gen.cpp`, CMake автоматично перекомпілює утиліту хоста, заново згенерує `crc32_table.cpp` та перекомпонує цільовий бінарник `firmware_app`.
3. **Паралельна генерація кількох файлів**:
   Якщо генератор створює кілька файлів одночасно (наприклад, `.h` заголовок та `.cpp` реалізацію), їх слід перелічити у списку `OUTPUT` однієї команди `add_custom_command()`. Це запобігає стану гонки (Race Condition), коли генератор запускається двічі паралельними потоками Ninja.
4. **Попередньо зібрані пакети інструментів хоста**:
   Якщо генератором виступає важкий сторонній інструмент (наприклад, компілятор `protoc` чи `flatc`), збірка якого триває хвилинами, краще встановити нативний бінарник у систему хоста через пакетний менеджер (`apt install protobuf-compiler`) і знаходити його через `find_program(PROTOC protoc NO_CMAKE_FIND_ROOT_PATH)` замість повної збірки з вихідного коду на кожній ітерації CI.

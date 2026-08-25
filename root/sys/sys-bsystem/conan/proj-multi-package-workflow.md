# ⚙️ Наскрізний конвеєр збірки, споживання та публікації пакетів у Conan 2.x

У практичній розробці розподілених систем мовою C++ створення окремого програмного компонента вимагає завершеного виробничого циклу: опису бібліотеки у вигляді формального рецепта, локальної перевірки через інтеграційний пакет `test_package`, крос-компіляції під цільову вбудовану платформу, криптографічної фіксації графа за допомогою `conan.lock` та публікації артефактів на корпоративний сервер JFrog Artifactory.

Нижче детально розібрано повний робочий проєкт промислового рівня. Він складається з телеметричної бібліотеки `libtelemetry` (стандарт C++20), мікросервісного споживчого демона `telemetry_daemon`, профілів крос-компіляції для процесорів ARM64 та автоматизованого сценарію конвеєра безперервної інтеграції (CI/CD).

## Частина 1. Проєктування та пакування бібліотеки libtelemetry

Бібліотека `libtelemetry` призначена для високопродуктивної серіалізації та перевірки цілісності вимірювальних кадрів бортових сенсорів. Для досягнення нульових накладних витрат на копіювання пам'яті інтерфейс бібліотеки спроєктовано на базі типів `std::span` та `std::string_view`, введених у стандарті C++20.

Такий підхід дозволяє передавати масиви структур безпосередньо з буферів драйверів вводу-виводу або областей спільної пам'яті (shared memory) без виділення динамічної пам'яті в купі на кожен виклик кодування.

### 1.1. Джерельний код бібліотеки

Публічний заголовковий файл `include/telemetry/telemetry.hpp` визначає структуру окремого вимірювального запису та інтерфейс класу пакувальника кадрів:

```cpp
#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <span>

namespace telemetry {

struct SensorRecord {
    uint32_t sensor_id{0};
    uint64_t timestamp_ns{0};
    double value{0.0};
};

class PacketEncoder {
public:
    explicit PacketEncoder(std::string_view channel_name);

    [[nodiscard]] std::vector<uint8_t> encode(std::span<const SensorRecord> records) const;
    [[nodiscard]] std::string_view channel_name() const noexcept;

private:
    std::string channel_name_;
};

} // namespace telemetry
```

Файл реалізації `src/telemetry.cpp` здійснює компактне бінарне пакування масиву вимірювань у неперервний буфер пам'яті. Метод розраховує точний сумарний обсяг байтів наперед і виконує рівно одну алокацію цільового вектора:

```cpp
#include "telemetry/telemetry.hpp"

#include <cstring>
#include <stdexcept>

namespace telemetry {

PacketEncoder::PacketEncoder(std::string_view channel_name)
    : channel_name_(channel_name) {
    if (channel_name_.empty()) {
        throw std::invalid_argument("Назва каналу телеметрії не може бути порожньою");
    }
}

std::string_view PacketEncoder::channel_name() const noexcept {
    return channel_name_;
}

std::vector<uint8_t> PacketEncoder::encode(std::span<const SensorRecord> records) const {
    const uint32_t record_count = static_cast<uint32_t>(records.size());
    const uint32_t name_len = static_cast<uint32_t>(channel_name_.size());
    
    // Розрахунок точного розміру буфера без проміжних алокацій
    const size_t total_size = sizeof(uint32_t) + name_len + 
                              sizeof(uint32_t) + (records.size() * sizeof(SensorRecord));
    
    std::vector<uint8_t> buffer(total_size);
    uint8_t* ptr = buffer.data();

    // Запис префікса назви каналу
    std::memcpy(ptr, &name_len, sizeof(name_len));
    ptr += sizeof(name_len);
    std::memcpy(ptr, channel_name_.data(), name_len);
    ptr += name_len;

    // Запис кількості записів та бінарного масиву
    std::memcpy(ptr, &record_count, sizeof(record_count));
    ptr += sizeof(record_count);

    if (!records.empty()) {
        const size_t payload_bytes = records.size_bytes();
        std::memcpy(ptr, records.data(), payload_bytes);
    }

    return buffer;
}

} // namespace telemetry
```

### 1.2. Конфігурація системи збірки CMakeLists.txt

Файл опису збірки бібліотеки формується за канонами Modern CMake. Важливо, що він використовує генераторні вирази `$<BUILD_INTERFACE:...>` та `$<INSTALL_INTERFACE:...>` для коректної трансляції шляхів до заголовків як під час внутрішньої збірки, так і після інсталяції в каталог пакета Conan. 

Також оголошуються стандартні шляхи каталогу встановлення через модуль `GNUInstallDirs`:

```cmake
cmake_minimum_required(VERSION 3.20)
project(telemetry VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(telemetry src/telemetry.cpp)

target_include_directories(telemetry PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Опис інсталяційного набору цілей
include(GNUInstallDirs)
install(TARGETS telemetry
    EXPORT telemetryTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
```

### 1.3. Рецепт conanfile.py для бібліотеки

Рецепт підтримує як статичне, так і динамічне лінкування, автоматично налаштовує прапорець `fPIC` для операційних систем POSIX, підключає стандартизований `cmake_layout` та експортує метадані для генераторів споживачів. 

У методі `package_info()` задаються властивості `cmake_file_name` та `cmake_target_name`, які гарантують, що згенеровані конфігураційні файли відповідатимуть канонічному імені цілі `telemetry::telemetry`:

```python
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
import os

class TelemetryConan(ConanFile):
    name = "telemetry"
    version = "1.0.0"
    license = "MIT"
    author = "Embedded Team <embedded@company.internal>"
    description = "Телеметрична серіалізація та кадрування датчиків"
    topics = ("telemetry", "sensors", "serialization")
    package_type = "library"

    # Матриця комбінаторних параметрів
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        # На платформі Windows прапорець fPIC не має сенсу
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        # Для shared-бібліотек на Linux fPIC завжди активний
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        # Автоматичне налаштування шляхів збірки під генератори CMake
        cmake_layout(self)

    def generate(self):
        # Генерація файлів conan_toolchain.cmake та конфігурацій залежностей
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        # Виклик CMake у підкаталозі build
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Інсталяція артефактів у package_folder
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # Оголошення публічних імпортованих цілей для споживачів
        self.cpp_info.libs = ["telemetry"]
        self.cpp_info.set_property("cmake_file_name", "telemetry")
        self.cpp_info.set_property("cmake_target_name", "telemetry::telemetry")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
```

### 1.4. Інтеграційний тестувальний пакет test_package

Каталог `test_package` є невіддільною частиною надійного рецепта. Його мета — не замінити модульні тести самої бібліотеки, а переконатися, що скомпільований, запакований та експортований у кеш пакет здатний бути знайдений через виклик `find_package(telemetry REQUIRED)` сторонньою програмою.

У файлі `test_package/CMakeLists.txt` споживається створена бібліотека:

```cmake
cmake_minimum_required(VERSION 3.20)
project(test_telemetry LANGUAGES CXX)

find_package(telemetry REQUIRED)

add_executable(test_app src/test_main.cpp)
target_link_libraries(test_app PRIVATE telemetry::telemetry)
```

Тестова програма `test_package/src/test_main.cpp` створює екземпляр класу пакувальника, формує вибірку показників датчиків та перевіряє ненульовий розмір сформованого бінарного кадру:

```cpp
#include <telemetry/telemetry.hpp>
#include <iostream>
#include <array>

int main() {
    telemetry::PacketEncoder encoder("engine_chamber_01");
    
    std::array<telemetry::SensorRecord, 2> records{{
        {101, 1718900000000ULL, 42.5},
        {102, 1718900001000ULL, 120.3}
    }};

    auto payload = encoder.encode(records);
    std::cout << "Успішно закодовано байтів: " << payload.size() << "\n";
    return payload.empty() ? 1 : 0;
}
```

Файл керування тестувальним пакетом `test_package/conanfile.py` містить спеціальний захисний блок `can_run(self)`. Ця перевірка запобігає спробі запуску скомпільованого бінарника під час крос-компіляції, коли архітектура цільового бінарника (наприклад, ARM64) несумісна з процесором машини збірки (x86_64), якщо в системі не налаштовано емулятор QEMU:

```python
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run
import os

class TestTelemetryConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        # Автоматичне посилання на щойно створений пакет
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # Виконання бінарника тільки якщо архітектура дозволяє запуск на машині збірки
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "test_app")
            self.run(cmd, env="conanrun")
```

Виконання команди створення та валідації пакета в локальному кеші:
```bash
conan create . --build=missing
```

Команда `conan create` завантажує джерела, компілює бібліотеку, виконує інсталяцію в `package_folder`, а потім створює ізольовану тимчасову папку для `test_package`, де через `CMakeDeps` знаходить скомпільований пакет і підтверджує його валідність.

## Частина 2. Споживчий мікросервіс telemetry_daemon

Демон `telemetry_daemon` є кінцевим прикладним застосунком. Він споживає щойно створену бібліотеку `telemetry::telemetry`, а також дві сторонні бібліотеки з реєстру ConanCenter: бібліотеку форматування виводу `fmt` та бібліотеку роботи з даними `nlohmann_json`.

### 2.1. Рецепт споживача conanfile.py

У рецепті споживача поле `package_type = "application"` вказує рушію Conan, що кінцевим продуктом є виконуваний файл, який не експортує бібліотечні заголовки іншим споживачам:

```python
from conan import ConanFile
from conan.tools.cmake import cmake_layout

class DaemonConan(ConanFile):
    name = "telemetry_daemon"
    version = "0.1.0"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("telemetry/1.0.0")
        self.requires("fmt/10.2.1")
        self.requires("nlohmann_json/3.11.3")

    def layout(self):
        cmake_layout(self)
```

### 2.2. Головний файл main.cpp

Програма зчитує показники датчиків, формує бінарний блок за допомогою `libtelemetry`, упаковує метадані у структурований JSON-документ та виводить результат у стандартний потік за допомогою бібліотеки `fmt`:

```cpp
#include <telemetry/telemetry.hpp>
#include <fmt/core.h>
#include <nlohmann/json.hpp>

#include <iostream>
#include <vector>

int main() {
    try {
        telemetry::PacketEncoder encoder("flight_telemetry");

        std::vector<telemetry::SensorRecord> batch = {
            {.sensor_id = 1, .timestamp_ns = 1718900000100ULL, .value = 101.325},
            {.sensor_id = 2, .timestamp_ns = 1718900000200ULL, .value = 298.150},
            {.sensor_id = 3, .timestamp_ns = 1718900000300ULL, .value = 9.80665}
        };

        auto binary_blob = encoder.encode(batch);

        nlohmann::json report;
        report["channel"] = encoder.channel_name();
        report["records_count"] = batch.size();
        report["encoded_bytes"] = binary_blob.size();
        report["status"] = "OK";

        fmt::print("Телеметричний звіт:\n{}\n", report.dump(4));
        return 0;
    } catch (const std::exception& e) {
        fmt::print(stderr, "Помилка демона: {}\n", e.what());
        return 1;
    }
}
```

### 2.3. Чистий файл CMakeLists.txt споживача

Файл збірки споживача не містить жодних специфічних команд Conan: він оперує виключно стандартними імпортованими цілями `fmt::fmt`, `nlohmann_json::nlohmann_json` та `telemetry::telemetry`:

```cmake
cmake_minimum_required(VERSION 3.20)
project(telemetry_daemon LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(telemetry REQUIRED)
find_package(fmt REQUIRED)
find_package(nlohmann_json REQUIRED)

add_executable(telemetry_daemon main.cpp)
target_link_libraries(telemetry_daemon PRIVATE
    telemetry::telemetry
    fmt::fmt
    nlohmann_json::nlohmann_json
)
```

## Частина 3. Крос-компіляція під архітектуру Linux ARM64

Для збірки застосунку під цільову вбудовану систему (наприклад, промисловий одноплатний комп'ютер на базі ARM Cortex-A53) на машині розробника x86_64 створюються два файли профілів у каталозі `profiles/`.

### 3.1. Білд-профіль для хост-машини (profiles/linux-x86_64)

Цей профіль описує середовище компіляції розробника, де виконуватимуться внутрішні інструменти збірки (компілятори, CMake, Ninja, генератори коду):

```ini
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=13
compiler.libcxx=libstdc++11
compiler.cppstd=20
build_type=Release
```

### 3.2. Хост-профіль для цільової плати (profiles/linux-arm64)

Цей профіль визначає цільовий процесор ARMv8, прапорці крос-компілятора `aarch64-linux-gnu-gcc` та конфігураційні змінні генератора CMakeToolchain. Змінні секції `[buildenv]` автоматично активуються під час викликів системи збірки:

```ini
[settings]
os=Linux
arch=armv8
compiler=gcc
compiler.version=13
compiler.libcxx=libstdc++11
compiler.cppstd=20
build_type=Release

[buildenv]
CC=aarch64-linux-gnu-gcc
CXX=aarch64-linux-gnu-g++
AR=aarch64-linux-gnu-ar
STRIP=aarch64-linux-gnu-strip

[conf]
tools.cmake.cmaketoolchain:system_name=Linux
tools.cmake.cmaketoolchain:system_processor=aarch64
```

## Частина 4. Повний сценарій CI/CD, фіксація графа та публікація

Нижче наведено виробничий Bash-сценарій, що виконує повний цикл у середовищі неперервної інтеграції: автентифікацію на сервері JFrog Artifactory, бінарну збірку бібліотеки, публікацію артефактів, генерацію замка залежностей `conan.lock` та детерміновану збірку кінцевого демона.

Ключовим кроком тут є створення `conan.lock`. Файл замка фіксує точні ревізії вихідного коду (RREV) та точні хеші скомпільованих бінарних пакетів (`package_id`), унеможливлюючи непередбачувані оновлення транзитивних залежностей під час нічних збірок:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> 1. Підключення до корпоративного сховища JFrog Artifactory"
conan remote add artifactory https://artifactory.company.internal/artifactory/api/conan/conan-local --force
conan remote login artifactory "${CI_CONAN_USER}" -p "${CI_CONAN_TOKEN}"

echo "==> 2. Збірка та пакування бібліотеки під цільову платформу ARM64"
conan create libs/telemetry \
    --profile:build=profiles/linux-x86_64 \
    --profile:host=profiles/linux-arm64 \
    --build=missing

echo "==> 3. Публікація бінарного пакета на віддалений сервер"
conan upload telemetry/1.0.0 -r artifactory --confirm

echo "==> 4. Фіксація повного графа залежностей споживача у conan.lock"
conan lock create apps/telemetry_daemon/conanfile.py \
    --profile:build=profiles/linux-x86_64 \
    --profile:host=profiles/linux-arm64 \
    --lockfile-out=conan.lock

echo "==> 5. Детерміноване встановлення залежностей споживача за замком"
conan install apps/telemetry_daemon \
    --profile:build=profiles/linux-x86_64 \
    --profile:host=profiles/linux-arm64 \
    --lockfile=conan.lock \
    --build=missing

echo "==> 6. Компіляція бінарника через стандартні команди CMakePresets"
cmake --preset conan-armv8-release -S apps/telemetry_daemon
cmake --build --preset conan-armv8-release

echo "==> Успішно! Бінарний виконуваний файл telemetry_daemon зібрано для ARM64."
```

Завдяки використанню `conan.lock` та попередньо скомпільованих бінарних пакетів із репозиторію Artifactory цей конвеєр виконується за лічені секунди, повністю гарантуючи відтворюваність та ідентичність бінарного коду на всіх серверах збірки.

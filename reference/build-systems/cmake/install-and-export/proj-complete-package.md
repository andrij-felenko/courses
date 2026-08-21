# ⚙️ Повний виробничий проєкт створення та споживання пакета CMake

У цьому практичному проєкті розібрано повний виробничий цикл створення сучасної модульної бібліотеки на C++, підготовки її до експорту, генерації релокованого пакета для `find_package()` та підключення у зовнішній клієнтській програмі.

## Постановка задачі

Ми розробляємо модульну бібліотеку `Hyperion`, призначену для високопродуктивних обчислень та телеметрії. Проєкт складається з двох взаємопов'язаних компонентів із різними вимогами до збірки:

1. **`Hyperion::core`** — скомпільована бібліотека, яка містить стан рушія обчислень та алгоритм підрахунку контрольних сум FNV-1a. Вона повинна підтримувати складання як у статичному (`STATIC`), так і в динамічному (`SHARED`) варіантах із коректним експортом двійкових символів на всіх платформах.
2. **`Hyperion::math`** — заголовочна бібліотека (header-only / `INTERFACE`), яка надає набір шаблонів швидкої векторної арифметики на базі C++20 концептів (`std::floating_point`, `std::integral`) та представлень `std::span`.

До системи збірки та пакування висуваються такі жорсткі вимоги:
- **Двоїстість використання:** бібліотека має бездоганно компілюватися та проходити тести всередині власного репозиторію (Build Tree), а після інсталяції в системний каталог чи префікс менеджера пакетів (Install Tree) — надавати однаковий інтерфейс імпортованих цілей.
- **Повна переміщуваність (relocatability):** каталог інсталяції не повинен містити жодного жорстко закодованого абсолютного шляху хост-машини. Встановлений пакет має безперешкодно працювати після перейменування каталогу чи перенесення на інший комп'ютер.
- **Автоматизація конфігурації:** створення файлів `HyperionConfig.cmake`, `HyperionConfigVersion.cmake` та `HyperionTargets.cmake` має виконуватися за допомогою стандартних модулів `GNUInstallDirs` та `CMakePackageConfigHelpers`.
- **Семантичне версіонування:** підтримка автоматичної перевірки сумісності версій клієнтських запитів за правилом `SameMajorVersion`.

---

## Структура репозиторію

Організуємо файлову структуру проєкту з чітким розділенням публічних інтерфейсів, вихідного коду реалізації, шаблонів конфігурації та прикладів використання:

```text
hyperion-project/
├── CMakeLists.txt
├── cmake/
│   └── HyperionConfig.cmake.in
├── include/
│   └── hyperion/
│       ├── export.hpp
│       ├── core.hpp
│       └── math.hpp
├── src/
│   └── core.cpp
├── tests/
│   └── test_core.cpp
└── examples/
    └── consumer_app/
        ├── CMakeLists.txt
        └── main.cpp
```

Каталог `include/hyperion/` містить публічні заголовки, доступні зовнішнім споживачам. Каталог `src/` ізолює приватну реалізацію, а `cmake/` містить шаблон конфігураційного файла для `find_package()`.

---

## Вихідний код компонентів бібліотеки

### 1. Заголовковий файл макросів експорту `include/hyperion/export.hpp`

Для коректного складання динамічної бібліотеки (`SHARED`) у Windows компілятор MSVC вимагає явного позначення символів ключовим словом `__declspec(dllexport)` під час компіляції самої бібліотеки та `__declspec(dllimport)` під час її підключення у клієнтському коді. Натомість у Linux (GCC/Clang) використовується атрибут видимості `__attribute__((visibility("default")))`.

```cpp
#pragma once

#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(HYPERION_STATIC_DEFINE)
    #define HYPERION_API
  #elif defined(hyperion_core_EXPORTS)
    #define HYPERION_API __declspec(dllexport)
  #else
    #define HYPERION_API __declspec(dllimport)
  #endif
#else
  #if defined(__GNUC__) && __GNUC__ >= 4
    #define HYPERION_API __attribute__((visibility("default")))
  #else
    #define HYPERION_API
  #endif
#endif
```

Зверніть увагу на макрос `hyperion_core_EXPORTS`: CMake автоматично визначає цей макрос під час збірки цілі `hyperion_core` як спільної бібліотеки (`SHARED`). Коли цей самий заголовок включається споживачем, макрос відсутній, і `HYPERION_API` автоматично перемикається на `__declspec(dllimport)`.

### 2. Публічний заголовок скомпільованого ядра `include/hyperion/core.hpp`

Клас `Engine` інкапсулює внутрішній стан та надає метод для обчислення некриптографічного хешу FNV-1a над довільним рядковим буфером:

```cpp
#pragma once

#include <string>
#include <string_view>
#include <cstdint>
#include "hyperion/export.hpp"

namespace hyperion {

class HYPERION_API Engine {
public:
    explicit Engine(std::string name);
    
    [[nodiscard]] std::string_view name() const noexcept;
    [[nodiscard]] uint32_t compute_hash(std::string_view payload) const noexcept;

private:
    std::string name_;
};

} // namespace hyperion
```

### 3. Реалізація ядра `src/core.cpp`

```cpp
#include "hyperion/core.hpp"

namespace hyperion {

Engine::Engine(std::string name)
    : name_(std::move(name)) {}

std::string_view Engine::name() const noexcept {
    return name_;
}

uint32_t Engine::compute_hash(std::string_view payload) const noexcept {
    // Алгоритм 32-бітного хешування FNV-1a
    uint32_t hash = 2166136261u;
    for (char c : payload) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 16777619u;
    }
    return hash;
}

} // namespace hyperion
```

### 4. Заголовочний модуль `include/hyperion/math.hpp`

Модуль реалізує шаблон підсумовування елементів вектора, обмежуючи типи даних за допомогою концептів мови C++20:

```cpp
#pragma once

#include <concepts>
#include <span>
#include <numeric>

namespace hyperion::math {

template <typename T>
requires std::floating_point<T> || std::integral<T>
[[nodiscard]] constexpr T accumulate_span(std::span<const T> values) noexcept {
    return std::accumulate(values.begin(), values.end(), T{0});
}

} // namespace hyperion::math
```

---

## Шаблон конфігурації `cmake/HyperionConfig.cmake.in`

Файл конфігурації виконується під час виклику `find_package(Hyperion CONFIG)` у клієнтському проєкті. Шаблон містить мінімальний захисний код:

```cmake
@PACKAGE_INIT@

# Підключення допоміжного макроса пошуку транзитивних залежностей
include(CMakeFindDependencyMacro)

# Підключення згенерованого файла імпортованих цілей
include("${CMAKE_CURRENT_LIST_DIR}/HyperionTargets.cmake")

# Перевірка наявності всіх обов'язкових компонентів
check_required_components(Hyperion)
```

Макрос `@PACKAGE_INIT@` генерує код для визначення відносного кореня інсталяції `PACKAGE_PREFIX_DIR`. Макрос `check_required_components(Hyperion)` гарантує, що якщо споживач передав список компонентів `COMPONENTS core math`, конфігурація перевірить їхню доступність.

---

## Головний сценарій збірки `CMakeLists.txt`

Сценарій `CMakeLists.txt` реалізує повний життєвий цикл збірки, тестування, експорту цілей та генерації пакетних метаданих:

```cmake
cmake_minimum_required(VERSION 3.20)
project(Hyperion
    VERSION 1.2.0
    DESCRIPTION "Виробнича модульна бібліотека телеметрії та обчислень"
    LANGUAGES CXX
)

# Задання обов'язкового стандарту C++20 для всіх цілей
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Підключення стандартних допоміжних модулів
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

# Опція типу бібліотеки: за замовчуванням динамічна збірка
option(BUILD_SHARED_LIBS "Збирати спільні (shared) бібліотеки" ON)

# -----------------------------------------------------------------------------
# 1. Оголошення цілі Hyperion::core (скомпільована частина)
# -----------------------------------------------------------------------------
add_library(hyperion_core src/core.cpp)

# Створення локального псевдоніма для однакового синтаксису в тестах
add_library(Hyperion::core ALIAS hyperion_core)

# Розділення шляхів включення для дерева джерел та дерева інсталяції
target_include_directories(hyperion_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_compile_features(hyperion_core PUBLIC cxx_std_20)

# Якщо бібліотека збирається як статична, транслюємо макрос споживачам
if(NOT BUILD_SHARED_LIBS)
    target_compile_definitions(hyperion_core PUBLIC HYPERION_STATIC_DEFINE)
endif()

# -----------------------------------------------------------------------------
# 2. Оголошення цілі Hyperion::math (заголовочна частина)
# -----------------------------------------------------------------------------
add_library(hyperion_math INTERFACE)
add_library(Hyperion::math ALIAS hyperion_math)

target_include_directories(hyperion_math
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_compile_features(hyperion_math INTERFACE cxx_std_20)

# -----------------------------------------------------------------------------
# 3. Правила інсталяції двійкових артефактів та заголовків
# -----------------------------------------------------------------------------
install(TARGETS hyperion_core hyperion_math
    EXPORT HyperionTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Встановлення структури публічних файлів заголовків
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)

# -----------------------------------------------------------------------------
# 4. Генерація файла імпортованих цілей HyperionTargets.cmake
# -----------------------------------------------------------------------------
set(HYPERION_CONFIG_INSTALL_DIR "${CMAKE_INSTALL_LIBDIR}/cmake/Hyperion")

install(EXPORT HyperionTargets
    FILE HyperionTargets.cmake
    NAMESPACE Hyperion::
    DESTINATION ${HYPERION_CONFIG_INSTALL_DIR}
)

# -----------------------------------------------------------------------------
# 5. Генерація файлів конфігурації пакета та перевірки версій
# -----------------------------------------------------------------------------
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/HyperionConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfig.cmake"
    INSTALL_DESTINATION ${HYPERION_CONFIG_INSTALL_DIR}
)

# Інсталяція конфігураційних файлів поруч із HyperionTargets.cmake
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfigVersion.cmake"
    DESTINATION ${HYPERION_CONFIG_INSTALL_DIR}
)
```

Зверніть увагу на реєстрацію псевдонімів `add_library(Hyperion::core ALIAS hyperion_core)`. Це дозволяє писати модульні тести та приклади всередині самого репозиторію точно так само, як це робитиме зовнішній споживач: лінкуючись із `Hyperion::core`, а не з внутрішнім іменем `hyperion_core`. Блок `if(NOT BUILD_SHARED_LIBS)` гарантує, що у статичному режимі макрос `HYPERION_STATIC_DEFINE` транзитивно передається через властивість `INTERFACE_COMPILE_DEFINITIONS` усім споживачам.

---

## Збірка та інсталяція в ізольований каталог

Виконаємо конфігурацію, компіляцію та інсталяцію бібліотеки у тимчасовий каталог `/tmp/hyperion-dist`:

```bash
# 1. Конфігурація проєкту в режимі Release із зазначенням префікса інсталяції
cmake -B build -S . \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/tmp/hyperion-dist

# 2. Компіляція двійкових артефактів
cmake --build build --config Release

# 3. Виконання інсталяції артефактів у заданий префікс
cmake --install build
```

### Анатомія створеного каталогу інсталяції

Після виконання команди `cmake --install` каталог `/tmp/hyperion-dist` містить повністю автономну структуру файлів:

```text
/tmp/hyperion-dist/
├── include/
│   └── hyperion/
│       ├── core.hpp
│       ├── export.hpp
│       └── math.hpp
├── lib/
│   ├── libhyperion_core.so (або .dylib на macOS чи .lib на Windows)
│   └── cmake/
│       └── Hyperion/
│           ├── HyperionConfig.cmake
│           ├── HyperionConfigVersion.cmake
│           ├── HyperionTargets.cmake
│           └── HyperionTargets-release.cmake
```

Розберемо вміст згенерованих файлів:
- **`HyperionTargets.cmake`** — містить визначення імпортованих цілей `add_library(Hyperion::core SHARED IMPORTED)` та `add_library(Hyperion::math INTERFACE IMPORTED)`. Він обчислює змінну `_IMPORT_PREFIX` підняттям на 3 рівні вгору від `lib/cmake/Hyperion/` до кореня `/tmp/hyperion-dist`.
- **`HyperionTargets-release.cmake`** — прив'язує властивість `IMPORTED_LOCATION_RELEASE` цілі `Hyperion::core` до відносного файлу `${_IMPORT_PREFIX}/lib/libhyperion_core.so`.
- **`HyperionConfigVersion.cmake`** — містить алгоритм перевірки SemVer. Якщо споживач запитає версію `1.0.0` або `1.2.0`, файл встановить `PACKAGE_VERSION_COMPATIBLE = TRUE`. Якщо споживач запитає `2.0.0`, файл встановить `PACKAGE_VERSION_COMPATIBLE = FALSE`.
- **`HyperionConfig.cmake`** — містить розгорнутий макрос `@PACKAGE_INIT@` та директиву `include` для підключення `HyperionTargets.cmake`.

---

## Клієнтський проєкт-споживач

Створимо ізольований клієнтський проєкт `consumer_app`, який використовує нашу бібліотеку виключно через механізм `find_package()`.

### Файл опису збірки `examples/consumer_app/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.20)
project(ConsumerApp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пошук встановленої бібліотеки в режимі конфігурації
find_package(Hyperion 1.2 REQUIRED CONFIG)

add_executable(consumer_app main.cpp)

# Лінкування з імпортованими цілями простору імен Hyperion::
target_link_libraries(consumer_app
    PRIVATE
        Hyperion::core
        Hyperion::math
)
```

### Вихідний код клієнта `examples/consumer_app/main.cpp`

Клієнтський код використовує обидва компоненти: скомпільований клас `Engine` та шаблонну заголовочну функцію `accumulate_span`:

```cpp
#include <iostream>
#include <array>
#include <hyperion/core.hpp>
#include <hyperion/math.hpp>

int main() {
    hyperion::Engine engine("TelemetryAlpha");
    
    constexpr std::array<double, 4> metrics = {10.5, 20.25, 5.75, 3.5};
    double total = hyperion::math::accumulate_span<double>(metrics);
    
    std::string payload = "SensorData:Total=" + std::to_string(total);
    uint32_t checksum = engine.compute_hash(payload);
    
    std::cout << "Engine: " << engine.name() << "\n";
    std::cout << "Metrics sum: " << total << "\n";
    std::cout << "Payload hash: 0x" << std::hex << checksum << std::dec << "\n";
    
    return 0;
}
```

---

## Компіляція споживача та перевірка переміщуваності

Сконфігуруємо та запустимо програму споживача, передавши шлях до префікса інсталяції через змінну `CMAKE_PREFIX_PATH`:

```bash
# 1. Конфігурація споживача
cmake -B build-consumer -S examples/consumer_app \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=/tmp/hyperion-dist

# 2. Збірка виконуваного файла
cmake --build build-consumer

# 3. Запуск зібраної програми
./build-consumer/consumer_app
```

Результат виконання програми:
```text
Engine: TelemetryAlpha
Metrics sum: 40
Payload hash: 0x6e7b1a2f
```

### Демонстрація переміщуваності (Relocation Test)

Найсуворішою перевіркою коректності генерації пакета є тест фізичного переміщення каталогу інсталяції в нове місце у файловій системі. Якщо в конфігураційних файлах залишився хоча б один жорсткий абсолютний шлях, повторна збірка споживача завершиться помилкою.

Виконаємо переміщення:

```bash
# Перемістимо каталог інсталяції в абсолютно інший каталог
mv /tmp/hyperion-dist /tmp/hyperion-relocated

# Сконфігуруємо споживача з новим шляхом (використовуючи --fresh для скидання кешу)
cmake -B build-consumer-relocated -S examples/consumer_app \
    --fresh \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=/tmp/hyperion-relocated

# Зберемо та запустимо програму
cmake --build build-consumer-relocated
./build-consumer-relocated/consumer_app
```

Збірка та запуск виконуються бездоганно. Це на практиці доводить, що система динамічного обчислення `_IMPORT_PREFIX` у згенерованому `HyperionTargets.cmake` та макрос `@PACKAGE_INIT@` у `HyperionConfig.cmake` повністю ізолюють пакет від структури файлової системи машини збірки.

---

## Аналіз діагностики та крайових випадків

Розглянемо типові поведінкові сценарії системи збірки під час зміни конфігурації клієнта:

1. **Запит несумісної версії:**
   Якщо споживач змінить виклик на `find_package(Hyperion 2.0.0 REQUIRED CONFIG)`, генератор звернеться до `HyperionConfigVersion.cmake`, порівняє мажорну версію `2` з поточною `1.2.0` і зупинить конфігурацію з чітким діагностичним повідомленням:
   ```text
   Could not find a configuration file for package "Hyperion" that is compatible with requested version "2.0.0".
   The following configuration files were considered but not accepted:
     /tmp/hyperion-relocated/lib/cmake/Hyperion/HyperionConfig.cmake, version: 1.2.0
   ```
2. **Зневадження пошуку через CMAKE_FIND_DEBUG_MODE:**
   Якщо клієнтський проєкт не знаходить пакет, запуск із діагностикою показує повний перелік перевірених шляхів:
   ```bash
   cmake -B build-debug -S examples/consumer_app --debug-find-pkg=Hyperion
   ```
   Це дозволяє миттєво побачити, чи враховано змінну `CMAKE_PREFIX_PATH` і за якими саме префіксами шукався файл `HyperionConfig.cmake`.

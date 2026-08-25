# ⚙️ Рефакторинг застарілого CMakeLists.txt: покроковий перехід до Modern CMake

У практичній інженерній роботі застарілий код системи збірки рідко з'являється у вигляді одного ізольованого рядка. Зазвичай це комплексна, заплутана спадщина попередніх розробників: змішування глобальних прапорців, небезпечні макроси, зашиті шляхи до файлової системи та сліпе збирання файлів через маски.

Нижче розглянуто повний практичний кейс: аналіз реального проєкту бібліотеки обробки зображень `ImageProcessor` із консольною утилітою `imgcli`, покрокова деконструкція семи застарілих антипатернів, інтеграція сучасних засобів санітайзерів та статичного аналізу, а також перетворення кодової бази на надійний, модульний проєкт стандарту Modern CMake.

## Початковий стан: моноліт антипатернів

Розглянемо фізичну структуру каталогів проєкту:

```
image_processor/
├── CMakeLists.txt
├── include/
│   └── imgproc/
│       └── filter.h
├── src/
│   ├── filter.cpp
│   ├── internal_simd.h
│   └── internal_simd.cpp
└── app/
    └── main.cpp
```

Початковий файл `CMakeLists.txt` був створений багато років тому за канонами CMake 2.8:

```cmake
# ❌ Застарілий CMakeLists.txt із комплексом антипатернів
cmake_minimum_required(VERSION 2.8)
project(image_processor)

# Антипатерн 1: Відсутність захисту від складання в сирцях
# Антипатерн 2: Ручна конкатенація глобальних прапорців компілятора
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -O3 -Wall")

# Антипатерн 3: Примусове знищення значень кешу
set(ENABLE_OPENMP ON CACHE BOOL "Увімкнути OpenMP" FORCE)

# Антипатерн 4: Збір файлів через GLOB_RECURSE
file(GLOB_RECURSE LIB_SOURCES "src/*.cpp")
file(GLOB_RECURSE APP_SOURCES "app/*.cpp")

# Антипатерн 5: Глобальні директиви каталогу та зашиті системні шляхи
include_directories(include src /usr/local/include)
add_definitions(-DIMGPROC_EXPORTS)
link_directories(/usr/local/lib)

# Антипатерн 6: Небезпечний макрос із витоком змінних
macro(add_filter_target TARGET_NAME)
    set(TEMP_DIR "generated_${TARGET_NAME}")
    add_custom_target("${TARGET_NAME}_meta" COMMAND echo "Building ${TARGET_NAME}")
endmacro()

add_filter_target(imgproc)

# Антипатерн 7: Глобальне лінкування без контролю видимості
add_library(imgproc STATIC ${LIB_SOURCES})
add_executable(imgcli ${APP_SOURCES})
link_libraries(pthread m)
target_link_libraries(imgcli imgproc)
```

### Чому ця конфігурація є аварійно небезпечною

Спроба роботи з таким проєктом у сучасному середовищі розробки швидко виявляє критичні вади:

1. **Забруднення робочої копії Git.** Якщо новачок виконає команду `cmake .` у корені проєкту, файлова система буде засмічена десятками тимчасових файлів `CMakeFiles/`, `CMakeCache.txt` та бінарних файлів Make/Ninja, які перекриють можливість створення окремих папок під налагоджувальні збірки.
2. **Сліпота генератора збірки до нових файлів.** Якщо додати у `src/` новий файл `src/blur.cpp` і запустити `ninja`, утиліта збірки не знатиме про появу файлу, бо часова мітка `CMakeLists.txt` не змінювалася. Лінкер впаде з помилкою відсутності символів.
3. **Неможливість збирання під різними компіляторами.** Прапорці `-std=c++17 -Wall -O3` є специфічними для GCC та Clang. Компілятор Microsoft Visual Studio (MSVC) видасть помилку на невідомі прапорці або проігнорує стандарт C++17.
4. **Блокування налагоджувальних режимів.** Жорсткий прапорець `-O3` змушує компілятор оптимізувати бінарний код навіть тоді, коли користувач викликає `cmake -DCMAKE_BUILD_TYPE=Debug`, унеможливлюючи покрокове налагодження в `gdb` або `lldb`.
5. **Неможливість конфігурації через CI.** Передача аргументу `-DENABLE_OPENMP=OFF` у командному рядку не матиме жодного ефекту: прапорець `FORCE` у файлі `CMakeLists.txt` примусово поверне значення `ON` під час кожного запуску конфігурації.
6. **Порушення модульної інкапсуляції.** Додавання папки `src` до глобального `include_directories` дозволяє коду утиліти `app/main.cpp` випадково підключити внутрішній файл `internal_simd.h`, який є приватною деталлю реалізації бібліотеки.
7. **Мутація змінних через макрос.** Виклик `add_filter_target` безповоротно затирає змінну `TEMP_DIR` у контексті того, хто його викликав, спричиняючи приховані баги в наступних рядках коду.

---

## Покроковий план рефакторингу

Для ліквідації дефектів виконаємо послідовну трансформацію конфігураційного файлу з детальним аналізом кожного кроку.

### Крок 1. Підняття версії та блокування збірок у дереві джерел

Встановлюємо актуальну версію стандарту та впроваджуємо апаратну заборону in-source збірок на самому початку файлу, до виклику `project()`:

```cmake
cmake_minimum_required(VERSION 3.20...3.30)
project(ImageProcessor 
    VERSION 1.2.0 
    LANGUAGES CXX
    DESCRIPTION "Сучасна бібліотека обробки зображень"
)

# Апаратне блокування in-source збірки
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR 
        "❌ In-source збірка суворо заборонена!\n"
        "CMake згенерував службові файли всередині дерева сирців.\n"
        "Створіть окремий каталог: cmake -B build"
    )
endif()
```

### Крок 2. Безпечне декларування опцій без FORCE

Замінюємо директиву примусового запису в кеш на команду `option()`. Це дозволяє зовнішнім системам (CI, скриптам тестування, пакетним менеджерам) безпечно керувати прапорцями з командного рядка:

```cmake
# Декларування опцій, відкритих для перевизначення користувачем
option(IMGPROC_ENABLE_OPENMP "Увімкнути багатопотокову оптимізацію OpenMP" ON)
option(IMGPROC_ENABLE_ASAN "Увімкнути AddressSanitizer для пошуку витоків пам'яті" OFF)
option(BUILD_TESTING "Збирати модульні тести проєкту" OFF)
```

### Крок 3. Перетворення макросу на функцію з локальною областю видимості

Замінюємо текстовий макрос `macro()` на функцію `function()`. Будь-які допоміжні змінні всередині функції стають локальними для поточного стек-фрейму і знищуються при поверненні:

```cmake
function(imgproc_add_filter_metadata target_name)
    cmake_parse_arguments(ARG "" "STAGE" "" ${ARGN})
    
    # Змінна temp_meta_dir є строго локальною для стек-фрейму цієї функції
    set(temp_meta_dir "${CMAKE_CURRENT_BINARY_DIR}/meta_${target_name}")
    
    add_custom_target("${target_name}_metadata"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${temp_meta_dir}"
        COMMENT "Формування метаданих фільтра для ${target_name}"
        VERBATIM
    )
endfunction()
```

### Крок 4. Створення цілі бібліотеки з явними джерелами та вимогами вжитку

Відмовляємося від небезпечного `file(GLOB)` на користь явного переліку файлів. Прив'язуємо стандарт C++, шляхи до заголовків та макроси виключно до створеної цілі `imgproc`:

```cmake
# Створюємо ціль бібліотеки з явним списком сирців
add_library(imgproc STATIC
    src/filter.cpp
    src/internal_simd.cpp
)

# Оголошуємо псевдонім у просторі імен для внутрішніх споживачів
add_library(ImageProcessor::imgproc ALIAS imgproc)

# Задаємо вимогу до стандарту мови C++
target_compile_features(imgproc PUBLIC cxx_std_17)

# Розподіляємо видимість шляхів заголовків
target_include_directories(imgproc
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Приватний макрос, потрібний лише самій бібліотеці
target_compile_definitions(imgproc
    PRIVATE
        IMGPROC_EXPORTS
)

# Компіляторо-незалежні прапорці діагностики
target_compile_options(imgproc PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
        -Wall -Wextra -Wpedantic -Wconversion
    >
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4 /permissive-
    >
)

# Підключення AddressSanitizer через властивості цілі
if(IMGPROC_ENABLE_ASAN)
    target_compile_options(imgproc PRIVATE
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined -fno-omit-frame-pointer>
    )
    target_link_options(imgproc PUBLIC
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined>
    )
endif()

# Підключення OpenMP як імпортованої цілі
if(IMGPROC_ENABLE_OPENMP)
    find_package(OpenMP REQUIRED)
    target_link_libraries(imgproc PUBLIC OpenMP::OpenMP_CXX)
endif()
```

### Крок 5. Створення виконуваного файлу та лінкування

Консольна програма `imgcli` лінкується з бібліотекою через `ImageProcessor::imgproc`. Вона автоматично успадковує публічні заголовки `include/imgproc/filter.h`, вимогу стандарту C++17 та прапорці OpenMP, але не бачить внутрішньої папки `src/` та не отримує прапорець `IMGPROC_EXPORTS`:

```cmake
add_executable(imgcli
    app/main.cpp
)

target_link_libraries(imgcli PRIVATE
    ImageProcessor::imgproc
)
```

---

## Фінальний чистий результат: `CMakeLists.txt`

Зібравши всі оновлені компоненти, отримуємо чистий, переносимий та стійкий до помилок проєктний файл:

```cmake
cmake_minimum_required(VERSION 3.20...3.30)
project(ImageProcessor
    VERSION 1.2.0
    LANGUAGES CXX
    DESCRIPTION "Бібліотека обробки зображень, побудована за канонами Modern CMake"
)

# 1. Захист від збирання у дереві сирців
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "Збірка всередині сирців заборонена! Використовуйте cmake -B build")
endif()

# 2. Опції конфігурації
option(IMGPROC_ENABLE_OPENMP "Увімкнути паралелізм OpenMP" ON)
option(IMGPROC_ENABLE_ASAN "Увімкнути AddressSanitizer" OFF)
option(BUILD_TESTING "Збирати юніт-тести" OFF)

# 3. Службові функції (замість макросів)
function(imgproc_add_filter_metadata target_name)
    set(temp_meta_dir "${CMAKE_CURRENT_BINARY_DIR}/meta_${target_name}")
    add_custom_target("${target_name}_metadata"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${temp_meta_dir}"
        COMMENT "Генерація метаданих для ${target_name}"
        VERBATIM
    )
endfunction()

# 4. Основна ціль бібліотеки
add_library(imgproc STATIC
    src/filter.cpp
    src/internal_simd.cpp
)
add_library(ImageProcessor::imgproc ALIAS imgproc)

target_compile_features(imgproc PUBLIC cxx_std_17)

target_include_directories(imgproc
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_definitions(imgproc
    PRIVATE
        IMGPROC_EXPORTS
)

target_compile_options(imgproc PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
        -Wall -Wextra -Wpedantic
    >
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4 /permissive-
    >
)

if(IMGPROC_ENABLE_ASAN)
    target_compile_options(imgproc PRIVATE
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined -fno-omit-frame-pointer>
    )
    target_link_options(imgproc PUBLIC
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined>
    )
endif()

if(IMGPROC_ENABLE_OPENMP)
    find_package(OpenMP REQUIRED)
    target_link_libraries(imgproc PUBLIC OpenMP::OpenMP_CXX)
endif()

imgproc_add_filter_metadata(imgproc)

# 5. Виконуваний файл додатку
add_executable(imgcli
    app/main.cpp
)

target_link_libraries(imgcli PRIVATE
    ImageProcessor::imgproc
)
```

---

## Вихідний код компонентів проєкту

Для перевірки функціонування підготуємо мінімальні вихідні файли компонентів:

:::tabs
```cpp
// include/imgproc/filter.h
#pragma once
#include <vector>
#include <cstdint>

namespace imgproc {

class Filter {
public:
    static void apply_grayscale(std::vector<uint8_t>& image_buffer);
};

} // namespace imgproc
```
:::

:::tabs
```cpp
// src/filter.cpp
#include "imgproc/filter.h"
#include "internal_simd.h"
#include <iostream>

namespace imgproc {

void Filter::apply_grayscale(std::vector<uint8_t>& image_buffer) {
    internal::simd_process_rgb(image_buffer.data(), image_buffer.size());
    std::cout << "Фільтр успішно застосовано до " << image_buffer.size() << " байтів." << std::endl;
}

} // namespace imgproc
```
:::

:::tabs
```cpp
// src/internal_simd.h
#pragma once
#include <cstddef>
#include <cstdint>

namespace imgproc::internal {

void simd_process_rgb(uint8_t* data, size_t size);

} // namespace imgproc::internal
```
:::

:::tabs
```cpp
// src/internal_simd.cpp
#include "internal_simd.h"

namespace imgproc::internal {

void simd_process_rgb(uint8_t* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        data[i] = static_cast<uint8_t>(data[i] * 0.9f);
    }
}

} // namespace imgproc::internal
```
:::

:::tabs
```cpp
// app/main.cpp
#include <imgproc/filter.h>
#include <vector>
#include <iostream>

int main() {
    std::vector<uint8_t> test_pixels(1024, 128);
    imgproc::Filter::apply_grayscale(test_pixels);
    std::cout << "Роботу програми завершено штатно." << std::endl;
    return 0;
}
```
:::

---

## Валідація, перевірка та діагностика

Складання проєкту та перевірка виконаних змін здійснюються стандартними командами Modern CMake:

```bash
# Конфігурація проєкту в окремому каталозі
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release

# Компіляція та лінкування з використанням усіх доступних ядер
cmake --build build -j $(nproc)

# Запуск згенерованого додатку
./build/imgcli
```

### Перевірка поведінки системи після рефакторингу

1. **Ізоляція сирців від артефактів збірки:** Каталог вихідного коду залишається абсолютно чистим. Для повного видалення всіх продуктів компіляції та тимчасового кешу достатньо виконати одну команду `rm -rf build`.
2. **Чутливість до змін файлової системи:** Якщо створити новий файл `src/blur.cpp` і додати його у список вихідних файлів цілі `imgproc`, утиліта `ninja` автоматично оновить граф збірки та перекомпілює проєкт без потреби у примусовій повторній ініціалізації.
3. **Архітектурна інкапсуляція:** Спроба додати рядок `#include "internal_simd.h"` у файл `app/main.cpp` негайно призведе до помилки компіляції `fatal error: internal_simd.h: No such file or directory`, оскільки приватні каталоги бібліотеки не поширюються на зовнішні цілі.
4. **Контроль інструментів динамічного аналізу:** Увімкнення опції AddressSanitizer через прапорець `cmake -B build -DIMGPROC_ENABLE_ASAN=ON` надійно додає необхідні прапорці інструментування до компілятора та лінкера для всіх пов'язаних цілей, не вимагаючи ручного редагування глобальних прапорців `CMAKE_CXX_FLAGS`.
5. **Діагностика через Graphviz:** Для візуальної перевірки правильності створеного графу залежностей достатньо запустити команду `cmake -B build --graphviz=build/graph.dot`, яка згенерує чітку схему цілей без паразитних глобальних зв'язків.

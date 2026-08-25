# ⚙️ Практика ізоляції політик у багаторівневих проєктах і модулях

У реальних проєктах системні інженери стикаються з проблемою неоднорідності: сучасний головний застосунок, написаний за стандартами CMake 3.28+, змушений включати до свого дерева сторонні підпроєкти (vendor dependencies), розроблені для CMake 3.0–3.10, а також підключати власні допоміжні модулі пошуку залежностей. Без суворої ізоляції політик налаштування стороннього коду просочуються в головний проєкт, ламаючи генерацію цілей або спричиняючи сотні попереджень на CI.

Коли кілька компонентів із різними версійними вимогами компілюються в межах одного графа збірки, виникає конфлікт інтересів. Головний проєкт розраховує на сучасні правила обробки аргументів і властивостей, тоді як стара бібліотека всередині підкаталогу може покладатися на застарілу поведінку розбору лапок або автоматичний пошук вихідних файлів. Якщо головний проєкт спробує примусово підняти версію для всього дерева, застарілий підпроєкт впаде з помилками; якщо ж опустити версію головного проєкту — буде втрачено доступ до таргет-орієнтованих абстракцій та генераторних виразів.

Нижче наведено робочу інженерну архітектуру проєкту, яка демонструє повноцінне вирішення цієї проблеми: автоматичну ізоляцію політик на рівні підкаталогів, безпечний модуль пошуку через стек `PUSH`/`POP` та роботу з легасі-опціями за сучасною політикою `CMP0077`.

## Архітектура та структура файлів проєкту

Проєкт складається з трьох ключових рівнів: кореневого застосунку, допоміжного модуля пошуку обладнання у папці `cmake/` та сторонньої застарілої бібліотеки стиснення даних `legacy_codec`, розміщеної у `third_party/`.

```
system_app/
├── CMakeLists.txt
├── cmake/
│   └── FindSensorEngine.cmake
├── third_party/
│   └── legacy_codec/
│       ├── CMakeLists.txt
│       ├── codec.h
│       └── codec.c
└── src/
    └── main.cpp
```

## 1. Головний CMakeLists.txt: керування політиками та діапазони

Головний файл декларує сучасний діапазон версій `3.20...3.30`. Це гарантує стан `NEW` для всіх актуальних політик, включно з `CMP0077` (повага до локальних змінних в `option()`), `CMP0054` (строгий розбір лапок у виразах `if`) та `CMP0115` (обов'язкові явні розширення файлів у цілях).

Зверніть увагу на порядок викликів: спочатку оголошуються локальні змінні для конфігурування підпроєкту, потім підключається підкаталог, і лише після цього завантажується власний модуль пошуку. Завдяки ізоляції областей видимості кожна стадія виконується у власному контрольованому середовищі.

```cmake
cmake_minimum_required(VERSION 3.20...3.30)
project(SystemApp VERSION 2.4.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Перевизначення опцій підпроєкту до виклику add_subdirectory.
# Завдяки політиці CMP0077 (NEW) підпроєкт не перезапише це значення у кеші.
set(CODEC_ENABLE_TESTS OFF)
set(CODEC_ENABLE_LOGGING ON)

# 2. Підключення легасі-підпроєкту.
# CMake автоматично створює ізольовану копію стека політик для каталогу third_party/legacy_codec.
add_subdirectory(third_party/legacy_codec)

# 3. Підключення власного модуля пошуку.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(SensorEngine REQUIRED)

# 4. Головний виконуваний файл.
add_executable(system_app src/main.cpp)
target_link_libraries(system_app PRIVATE legacy_codec SensorEngine::SensorEngine)
```

## 2. Підпроєкт legacy_codec: автономний стек політик

Файл `third_party/legacy_codec/CMakeLists.txt` являє собою типову бібліотеку минулого десятиліття, написану під CMake 3.5. Він викликає власний `cmake_minimum_required(VERSION 3.5)`, що знижує версійний рівень політик лише всередині цього каталогу.

Коли підпроєкт виконує команду `option(CODEC_ENABLE_TESTS "..." ON)`, інтерпретатор перевіряє поточний стан політики `CMP0077`. Оскільки в кореневому проєкті було встановлено версійний зріз 3.20+, політика `CMP0077` перебуває у стані `NEW`. Інтерпретатор бачить звичайну змінну `CODEC_ENABLE_TESTS`, попередньо виставлену батьком у значення `OFF`, і м'яко пропускає запис у кеш. Як результат — непотрібні юніт-тести сторонньої бібліотеки не додаються до загального плану компіляції.

```cmake
cmake_minimum_required(VERSION 3.5)
project(LegacyCodec LANGUAGES C)

# Якщо головний проєкт задав CODEC_ENABLE_TESTS як звичайну змінну,
# за активної CMP0077 ця команда нічого не зробить і збереже OFF.
option(CODEC_ENABLE_TESTS "Build internal unit tests for legacy codec" ON)
option(CODEC_ENABLE_LOGGING "Enable verbose stderr logging" OFF)

add_library(legacy_codec STATIC codec.c)
target_include_directories(legacy_codec PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")

if(CODEC_ENABLE_LOGGING)
  target_compile_definitions(legacy_codec PRIVATE CODEC_VERBOSE=1)
endif()

if(CODEC_ENABLE_TESTS)
  message(STATUS "Legacy codec tests are ENABLED")
else()
  message(STATUS "Legacy codec tests are DISABLED by parent project")
endif()
```

## 3. Безпечний модуль FindSensorEngine.cmake зі стеком PUSH/POP

Модулі, які підключаються через `include()` або `find_package()`, виконуються в поточному контексті викликача. Якщо модуль всередині себе виконує `cmake_policy(SET ...)` або викликає старі скрипти, це може непередбачувано спотворити поведінку наступних рядків коду кореневого `CMakeLists.txt`.

Щоб гарантувати повну ізоляцію, модуль відкривається командою `cmake_policy(PUSH)` і обов'язково завершується командою `cmake_policy(POP)`. Це фіксує вихідний стан стека політик, дозволяє модулю безпечно виставити потрібні йому правила (наприклад, суворий синтаксис `CMP0054` або сучасний пошук шляхів за `CMP0144`), а потім чисто повернути керування викликачу.

```cmake
# cmake/FindSensorEngine.cmake
# Захист стека політик викликача:
cmake_policy(PUSH)

# Модуль вимагає строгої поведінки розбору лапок за CMP0054 та нових шляхів коренів за CMP0144:
cmake_policy(SET CMP0054 NEW)
if(POLICY CMP0144)
  cmake_policy(SET CMP0144 NEW)
endif()

find_path(SENSOR_ENGINE_INCLUDE_DIR
  NAMES sensor_engine.hpp sensor_engine.h
  PATHS /opt/sensors/include /usr/local/include
)

find_library(SENSOR_ENGINE_LIBRARY
  NAMES sensor_engine
  PATHS /opt/sensors/lib /usr/local/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(SensorEngine
  DEFAULT_MSG
  SENSOR_ENGINE_LIBRARY
  SENSOR_ENGINE_INCLUDE_DIR
)

if(SensorEngine_FOUND AND NOT TARGET SensorEngine::SensorEngine)
  add_library(SensorEngine::SensorEngine UNKNOWN IMPORTED)
  set_target_properties(SensorEngine::SensorEngine PROPERTIES
    IMPORTED_LOCATION "${SENSOR_ENGINE_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${SENSOR_ENGINE_INCLUDE_DIR}"
  )
endif()

# Обов'язкове відновлення стека викликача наприкінці модуля:
cmake_policy(POP)
```

## 4. Вихідний код компонентів

Нижче наведено вихідний код бібліотеки кодування та головного застосунку, що ілюструє безшовне поєднання компонентів мовами C та C++. Завдяки таргет-орієнтованим властивостям заголовочні файли мови C автоматично стають доступними для C++ компонентів без глобальних шляхів пошуку.

Заголовковий файл кодека з підтримкою C++ зв'язування:

:::tabs
```c
/* third_party/legacy_codec/codec.h */
#ifndef CODEC_H
#define CODEC_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

int legacy_encode(const char *input, size_t input_len, char *output, size_t max_out);

#ifdef __cplusplus
}
#endif

#endif /* CODEC_H */
```
```cpp
// third_party/legacy_codec/codec.hpp — C++ інтерфейс-обгортка
#pragma once
#include <string_view>
#include <span>
#include <vector>
#include <cstdint>

extern "C" {
#include "codec.h"
}

namespace legacy {
inline std::vector<char> encode(std::string_view input) {
    std::vector<char> buffer(input.size() * 2 + 16);
    int written = legacy_encode(input.data(), input.size(), buffer.data(), buffer.size());
    if (written >= 0) {
        buffer.resize(static_cast<size_t>(written));
    } else {
        buffer.clear();
    }
    return buffer;
}
} // namespace legacy
```
:::

Реалізація механізму побайтового кодування:

:::tabs
```c
/* third_party/legacy_codec/codec.c */
#include "codec.h"
#include <stdio.h>
#include <string.h>

int legacy_encode(const char *input, size_t input_len, char *output, size_t max_out) {
    if (!input || !output || max_out < input_len + 1) {
        return -1;
    }
#ifdef CODEC_VERBOSE
    fprintf(stderr, "[codec] Encoding %zu bytes of stream\n", input_len);
#endif
    for (size_t i = 0; i < input_len; ++i) {
        output[i] = (char)(input[i] ^ 0x5A);
    }
    output[input_len] = '\0';
    return (int)input_len;
}
```
```cpp
// third_party/legacy_codec/codec_impl.cpp — еквівалентна C++ реалізація
#include "codec.h"
#include <iostream>
#include <algorithm>

extern "C" int legacy_encode(const char *input, size_t input_len, char *output, size_t max_out) {
    if (!input || !output || max_out < input_len + 1) {
        return -1;
    }
#ifdef CODEC_VERBOSE
    std::cerr << "[codec] Encoding " << input_len << " bytes of stream\n";
#endif
    std::transform(input, input + input_len, output, [](char c) {
        return static_cast<char>(c ^ 0x5A);
    });
    output[input_len] = '\0';
    return static_cast<int>(input_len);
}
```
:::

Головна програма `src/main.cpp`, яка використовує як спільну бібліотеку кодування, так і знайдений модуль сенсорів:

```cpp
// src/main.cpp
#include <iostream>
#include <string_view>
#include <vector>
#include "codec.h"

int main() {
    std::string_view raw_payload = "Telemetry_Packet_0x89A";
    std::vector<char> encoded(raw_payload.size() + 1);

    int status = legacy_encode(raw_payload.data(), raw_payload.size(),
                               encoded.data(), encoded.size());

    if (status >= 0) {
        std::cout << "Successfully encoded payload. Size: " << status << " bytes\n";
    } else {
        std::cerr << "Encoding failed!\n";
        return 1;
    }
    return 0;
}
```

## 5. Перевірка результатів конфігурації у терміналі

Коли користувач запускає процес генерації файлів збірки, інтерпретатор CMake демонструє точне виконання встановлених правил:

```text
-- The C compiler identification is GNU 13.2.0
-- The CXX compiler identification is GNU 13.2.0
-- Legacy codec tests are DISABLED by parent project
-- Found SensorEngine: /usr/local/lib/libsensor_engine.so
-- Configuring done (0.2s)
-- Generating done (0.0s)
-- Build files have been written to: /path/to/system_app/build
```

### Аналіз поведінки системи

1. **Перехоплення опції підпроєкту:** Повідомлення `Legacy codec tests are DISABLED by parent project` доводить, що завдяки активній політиці `CMP0077` (стан `NEW`) звичайна змінна викликача перешкодила повторній ініціалізації значення опції в кеші. Підпроєкт підхопив налаштування головного проєкту без ручного втручання.
2. **Відсутність паразитних попереджень:** Жодних скарг на застарілу семантику `CMP0054` чи `CMP0048` не з'явилося, оскільки сторонній підпроєкт отримав власну локальну копію стека, а модуль `FindSensorEngine.cmake` коректно зберіг і відновив стек викликача через пару `PUSH`/`POP`.
3. **Цілісність графа:** Головний виконуваний файл `system_app` успішно отримав властивості та прапорці від обох залежностей без взаємного конфлікту налаштувань компілятора.

## 6. Інтеграція через FetchContent та типові пастки

У сучасних проєктах сторонні підпроєкти дедалі частіше завантажуються динамічно під час конфігурації за допомогою модуля `FetchContent`. Важливо пам'ятати, як політики взаємодіють із цим механізмом:

Коли ви викликаєте `FetchContent_MakeAvailable(foo)`, модуль `FetchContent` всередині викликає команду `add_subdirectory()` для завантаженого вихідного коду. Це означає, що завантажений репозиторій автоматично отримує власну ізольовану область стека політик.

Проте якщо завантажена бібліотека застрягла на декларації `cmake_minimum_required(VERSION 2.8)`, вона може викликати попередження про десятки політик, що перебувають у стані `UNSET`. Щоб уникнути засмічення журналу збірки на CI без внесення правок у чужий код, головний проєкт може глобально виставити поведінку за замовчуванням:

```cmake
# Попереднє налаштування для сторонніх репозиторіїв у FetchContent:
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
set(CMAKE_POLICY_DEFAULT_CMP0048 NEW)

FetchContent_Declare(
  legacy_lib
  GIT_REPOSITORY https://example.com/legacy_lib.git
  GIT_TAG v1.4.2
)
FetchContent_MakeAvailable(legacy_lib)
```

Змінні `CMAKE_POLICY_DEFAULT_CMPxxxx` призначають бажаний стан політик саме для тих підпроєктів, де вони не налаштовані явно, дозволяючи будувати монолітні багаторівневі системи збірки із передбачуваним результатом.

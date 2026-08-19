# ⚙️ Практикум: налаштування PCH, автоматизація IWYU та діагностика у CMake

Коли кодова база C++ розростається до сотень трансляційних одиниць, ручне відстеження включень стає неможливим: розробники випадково додають важкі бібліотеки у базові заголовки, забувають необхідні директиви або накопичують сотні невикористовуваних включень. Для підтримки чистоти архітектури та високої швидкості інкрементальної збірки сучасні інженерні команди автоматизують три ключові процеси: попередню компіляцію стабільних заголовків (PCH), регулярний аудит залежностей (IWYU) та машинну верифікацію самодостатності кожного заголовкового файлу.

У цьому практичному посібнику розбирається наскрізна побудова конвеєра збірки на базі CMake та Ninja, де оптимізація часу трансляції поєднується з автоматизованим контролем якості заголовкових файлів.

---

## 1. Архітектура попередньо скомпільованих заголовків у CMake

Починаючи з версії CMake 3.16, підтримка попередньо скомпільованих заголовків (Precompiled Headers, PCH) є стандартизованою та вбудованою через команду `target_precompile_headers()`. Раніше розробники змушені були писати власні громіздкі макроси для передачі специфичних прапорців компіляторів: `/Yu` та `/Yc` для MSVC, `-include` та `-Winvalid-pch` для GCC, `-include-pch` для Clang. CMake уніфікував цю поведінку, самостійно генеруючи синтетичні файли заголовків та об'єктні контейнери дампу пам'яті (`.gch`, `.pch`).

### Внутрішня механіка генерації PCH у системі збірки

Коли CMake обробляє директиву `target_precompile_headers()`, він виконує таку послідовність низькорівневих операцій:

1. У каталозі збірки створюється проміжний файл `cmake_pch.hxx` (або `cmake_pch.h` для C), який містить послідовний перелік усіх указаних директив `#include`.
2. Компілятор викликається для трансляції `cmake_pch.hxx` в окремий бінарний артефакт AST:
   - У **GCC** створюється каталог `cmake_pch.hxx.gch`, всередині якого зберігається дамп пам'яті компілятора.
   - У **Clang** генерується серіалізований файл бінарного модуля `cmake_pch.hxx.pch`.
   - У **MSVC** компілюється допоміжний файл `cmake_pch.cxx` з прапорцем `/Yc"cmake_pch.hxx"`, що створює файл `cmake_pch.pch`.
3. Під час компіляції кожного вихідного файлу `.cpp` зазначеної цілі система збірки Ninja або Make автоматично інжектує препроцесорний прапорець примусового включення (`-include-pch` або `/Yu`), завантажуючи готовий дамп синтаксичного дерева в оперативну пам'ять за лічені мілісекунди без повторного парсингу вихідного тексту.

### Критерії відбору заголовків для PCH

Головне інженерне правило роботи з PCH: **у попередню компіляцію поміщають виключно стабільні зовнішні заголовки**, які не змінюються в процесі повсякденної розробки:

- **Стандартна бібліотека C++**: `<vector>`, `<string>`, `<string_view>`, `<memory>`, `<algorithm>`, `<unordered_map>`, `<map>`, `<chrono>`, `<functional>`, `<optional>`, `<variant>`.
- **Системні API операційної системи**: `<windows.h>`, `<unistd.h>`, `<sys/socket.h>`, `<fcntl.h>`.
- **Важкі сторонні бібліотеки**: `<fmt/format.h>`, `<nlohmann/json.hpp>`, `<boost/asio.hpp>`.

Якщо помилково помістити в PCH заголовок власного проєкту, який часто редагується програмістами, виникає зворотний ефект: будь-яка правка такого файлу інвалідує бінарний файл `cmake_pch.hxx.pch`, внаслідок чого система збірки змушена перекомпілювати 100% файлів проєкту з нуля.

### Повна конфігурація CMakeLists.txt з ізоляцією та перевикористанням PCH

```cmake
cmake_minimum_required(VERSION 3.20)
project(EngineCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Створення статичної бібліотеки ядра
add_library(core_lib STATIC
    src/UserSession.cpp
    src/Database.cpp
    src/Network.cpp
)

target_include_directories(core_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Оголошення попередньо скомпільованих заголовків для бібліотеки
target_precompile_headers(core_lib
    PRIVATE
        # Контейнери та утиліти STL
        <vector>
        <string>
        <string_view>
        <memory>
        <unordered_map>
        <map>
        <algorithm>
        <chrono>
        <functional>
        <optional>
        <variant>
        # Сторонні важкі заголовки
        <fmt/format.h>
)

# Використання спільного PCH між кількома цілями (REUSE_FROM)
add_executable(engine_app
    src/main.cpp
)

target_link_libraries(engine_app PRIVATE core_lib)

# Повторне використання вже згенерованого PCH від core_lib для уникнення дублювання
target_precompile_headers(engine_app REUSE_FROM core_lib)

# Тестовий бінарник, який також повторно використовує базовий PCH
add_executable(engine_tests
    tests/test_main.cpp
    tests/test_session.cpp
)
target_link_libraries(engine_tests PRIVATE core_lib)
target_precompile_headers(engine_tests REUSE_FROM core_lib)
```

### Пастки інвалідації кешу та прапорців компіляції

PCH надзвичайно чутливий до середовища компіляції. Бінарний образ AST залишається валідним лише за умови повної ідентичності прапорців між генерацією PCH та трансляцією цільового `.cpp` файлу:

- Будь-яка зміна макросів препроцесора через `-D` (наприклад, `-DDEBUG` проти `-DNDEBUG`) робить PCH непридатним.
- Зміна рівня оптимізації (`-O0` проти `-O3`) або версії стандарту C++ (`-std=c++17` проти `-std=c++20`) викликає фатальну помилку або тиху відмову від PCH з падінням швидкодії.
- Використання властивості `REUSE_FROM` вимагає, щоб ціль-джерело і ціль-споживач мали однаковий набір каталогів включення (`include_directories`) та сумісні прапорці компілятора.

---

## 2. Автоматизація Include What You Use (IWYU)

Інструмент `include-what-you-use` (IWYU) розроблено на основі бібліотек Clang Tooling. Він виконує повний обхід абстрактного синтаксичного дерева (AST), фіксуючи кожне використання типів, викликів функцій, розгортання шаблонів та звернень до макросів. Після цього IWYU зіставляє використані символи зі списком безпосередніх директив `#include` у файлі.

### Як працює аналізатор AST всередині IWYU

Під час обходу AST аналізатор класифікує використання сутностей за двома категоріями:

1. **Потреба у повному типі (Full Type Requirement)**:
   - Обчислення розміру (`sizeof(T)`), вирівнювання (`alignof(T)`).
   - Створення об'єкта як локальної змінної чи поля класу (`T obj;`).
   - Доступ до методів або полів класу (`ptr->method()`).
   - Успадкування (`class Derived : public T`).
   - У цих випадках IWYU вимагає наявності прямого `#include <T.h>`.

2. **Достатність неповного типу (Forward Declaration Sufficiency)**:
   - Оголошення покажчика чи посилання (`T*`, `T&`) у сигнатурі функції або полі класу.
   - Параметри та типи повернення у попередніх прототипах функцій.
   - У таких випадках IWYU пропонує видалити зайвий `#include` і замінити його попереднім оголошенням `class T;`.

### Налаштування карти трансляцій (.iwyu.imp)

Найбільша практична проблема IWYU — пропозиція включити внутрішні, нестандартні заголовки реалізації стандартної бібліотеки або фреймворків. Наприклад, у компіляторі GCC заголовок `<vector>` усередині розбитий на десятки службових файлів: `<bits/stl_vector.h>`, `<bits/stl_bvector.h>`, `<bits/stl_construct.h>`. Зустрівши тип `std::vector`, «наївний» аналізатор може порадити включити саме `<bits/stl_vector.h>`, що порушує переносимість і ламає збірку під іншими компіляторами.

Для зіставлення внутрішніх файлів з їхніми публічними інтерфейсами використовують файл мапінгу `.iwyu.imp`.

Створимо файл конфігурації `iwyu_mappings.imp`:

```json
[
  { "include": ["<bits/stl_vector.h>", "private", "<vector>", "public"] },
  { "include": ["<bits/stl_map.h>", "private", "<map>", "public"] },
  { "include": ["<bits/stl_tree.h>", "private", "<map>", "public"] },
  { "include": ["<bits/unique_ptr.h>", "private", "<memory>", "public"] },
  { "include": ["<bits/shared_ptr.h>", "private", "<memory>", "public"] },
  { "include": ["<bits/stdint-uintn.h>", "private", "<cstdint>", "public"] },
  { "include": ["<bits/chrono.h>", "private", "<chrono>", "public"] },
  { "include": ["@<boost/smart_ptr/.*>", "private", "<boost/smart_ptr.hpp>", "public"] },
  { "symbol": ["std::string", "private", "<string>", "public"] },
  { "symbol": ["std::string_view", "private", "<string_view>", "public"] },
  { "symbol": ["std::vector", "private", "<vector>", "public"] },
  { "symbol": ["std::unique_ptr", "private", "<memory>", "public"] },
  { "symbol": ["std::shared_ptr", "private", "<memory>", "public"] },
  { "symbol": ["std::make_unique", "private", "<memory>", "public"] },
  { "symbol": ["std::make_shared", "private", "<memory>", "public"] },
  { "symbol": ["std::size_t", "private", "<cstddef>", "public"] },
  { "symbol": ["uint32_t", "private", "<cstdint>", "public"] },
  { "symbol": ["int64_t", "private", "<cstdint>", "public"] }
]
```

### Інтеграція IWYU в систему збірки CMake

CMake дозволяє запускати IWYU прозоро під час кожної компіляції за допомогою цільової властивості `CXX_INCLUDE_WHAT_YOU_USE`:

```cmake
# Перевірка наявності програми IWYU в системі
find_program(IWYU_TOOL_PATH NAMES include-what-you-use iwyu)

option(ENABLE_IWYU "Увімкнути автоматичний аудит заголовків через IWYU" OFF)

if(IWYU_TOOL_PATH AND ENABLE_IWYU)
    message(STATUS "IWYU знайдено: ${IWYU_TOOL_PATH}")
    
    # Формування аргументів командного рядка для аналізатора
    set(IWYU_COMMAND_LINE
        "${IWYU_TOOL_PATH}"
        "-Xiwyu" "--mapping_file=${CMAKE_CURRENT_SOURCE_DIR}/iwyu_mappings.imp"
        "-Xiwyu" "--max_line_length=120"
        "-Xiwyu" "--no_fwd_decls"
        "-Xiwyu" "--verbose=1"
    )
    
    # Прив'язка аналізатора до бібліотеки
    set_target_properties(core_lib PROPERTIES
        CXX_INCLUDE_WHAT_YOU_USE "${IWYU_COMMAND_LINE}"
    )
endif()
```

### Скрипт автоматичного застосування правок IWYU

Для масового рефакторингу кодової бази використовують утиліту `fix_includes.py`. Скрипт зчитує діагностичний звіт IWYU і автоматично редагує вихідні файли, вставляючи пропущені директиви `#include`, видаляючи мертві включення та сортуючи список заголовків за алфавітом.

```python
#!/usr/bin/env python3
"""Скрипт запуску IWYU та автоматичного виправлення заголовків."""
import subprocess
import sys
import os

def run_iwyu_cleanup(build_dir, source_dir):
    compile_commands = os.path.join(build_dir, "compile_commands.json")
    if not os.path.exists(compile_commands):
        print(f"Помилка: {compile_commands} не знайдено! Зберіть проєкт із -DCMAKE_EXPORT_COMPILE_COMMANDS=ON")
        sys.exit(1)

    print("=== Крок 1: Запуск аналізу через iwyu_tool.py ===")
    iwyu_report_file = os.path.join(build_dir, "iwyu_report.txt")
    mapping_path = os.path.join(source_dir, "iwyu_mappings.imp")
    
    cmd = [
        "iwyu_tool.py",
        "-p", build_dir,
        "--",
        "-Xiwyu", f"--mapping_file={mapping_path}",
        "-Xiwyu", "--no_default_mappings"
    ]
    
    with open(iwyu_report_file, "w", encoding="utf-8") as out:
        subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, text=True)
    
    print(f"Звіт IWYU збережено у: {iwyu_report_file}")
    
    print("=== Крок 2: Автоматичне виправлення коду через fix_includes.py ===")
    with open(iwyu_report_file, "r", encoding="utf-8") as report:
        fix_cmd = [
            "fix_includes.py",
            "--comments",        # Додавати коментарі з назвами символів біля include
            "--safe_headers",   # Захищати системні заголовки від агресивного видалення
            "--reorder"         # Сортувати заголовки за канонічним порядком
        ]
        subprocess.run(fix_cmd, stdin=report, text=True)
    
    print("Очищення заголовків успішно завершено.")

if __name__ == "__main__":
    b_dir = sys.argv[1] if len(sys.argv) > 1 else "build"
    s_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    run_iwyu_cleanup(b_dir, s_dir)
```

---

## 3. Автоматична верифікація самодостатності заголовків (Header Self-Containment)

Правило самодостатності вимагає, щоб будь-який заголовковий файл успішно компілювався, якщо його включити першим у порожній `.cpp` файл. Порушення цього правила призводить до прихованих дефектів порядку включення, коли файл компілюється лише завдяки тому, що інший заголовок перед ним випадково імпортував потрібний тип.

### Підхід CMake 3.25+: `VERIFY_INTERFACE_HEADER_SETS`

Починаючи з CMake 3.25, система збірки надає штатний механізм контролю самодостатності заголовків через концепцію `FILE_SET`:

```cmake
# Оголошення публічного набору заголовків бібліотеки
target_sources(core_lib
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/UserSession.h
            include/Database.h
            include/Network.h
)

# Увімкнення автоматичної перевірки самодостатності
set_target_properties(core_lib PROPERTIES
    VERIFY_INTERFACE_HEADER_SETS ON
)
```

Під час генерації проєкту CMake автоматично створює у каталозі збірки тимчасові файли `UserSession.h.cxx`, `Database.h.cxx`, `Network.h.cxx`. Кожен із них містить рівно один рядок:

```cpp
#include "UserSession.h"
```

Якщо заголовок `UserSession.h` використовує `std::vector`, але забув директиву `#include <vector>`, компіляція згенерованого файлу `UserSession.h.cxx` негайно завершиться фатальною помилкою, запобігаючи потраплянню зламаного заголовка в репозиторій.

### Універсальний генератор перевірок для попередніх версій CMake

Для проєктів, які використовують CMake версій 3.15–3.24, аналогічну поведінку реалізують через користувацьку функцію:

```cmake
# Функція генерації автономних перевірочних одиниць
function(add_header_self_containment_test target_name header_files)
    set(test_sources "")
    
    foreach(hdr_path IN LISTS header_files)
        get_filename_component(hdr_base "${hdr_path}" NAME_WE)
        set(gen_cpp "${CMAKE_CURRENT_BINARY_DIR}/header_checks/test_${hdr_base}.cpp")
        
        # Генерація ізольованого файлу трансляції
        file(WRITE "${gen_cpp}"
            "// Автоматичний синтетичний тест самодостатності\n"
            "#include \"${hdr_path}\"\n"
            "int main() { return 0; }\n"
        )
        list(APPEND test_sources "${gen_cpp}")
    endforeach()

    # Створення тестового таргета
    add_executable(${target_name}_verify_headers EXCLUDE_FROM_ALL ${test_sources})
    target_link_libraries(${target_name}_verify_headers PRIVATE ${target_name})
    
    # Додавання кастомної команди до глобального списку перевірок
    add_custom_target(check_headers DEPENDS ${target_name}_verify_headers)
endfunction()
```

---

## 4. Пайплайн профілювання збірки в CI/CD: Clang -ftime-trace

Для запобігання випадковій деградації часу компіляції в процесі розробки команди впроваджують автоматичний аудит у систему неперервної інтеграції (CI/CD). Компілятор Clang з прапорцем `-ftime-trace` записує детальний хронометраж кожної операції фронтенду у форматі JSON.

### Реалізація CI-скрипту з аналізатором ClangBuildAnalyzer

Скрипт автоматично виконує чисту збірку проєкту з трасуванням, збирає всі файли `.json` та формує структурований звіт про найважчі заголовки та шаблони:

```python
#!/usr/bin/env python3
"""CI-скрипт діагностики часу збірки та агрегації результатів ftime-trace."""
import subprocess
import sys
import os
import shutil

def run_build_profiling(build_dir):
    print("=== Крок 1: Конфігурація та чиста збірка з -ftime-trace ===")
    os.makedirs(build_dir, exist_ok=True)
    
    # Генерація Ninja-проєкту з прапорцем трасування Clang
    cmake_cmd = [
        "cmake", "-B", build_dir, "-G", "Ninja",
        "-DCMAKE_CXX_COMPILER=clang++",
        "-DCMAKE_CXX_FLAGS=-ftime-trace",
        "-DCMAKE_BUILD_TYPE=Release"
    ]
    subprocess.run(cmake_cmd, check=True)
    
    # Повне очищення перед вимірюванням
    subprocess.run(["ninja", "-C", build_dir, "-t", "clean"], check=True)
    
    # Запуск повної збірки
    subprocess.run(["ninja", "-C", build_dir], check=True)
    
    print("=== Крок 2: Агрегація даних через ClangBuildAnalyzer ===")
    cba_binary = shutil.which("ClangBuildAnalyzer")
    if not cba_binary:
        print("Помилка: ClangBuildAnalyzer не знайдено у PATH!")
        sys.exit(1)
        
    trace_archive = os.path.join(build_dir, "build_trace_data.bin")
    
    # Збирання всіх окремих .json файлів трасування у бінарний архів
    subprocess.run([cba_binary, "--all", build_dir, trace_archive], check=True)
    
    # Генерація фінального текстового аналітичного звіту
    analysis = subprocess.run([cba_binary, "--analyze", trace_archive],
                              capture_output=True, text=True, check=True)
    
    report_output_path = os.path.join(build_dir, "build_speed_report.txt")
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(analysis.stdout)
        
    print(analysis.stdout)
    print(f"\nЗвіт профілювання збережено: {report_output_path}")

if __name__ == "__main__":
    run_build_profiling("build_profile_ci")
```

### Інтерпретація метрик звіту ClangBuildAnalyzer

Звіт аналізатора надає об'єктивні числові метрики, які вказують на конкретні вузькі місця кодової бази:

1. **Розділ «Top expensive headers»**: показує заголовки, сумарний час парсингу яких у всіх трансляційних одиницях є найбільшим. Якщо верхні рядки займають заголовки вашого проєкту, їх необхідно терміново оптимізувати через попередні оголошення (Forward Declarations) або розділити на дрібніші частини.
2. **Розділ «Top expensive template instantiations»**: показує конкретні шаблонні класи або функції, розгортання яких забирає найбільше часу процесора. Це прямий сигнал для використання техніки явного інстанціювання (`extern template`).
3. **Розділ «Files taking the longest to compile»**: перелічує файли `.cpp`, які гальмують паралельну збірку всієї системи.

---

## 5. Взаємодія PCH із Unity Builds у CMake

Для екстремального скорочення часу повної (clean) збірки у великих проєктах нерідко застосовують техніку Unity Builds (також відому як Jumbo Builds). Починаючи з CMake 3.16, ця техніка вмикається встановленням властивості `UNITY_BUILD ON`.

### Механіка об'єднання трансляційних одиниць

Замість компіляції кожного вихідного файлу `.cpp` окремим процесом компілятора, CMake автоматично генерує синтетичні файли `Unity_0_cxx.cxx`, `Unity_1_cxx.cxx`, кожен з яких містить прямі включення групи вихідних файлів проєкту:

```cpp
// Згенерований файл Unity_0_cxx.cxx
#include "E:/project/src/UserSession.cpp"
#include "E:/project/src/Database.cpp"
#include "E:/project/src/Network.cpp"
```

При такому підході спільні заголовкові файли, включені цими трьома вихідними файлами, парсяться компілятором лише **один раз на групу**, а не тричі. Поєднання PCH та Unity Build дозволяє досягти максимальної пропускної здатності процесора під час нічних чистих збірок у CI/CD.

```cmake
# Увімкнення комбінованого режиму PCH + Unity Build
set_target_properties(core_lib PROPERTIES
    UNITY_BUILD ON
    UNITY_BUILD_BATCH_SIZE 8
)
```

### Пастки та конфлікти Unity Builds

Незважаючи на колосальне прискорення чистої збірки, режим Unity Build несе серйозні архітектурні ризики, які вимагають суворої гігієни коду:

1. **Колізії імен в анонімних просторах (`unnamed namespaces`)**. Якщо два різні файли `A.cpp` та `B.cpp` визначають допоміжну функцію з однаковою назвою `helper()` всередині `namespace { ... }`, при їх об'єднанні в один Unity-файл виникає помилка повторного визначення символу (ODR violation).
2. **Витік локальних макросів**. Макрос `#define BUFFER_SIZE 1024`, оголошений у `A.cpp`, залишається активним під час компіляції наступного файлу `B.cpp` у тому самому Unity-блоці, створюючи непередбачувані побічні ефекти.
3. **Фальшива ілюзія самодостатності**. Файл `B.cpp` може випадково використовувати тип із `A.h`, не включаючи його явно, оскільки `A.h` уже був підключений попереднім файлом `A.cpp`. Поза Unity-збіркою такий файл не скомпілюється.

Для запобігання цим проблемам на локальних машинах розробників Unity Build зазвичай вимикають, залишаючи класичну роздільну компіляцію з PCH, а Unity вмикають виключно для релізних білдів.

---

## 6. Перехід до C++20 Модулів у CMake 3.28+: Динамічне сканування залежностей (dyndep)

Починаючи з версії CMake 3.28 та Ninja 1.11, система збірки підтримує повноцінний двофазний конвеєр трансляції C++20 Модулів за допомогою механізму **Ninja Dyndep** (Dynamic Dependencies).

### Чому модулі змінили архітектуру генератора збірки

У класичному C++ граф залежностей між файлами був статичним і визначався структурою каталогів. Компілятор міг паралельно компілювати всі `.cpp` файли в довільному порядку, оскільки заголовки `.h` підставлялися препроцесором на льоту.

У C++20 модулях з'явилася сувора **послідовність компіляції**: файл `Consumer.cpp`, який містить `import Core.Session;`, фізично не може почати компілюватися, поки компілятор не завершить трансляцію файлу інтерфейсу `Session.ixx` і не запише на диск двійковий файл інтерфейсу модуля (BMI: `.pcm` у Clang, `.ifc` у MSVC).

Для розв'язання цієї проблеми CMake та Ninja реалізують фазу динамічного сканування (`Scanning Phase`):

1. Ninja запускає швидкий сканер компілятора (`clang-scan-deps` або `/scanDependencies`) для всіх вихідних файлів.
2. Сканер повертає топологічний граф директив `export module` та `import module`.
3. Ninja динамічно оновлює внутрішній граф робіт без перезапуску CMake, забезпечуючи коректний порядок компіляції залежних модульних бінарників.

### Приклад конфігурації C++20 Модулів у CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.28)
project(ModularApp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(network_module)

# Оголошення інтерфейсних файлів C++20 модулів
target_sources(network_module
    PUBLIC
        FILE_SET CXX_MODULES
        BASE_DIRS src/modules
        FILES
            src/modules/Network.ixx
            src/modules/Session.ixx
    PRIVATE
        src/modules/NetworkImpl.cpp
)

add_executable(app_modular src/main.cpp)
target_link_libraries(app_modular PRIVATE network_module)
```

---

## 7. Практичні анотації IWYU в сирцевому коді

Під час роботи з IWYU виникають ситуації, коли аналізатор не може автоматично здогадатися про архітектурні наміри розробника — наприклад, при створенні фасадних бібліотек або роботі з платформозалежними макросами. Для точного керування поведінкою IWYU застосовують спеціальні коментарі-прагми.

### Захист фасадних заголовків: `// IWYU pragma: export`

Якщо заголовок `Engine.h` спроєктований як єдина точка входу до бібліотеки і навмисно реекспортує `Vector.h`, `Matrix.h` та `Transform.h`, аналізатор IWYU за замовчуванням вимагатиме від користувача включати внутрішні файли напряму. Прагма `export` повідомляє інструменту, що цей заголовок бере на себе транзитивну відповідальність:

```cpp
// include/Engine.h — фасадний заголовок підсистеми
#pragma once

// IWYU pragma: begin_exports
#include "Engine/Vector.h"
#include "Engine/Matrix.h"
#include "Engine/Transform.h"
// IWYU pragma: end_exports
```

### Захист неявних включень: `// IWYU pragma: keep`

Коли заголовок містить перевантаження операторів, спеціалізації шаблонів або дескриптори налагодження, які не викликаються явно за іменем символу, IWYU може помилково вважати заголовок мертвим і запропонувати його видалити. Директива `keep` блокує видалення:

```cpp
#include <spdlog/fmt/ostr.h> // IWYU pragma: keep — потрібен для перевантаження operator<<
#include "CustomPayload.h"
```

### Приховування внутрішніх заголовків: `// IWYU pragma: private`

Для внутрішніх заголовків підсистем, пряме підключення яких користувачем заборонено, вказують публічний заголовок-замінник:

```cpp
// include/Engine/Detail/MemoryPool.h
#pragma once
// IWYU pragma: private, include "Engine/Memory.h"

namespace Engine::Detail {
    class MemoryPool {};
}
```

---

## 8. Оптимізація пам'яті та дискового введення-виведення для PCH

Згенерований PCH-файл для важких бібліотек (таких як Boost або великі підсистеми GUI) часто сягає розміру 150–400 МБ. У високопаралельних збірках (наприклад, 32 або 64 потоки Ninja) одночасне зчитування гігантського файлу `cmake_pch.hxx.pch` створює колосальне навантаження на підсистему введення-виведення (I/O) диска.

### Розміщення PCH у віртуальній пам'яті (RAM-диск та tmpfs)

Для усунення дискових затримок та продовження ресурсу твердотільних накопичувачів (SSD) рекомендується розміщувати каталог проміжних файлів у оперативній пам'яті:

- **У Linux**: використання каталогу `/dev/shm` або монтаж каталогу збірки як `tmpfs`:
  ```bash
  sudo mount -t tmpfs -o size=8G tmpfs /path/to/project/build
  ```
- **У Windows**: використання сторонніх RAM-дисків або спеціалізованих кешуючих утиліт файлової системи (Dev Drive на базі ReFS з увімкненим CoW — Copy-on-Write).

Це знижує затримку доступу до серіалізованого синтаксичного дерева PCH з 5–10 мс до часток мікросекунди, забезпечуючи максимальну утилізацію процесорних ядер.

---

## 9. Налаштування CI-гейтів на регресію часу збірки

Навіть після ідеального рефакторингу кодова база схильна до поступової деградації: розробник може випадково додати важкий заголовок у спільний базовий клас заради одного виклику допоміжної функції. Для запобігання цьому в конвеєрі неперервної інтеграції (CI/CD) налаштовують автоматичні пороги перевірки (Performance Regression Gates):

1. **Поріг кількості токенів у трансляційній одиниці**: якщо середній розмір препроцесованого виходу (`.i`) зростає більш ніж на 15% у рамках одного Pull Request, CI видає попередження із зазначенням доданих заголовків.
2. **Поріг часу чистої та інкрементальної збірки**: скрипт порівнює звіт `ClangBuildAnalyzer` з еталонним звітом головної гілки `main`. Якщо час парсингу змінених файлів зріс понад ліміт (наприклад, на 1.5 секунди), збірка блокується до проведення рефакторингу залежностей.
3. **Автоматичний моніторинг глибини графа включень**: утиліти на зразок `gcc -H` або `ninja -t graph` дозволяють обчислити максимальну глибину транзитивних зв'язків. Якщо глибина ланцюга перевищує 12 рівнів, розробнику пропонується застосувати патерн Pimpl або винести залежності через Forward Declarations.

Практичні вимірювання показують, що впровадження такого автоматизованого конвеєра скорочує час повної збірки проєкту середнього розміру (близько 500 000 рядків коду) з 14 хвилин до 2 хвилин 40 секунд, а середній час інкрементальної збірки при зміні одного `.cpp` файлу стабілізується на рівні 0.8–1.2 секунди.

---

## 10. Порівняльна матриця технологій оптимізації збірки

| Критерій | Текстові заголовки | Precompiled Headers (PCH) | Unity Builds | C++20 Модулі (BMI) |
| :--- | :--- | :--- | :--- | :--- |
| **Швидкість чистої збірки (Clean Build)** | Найнижча (`O(N · M)`) | Висока (прискорення 3–5×) | Найвища (прискорення 5–10×) | Дуже висока (`O(N + M)`) |
| **Швидкість інкрементальної збірки** | Середня | Залежить від змін у PCH | Низька (перезбірка блоку) | Максимальна (O(1) для TU) |
| **Герметичність від макросів** | Відсутня | Відсутня (макроси витікають) | Відсутня (ризик колізій) | Повна (макроси ізольовані) |
| **Підтримка IDE та тулчейнів** | 100% універсальна | Повна (GCC, Clang, MSVC) | Повна (усі компілятори) | Активно зріє (CMake 3.28+) |
| **Вимоги до пам'яті компілятора** | Низькі | Помірні (100–300 МБ на PCH) | Високі (великі блоки AST) | Дуже низькі (компактний BMI) |

Впровадження описаного комплексу інструментів перетворює контроль залежностей зі стихійного ручного процесу на вимірювану, автоматизовану інженерну систему, гарантуючи стабільний час компіляції великих C++ проєктів протягом багатьох років.

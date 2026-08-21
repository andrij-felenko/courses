# ⚙️ Повний конвеєр тестування: фікстури, GoogleTest, Санітайзери та CI

Цей проект демонструє побудову надійного, повністю автоматизованого тестового конвеєра в CMake. Він поєднує модульне тестування на базі GoogleTest із динамічним опитуванням тестів, інтеграційне тестування з декларативними фікстурами життєвого циклу (підготовка й очищення сховища), конфігурацію адресного санітайзера (ASan) та автоматизовану генерацію звітів JUnit XML для CI/CD.

Тестова інфраструктура розв'язує три типові інженерні проблеми великих C++ систем:
1. **Ізоляція стану:** модульні тести перевіряють чисті функції в пам'яті, тоді як інтеграційні тести потребують зовнішнього сховища, створення якого та гарантоване видалення не повинні залежати від успіху окремих асертів.
2. **Точність діагностики:** заміна статичного аналізу коду на динамічне опитування бінарника гарантує, що жоден тест GoogleTest не буде пропущений через макроси чи шаблони.
3. **Безпека роботи з пам'яттю:** підключення санітайзерів (ASan/UBSan) дозволяє перехоплювати витоки пам'яті та виходи за межі масивів ще на етапі виконання тестів у CI, перериваючи процес із детальним трасуванням стека.

## Архітектурний дизайн тестового набору

У проєкті реалізовано дворівневу схему тестування:
- **Модульний рівень (Unit tests):** швидкі незалежні тести математичного ядра обчислювача. Вони не створюють файлів на диску, не відкривають сокетів і виконуються паралельно з максимальним пріоритетом. Для них підключається GoogleTest через модуль `FetchContent`.
- **Інтеграційний рівень (Integration tests):** перевірка довготривалого збереження даних на диск. Цей рівень залежить від зовнішнього файлового сховища. Замість ручного створення файлів перед запуском CMake або всередині кожного тесту, життєвий цикл сховища передано під контроль фікстур CTest.

Розподіл обов'язків гарантує, що навіть у разі падіння основного інтеграційного тесту через помилку сегментації або перевищення таймауту, тимчасові файли на диску будуть гарантовано видалені кроком очищення.

## Структура файлів проєкту

```
test_pipeline/
├── CMakeLists.txt
├── src/
│   ├── calculator.hpp
│   └── calculator.cpp
├── tests/
│   ├── unit/
│   │   └── test_calculator.cpp
│   ├── integration/
│   │   ├── db_fixture.cpp
│   │   └── test_storage.cpp
│   └── scripts/
│       └── run_ci.sh
```

## Головний файл конфігурації CMakeLists.txt

Файл описує ціль бібліотеки, вмикає опціональні прапорці компіляторних санітайзерів і реєструє тестові набори за допомогою сучасних команд CTest.

```cmake
cmake_minimum_required(VERSION 3.24)
project(EngineTests LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Опція збірки з адресним санітайзером та перевіркою UB
option(ENABLE_ASAN "Увімкнути AddressSanitizer та UndefinedBehaviorSanitizer" OFF)

if(ENABLE_ASAN)
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer -g)
        add_link_options(-fsanitize=address,undefined)
    endif()
endif()

# 1. Основна ціль бібліотеки
add_library(calc_engine STATIC src/calculator.cpp)
target_include_directories(calc_engine PUBLIC src)

# 2. Активація CTest у корені проєкту
include(CTest) # або enable_testing()

if(BUILD_TESTING)
    # Підключення GoogleTest через FetchContent
    include(FetchContent)
    FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
    )
    # Забороняємо GTest встановлювати свої заголовки у системні каталоги
    set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)

    include(GoogleTest)

    # ── Модульні тести (GoogleTest) ──────────────────────────────────────────
    add_executable(unit_tests tests/unit/test_calculator.cpp)
    target_link_libraries(unit_tests PRIVATE calc_engine GTest::gtest_main)

    # Динамічне опитування тестів після компіляції бінарника
    gtest_discover_tests(unit_tests
        PROPERTIES
            LABELS "unit"
            TIMEOUT 10
    )

    # ── Інтеграційні тести з декларативними фікстурами ────────────────────────
    add_executable(db_fixture_runner tests/integration/db_fixture.cpp)
    add_executable(storage_tests tests/integration/test_storage.cpp)
    target_link_libraries(storage_tests PRIVATE calc_engine)

    # Реєстрація етапу підготовки: створення тимчасової бази даних
    add_test(NAME db_setup
        COMMAND db_fixture_runner --setup "$<TARGET_FILE_DIR:storage_tests>/temp_db.dat"
    )
    set_tests_properties(db_setup PROPERTIES
        FIXTURES_SETUP "DatabaseFixture"
        LABELS "integration"
        TIMEOUT 15
    )

    # Реєстрація основного інтеграційного тесту, що читає створену БД
    add_test(NAME test_storage_read_write
        COMMAND storage_tests "$<TARGET_FILE_DIR:storage_tests>/temp_db.dat"
    )
    set_tests_properties(test_storage_read_write PROPERTIES
        FIXTURES_REQUIRED "DatabaseFixture"
        LABELS "integration"
        TIMEOUT 30
        COST 25.0
    )

    # Реєстрація обов'язкового очищення: видалення файлу БД навіть при аварії
    add_test(NAME db_cleanup
        COMMAND db_fixture_runner --cleanup "$<TARGET_FILE_DIR:storage_tests>/temp_db.dat"
    )
    set_tests_properties(db_cleanup PROPERTIES
        FIXTURES_CLEANUP "DatabaseFixture"
        LABELS "integration"
    )
endif()
```

## Реалізація модуля та модульних тестів

Бібліотека надає математичні функції з безпечною обробкою помилок через `std::expected` (або коди статусів у C) та операції файлового запису.

:::tabs
```cpp
// src/calculator.hpp
#pragma once
#include <string>
#include <expected>

namespace engine {

enum class MathError {
    DivisionByZero,
    Overflow
};

class Calculator {
public:
    [[nodiscard]] std::expected<double, MathError> divide(double a, double b) const noexcept;
    [[nodiscard]] bool write_record(const std::string& filepath, int key, double value) const;
};

} // namespace engine
```
```c
/* src/calculator.h (C-інтерфейс бібліотеки) */
#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CALC_OK = 0,
    CALC_ERR_DIV_BY_ZERO = 1,
    CALC_ERR_OVERFLOW = 2
} CalcStatus;

CalcStatus calc_divide(double a, double b, double* out_result);
bool calc_write_record(const char* filepath, int key, double value);

#ifdef __cplusplus
}
#endif

#endif
```
:::

:::tabs
```cpp
// src/calculator.cpp
#include "calculator.hpp"
#include <fstream>

namespace engine {

std::expected<double, MathError> Calculator::divide(double a, double b) const noexcept {
    if (b == 0.0) {
        return std::unexpected(MathError::DivisionByZero);
    }
    return a / b;
}

bool Calculator::write_record(const std::string& filepath, int key, double value) const {
    std::ofstream out(filepath, std::ios::app);
    if (!out) return false;
    out << key << ":" << value << "\n";
    return true;
}

} // namespace engine
```
```c
/* src/calculator.c (C-реалізація) */
#include "calculator.h"
#include <stdio.h>

CalcStatus calc_divide(double a, double b, double* out_result) {
    if (!out_result) return CALC_ERR_OVERFLOW;
    if (b == 0.0) return CALC_ERR_DIV_BY_ZERO;
    *out_result = a / b;
    return CALC_OK;
}

bool calc_write_record(const char* filepath, int key, double value) {
    FILE* f = fopen(filepath, "a");
    if (!f) return false;
    fprintf(f, "%d:%f\n", key, value);
    fclose(f);
    return true;
}
```
:::

### Модульні тести (GoogleTest)

Модульні тести перевіряють граничні випадки ділення на нуль та валідні розрахунки. Завдяки `gtest_discover_tests()` кожен виклик `TEST_F` реєструється як окремий тест у CTest.

```cpp
// tests/unit/test_calculator.cpp
#include <gtest/gtest.h>
#include "calculator.hpp"

class CalculatorTest : public ::testing::Test {
protected:
    engine::Calculator calc;
};

TEST_F(CalculatorTest, HandlesValidDivision) {
    auto res = calc.divide(10.0, 2.0);
    ASSERT_TRUE(res.has_value());
    EXPECT_DOUBLE_EQ(*res, 5.0);
}

TEST_F(CalculatorTest, RejectsDivisionByZero) {
    auto res = calc.divide(5.0, 0.0);
    ASSERT_FALSE(res.has_value());
    EXPECT_EQ(res.error(), engine::MathError::DivisionByZero);
}
```

### Допоміжний виконавець фікстур (Fixture Runner)

Фікстурний виконавець керує створенням файлу схеми бази даних та його видаленням. Завдяки механізму `FIXTURES_CLEANUP` операція видалення гарантовано запускається навіть тоді, коли інтеграційний тест зазнав аварійного збою.

```cpp
// tests/integration/db_fixture.cpp
#include <iostream>
#include <fstream>
#include <string_view>
#include <filesystem>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: db_fixture_runner --setup|--cleanup <db_path>\n";
        return 1;
    }

    std::string_view mode = argv[1];
    std::filesystem::path db_path = argv[2];

    if (mode == "--setup") {
        std::cout << "[FIXTURE] Ініціалізація тестового сховища: " << db_path << "\n";
        std::ofstream db_file(db_path, std::ios::trunc);
        if (!db_file) {
            std::cerr << "[FIXTURE ERROR] Не вдалося створити файл БД!\n";
            return 2;
        }
        db_file << "SCHEMA_VERSION=1\n";
        return 0; // Успішна підготовка
    }

    if (mode == "--cleanup") {
        std::cout << "[FIXTURE] Видалення тимчасового сховища: " << db_path << "\n";
        std::error_code ec;
        std::filesystem::remove(db_path, ec);
        return 0; // Очищення завершено
    }

    std::cerr << "[FIXTURE ERROR] Невідомий режим: " << mode << "\n";
    return 3;
}
```

### Інтеграційний тест

Інтеграційний тест виконує реальний запис у підготовлений файл сховища та верифікує наявність доданих даних.

```cpp
// tests/integration/test_storage.cpp
#include <iostream>
#include <fstream>
#include <string>
#include "calculator.hpp"

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Помилка: відсутній шлях до тестової БД\n";
        return 1;
    }

    std::string db_file = argv[1];
    std::cout << "[INTEGRATION] Запуск перевірки запису в " << db_file << "\n";

    engine::Calculator calc;
    bool ok = calc.write_record(db_file, 42, 3.14159);
    if (!ok) {
        std::cerr << "[FAIL] Не вдалося додати запис у сховище\n";
        return 2;
    }

    std::ifstream in(db_file);
    std::string line;
    bool found = false;
    while (std::getline(in, line)) {
        if (line.find("42:3.14159") != std::string::npos) {
            found = true;
            break;
        }
    }

    if (!found) {
        std::cerr << "[FAIL] Запис не знайдено в базі даних\n";
        return 3;
    }

    std::cout << "[PASS] Інтеграційний тест пройдено успішно.\n";
    return 0;
}
```

## Автоматизований запуск у CI/CD середовищі

Скрипт автоматизації для сервера CI демонструє поєднання збірки з санітайзерами, паралельного запуску через CTest, керування змінними середовища та збереження звіту в форматі JUnit XML:

```bash
#!/usr/bin/env bash
set -euo pipefail

BUILD_DIR="build_ci"

# 1. Конфігурація з санітайзерами пам'яті
cmake -B "${BUILD_DIR}" -G Ninja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DENABLE_ASAN=ON \
    -DBUILD_TESTING=ON

# 2. Паралельна компіляція бінарників
cmake --build "${BUILD_DIR}" --parallel "$(nproc)"

# 3. Налаштування опцій санітайзерів для автоматичного переривання при витоках
export ASAN_OPTIONS="detect_leaks=1:abort_on_error=1:halt_on_error=1"
export UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"

# 4. Виконання CTest з паралелізмом, лімітами та генерацією JUnit XML
ctest --test-dir "${BUILD_DIR}" \
    --parallel "$(nproc)" \
    --output-on-failure \
    --output-junit "${BUILD_DIR}/junit-report.xml" \
    --repeat until-pass:2

echo "Тестування завершено. Звіт збережено у ${BUILD_DIR}/junit-report.xml"
```

## Покроковий аналіз виконання конвеєра

Коли скрипт `run_ci.sh` викликає `ctest`, підсистема тестування виконує таку послідовність дій:

1. **Фаза аналізу метаданих:** CTest зчитує `CTestTestfile.cmake` та підключений файл `unit_tests_include.cmake`. У пам'яті будується орієнтований граф тестів: модульні тести `CalculatorTest.HandlesValidDivision` та `CalculatorTest.RejectsDivisionByZero` не мають попередників, тоді як `test_storage_read_write` позначається як залежний від фікстури `DatabaseFixture`.
2. **Фаза планування черги:** CTest перевіряє значення властивості `COST`. Тест `test_storage_read_write` має `COST 25.0`, тому він отримує найвищий пріоритет. Планувальник бачить вимогу `FIXTURES_REQUIRED "DatabaseFixture"` і автоматично ставить на перше місце крок підготовки `db_setup`.
3. **Паралельне виконання:**
   - На першому доступному ядрі запускається процес `./db_fixture_runner --setup ...`.
   - Одночасно на інших ядрах паралельно запускаються модульні тести GoogleTest.
   - Як тільки `db_setup` завершується з кодом `0`, планувальник негайно спавнить процес `./storage_tests ...`.
4. **Гарантоване завершення фікстури:** Після завершення роботи `storage_tests` (незалежно від того, чи повернув він код `0`, чи впав за сигналом або таймаутом), CTest автоматично запускає фінальний процес `./db_fixture_runner --cleanup ...`.
5. **Генерація артефактів:** CTest агрегує зібрану статистику (тривалість кожного кроку в мілісекундах, коди виходу, перехоплені логи) та записує валідний XML-файл `junit-report.xml`.

## Трасування та розбір типових помилок

Під час розгортання подібного конвеєра в реальних проєктах розробники найчастіше стикаються з трьома категоріями проблем:

- **Хибні витоки пам'яті у сторонніх бібліотеках:** Якщо системні драйвери або сторонні бібліотеки виділяють статичні буфери, які операційна система звільняє автоматично при завершенні процесу, LeakSanitizer може сигналізувати про витік. Для таких випадків створюють файл придушення `lsan.supp` і передають його через `LSAN_OPTIONS="suppressions=tests/lsan.supp"`.
- **Зависання тестів через взаємні блокування (Deadlock):** Властивість `TIMEOUT 15.0` надійно запобігає нескінченному виситьому стану процесу в CI. Коли таймаут спрацьовує, CTest перехоплює поточний вивід і формує статус `Timeout`, що дозволяє розробнику одразу побачити останній виконаний рядок коду.
- **Діагностика нестабільних перевірок (Flaky Tests):** Якщо певний мережевий тест періодично падає, локальний виклик `ctest --repeat until-fail:50 -R test_network` дозволяє швидко відтворити рідкісний стан гонитви без багаторазового перезапуску всього тестового набору вручну.

Коли цей сценарій виконується на сервері GitHub Actions або GitLab CI, файл `junit-report.xml` автоматично підхоплюється інтерфейсом системи. Розробник отримує точну статистику за всіма модульними та інтеграційними тестами без необхідності вручну розбирати консольний лог.

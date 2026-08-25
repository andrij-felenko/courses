# ⚙️ Модульна бібліотека на CMake 3.28+ і Ninja

Створення модульних проєктів у C++20 вимагає принципово нового підходу до побудови систем збірки. Якщо для класичних заголовків системі збірки достатньо було передати прапорці `-I` з каталогами пошуку, а всі файли `.cpp` компілювати повністю незалежно й паралельно, то поява бінарного інтерфейсу модуля (BMI) встановлює між джерельними файлами жорсткий топологічний порядок. Доки інтерфейс модуля або його розділу не скомпільовано у відповідний бінарний артефакт (`.pcm` у Clang, `.ifc` у MSVC чи `.gcm` у GCC), жоден споживач цього модуля не може навіть розпочати розбір коду.

Нижче розібрано повну інженерну реалізацію багатофайлової модульної бібліотеки лінійної алгебри `matrix_lib` з розбиттям на інтерфейсні та внутрішні розділи, окремою одиницею реалізації, інтеграцією системних заголовків через глобальний фрагмент модуля, підтримкою експорту пакетів через CMake `install(EXPORT)`, детальним аналізом низькорівневих викликів компіляторів та простеженням протоколу динамічного сканування P1689R5 під генератором Ninja.

## Архітектура модульного проєкту

Проєкт складається з логічного модуля `matrix`, розбитого на окремі файли за їхніми інженерними ролями, та клієнтського додатку:

```text
modular_matrix_project/
├── CMakeLists.txt
├── src/
│   ├── matrix.cppm           # Головна інтерфейсна одиниця (Primary Interface Unit)
│   ├── matrix_types.cppm     # Інтерфейсний розділ (Interface Partition :types)
│   ├── matrix_ops.cppm       # Внутрішній розділ реалізації (Internal Partition :ops)
│   ├── matrix_io.cpp         # Одиниця реалізації модуля (Module Implementation Unit)
│   └── matrix_storage.cppm   # Розділ збереження з глобальним фрагментом (:storage)
└── app/
    └── main.cpp              # Клієнтський код (споживач модуля)
```

Розподіл інженерних обов'язків між джерельними файлами базується на принципі локалізації змін:

1. `matrix_types.cppm` — інтерфейсний розділ `matrix:types`. Оголошує та експортує фундаментальні структури даних (`Matrix2x2`, `Vector2`). Оскільки це інтерфейсний розділ, він є публічною частиною модуля.
2. `matrix_ops.cppm` — внутрішній розділ `matrix:ops`. Оголошує низькорівневі математичні алгоритми (обчислення визначника, множення на вектор). Цей розділ доступний лише іншим файлам модуля `matrix` і повністю прихований від зовнішнього споживача.
3. `matrix_storage.cppm` — розділ збереження даних на диск `matrix:storage`. Демонструє використання глобального фрагмента модуля (`module;`) для безпечного підключення низькорівневих системних заголовків POSIX та C без витоку їхніх макросів у клієнтський код.
4. `matrix.cppm` — головна інтерфейсна одиниця модуля `matrix`. Вона реекспортує відкриті розділи `:types` та `:storage`, імпортує закритий розділ `:ops` і оголошує публічні функції високого рівня (`solve_2x2`, `multiply`).
5. `matrix_io.cpp` — одиниця реалізації модуля `matrix`. Містить важкі тіла функцій форматування виводу матриць у консоль. Цей файл не має ключового слова `export`. Будь-яка зміна форматування всередині нього не змінює бінарний інтерфейс (BMI) модуля `matrix`, тому споживачі бібліотеки взагалі не потребують перекомпіляції під час правок цього файлу.
6. `main.cpp` — клієнтський виконуваний файл, який взаємодіє з бібліотекою виключно через семантичний імпорт `import matrix;`.

## Джерельний код модульної системи

### 1. Інтерфейсний розділ типів: `src/matrix_types.cppm`

Інтерфейсний розділ оголошується директивою `export module matrix:types;`. Усі сутності, позначені ключовим словом `export`, експортуються в простір імен розділу:

```cpp
export module matrix:types;

import <array>;
import <cstddef>;

export namespace math {

struct Vector2 {
    double x{0.0};
    double y{0.0};
};

struct Matrix2x2 {
    std::array<double, 4> data{1.0, 0.0, 0.0, 1.0}; // Одинична матриця за замовчуванням

    [[nodiscard]] constexpr double at(std::size_t row, std::size_t col) const noexcept {
        return data[row * 2 + col];
    }

    [[nodiscard]] constexpr double& at(std::size_t row, std::size_t col) noexcept {
        return data[row * 2 + col];
    }
};

} // namespace math
```

### 2. Внутрішній розділ операцій: `src/matrix_ops.cppm`

Внутрішній розділ оголошується як `module matrix:ops;` без префікса `export`. Він слугує для внутрішньої декомпозиції коду бібліотеки:

```cpp
module matrix:ops;

import :types; // Імпорт інтерфейсного розділу всередині того самого модуля

namespace math::internal {

[[nodiscard]] constexpr double determinant(const Matrix2x2& m) noexcept {
    return m.at(0, 0) * m.at(1, 1) - m.at(0, 1) * m.at(1, 0);
}

[[nodiscard]] constexpr Vector2 transform(const Matrix2x2& m, const Vector2& v) noexcept {
    return Vector2{
        m.at(0, 0) * v.x + m.at(0, 1) * v.y,
        m.at(1, 0) * v.x + m.at(1, 1) * v.y
    };
}

} // namespace math::internal
```

### 3. Розділ збереження з глобальним фрагментом: `src/matrix_storage.cppm`

Коли модулю потрібні системні C-заголовки (наприклад, `<fcntl.h>`, `<unistd.h>` або `<sys/stat.h>`), їх не можна підключати через звичайний `#include` у тілі модуля, бо це порушить правила модуляризації. Їх розміщують у **глобальному фрагменті модуля** перед директивою `export module`:

```cpp
module; // Початок глобального фрагмента модуля

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

export module matrix:storage;

import :types;
import <string_view>;
import <system_error>;

export namespace math {

[[nodiscard]] std::error_code save_to_binary_file(std::string_view path, const Matrix2x2& m) noexcept {
    int fd = ::open(path.data(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        return std::error_code(errno, std::generic_category());
    }

    ssize_t written = ::write(fd, m.data.data(), sizeof(double) * 4);
    ::close(fd);

    if (written != sizeof(double) * 4) {
        return std::make_error_code(std::errc::io_error);
    }
    return {};
}

} // namespace math
```

Макроси `O_WRONLY`, `O_CREAT`, `O_TRUNC` та системні функції оголошені у глобальному фрагменті, тому вони доступні для компіляції цієї функції, але **жоден із цих макросів не вийде назовні** до споживачів модуля `matrix`.

### 4. Головна інтерфейсна одиниця: `src/matrix.cppm`

Головний інтерфейс визначає публічне обличчя модуля. Він явно декларує, які розділи передаються назовні, а які залишаються внутрішньою таємницею:

```cpp
export module matrix;

// Реекспорт: усі клієнти matrix автоматично бачать типи з :types та операції збереження з :storage
export import :types;
export import :storage;

// Приватний імпорт: внутрішні алгоритми потрібні тут, але не виходять назовні
import :ops;

import <optional>;
import <string>;

export namespace math {

[[nodiscard]] Matrix2x2 multiply(const Matrix2x2& a, const Matrix2x2& b) noexcept {
    Matrix2x2 res;
    for (std::size_t r = 0; r < 2; ++r) {
        for (std::size_t c = 0; c < 2; ++c) {
            res.at(r, c) = a.at(r, 0) * b.at(0, c) + a.at(r, 1) * b.at(1, c);
        }
    }
    return res;
}

[[nodiscard]] std::optional<Vector2> solve_2x2(const Matrix2x2& a, const Vector2& b) noexcept {
    const double det = internal::determinant(a);
    constexpr double eps = 1e-12;
    if (det > -eps && det < eps) {
        return std::nullopt; // Матриця вироджена
    }

    const double inv_det = 1.0 / det;
    return Vector2{
        (b.x * a.at(1, 1) - b.y * a.at(0, 1)) * inv_det,
        (a.at(0, 0) * b.y - a.at(1, 0) * b.x) * inv_det
    };
}

// Оголошення функції друку: її реалізацію навмисно винесено у matrix_io.cpp
void print_matrix(const Matrix2x2& m, const std::string& label);

} // namespace math
```

### 5. Одиниця реалізації модуля: `src/matrix_io.cpp`

Одиниця реалізації модуля починається директивою `module matrix;`. Вона належить до сфери модуля `matrix` (Module Purview) і бачить абсолютно всі його оголошення, але сама не може нічого експортувати:

```cpp
module matrix;

import <iostream>;
import <iomanip>;

namespace math {

void print_matrix(const Matrix2x2& m, const std::string& label) {
    std::cout << "=== " << label << " ===\n";
    for (std::size_t r = 0; r < 2; ++r) {
        std::cout << "| ";
        for (std::size_t c = 0; c < 2; ++c) {
            std::cout << std::setw(8) << std::fixed << std::setprecision(3) << m.at(r, c) << " ";
        }
        std::cout << "|\n";
    }
}

} // namespace math
```

### 6. Клієнтський виконуваний файл: `app/main.cpp`

Клієнтський код повністю позбавлений препроцесорних директив підключення локальних заголовків:

```cpp
import matrix;
import <iostream>;

int main() {
    math::Matrix2x2 a;
    a.at(0, 0) = 2.0; a.at(0, 1) = 1.0;
    a.at(1, 0) = 1.0; a.at(1, 1) = 3.0;

    math::Vector2 b{5.0, 5.0};

    math::print_matrix(a, "Матриця A");

    const auto sol = math::solve_2x2(a, b);
    if (sol.has_value()) {
        std::cout << "Розв'язок Ax = b: x = " << sol->x << ", y = " << sol->y << "\n";
    } else {
        std::cout << "Система не має розв'язку\n";
    }

    auto err = math::save_to_binary_file("matrix.bin", a);
    if (err) {
        std::cout << "Помилка запису файлу: " << err.message() << "\n";
    } else {
        std::cout << "Матрицю успішно записано у matrix.bin\n";
    }

    return 0;
}
```

## Конфігурація CMake 3.28+ та файлові набори `FILE_SET`

У класичному CMake джерельні файли передавалися через звичайний виклик `target_sources`. Для модулів C++20 цього недостатньо, оскільки системі збірки потрібно знати:

- Які саме файли є модульними інтерфейсами, а які — звичайними файлами реалізації.
- Де проходить базовий каталог модуля для формування ієрархії логічних імен (`BASE_DIRS`).
- Як експортувати інтерфейсні файли при створенні інсталяційних пакетів через `install(EXPORT)`.

Для розв'язання цієї задачі стандарт CMake 3.28 ввів механізм файлових наборів типу `CXX_MODULES`:

```cmake
cmake_minimum_required(VERSION 3.28)
project(ModularMatrixProject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Додавання модульної бібліотеки
add_library(matrix_lib)

# 1. Реєстрація інтерфейсних файлів модулів та розділів
target_sources(matrix_lib
    PUBLIC
        FILE_SET CXX_MODULES TYPE CXX_MODULES
        BASE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/src
        FILES
            src/matrix.cppm
            src/matrix_types.cppm
            src/matrix_ops.cppm
            src/matrix_storage.cppm
)

# 2. Додавання звичайних файлів реалізації (не потребують генерації експортного BMI)
target_sources(matrix_lib
    PRIVATE
        src/matrix_io.cpp
)

# Налаштування властивостей компілятора
target_compile_features(matrix_lib PUBLIC cxx_std_20)

# Створення клієнтської програми
add_executable(matrix_app app/main.cpp)

# Підключення модульної бібліотеки до клієнта
target_link_libraries(matrix_app PRIVATE matrix_lib)

# Налаштування встановлення бібліотеки для зовнішнього споживання
install(TARGETS matrix_lib
    EXPORT MatrixLibTargets
    FILE_SET CXX_MODULES DESTINATION include/modules
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(EXPORT MatrixLibTargets
    FILE MatrixLibConfig.cmake
    NAMESPACE math::
    DESTINATION lib/cmake/MatrixLib
    CXX_MODULES_DIRECTORY modules
)
```

## Як працює сканування залежностей: протокол P1689

Найбільшою перешкодою для впровадження модулів тривалий час була проблема «курки та яйця»: система збірки не може скомпілювати `main.cpp`, доки не отримає файл `matrix.pcm`, але система збірки не знає, що `main.cpp` потребує `matrix.pcm`, доки не проаналізує вихідний код `main.cpp`.

У класичній збірці Makefile чи Ninja аналізували файли `.d` (згенеровані компілятором прапорцями `-MMD -MF`), проте ці файли створювалися **під час або після** компіляції `.cpp`. Для модулів такий підхід не працює, оскільки залежність між модулями блокує сам початок компіляції.

Для вирішення цієї проблеми комітет ISO розробив документ **P1689R5 («Format for describing builds of C++20 Modules»)**. Він розділив процес збірки кожного джерельного файлу на чіткі стадії.

### Крок 1. Фаза швидкого сканування (Scanning)

Генератор Ninja запускає компілятор у надшвидкому режимі сканування, який лише токенізує директиви препроцесора та модульні інструкції без генерації машинного коду та без повної інстанціації шаблонів.

Команда сканування у Clang виглядає так:

```bash
clang-scan-deps -format=p1689 -- clang++ -std=c++20 -c src/matrix.cppm -o src/matrix.o
```

Компілятор повертає стандартизований JSON-звіт про те, що цей файл надає (`provides`) та чого він вимагає (`requires`):

```json
{
  "version": 1,
  "revision": 0,
  "rules": [
    {
      "primary-output": "src/matrix.cppm.o",
      "provides": [
        {
          "logical-name": "matrix",
          "is-interface": true
        }
      ],
      "requires": [
        {
          "logical-name": "matrix:types"
        },
        {
          "logical-name": "matrix:ops"
        },
        {
          "logical-name": "matrix:storage"
        }
      ]
    }
  ]
}
```

### Крок 2. Побудова динамічних ребер у Ninja (`dyndep`)

Ninja зчитує згенеровані JSON-файли через внутрішню інструкцію `dyndep`. На основі логічних імен (`logical-name`) Ninja динамічно створює ребра графа збірки:

```text
build src/matrix_types.pcm: dyndep
build src/matrix_ops.pcm: dyndep
build src/matrix_storage.pcm: dyndep
build src/matrix.pcm: dyndep | src/matrix_types.pcm src/matrix_ops.pcm src/matrix_storage.pcm
build app/main.o: dyndep | src/matrix.pcm
```

### Крок 3. Низькорівнева генерація артефактів (Clang, GCC, MSVC)

Отримавши динамічний граф, Ninja викликає компілятор для генерації бінарного інтерфейсу (BMI), а потім для створення двійкового об'єктного файлу.

У компіляторі **Clang**:

```bash
# 1. Генерація BMI розділів
clang++ -std=c++20 --precompile src/matrix_types.cppm -o build/matrix_types.pcm
clang++ -std=c++20 --precompile src/matrix_ops.cppm \
    -fmodule-file=matrix:types=build/matrix_types.pcm \
    -o build/matrix_ops.pcm
clang++ -std=c++20 --precompile src/matrix_storage.cppm \
    -fmodule-file=matrix:types=build/matrix_types.pcm \
    -o build/matrix_storage.pcm

# 2. Генерація головного BMI
clang++ -std=c++20 --precompile src/matrix.cppm \
    -fmodule-file=matrix:types=build/matrix_types.pcm \
    -fmodule-file=matrix:ops=build/matrix_ops.pcm \
    -fmodule-file=matrix:storage=build/matrix_storage.pcm \
    -o build/matrix.pcm

# 3. Генерація об'єктного коду реалізації та споживача
clang++ -std=c++20 -c src/matrix_io.cpp \
    -fmodule-file=matrix=build/matrix.pcm \
    -o build/matrix_io.o

clang++ -std=c++20 -c app/main.cpp \
    -fmodule-file=matrix=build/matrix.pcm \
    -o build/main.o
```

У компіляторі **GCC (версії 14+)**:

```bash
# GCC використовує механізм C++ Module Mapper (каталог gcm.cache)
g++ -std=c++20 -fmodules-ts -c src/matrix_types.cppm
g++ -std=c++20 -fmodules-ts -c src/matrix_ops.cppm
g++ -std=c++20 -fmodules-ts -c src/matrix_storage.cppm
g++ -std=c++20 -fmodules-ts -c src/matrix.cppm
g++ -std=c++20 -fmodules-ts -c src/matrix_io.cpp
g++ -std=c++20 -fmodules-ts -c app/main.cpp
```

У компіляторі **MSVC (Visual Studio 2022 / 19.38+)**:

```cmd
:: MSVC компілює інтерфейси з прапорцем /interface та створює .ifc
cl /std:c++20 /interface /TP /c src/matrix_types.cppm /Fo:build\matrix_types.obj /ifcOutput:build\matrix_types.ifc
cl /std:c++20 /interface /TP /c src/matrix_ops.cppm /reference matrix:types=build\matrix_types.ifc /Fo:build\matrix_ops.obj /ifcOutput:build\matrix_ops.ifc
cl /std:c++20 /interface /TP /c src/matrix_storage.cppm /reference matrix:types=build\matrix_types.ifc /Fo:build\matrix_storage.obj /ifcOutput:build\matrix_storage.ifc
cl /std:c++20 /interface /TP /c src/matrix.cppm /reference matrix:types=build\matrix_types.ifc /reference matrix:ops=build\matrix_ops.ifc /reference matrix:storage=build\matrix_storage.ifc /Fo:build\matrix.obj /ifcOutput:build\matrix.ifc
cl /std:c++20 /TP /c src/matrix_io.cpp /reference matrix=build\matrix.ifc /Fo:build\matrix_io.obj
cl /std:c++20 /TP /c app/main.cpp /reference matrix=build\matrix.ifc /Fo:build\main.obj
```

## Споживання встановленої модульної бібліотеки через `find_package`

Коли модульна бібліотека зібрана та встановлена в систему за допомогою `cmake --install build`, зовнішній проєкт може підключити її через звичайний файл конфігурації. У клієнтському проєкті створюється наступний `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.28)
project(ExternalConsumer CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пошук встановленої модульної бібліотеки
find_package(MatrixLib REQUIRED CONFIG)

add_executable(consumer_app consumer_main.cpp)

# Підключення автоматично імпортує вихідні інтерфейси модулів у дерево збірки споживача
target_link_libraries(consumer_app PRIVATE math::matrix_lib)
```

Зверніть увагу на фундаментальну відмінність: CMake автоматично компілює бінарні інтерфейси модулів (`.pcm`/`.ifc`) безпосередньо в каталозі збірки споживача, використовуючи встановлені `.cppm` файли та прапорці компілятора споживача. Це гарантує повну сумісність ABI та налаштувань оптимізації.

## Аналіз швидкості інкрементальної збірки

Щоб зрозуміти практичну цінність розподілу на інтерфейси, розділи та файли реалізації, розглянемо поведінку збірки при різних типах правок:

### Сценарій 1. Зміна внутрішньої логіки виводу в `src/matrix_io.cpp`

Інженер змінює форматування чисел у функції `print_matrix` (наприклад, змінює точність `setprecision` з 3 на 6).

- **Що відбувається**: модифіковано файл `matrix_io.cpp`. Цей файл не є інтерфейсом і не генерує BMI.
- **Дії системи збірки**: Ninja перекомпілює **лише один файл** `matrix_io.o` і відразу запускає лінкер.
- **Час перезбірки**: кілька мілісекунд. Клієнтський `main.cpp` та модульні інтерфейси `matrix.pcm` навіть не відкриваються.

Якби цей код було написано у класичному стилі заголовків, де функція або шаблонний клас матриці лежав у спільному `matrix.h`, зміна `matrix.h` призвела б до автоматичної перекомпіляції `matrix.cpp`, `main.cpp` та всіх інших файлів проєкту, які підключали цей заголовок.

### Сценарій 2. Зміна внутрішнього розділу `src/matrix_ops.cppm`

Інженер оптимізує функцію `determinant` у розділі `matrix:ops`.

- **Що відбувається**: оновлюється `matrix_ops.pcm` та `matrix.pcm`. Проте, оскільки публічна сигнатура `solve_2x2` у `matrix.cppm` не змінилася, сучасні компілятори з підтримкою смарт-хешування інтерфейсів можуть запобігти перекомпіляції файлів, які залежать лише від зовнішнього API.
- **Підсумок**: повне розділення фізичної структури дозволяє локалізувати вплив змін у межах мінімального набору файлів.

## Інженерний чеклист для налаштування модулів у проєкті

1. **Версії інструментів**: переконайтеся, що використовується CMake `≥ 3.28`, Ninja `≥ 1.11`, а також Clang `≥ 17`, GCC `≥ 14` або MSVC `≥ 19.38`. Старіші версії містять неповноцінні або експериментальні реалізації сканування P1689.
2. **Розширення файлів**: використовуйте розширення `.cppm` (загальноприйняте в екосистемі LLVM/Clang та CMake) або `.ixx` (традиційне для MSVC) для інтерфейсних одиниць, та звичайне `.cpp` для одиниць реалізації.
3. **Гігієна макросів**: ніколи не розміщуйте `#define` перед інструкціями `import` з розрахунком на зміну поведінки модуля. Модуль компілюється в ізольованому контексті й не бачить зовнішніх препроцесорних макросів споживача.
4. **Розділи замість підмодулів**: не створюйте штучних вкладених модулів на зразок `matrix_types` та `matrix_ops` окремо, якщо вони є частиною однієї логічної бібліотеки. Використовуйте розділи модуля (`matrix:types`, `matrix:ops`), оскільки вони гарантують єдину назву бібліотеки для кінцевого споживача.
5. **Глобальний фрагмент для C-API**: усі заголовки сторонніх C-бібліотек та операційної системи мають знаходитися виключно між `module;` та `export module`, щоб гарантувати ізоляцію макросів від решти системи.

# 📋 Поверхня інтерфейсу розрахунку фазових рівноваг та варіантності

У даній встановидавчій інспекції інтерфейсу розглянуто програмну поверхню (API) бібліотеки термодинамічного аналізу гетерогенних систем `libthermo_phase`. Інтерфейс призначено для обчислення числа компонентів Гіббса, рангу стехіометричної матриці, варіантності системи та контролю рівноважних станів у промислових термодинамічних симуляторах.

Модуль надає двійково сумісний низькорівневий інтерфейс мовою C (для інтеграції з кодом на Fortran, Python C-extensions, Rust FFI, Julia ccall та вбудованими контролерами) та об'єктно-орієнтований обгортковий інтерфейс мовою C++ з використанням семантики системних типів `std::optional`, `std::expected` та RAII.

## 1. Загальна архітектура та специфікація типів даних

Аналіз термодинамічної варіантності описується структурою термодинамічної системи, яка містить перелік компонентів, стехіометричну матрицю, число початкових обмежень, кількість співіснуючих фаз та тип середовища (загальна система з параметрами `T, P` чи конденсована система при `P = const`).

### 1.1 Перелік кодів помилок та термодинамічних станів

Тип `ThermoStatusCodeC` (мовою C) та enum class `Status` (мовою C++) визначають термодинамічний та чисельний статус результату обчислень:
- `THERMO_SUCCESS` / `Status::Success` (`0`): Обчислення успішне, варіантність `F >= 0`. Система знаходиться у стійкій або метастійкій термодинамічній рівновазі.
- `THERMO_WARN_OVERDETERMINED` / `Status::WarnOverdetermined` (`1`): Систему перевизначено (`F < 0`). Задане число фаз `P` перевищує максимально можливе число фаз `K + 2`. Одночасне співіснування такої кількості фаз термодинамічно неможливе за довільних умов. Одна або декілька фаз мають схлопнутися.
- `THERMO_WARN_CRITICAL_POINT` / `Status::WarnCriticalPoint` (`2`): Система перебуває у критичній точці або азеотропній рівновазі. Виникли додаткові термодинамічні обмеження рівності складів фаз (`x[V] = x[L]`), що зменшує число вільних інтенсивних змінних на одиницю.
- `THERMO_ERR_INVALID_SPECIES` / `Status::ErrInvalidSpecies` (`-1`): Невілідна кількість речовин (`N <= 0`). Передано порожній масив сполук.
- `THERMO_ERR_INVALID_PHASES` / `Status::ErrInvalidPhases` (`-2`): Невілідна кількість фаз (`P < 1`). У гетерогенній системі повинна існувати принаймні одна фаза.
- `THERMO_ERR_NULL_POINTER` / `Status::ErrNullPointer` (`-3`): Передано нульовий вказівник у C-API.

### 1.2 Структура пам'яті та бінарна сумісність (ABI)

Для забезпечення бінарної сумісності (ABI) між різними компіляторами (GCC, Clang, MSVC) для структур `PhaseSystemSpecC` та `PhaseResultSpecC` дотримуються такі правила вирівнювання:
- Поля типу `size_t` мають розмір 8 байтів на 64-бітних архітектурах і вирівнюються по 8-байтній межі.
- Вказівники `stoich_matrix_flat` та `status_message` мають розмір 8 байтів та 8-байтне вирівнювання.
- Прапор `is_condensed` типу `bool` має розмір 1 байт та розташовується перед вказівником із додаванням 7 байтів падінгу (padding), що гарантує сумарний розмір структури `PhaseSystemSpecC` у 48 байтів без прихованого зміщення полів при передачі між C та Fortran/Python.

## 2. Специфікація програмних інтерфейсів

:::tabs
```c
#ifndef LIBTHERMO_PHASE_H
#define LIBTHERMO_PHASE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    THERMO_SUCCESS = 0,
    THERMO_WARN_OVERDETERMINED = 1,
    THERMO_WARN_CRITICAL_POINT = 2,
    THERMO_ERR_INVALID_SPECIES = -1,
    THERMO_ERR_INVALID_PHASES = -2,
    THERMO_ERR_NULL_POINTER = -3
} ThermoStatusCodeC;

typedef struct {
    size_t num_species;
    size_t num_reactions;
    size_t num_constraints;
    size_t num_phases;
    bool is_condensed;
    const double* stoich_matrix_flat;
} PhaseSystemSpecC;

typedef struct {
    size_t rank_reactions;
    size_t gibbs_components;
    int degrees_of_freedom;
    ThermoStatusCodeC status_code;
    const char* status_message;
} PhaseResultSpecC;

/**
 * @brief Обчислює ранг стехіометричної матриці методом Гаусса.
 * @param matrix_flat Одновимірний масив матриці розміром (rows x cols).
 * @param rows Кількість рядків (реакцій).
 * @param cols Кількість стовпчиків (сполук).
 * @param eps Поріг порівняння з нулем.
 * @return Ранг матриці або -1 при некоректних аргументах.
 */
int thermo_compute_stoich_rank(
    const double* matrix_flat,
    size_t rows,
    size_t cols,
    double eps
);

/**
 * @brief Обчислює число компонентів Гіббса K = N - R - q.
 * @param num_species Кількість речовин N.
 * @param rank_reactions Ранг стехіометричної матриці R.
 * @param num_constraints Число додаткових обмежень q.
 * @return Кількість компонентів Гіббса.
 */
size_t thermo_compute_gibbs_components(
    size_t num_species,
    size_t rank_reactions,
    size_t num_constraints
);

/**
 * @brief Обчислює варіантність гетерогенної системи F = K - P + env.
 * @param gibbs_components Число компонентів K.
 * @param num_phases Число фаз P.
 * @param is_condensed Прапор конденсованої системи (true: env=1, false: env=2).
 * @return Кількість ступенів вільності F.
 */
int thermo_compute_degrees_of_freedom(
    size_t gibbs_components,
    size_t num_phases,
    bool is_condensed
);

/**
 * @brief Головна функція повного аналізу гетерогенної фазової системи.
 * @param spec Вказівник на специфікацію системи.
 * @param result Вказівник на структуру результату.
 * @return Код статусу виконання ThermoStatusCodeC.
 */
ThermoStatusCodeC thermo_analyze_phase_system(
    const PhaseSystemSpecC* spec,
    PhaseResultSpecC* result
);

/**
 * @brief Повертає текстовий підпис коду статусу.
 * @param code Код помилки або попередження.
 * @return Статичний рядок із поясненням.
 */
const char* thermo_status_to_string(ThermoStatusCodeC code);

#ifdef __cplusplus
}
#endif

#endif /* LIBTHERMO_PHASE_H */
```
```cpp
#ifndef LIBTHERMO_PHASE_HPP
#define LIBTHERMO_PHASE_HPP

#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstddef>

namespace thermo {

enum class Status {
    Success = 0,
    WarnOverdetermined = 1,
    WarnCriticalPoint = 2,
    ErrInvalidSpecies = -1,
    ErrInvalidPhases = -2,
    ErrNullPointer = -3
};

struct PhaseSystemConfig {
    std::vector<std::string> species_names;
    std::vector<std::vector<double>> stoich_matrix;
    std::size_t num_constraints = 0;
    std::size_t num_phases = 1;
    bool is_condensed = false;
};

struct PhaseAnalysisResult {
    std::size_t rank_reactions = 0;
    std::size_t gibbs_components = 0;
    int degrees_of_freedom = 0;
    Status status = Status::Success;
    std::string description;

    [[nodiscard]] bool is_valid() const noexcept {
        return degrees_of_freedom >= 0;
    }
};

class PhaseRuleCalculator {
public:
    explicit PhaseRuleCalculator(double epsilon = 1e-9) noexcept
        : m_epsilon(epsilon) {}

    [[nodiscard]] std::expected<PhaseAnalysisResult, Status>
    analyze(const PhaseSystemConfig& config) const;

    [[nodiscard]] std::size_t calculate_matrix_rank(
        const std::vector<std::vector<double>>& matrix,
        std::size_t num_cols
    ) const;

    [[nodiscard]] static std::size_t calculate_gibbs_components(
        std::size_t num_species,
        std::size_t rank,
        std::size_t constraints
    ) noexcept;

    [[nodiscard]] static int calculate_degrees_of_freedom(
        std::size_t components,
        std::size_t phases,
        bool is_condensed
    ) noexcept;

    [[nodiscard]] static std::string_view status_to_string(Status status) noexcept;

private:
    double m_epsilon = 1e-9;
};

} // namespace thermo

#endif /* LIBTHERMO_PHASE_HPP */
```
:::

## 3. Детальний опис функцій, параметрів та контрактів виконання

### 3.1 Головна функція `thermo_analyze_phase_system` / Метод `PhaseRuleCalculator::analyze`

- **Призначення**: Здійснює комплексний розрахунок варіантності гетерогенної фізико-хімічної системи на основі правила фаз Гіббса.
- **Вхідні параметри**:
  - `spec` / `config`: Конфігураційна структура, яка містить кількісні характеристики гетерогенної системи.
- **Попередні умови (Pre-conditions)**:
  - `spec != NULL` (у C-API) та `result != NULL`.
  - `spec->num_species > 0` (у C-API) або `!config.species_names.empty()` (у C++ API).
  - `spec->num_phases >= 1` або `config.num_phases >= 1`.
  - У разі відсутності хімічних реакцій розмірність стехіометричної матриці допускається рівною `0 × N` (чиста гетерогенна фізична система без хімічних перетворень).
- **Постумови (Post-conditions)**:
  - Значення `rank_reactions` задовольняє нерівність `0 <= rank_reactions <= min(R, N)`.
  - Значення `gibbs_components` обчислюється як `K = max(1, N - R - q)`.
  - Значення `degrees_of_freedom` розраховується як `F = K - P + 2` (або `F = K - P + 1` при `is_condensed == true`).
  - Результат виконання повертає код `THERMO_SUCCESS` при `F >= 0` або `THERMO_WARN_OVERDETERMINED` при `F < 0`.

### 3.2 Допоміжна функція `thermo_compute_stoich_rank` / Метод `calculate_matrix_rank`

- **Призначення**: Проводить метод Гаусса з частковим вибором головного елемента по стовпчиках для визначення лінійно незалежних рядків стехіометричної матриці.
- **Аргументи**:
  - `matrix_flat` / `matrix`: Матриця стехіометричних коефіцієнтів.
  - `rows`: Кількість реакцій `R`.
  - `cols`: Кількість сполук `N`.
  - `eps`: Поріг відсікання машинного нуля `1e-9`.
- **Повертане значення**: Цілочисельне значення рангу `0 <= rank <= min(rows, cols)`. У разі невілідного вказівника на масив повертається `-1`.

### 3.3 Допоміжна функція `thermo_compute_gibbs_components` / Метод `calculate_gibbs_components`

- **Призначення**: Розраховує кількість незалежних компонентів Гіббса за формулою `K = N - R - q`.
- **Аргументи**:
  - `num_species`: Загальне число вихідних сполук `N`.
  - `rank`: Ранг стехіометричної матриці `R`.
  - `constraints`: Число початкових концентраційних та зарядових обмежень `q`.
- **Повертане значення**: Невід'ємне число компонентів `K >= 1`. Якщо алгебраїчна різниця `N - R - q` виявляється менше одиниці, функція автоматично повертає мінімальне фізично допустиме значення `1`.

### 3.4 Допоміжна функція `thermo_compute_degrees_of_freedom` / Метод `calculate_degrees_of_freedom`

- **Призначення**: Обчислює число ступенів вільності системи за формулою `F = K - P + env`.
- **Аргументи**:
  - `components`: Число компонентів Гіббса `K`.
  - `phases`: Число співіснуючих фаз `P`.
  - `is_condensed`: Прапор конденсованої системи (`env = 1` при `P = const`, `env = 2` при вільній зміні `T, P`).
- **Повертане значення**: Ціле число `F`. Від'ємне значення `F < 0` свідчить про перевизначеність системи.

## 4. Керування пам'яттю та виняткобезпечність

1. **Гарантії керування пам'яттю у C-API**:
   - Усі структури даних `PhaseSystemSpecC` та `PhaseResultSpecC` виділяються та звільняються викликаючою стороною (Caller-Allocated Memory pattern).
   - Матриця `stoich_matrix_flat` передається у вигляді неперерваного одновимірного масиву вказуваного типом `const double*`, розміром `rows * cols` елементів. Бібліотека не створює динамічних копій масиву у купі (Heap allocations avoided).
   - Рядок `status_message` є вказувачем на статичну константну пам'ять у секції даних бібліотеки, яка не потребує виклику `free()`.

2. **Гарантії безпеки у C++ API**:
   - Клас `PhaseRuleCalculator` володіє строгою гарантією виняткобезпечності (Strong Exception Guarantee).
   - Повернення результату виконується через шаблонний клас `std::expected<PhaseAnalysisResult, Status>`, що повністю усуває необхідність використання винятків `try/catch` для обробки термодинамічних помилок.
   - Метод `status_to_string` повертає `std::string_view` на статичний літерал, що не створює алокацій у динамічній пам'яті.

## 5. Повний приклад використання C та C++ програмного інтерфейсу

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include "libthermo_phase.h"

int main(void) {
    // Система парового реформінгу метану: 5 сполук, 2 реакції
    double stoich[2 * 5] = {
        -1.0, -1.0,  1.0,  0.0,  3.0,  /* CH4 + H2O ⇌ CO + 3 H2 */
         0.0, -1.0, -1.0,  1.0,  1.0   /* CO + H2O ⇌ CO2 + H2   */
    };

    PhaseSystemSpecC spec;
    spec.num_species = 5;
    spec.num_reactions = 2;
    spec.num_constraints = 0;
    spec.num_phases = 1;
    spec.is_condensed = false;
    spec.stoich_matrix_flat = stoich;

    PhaseResultSpecC result;
    ThermoStatusCodeC code = thermo_analyze_phase_system(&spec, &result);

    if (code == THERMO_SUCCESS) {
        printf("--- Аналіз фазової рівноваги (C-API) ---\n");
        printf("Ранг реакцій R: %zu\n", result.rank_reactions);
        printf("Компоненти Гіббса K: %zu\n", result.gibbs_components);
        printf("Ступені вільності F: %d\n", result.degrees_of_freedom);
        printf("Статус: %s\n", result.status_message);
    } else {
        printf("Помилка обчислення: %s\n", thermo_status_to_string(code));
    }

    return 0;
}
```
```cpp
#include <iostream>
#include "libthermo_phase.hpp"

int main() {
    thermo::PhaseSystemConfig config;
    config.species_names = {"CH4", "H2O", "CO", "CO2", "H2"};
    config.num_phases = 1;
    config.is_condensed = false;
    config.num_constraints = 0;

    // Матриця 2 x 5 двох незалежних реакцій
    config.stoich_matrix = {
        {-1.0, -1.0,  1.0,  0.0,  3.0}, // CH4 + H2O ⇌ CO + 3 H2
        { 0.0, -1.0, -1.0,  1.0,  1.0}  // CO + H2O ⇌ CO2 + H2
    };

    thermo::PhaseRuleCalculator calc(1e-9);
    auto result_exp = calc.analyze(config);

    if (result_exp.has_value()) {
        const auto& res = result_exp.value();
        std::cout << "--- Аналіз фазової рівноваги (C++ API) ---\n";
        std::cout << "Ранг реакцій R: " << res.rank_reactions << "\n";
        std::cout << "Компоненти Гіббса K: " << res.gibbs_components << "\n";
        std::cout << "Ступені вільності F: " << res.degrees_of_freedom << "\n";
        std::cout << "Статус: " << res.description << "\n";
        std::cout << "Чи вілідна рівновага: " << (res.is_valid() ? "Так" : "Ні") << "\n";
    } else {
        std::cout << "Помилка обчислень: " 
                  << thermo::PhaseRuleCalculator::status_to_string(result_exp.error()) 
                  << "\n";
    }

    return 0;
}
```
:::

## 6. Приклад зв'язування з мовою Python (CFFI / ctypes Binding)

При використанні бібліотеки у наукових обчислювальних середовищах на Python інтерфейс мовою C легко обгортається за допомогою модуля `ctypes`:

```python
import ctypes

class PhaseSystemSpecC(ctypes.Structure):
    _fields_ = [
        ("num_species", ctypes.c_size_t),
        ("num_reactions", ctypes.c_size_t),
        ("num_constraints", ctypes.c_size_t),
        ("num_phases", ctypes.c_size_t),
        ("is_condensed", ctypes.c_bool),
        ("stoich_matrix_flat", ctypes.POINTER(ctypes.c_double))
    ]

class PhaseResultSpecC(ctypes.Structure):
    _fields_ = [
        ("rank_reactions", ctypes.c_size_t),
        ("gibbs_components", ctypes.c_size_t),
        ("degrees_of_freedom", ctypes.c_int),
        ("status_code", ctypes.c_int),
        ("status_message", ctypes.c_char_p)
    ]

# Завантаження динамічної бібліотеки
lib = ctypes.CDLL("./libthermo_phase.so")
lib.thermo_analyze_phase_system.argtypes = [
    ctypes.POINTER(PhaseSystemSpecC), 
    ctypes.POINTER(PhaseResultSpecC)
]
lib.thermo_analyze_phase_system.restype = ctypes.c_int
```

Цей шар біндінгів володіє нульовими накладними витратами на копіювання даних (Zero-Copy Data Transfer), оскільки масиви NumPy передаються безпосередньо за вказівником на буфер пам'яті.

## 7. Модель багатопотоковості та повторної входжуваності (Thread-Safety)

Бібліотека `libthermo_phase` розроблена за принципами функціональної чистоти (Pure Functional Paradigm).

Основні гарантії паралельного виконання:
- **Відсутність мутабельного глобального стану**: Бібліотека не містить змінних типу `static` або глобальних буферів у пам'яті.
- **Реентрабельність (Reentrancy)**: Будь-яка функція C-API або метод C++ API може бути безпечно викликана з кількох паралельних потоків (OpenMP threads, POSIX threads, `std::jthread`) для різних або однакових екземплярів систем.
- **Відсутність блокувань (Lock-Free Execution)**: Функції не використовують м'ютекси (`std::mutex`) або атоміки, що забезпечує максимальну швидкодію при масштабуванні на багатоядерних суперкомп'ютерних кластерах.

## 8. Покрокова трасування виконання виклику в C-API

Простежимо виконання функції `thermo_analyze_phase_system(&spec, &result)` при передачі багатокомпонентного електролітного розчину розчинності солей:

1. **Перевірка вказівників**: На першому кроці функція перевіряє `spec != NULL` та `result != NULL`. Якщо один із них дорівнює `NULL`, повертається `THERMO_ERR_NULL_POINTER`.
2. **Перевірка параметрів сполук та фаз**: Перевіряється `spec->num_species > 0` та `spec->num_phases >= 1`. Якщо `num_species == 0`, повертається `THERMO_ERR_INVALID_SPECIES`.
3. **Обчислення рангу стовпчиків**: Викликається `thermo_compute_stoich_rank()`. Створюється локальна копія матриці на стеку (для `N <= 16`) або у тимчасовій виділеній пам'яті. Виконується трикутне зведення.
4. **Обчислення компонентів та варіантності**: Визначений ранг `R` віднімається від кількості сполук `N` та додаткових обмежень `q`. Значення `F` записується у `result->degrees_of_freedom`.
5. **Встановлення підсумкового тексту**: У `result->status_message` записується статичний рядок із поясненням та повертається підсумковий код `THERMO_SUCCESS`.

## 9. Інтеграція з мовою Rust (Rust FFI Binding)

Для безпечного використання у сучасних системних проектах мовою Rust C-інтерфейс бібліотеки імпортується за допомогою модуля `extern "C"`:

```rust
use std::os::raw::{c_char, c_double, c_int};

#[repr(C)]
pub struct PhaseSystemSpecC {
    pub num_species: usize,
    pub num_reactions: usize,
    pub num_constraints: usize,
    pub num_phases: usize,
    pub is_condensed: bool,
    pub stoich_matrix_flat: *const c_double,
}

#[repr(C)]
pub struct PhaseResultSpecC {
    pub rank_reactions: usize,
    pub gibbs_components: usize,
    pub degrees_of_freedom: c_int,
    pub status_code: c_int,
    pub status_message: *const c_char,
}

extern "C" {
    pub fn thermo_analyze_phase_system(
        spec: *const PhaseSystemSpecC,
        result: *mut PhaseResultSpecC,
    ) -> c_int;
}
```

Використання атрибута `#[repr(C)]` у мові Rust гарантує точний збіг ABI-структур пам'яті з C-компілятором GCC/Clang.

## 10. Оптимізація SIMD (AVX-512) для великих баз хімічних реакцій

При розрахунку згоряння складних вуглеводневих сумішей (наприклад, авіаційного гасу) число сполук досягає `N = 500`, а число реакцій `R = 2500`.

Для прискорення Гауссового розкладу стехіометричної матриці у C-реалізації бібліотеки застосовується SIMD-векторизація AVX-512:
- Внутрішні цикли множення та віднімання елементів рядків `temp[row][c] -= factor * temp[pivot_row][c]` вирівнюються по 64-байтній межі в пам'яті.
- Використовуються векторні інструкції `_mm512_fnmadd_pd` для одночасного виконання множення та віднімання восьми чисел подвійної точності (double precision) за один такт процесора.
- Це забезпечує 6-кратне прискорення розрахунку рангу матриці для великомасштабних згоряльних моделей порівняно зі скалярним кодом.

## 11. Шаблони C++20 та концепт-обмеження (C++20 Concepts)

У версії для C++20 обчислювальний модуль надає концепт-обмежений шаблонний інтерфейс для підтримки довільних контейнерів користувача без примусового копіювання у `std::vector`:

```cpp
template <typename Container>
concept StoichiometricContainer = requires(Container c) {
    { c.size() } -> std::convertible_to<std::size_t>;
    { c[0][0] } -> std::convertible_to<double>;
};
```

Цей підхід дозволяє передавати у метод `analyze()` масиви Eigen, Armadillo або `std::mdspan` без додаткових накладних витрат.

## 12. Логування та трасування чисельної збіжності

У промислових симуляторах для відлагодження термодинамічних розрахунків бібліотека підтримує колбек-функцію логування (Logging Callback).

:::tabs
```c
typedef void (*ThermoLogCallbackC)(int level, const char* message);

void thermo_set_log_callback(ThermoLogCallbackC callback);
```
```cpp
using ThermoLogCallback = std::function<void(int level, std::string_view message)>;

void set_log_callback(ThermoLogCallback callback);
```
:::

Під час виконання розрахунку Гауссового рангу матриці система може надсилати детальні повідомлення рівня `TRACE` про вибрані опорні елементи (pivots), коефіцієнти масштабування та виявлені лінійно залежні реакції. Якщо логування не активовано (`callback == NULL`), усі діагностичні виклики повністю оптимізуються компілятором і не впливають на швидкодію.

## 13. Збирання бібліотеки та експорт символів (CMake & Dynamic Linkage)

Для підключення бібліотеки у кросплатформенні CMake-проекти надаються конфігурації статичного та динамічного зв'язування.

Налаштування видимості символів:
- У ОС Windows використовується макрос `__declspec(dllexport)` для експорту функцій C-API у `.dll` файли.
- У ОС Linux / macOS використовується макрос `__attribute__((visibility("default")))` у компіляторах GCC та Clang, при цьому всі внутрішні службові функції приховуються прапором `-fvisibility=hidden`.

## 14. Модульне тестування та валідація (GoogleTest Suite)

Для автоматичної перевірки коректності функцій C та C++ API у складі бібліотеки розроблено набір юніт-тестів на фреймворку GoogleTest.

Тестова сюїта покриває такі ключові сценарії:
- Перевірку обчислення рангу для нульових та вироджених матриць;
- Валідацію розрахунку варіантності для води, евтектичних сплавів та газів під тиском;
- Навантажувальне тестування обробки масивів великої розмірності (`N = 1000`);
- Перевірку поведінки при передачі `NULL`-вказувачів та порожніх списків сполук.

## 15. Інтеграція з мовою Julia (Julia ccall Binding)

У високоефективних середовищах моделювання на мові Julia функціонал бібліотеки підключається за допомогою прямого механізму `ccall`:

```julia
struct PhaseSystemSpecC
    num_species::Csize_t
    num_reactions::Csize_t
    num_constraints::Csize_t
    num_phases::Csize_t
    is_condensed::Cbool
    stoich_matrix_flat::Ptr{Cdouble}
end

function analyze_phase_system(spec::PhaseSystemSpecC, result_ptr::Ptr{Nothing})
    return ccall(
        (:thermo_analyze_phase_system, "./libthermo_phase.so"),
        Cint,
        (Ref{PhaseSystemSpecC}, Ptr{Nothing}),
        spec, result_ptr
    )
end
```

Це дозволяє науковим співробітникам виконувати термодинамічні розрахунки у Julia без проміжних шарів алокації.

## 16. Сумісність із мовою Fortran (ISO_C_BINDING)

Для підключення у спадкові геологічні та металургійні модулі на Fortran 2003/2008 надається заголовочний модуль `iso_c_binding`:

```fortran
module thermo_phase_bind
    use iso_c_binding
    implicit none

    type, bind(C) :: PhaseSystemSpecC
        integer(c_size_t) :: num_species
        integer(c_size_t) :: num_reactions
        integer(c_size_t) :: num_constraints
        integer(c_size_t) :: num_phases
        logical(c_bool)   :: is_condensed
        type(c_ptr)       :: stoich_matrix_flat
    end type PhaseSystemSpecC
end module thermo_phase_bind
```

Це гарантує прямий виклик обчислювальних процедур з моделей фізики океану та металургійного термоаналізу.

## 17. Інтеграція з промисловим стандартом CAPE-OPEN

У хімічній промисловості інтерфейс `libthermo_phase` адаптується під стандарт CAPE-OPEN (Computer-Aided Process Engineering).

Для підтримки CAPE-OPEN реалізуються такі кроки:
1. **Експорт COM / CORBA інтерфейсів**: Структури `PhaseSystemSpecC` обгортаються у двонаправлені інспекційні COM-об'єкти для зв'язку з технологічними симуляторами Aspen HYSYS та PRO/II.
2. **Перетворення одиниць вимірювання**: Повертані значення ступенів вільності `F` переводяться у специфікації активних параметрів потоку (Stream Pressure, Temperature, Enthalpy specifications).
3. **Обробка вироджень**: Якщо технологічний потік переходить у стан азеотропу, інтерфейс сигналізує про заміну диваріантного розрахунку на моноваріантний розрахунок лінії кипіння.

## 18. Порівняльний аналіз C та C++ програмних інтерфейсів

У наведеній нижче таблиці підсумовано ключові архітектурні відмінності двох рівнів API:

| Критерій | C-API (`libthermo_phase.h`) | C++ API (`libthermo_phase.hpp`) |
| :--- | :--- | :--- |
| **Стиль керування пам'яттю** | Ручний (Stack/Caller allocated) | Автоматичний RAII (`std::vector`) |
| **Обробка помилок** | Коди повернення `ThermoStatusCodeC` | Типобезпечний `std::expected` |
| **Передача матриць** | Одновимірний вказівник `const double*` | Двовимірний `std::vector<std::vector<double>>` |
| **Потокобезпечність** | Абсолютна (Stateless C-functions) | Абсолютна (`const` static-ready methods) |
| **Двійкова сумісність (ABI)** | Повна C-ABI сумісність з FFI | Вимагає C++20 ABI сумісного компілятора |

## 19. Інтеграція у термодинамічні симуляційні комплекси

При розробці плагінів для термодинамічних пакетів (таких як Aspen Plus, CAPE-OPEN або Thermo-Calc) модуль `libthermo_phase` слугує вхідним preconditioner-фільтром.

Типова послідовність викликів у розрахунковому модулі:
1. **Ініціалізація та валідація**: Модуль отримує список молекулярних ід-номерів речовин від ядра симулятора та перевіряє їхню присутність у базі даних.
2. **Побудова стехіометрії**: Автоматичне формування стехіометричної матриці `stoich_matrix` на основі атомних матриць сполук.
3. **Виклик `thermo_analyze_phase_system()`**: Визначення числа незалежних компонентів `K` та ступенів вільності `F`.
4. **Контроль збіжності оптимізатора**: Якщо розраховане `F = 0`, розрахунковий модуль симулятора фіксує нонваріантний стан (наприклад, ізотерму евтектичного плавлення чи азеотропну точку кипіння), запобігаючи нескінченним ітераціям чисельного шукача коренів.

## 20. Крайові випадки та обробка некоректних даних

1. **Порожній список сполук (`N = 0`)**: Метод `analyze()` повертає помилку `Status::ErrInvalidSpecies`.
2. **Нульова кількість фаз (`P = 0`)**: Метод повертає `Status::ErrInvalidPhases`.
3. **Нульова кількість реакцій (`R = 0`)**: У чисто фізичних системах без хімічних взаємодій ранг матриці приймається рівним `0`, а число компонентів Гіббса дорівнює кількості сполук `K = N - q`.
4. **Чисельна виродженість стехіометрії**: Якщо коефіцієнти реакцій відрізняються менше ніж на поріг `m_epsilon`, алгоритм об'єднує їх в одну лінійно залежну реакцію.
5. **Розчини електролітів**: У водних розчинах солей додається одне обмеження електронетральності (`q = 1`), що гарантує збереження сумарного заряду розчину.
6. **Наднекритичні флюїди**: При високому тиску та температурі вище критичної точки рідка та газова фази стають нерозрізними (`P = 1`), що автоматично збільшує варіантність системи на 1 ступінь вільності.

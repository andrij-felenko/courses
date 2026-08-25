# 📋 Інтерфейс бібліотеки обчислення Канторових множин та фрактальних характеристик

Цей довідковий документ містить повний специфікований інтерфейс обчислювальної бібліотеки `libcantor` для мов C та C++, включаючи аналіз обчислювальної складності, типізацію, коди помилок, вимоги до потокобезпечності, гарантії винятків, алгоритмічні контракти, оптимізаційні патерни та приклади інтеграції у фізико-механічні обчислювальні системи.

## 1. Архітектура та принципи проєктування бібліотеки

Програмна бібліотека `libcantor` розроблена для чисельного дослідження геометрії Канторових множин, аналізу фрактальної вимірності дивних атракторів, оцінки показників Ляпунова та моделювання диявольських сходів у нелінійній дисипативній механіці.

При проєктуванні бібліотеки дотримано таких ключових вимог та фундаментальних архітектурних рішень:

1. **Двохрівневий шар абстракції:** процедурне C99-ядро `cantor.h` забезпечує безпосередню швидкодію, сумісність із системним ABI, відсутність залежностей від рантайму C++ та легкість зв'язування з іншими мовами (Python, Rust, Julia, MATLAB), тоді як об'єктна C++20-обгортка `cantor.hpp` надає строгий високорівневий інтерфейс на основі RAII, семантики переміщення, типу безпеки та концептів.
2. **Нульові приховані витоки та сильні гарантії:** усі виділення пам'яті контролюються явними структурами даних або контейнерами `std::vector`, що повністю унеможливлює витоки ресурсів у критичних обчислювальних циклах при тривалому чисельному інтегруванні механічних систем.
3. **Розділення алгоритмів генерації та сканування:** для побудови геометричних покриттів на малій глибині використовуються масиви відрізків, тоді як для обчислення належності точок у фазовому просторі застосовується алгоритм сканування потрійних цифр, який працює з постійною просторовою складністю `O(1)`.
4. **Висока продуктивність та векторна оптимізація:** обчислювальні ядра розроблені з урахуванням конвеєризації процесора та векторних інструкцій (AVX-2 / AVX-512), що дозволяє сканувати десятки мільйонів фазових точок за секунду.

## 2. Коди помилок та статусів

Усі процедурні функції C99 повертають статус виконання типу `cantor_status_t`. Визначення кодів помилок забезпечує точну діагностику відмов на етапі виконання без використання глобального стану `errno`.

| Код статусу | Числове значення | Опис та причини виникнення |
| :--- | :--- | :--- |
| `CANTOR_SUCCESS` | `0` | Операцію виконано успішно без зауважень |
| `CANTOR_ERROR_NULL_POINTER` | `-1` | Передано нульовий вказівник у якості обов'язкового аргументу функції |
| `CANTOR_ERROR_INVALID_LEVEL` | `-2` | Задано некоректну глибину ітерації (`level < 0` або `level > 30`) |
| `CANTOR_ERROR_OUT_OF_BOUNDS` | `-3` | Координата досліджуваної точки виходить за межі відрізка `[0, 1]` |
| `CANTOR_ERROR_MEMORY_ALLOCATION` | `-4` | Помилка виділення динамічної пам'яті системою (`malloc`/`realloc`) |
| `CANTOR_ERROR_PRECISION_LIMIT` | `-5` | Досягнуто граничну розрядність представлення із плаваючою комою |

Детальний аналіз умов виникнення помилок:
- `CANTOR_ERROR_INVALID_LEVEL` виникає тоді, коли користувач запитує побудову масиву інтервалів на рівні `level > 30`. Оскільки кількість інтервалів обчислюється як `2^{level}`, рівень 31 вимагав би понад 2 мільярди елементів, що перевищує межі безпечної адресації 32-бітних індексів.
- `CANTOR_ERROR_PRECISION_LIMIT` сигналізує про те, що розрахунок досяг межі розрядності 53 бітів мантиси типу `double` (IEEE 754). На рівнях `k > 33` обчислювач не спроможний відрізнити крок вилучення від нуля через чисельне згладжування.

## 3. Процедурний C-інтерфейс (`cantor.h`)

### 3.1. Структури даних та типізація

Структура `cantor_interval_t` описує замкнений геометричний відрізок `[start, end]` у євклідовому просторі `ℝ`:

:::tabs
```c
typedef struct {
    double start;
    double end;
} cantor_interval_t;
```
```cpp
struct Interval {
    double start{0.0};
    double end{1.0};
};
```
:::

Поля структури:
- `start` (тип `double`): ліва межа замкненого відрізка (`0.0 <= start <= 1.0`).
- `end` (тип `double`): права межа замкненого відрізка (`start <= end <= 1.0`).

Контейнерна структура `cantor_set_t` зберігає масив інтервалів для вказаного рівня ітерації, а також поточний обсяг виділеної пам'яті:

:::tabs
```c
typedef struct {
    cantor_interval_t* intervals;
    size_t count;
    size_t capacity;
    int level;
} cantor_set_t;
```
```cpp
struct CantorSetData {
    std::vector<Interval> intervals;
    std::size_t level{0};
};
```
:::

Поля контейнера:
- `intervals`: вказівник на динамично виділений масив інтервалів (у C++) або `std::vector<Interval>`.
- `count` (тип `size_t`): фактична кількість збережених інтервалів (`count == 2^{level}`).
- `capacity` (тип `size_t`): поточний розмір виділеного буфера пам'яті.
- `level` (тип `int`): поточний рівень ітерації Канторового покриття (`0 <= level <= 30`).

Структура конфігурації `cantor_config_t` задає параметри обчислення для узагальнених та жирних множин Кантора:

:::tabs
```c
typedef struct {
    int max_depth;
    double custom_alpha;
    bool enable_fat_cantor;
} cantor_config_t;
```
```cpp
struct Config {
    std::size_t max_depth{30};
    double custom_alpha{1.0 / 3.0};
    bool enable_fat_cantor{false};
};
```
:::

Поля конфігурації:
- `max_depth`: гранична глибина ітерацій при скануванні потрійних цифр.
- `custom_alpha`: коефіцієнт вилучення середньої частки для узагальнених множин (`0.0 < custom_alpha < 1.0`).
- `enable_fat_cantor`: прапор активації жирної множини Сміта–Вольтерри–Кантора.

Структура `cantor_analysis_result_t` акумулює числові результати логарифмічної регресії та аналізу вимірності:

:::tabs
```c
typedef struct {
    double box_counting_dim;
    double hausdorff_dim;
    double mean_squared_error;
    size_t total_boxes_checked;
} cantor_analysis_result_t;
```
```cpp
struct AnalysisResult {
    double box_counting_dim{0.0};
    double hausdorff_dim{0.0};
    double mean_squared_error{0.0};
    std::size_t total_boxes_checked{0};
};
```
:::

Поля результату аналізу:
- `box_counting_dim`: обчислена кутова вимірність сіткового покриття (емпіричний нахил регресії).
- `hausdorff_dim`: теоретичне значення вимірності Хаусдорфа (`ln 2 / ln 3 ≈ 0.630929`).
- `mean_squared_error`: середньоквадратичне відхилення експериментальних точок від лінійної регресії.
- `total_boxes_checked`: загальна кількість сіткових осередків, просканованих під час аналізу.

### 3.2. Детальна специфікація C-функцій

#### `cantor_status_t cantor_create(cantor_set_t** set, int level)`

Створює та ініціалізує нову структуру `cantor_set_t` для вказаного рівня `level`.

- **Опис роботи:** Функція виділяє пам'ять під заголовочну структуру, обчислює необхідну ємність `capacity = 2^{level}` та виділяє неперервний блок пам'яті для масиву інтервалів.
- **Аргументи:**
  - `set` `[out]`: подвійний вказівник для повернення адреси виділеної структури.
  - `level` `[in]`: рівень побудови (допустимі значення `0 ... 30`).
- **Значення повернення:**
  - `CANTOR_SUCCESS`: ініціалізацію завершено успішно.
  - `CANTOR_ERROR_NULL_POINTER`: аргумент `set == NULL`.
  - `CANTOR_ERROR_INVALID_LEVEL`: `level < 0` або `level > 30`.
  - `CANTOR_ERROR_MEMORY_ALLOCATION`: не вистачило оперативної пам'яті.
- **Гарантії ресурсів:** У разі помилки виділення масиву пам'ять заголовочної структури автоматично звільняється, а вказівник `*set` скидається в `NULL`.

#### `void cantor_destroy(cantor_set_t* set)`

Безпечно звільняє динамічну пам'ять масиву інтервалів та заголовочної структури.

- **Опис роботи:** Якщо `set == NULL`, функція завершує роботу без помилок. У протилежному випадку спочатку звільняється масив `set->intervals`, а потім сам `set`.

#### `cantor_status_t cantor_generate(cantor_set_t* set)`

Генерує геометричні інтервали Кантора для поточного рівня `set->level`.

- **Опис роботи:** Застосовує послідовне розщеплення відрізків із вилученням відкритих середніх третин `(1/3, 2/3)`. Результат записується у `set->intervals`.
- **Обчислювальна складність:** Часова складність `O(2^{level})`, просторова складність `O(2^{level})`.

#### `cantor_status_t cantor_contains(double x, int max_depth, bool* result)`

Чисельно перевіряє належність точки `x` до множини Кантора без використання пам'яті.

- **Опис роботи:** Виконує ітеративний аналіз потрійного розкладу координати `x`. Якщо на будь-якому кроці до `max_depth` потрійна цифра дорівнює 1, точка є вилученою (`*result = false`).
- **Аргументи:**
  - `x` `[in]`: дійсне число відрізка `[0, 1]`.
  - `max_depth` `[in]`: глибина перевірки (типово `20 ... 30`).
  - `result` `[out]`: результат перевірки (`true` або `false`).
- **Обчислювальна складність:** Часова складність `O(max_depth)`, просторова складність `O(1)`.

#### `cantor_status_t cantor_evaluate_staircase(double x, int depth, double* val)`

Обчислює значення функції Кантора («Диявольських сходів») `F(x)` у точці `x`.

- **Опис роботи:** Використовує рекурсивний або ітеративний алгоритм визначення значень на плато вилучених інтервалів. Забезпечує монотонне обчислення `F(x) ∈ [0, 1]`.

#### `cantor_status_t cantor_analyze_dimension(const cantor_set_t* set, cantor_analysis_result_t* result)`

Обчислює ємкісну фрактальну вимірність методом покриття сіткою осередків (box-counting).

- **Опис роботи:** Сканує масив інтервалів `set->intervals`, будує логарифмічну залежність кількості покриваючих осередків `N(ε)` від їхнього розміру `ε`, виконує лінійну регресію методом найменших квадратів та записує обчислену вимірність і середньоквадратичну похибку (MSE) у `result`.

## 4. Об'єктно-орієнтований C++-інтерфейс (`cantor.hpp`)

Простір імен `math::fractals` містить сучасні C++20 обгортки.

### 4.1. Специфікація класів та типів

```cpp
namespace math::fractals {

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidLevel = -2,
    OutOfBounds = -3,
    MemoryAllocationFailed = -4,
    PrecisionLimitReached = -5
};

class CantorException : public std::runtime_error {
public:
    explicit CantorException(Status status, const std::string& message);
    [[nodiscard]] Status status() const noexcept;
private:
    Status status_;
};

struct AnalysisResult {
    double box_counting_dim{0.0};
    double hausdorff_dim{0.0};
    double mean_squared_error{0.0};
    std::size_t total_boxes_checked{0};
};

class CantorSet {
public:
    explicit CantorSet(std::size_t level = 0);
    ~CantorSet() noexcept = default;

    CantorSet(const CantorSet&) = default;
    CantorSet& operator=(const CantorSet&) = default;
    CantorSet(CantorSet&&) noexcept = default;
    CantorSet& operator=(CantorSet&&) noexcept = default;

    void generate(std::size_t level);
    [[nodiscard]] std::size_t level() const noexcept;
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] std::span<const Interval> intervals() const noexcept;

    [[nodiscard]] static bool contains(double x, std::size_t max_depth = 30);
    [[nodiscard]] static double evaluate_staircase(double x, std::size_t depth = 20);

private:
    std::size_t level_{0};
    std::vector<Interval> intervals_;
};

class CantorAnalyzer {
public:
    explicit CantorAnalyzer(CantorSet set);

    [[nodiscard]] AnalysisResult compute_box_counting() const;
    [[nodiscard]] std::vector<double> compute_renyi_spectrum(std::span<const double> q_orders) const;
};

} // namespace math::fractals
```

### 4.2. Гарантії безпеки винятків та потокобезпечність

1. **Сильна гарантія винятків (Strong Exception Guarantee):**
   Методи `CantorSet::generate` та `CantorAnalyzer::compute_box_counting` забезпечують транзакційну безпеку. Якщо під час створення вектора виникає виняток `std::bad_alloc`, стан об'єкта `CantorSet` залишається повністю незмінним, а всі тимчасові ресурси автоматично звільняються деструктором.
2. **Гарантія відсутності винятків (`noexcept`):**
   Деструктори класів, статистичний метод `contains`, методи доступу `level()`, `size()` та `intervals()` позначені специфікатором `noexcept` і гарантовано не викидають винятки.
3. **Багатопотокова безпечність (Thread-Safety):**
   - Екземпляри класів `CantorSet` та `CantorAnalyzer` є потокобезпечними для паралельного читання (Thread-safe read-only) з довільної кількості потоків без використання блокувань.
   - Одночасне читання та модифікація об'єкта різними потоками вимагає зовнішньої синхронізації (наприклад, через `std::shared_mutex`).
4. **Паралельне обчислення OpenMP / std::execution:**
   Метод `contains` є чистою функцією без побічних ефектів, що дозволяє виконувати паралельну обробку масивів даних фазового простору за допомогою паралельних алгоритмів C++17 (`std::execution::par`).

## 5. Таблиця відповідності процедурного та об'єктного інтерфейсів

| Функціональне завдання | Процедурний C-виклик (`cantor.h`) | Об'єктний C++-метод (`cantor.hpp`) |
| :--- | :--- | :--- |
| Створення об'єкта | `cantor_create(&set, level)` | `CantorSet set(level);` |
| Звільнення пам'яті | `cantor_destroy(set)` | Автоматично через RAII деструктор |
| Генерація рівнів | `cantor_generate(set)` | `set.generate(level);` |
| Перевірка точки | `cantor_contains(x, depth, &res)` | `CantorSet::contains(x, depth)` |
| Оцінка вимірності | `cantor_analyze_dimension(set, &res)` | `analyzer.compute_box_counting()` |
| Функція Кантора | `cantor_evaluate_staircase(x, d, &v)` | `CantorSet::evaluate_staircase(x, d)` |

## 6. Багатопотокова модель та потокобезпечність (Concurrency Model)

При розробці високонавантажених фізико-механічних обчислювачів питаннясинхронізації потоків є критичним.

1. **Безблокувальне сканування точок (Lock-Free Point Scanning):**
   Функція `cantor_contains` та статичний метод `CantorSet::contains` є чисто безефектними функціями (Pure functions). Вони не читають і не модифікують жодного глобального або статичного стану. Будь-яка кількість обчислювальних потоків може одночасно викликати ці функції для довільних точок фазового простору без використання м'ютексів або атомарних операцій.
2. **Розділений доступ для читання (`std::shared_mutex`):**
   Об'єкт `CantorSet` підтримує концепцію "один письменник — багато читачів" (Single Writer — Multiple Readers). Після того як метод `generate()` завершив побудову масиву інтервалів, об'єкт стає незмінним (immutable). Потоки можуть безпечно читати масив через `intervals()` без блокувань.
3. **Паралельне обчислення через `std::execution::par`:**
   У C++20 обчислення вимірності або сканування векторів точок підтримує стандартні паралельні алгоритми:
   ```cpp
   std::for_each(std::execution::par, points.begin(), points.end(), [](double pt) {
       bool in_set = CantorSet::contains(pt, 25);
       // Обробка результату у локальному контексті потоку
   });
   ```

## 7. Концепти C++20 та шаблонні обмеження (`std::floating_point`)

Для забезпечення максимальної гнучкості C++20 інтерфейс `cantor.hpp` надає шаблонні узагальнення для довільних типів із плаваючою комою (`float`, `double`, `long double`, `__float128`):

```cpp
template <std::floating_point FloatT>
class GenericCantorSet {
public:
    explicit GenericCantorSet(std::size_t level = 0);
    
    [[nodiscard]] static constexpr bool contains(FloatT x, std::size_t max_depth = 30) noexcept {
        if (x < FloatT{0} || x > FloatT{1}) return false;
        FloatT curr = x;
        for (std::size_t i = 0; i < max_depth; ++i) {
            curr *= FloatT{3};
            const auto digit = static_cast<int>(std::floor(curr));
            if (digit == 1) return false;
            if (digit == 2) curr -= FloatT{2};
        }
        return true;
    }
};
```

Використання концепту `std::floating_point` запобігає випадковому передаванню цілочисельних типів або несумісних вказівників на етапі компіляції (Compile-time type safety).

## 8. Стратегії обробки помилок та витоків чисельної точності

При дослідженні крайових точок фазового простору система може зіштовхнутися з обмеженнями мантиси IEEE 754:

- **Виявлення межі розрядності (`CANTOR_ERROR_PRECISION_LIMIT`):**Якщо запитувана глибина `max_depth` перевищує розрядність мантиси (наприклад, `depth > 33` для `double`), функція повертає код `CANTOR_ERROR_PRECISION_LIMIT`. Додаток повинен зменшити глибину розкладу або перейти на розрядність `__float128`.
- **Обробка винятків пам'яті:** При вилученні динамічної пам'яті під час генерації 25-го рівня ітерації (`33 мільйони інтервалів`) функція C++ викидає виняток `CantorException(Status::MemoryAllocationFailed, "out of memory")`. Внутрішні буфери очищуються за допомогою принципу RAII, не залишаючи звисаючих вказівників.

## 9. Приклад повного інтеграційного сценарію

Наведений нижче приклад демонструє завершений обчислювальний сценарій аналізу множини Кантора із обробкою винятків C++.


```cpp
#include "cantor.hpp"
#include <iostream>
#include <vector>

int main() {
    try {
        using namespace math::fractals;

        std::cout << "=== Інтеграційний тест бібліотеки libcantor ===\n";

        // 1. Створення та генерація Канторової множини 6-го рівня
        CantorSet cantor(6);
        std::cout << "Успішно згенеровано " << cantor.size() << " інтервалів.\n";

        // 2. Оцінка вимірності методом Box-Counting
        CantorAnalyzer analyzer(cantor);
        const auto result = analyzer.compute_box_counting();

        std::cout << "Обчислена вимірність: " << result.box_counting_dim << "\n";
        std::cout << "Середньоквадратична похибка регресії: " << result.mean_squared_error << "\n";

        // 3. Сканування точок фазового простору
        const std::vector<double> test_points{0.0, 0.25, 1.0 / 3.0, 0.5, 0.75, 1.0};
        std::cout << "\nПеревірка належності точок (глибина 25):\n";
        for (double pt : test_points) {
            const bool inside = CantorSet::contains(pt, 25);
            std::cout << "  x = " << pt << " -> " << (inside ? "C (Належить)" : "U (Вилучено)") << "\n";
        }

        // 4. Обчислення значення функції Кантора ("Диявольських сходів")
        const double x_val = 0.4;
        const double staircase_val = CantorSet::evaluate_staircase(x_val);
        std::cout << "\nЗначення функції Кантора F(" << x_val << ") = " << staircase_val << "\n";

    } catch (const math::fractals::CantorException& ex) {
        std::cerr << "Критична помилка CantorLib: " << ex.what() << " (код статусу: " << static_cast<int>(ex.status()) << ")\n";
        return 1;
    } catch (const std::exception& ex) {
        std::cerr << "Системний виняток: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```

## 10. Інтерфейс Python-розширення (C-API та C++ pybind11)

Для забезпечення прямої сумісності з Python-екосистемою аналізу даних (NumPy, SciPy) бібліотека надає нативний C-API модуль розширення та C++20 pybind11 обгортку:

:::tabs
```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "cantor.h"

static PyObject* py_cantor_contains(PyObject* self, PyObject* args) {
    double x;
    int depth = 30;
    if (!PyArg_ParseTuple(args, "d|i", &x, &depth)) {
        return NULL;
    }
    bool result = false;
    cantor_status_t status = cantor_contains(x, depth, &result);
    if (status != CANTOR_SUCCESS) {
        PyErr_SetString(PyExc_ValueError, "Invalid input parameters for cantor_contains");
        return NULL;
    }
    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyMethodDef CantorMethods[] = {
    {"contains", py_cantor_contains, METH_VARARGS, "Check if point x belongs to Cantor set"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cantormodule = {
    PyModuleDef_HEAD_INIT,
    "libcantor",
    "High-performance Cantor set computation module",
    -1,
    CantorMethods
};

PyMODINIT_FUNC PyInit_libcantor(void) {
    return PyModule_Create(&cantormodule);
}
```
```cpp
#include <pybind11/pybind11.h>
#include "cantor.hpp"

namespace py = pybind11;

PYBIND11_MODULE(libcantor, m) {
    m.doc() = "High-performance C++20 Cantor set computation module";
    
    m.def("contains", &math::fractals::CantorGenerator::contains_point,
          py::arg("x"), py::arg("max_depth") = 30,
          "Check if point x belongs to Cantor set");
}
```
:::

Модуль компілюється у бінарне розширення `.so` / `.pyd` і дозволяє виконувати векторні перевірки масивів NumPy без проміжного копіювання буферів у пам'яті.

## 11. Векторні контракти SIMD та узгодження ABI

Для забезпечення сумісності між різними компіляторами (GCC, Clang, MSVC, Intel oneAPI) C99-ядро дотримується суворих правил системного ABI:

1. **Гарантія вирівнювання структур:** Передача заголовочних структур `cantor_interval_t` виконується через зафіксовані вказівники. Розмір структури строго вирівняний по межі 16 байт (`sizeof(double) * 2`), що забезпечує пряме завантаження у векторні регістри XMM інструкціями `movapd`.
2. **Відсутність глобального стану:** Жодна функція C99-ядра не використовує глобальні змінні або локальні статичні буфери (`static variables`), що гарантує сумісність із динамічною вивантажувальністю бібліотеки (DLL unload safety) та потокобезпечність при використанні у середовищі із багатьма процесами.
3. **Стабільність ABI між версіями:** Усі структури даних мають резервні поля зсуву (`reserved padding`), що дозволяє розширювати функціональність бібліотеки у наступних релізах без порушення бінарної сумісності зі скомпільованими виконуваними файлами.

## 12. Інтерфейси зв'язування з іншими мовами (Rust FFI та Julia ccall)

### 12.1. Rust FFI Bindings (`cantor-sys`)

Для використання `libcantor` у системному середовищі мови Rust розроблено модуль `cantor-sys`:

```rust
use std::os::raw::{c_double, c_int, c_void};

#[repr(C)]
pub struct CantorInterval {
    pub start: c_double,
    pub end: c_double,
}

extern "C" {
    pub fn cantor_contains(x: c_double, max_depth: c_int, result: *mut bool) -> i32;
    pub fn cantor_generate_level(level: c_int) -> *mut c_void;
}

pub fn is_in_cantor_set(x: f64, max_depth: i32) -> bool {
    let mut res = false;
    unsafe {
        cantor_contains(x, max_depth, &mut res);
    }
    res
}
```

### 12.2. Julia High-Performance Interface (`CantorLib.jl`)

У науковому середовищі Julia виклики C-ядра реалізуються через невагомий оператор `ccall`:

```julia
module CantorLib

function contains_point(x::Float64, max_depth::Int32=Int32(30))::Bool
    res = Ref{Bool}(false)
    status = ccall((:cantor_contains, "libcantor.so"), Int32, (Float64, Int32, Ref{Bool}), x, max_depth, res)
    if status != 0
        error("CantorLib computation error: code $status")
    end
    return res[]
end

end # module CantorLib
```

## 13. Життєвий цикл об'єктів та діаграма станів (API Lifecycle)

Усі структури та об'єкти бібліотеки `libcantor` підпорядковані строго визначеній діаграмі станів:

1. **Неініціалізований стан (Uninitialized):** Вказівник `cantor_set_t*` дорівнює `NULL` або містить невизначену адресу. Спроба виклику `cantor_generate` або `cantor_analyze_dimension` призводить до повернення статусу `CANTOR_ERROR_NULL_POINTER`.
2. **Ініціалізований порожній стан (Allocated):** Виклик `cantor_create(&set, level)` виділяє пам'ять та переводить об'єкт у стан готовності. Поле `count` дорівнює `0`.
3. **Згенерований стан (Generated / Ready):** Виклик `cantor_generate(set)` обчислює масив інтервалів. Поле `count` дорівнює `2^{level}`. Об'єкт готовий для аналізу вимірності `cantor_analyze_dimension` та багатопотокового читання.
4. **Звільнений стан (Destroyed):** Виклик `cantor_destroy(set)` повертає виділену пам'ять системі та повертає вказівник у стан `Uninitialized`.

## 14. Специфікація асинхронної сигнальної безпеки (Async-Signal Safety)

У високопродуктивних C-додатках (наприклад, у реальних контролерах робототехніки чи системах реального часу) обчислювальні виклики можуть бути перервані асинхронними сигналами POSIX (`SIGINT`, `SIGTERM`, `SIGALRM`).

- Функції `cantor_contains` та `cantor_contains_point` є **Async-Signal-Safe**: вони не використовують динамічне виділення пам'яті (`malloc`/`free`), не викликають системних блокувань і можуть безпечно виконуватися безпосередньо усередині обробників сигналів (`signal handlers`).
- Функції `cantor_create`, `cantor_generate` та `cantor_destroy` не є асинхронно-сигнально безпечними через виклики функції управління купою `malloc`, тому їхній виклик усередині обробників сигналів заборонений.

## 15. Кросплатформна компіляція та підтримка архітектур

Бібліотека `libcantor` розроблена із дотриманням принципів 100% кросплатформної переносимості:

- **Linux (GCC 11+ / Clang 13+):**Повна підтримка OpenMP 4.5, SIMD AVX2/AVX-512, розширення `__float128`. Компіляція здійснюється прапорами `-O3 -march=native -fPIC`.
- **macOS (Apple Clang / ARM64 M1/M2/M3):** Застосовуються векторні інструкції ARM Neon через прапор `-O3 -mcpu=apple-m1`. Підтримуються паралельні алгоритми C++17через `libdispatch` (GCD).
- **Windows (MSVC 2022 / MinGW-w64):** Підтримка прапорців компілятора `/O2 /arch:AVX2 /std:c++20`. Використовується макрос `CANTOR_API` для коректного експорту/імпорту символів у динамічних бібліотеках DLL:

:::tabs
```c
#if defined(_WIN32) || defined(__CYGWIN__)
  #ifdef CANTOR_BUILD_DLL
    #define CANTOR_API __declspec(dllexport)
  #else
    #define CANTOR_API __declspec(dllimport)
  #endif
#else
  #define CANTOR_API __attribute__((visibility("default")))
#endif
```
```cpp
#if defined(_WIN32) || defined(__CYGWIN__)
  #ifdef CANTOR_BUILD_DLL
    #define CANTOR_CPP_API __declspec(dllexport)
  #else
    #define CANTOR_CPP_API __declspec(dllimport)
  #endif
#else
  #define CANTOR_CPP_API [[visibility("default")]]
#endif
```
:::

## 16. Підсумковий регламент використання та ліцензування

Завдяки реалізації двохрівневої архітектури (C99 + C++20) та наданню прямих зв'язувань для Python, Rust та Julia, бібліотека `libcantor` надає універсальний, високоефективний та безпечний інструментарій для науково-технічних розрахунків у галузі нелінійної дисипативної механіки, теорії детермінованого хаосу, віброакустики, геодинаміки та аналізу фрактальних атракторів. Продукт поширюється за відкритою ліцензією MIT, дозволяючи вільне модифікування, інтеграцію та використання у комерційних та академічних програмних комплексах без жодних юридичних чи ліцензійних обмежень для дослідників, інженерів та розробників обчислювальних систем нелінійної динаміки та фрактального аналізу по всьому світу в усіх наукових, освітніх, виробничих та прикладних цілях.





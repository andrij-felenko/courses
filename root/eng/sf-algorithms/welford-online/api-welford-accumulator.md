# 📋 Специфікація інтерфейсу потокового акумулятора (C/C++ API)

<preknowlist>
- [Вибіркова дисперсія](root:math-probability/sample-variance) — інтерпретація розрахованих статистичних оцінок.
- [Похибка машинної арифметики](root:math-numeric/float-arithmetic-error) — вимоги до числової стабільності інтерфейсів.
</preknowlist>

Інтерфейс потокового акумулятора надає мінімальний, детермінований і високопродуктивний набір функцій для однопрохідного розрахунку описових статистик у системах реального часу. Контракт гарантує нульове динамічне виділення пам'яті під час роботи, строгу числову стійкість до зсуву вихідних даних та повну потокобезпечність на рівні окремих екземплярів структури.

Бібліотека спроектована для роботи в критичних за затримками середовищах: обробниках мережевих переривань, ядрах операційних систем, вбудованих прошивках систем керування та серверах високочастотної фінансової аналітики. Конструкція типів забезпечує сумісність як із класичними мовами низького рівня (C99/C11), так і з сучасними стандартами C++20 через механізми статичного поліморфізму та концептів.

### 1. Загальні характеристики контракту

| Властивість | Значення | Примітка |
|---|---|---|
| Просторова складність | `O(1)` пам'яті на екземпляр | Рівно 64 байти стану (один кеш-рядок процесора) |
| Часова складність оновлення | `O(1)` операцій на відлік | Не містить розгалужень у гарячому тракті обчислень |
| Часова складність злиття | `O(1)` операцій | Повне об'єднання двох вибірок довільного розміру |
| Динамічна пам'ять | `0` байтів (`no heap allocation`) | Усі структури розміщуються на стеку або у статичній пам'яті |
| Потокобезпечність | Неблокуюча незалежність | Різні потоки можуть паралельно писати у власні екземпляри без синхронізації |
| Стандарт мов | C99 / C++20 | Сумісність з автономними середовищами (`freestanding`) |

### 2. Типи даних та структури стану

Основна структура накопичувача містить внутрішній стан розрахунку перших чотирьох моментів та допоміжних екстремумів:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t count;      /* Загальна кількість врахованих спостережень (n) */
    double mean;         /* Поточне вибіркове середнє (перший сирий момент M1) */
    double M2;           /* Сума квадратів відхилень: ∑(x - μ)² */
    double M3;           /* Сума кубів відхилень: ∑(x - μ)³ */
    double M4;           /* Сума четвертих степенів відхилень: ∑(x - μ)⁴ */
    double min_val;      /* Найменше зафіксоване значення у вибірці */
    double max_val;      /* Найбільше зафіксоване значення у вибірці */
} welford_acc_t;
```
```cpp
#include <cstdint>
#include <limits>

namespace stats {

template <typename FloatType = double>
struct AccumulatorState {
    std::uint64_t count{0};
    FloatType mean{0.0};
    FloatType M2{0.0};
    FloatType M3{0.0};
    FloatType M4{0.0};
    FloatType min_val{std::numeric_limits<FloatType>::infinity()};
    FloatType max_val{-std::numeric_limits<FloatType>::infinity()};
};

} // namespace stats
```
:::

#### Інваріанти стану та просторове розміщення

У будь-який момент часу між викликами функцій оновлення для коректного екземпляра акумулятора гарантуються такі математичні інваріанти:
1. `count >= 0`.
2. Якщо `count == 0`, то `mean == 0.0`, `M2 == 0.0`, `M3 == 0.0`, `M4 == 0.0`, `min_val == +INFINITY`, `max_val == -INFINITY`.
3. Якщо `count == 1`, то `mean == x_1`, `M2 == 0.0`, `M3 == 0.0`, `M4 == 0.0`, `min_val == max_val == x_1`.
4. Для будь-якого `count >= 2` виконується умова невід'ємності: `M2 >= 0.0` та `M4 >= 0.0`.
5. `min_val <= mean <= max_val`.

Розмір структури становить рівно 56 байтів корисного навантаження (сім 8-байтних полів: 1 цілочисельний лічильник та 6 чисел подвійної точності). При вирівнюванні за межею 64 байтів структура доповнюється 8 байтами невикористаного заповнення (padding), що повністю запобігає перетину меж кеш-ліній під час читання та запису даних процесором.

### 3. Коди статусів та обробка помилок

Для функцій, що повертають діагностичний стан або перевіряють коректність числових операцій, використовується єдиний набір кодів завершення:

:::tabs
```c
typedef enum {
    WELFORD_OK                = 0,  /* Успішне виконання */
    WELFORD_ERR_NULL_PTR      = 1,  /* Передано нульовий покажчик */
    WELFORD_ERR_INSUFFICIENT  = 2,  /* Недостатньо спостережень для оцінки (n < 2) */
    WELFORD_ERR_DEGENERATE    = 3,  /* Вироджена вибірка (дисперсія дорівнює нулю) */
    WELFORD_ERR_NAN_INPUT     = 4   /* Відкинуто нечислове вхідне значення NaN */
} welford_status_t;
```
```cpp
#include <cstdint>

namespace stats {

enum class Status : std::uint8_t {
    Ok = 0,
    NullPointer = 1,
    InsufficientData = 2,
    DegenerateSample = 3,
    NanInput = 4
};

} // namespace stats
```
:::

Код `WELFORD_ERR_INSUFFICIENT` повертається функціями розрахунку вибіркової дисперсії або коваріації, якщо розмір вибірки `count < 2`. У такому стані число ступенів свободи `n - 1` дорівнює нулю, і математична оцінка не визначена. 

Статус `WELFORD_ERR_DEGENERATE` виникає під час спроби обчислити нормалізовані коефіцієнти форми (асиметрію чи ексцес) або нахил лінії лінійної регресії для вибірки, де всі елементи ідентичні (тобто сума квадратів `M2 <= 1e-15`). У цьому разі ділення на нульову дисперсію блокується на рівні інтерфейсу, запобігаючи генерації нечислових значень `NaN` або переповнень `+Inf`.

### 4. Функції життєвого циклу та мутації

#### Ініціалізація акумулятора

:::tabs
```c
/* Ініціалізує новий акумулятор або скидає наявний стан */
void welford_init(welford_acc_t *acc);
```
```cpp
namespace stats {

template <typename FloatType = double>
class StreamingAccumulator {
public:
    constexpr StreamingAccumulator() noexcept = default;
    void reset() noexcept;
};

} // namespace stats
```
:::

- **Призначення:** ініціалізує новий акумулятор або скидає наявний стан до початкових нульових значень.
- **Параметри:** `acc` — вказівник на структуру накопичувача. Якщо передано `NULL`, функція виконує безпечне повернення без дій.
- **Передмови:** пам'ять під структуру `acc` повинна бути попередньо виділена викликачем.
- **Післямови:** усі поля структури встановлено у початковий стан відповідно до інваріанту `count == 0`.
- **Часова складність:** `O(1)`.

#### Додавання одного спостереження

:::tabs
```c
/* Додає одне спостереження за рекурентними формулами Велфорда-Пебея */
void welford_push(welford_acc_t *acc, double x);
```
```cpp
namespace stats {

template <typename FloatType = double>
void StreamingAccumulator<FloatType>::push(FloatType x) noexcept;

} // namespace stats
```
:::

- **Призначення:** додає одне нове числове спостереження `x` до потоку, оновлюючи середнє значення та центральні моменти за рекурентними формулами Велфорда-Пебея.
- **Параметри:** `acc` — вказівник на дійсний екземпляр накопичувача; `x` — дійсне число.
- **Обробка виняткових значень:** якщо `x` є нечисловим значенням (`isnan(x) == true`), виклик ігнорується, стан акумулятора не змінюється.
- **Часова складність:** `O(1)`, містить рівно 1 ділення, 14 множень та 8 додавань/віднімань чисел із рухомою комою.

#### Пакетне додавання спостережень

:::tabs
```c
/* Послідовно додає масив спостережень довжиною length */
void welford_push_batch(welford_acc_t *acc, const double *data, size_t length);
```
```cpp
#include <span>

namespace stats {

template <typename FloatType = double>
void StreamingAccumulator<FloatType>::push_batch(std::span<const FloatType> batch) noexcept;

} // namespace stats
```
:::

- **Призначення:** послідовно додає масив неперервно розташованих у пам'яті спостережень довжиною `length`.
- **Параметри:** `acc` — вказівник на екземпляр накопичувача; `data` / `batch` — масив значень.
- **Особливості оптимізації:** пакетний метод мінімізує накладні витрати на виклик функцій через інлайнінг внутрішнього циклу і дає змогу компілятору оптимізувати доступ до пам'яті завдяки послідовному зчитуванню кеш-рядків.
- **Часова складність:** `O(length)`.

#### Паралельне злиття двох акумуляторів

:::tabs
```c
/* Об'єднує два незалежні акумулятори за формулами Чена-Пебея */
void welford_merge(welford_acc_t *dst, const welford_acc_t *src);
```
```cpp
namespace stats {

template <typename FloatType = double>
StreamingAccumulator<FloatType>& StreamingAccumulator<FloatType>::operator+=(
    const StreamingAccumulator<FloatType>& other) noexcept;

} // namespace stats
```
:::

- **Призначення:** виконує паралельне об'єднання двох незалежних акумуляторів за формулами Чена-Пебея. Результат записується в `dst`.
- **Властивості:** операція є строго математично асоціативною та комутативною з точністю до похибок машинного заокруглення. Вона дає змогу агрегувати результати паралельних обчислювальних потоків або розподілених вузлів кластера без перегляду вихідних сирих даних.
- **Часова складність:** `O(1)`.

### 5. Двовимірний акумулятор коваріації та лінійної регресії

Для аналізу взаємозв'язку між двома потоковими змінними `X` та `Y` інтерфейс надає спеціалізовану структуру `welford_cov_acc_t`:

:::tabs
```c
typedef struct {
    uint64_t count;      /* Кількість пар спостережень (n) */
    double mean_x;       /* Поточне середнє змінної X */
    double mean_y;       /* Поточне середнє змінної Y */
    double M2_x;         /* Сума квадратів відхилень X: ∑(x - μ_x)² */
    double M2_y;         /* Сума квадратів відхилень Y: ∑(y - μ_y)² */
    double C_xy;         /* Сума добутків відхилень: ∑(x - μ_x)(y - μ_y) */
} welford_cov_acc_t;

void welford_cov_init(welford_cov_acc_t *acc);
void welford_cov_push(welford_cov_acc_t *acc, double x, double y);
double welford_covariance(const welford_cov_acc_t *acc);
double welford_correlation(const welford_cov_acc_t *acc);
```
```cpp
#include <cstdint>
#include <cmath>

namespace stats {

template <typename FloatType = double>
class CovarianceAccumulator {
public:
    constexpr CovarianceAccumulator() noexcept = default;
    void push(FloatType x, FloatType y) noexcept;
    [[nodiscard]] FloatType covariance() const noexcept;
    [[nodiscard]] FloatType correlation() const noexcept;
    [[nodiscard]] std::uint64_t count() const noexcept;

private:
    std::uint64_t count_{0};
    FloatType mean_x_{0.0};
    FloatType mean_y_{0.0};
    FloatType M2_x_{0.0};
    FloatType M2_y_{0.0};
    FloatType C_xy_{0.0};
};

} // namespace stats
```
:::

- `welford_covariance` повертає вибіркову незміщену коваріацію `Cov(X, Y) = C_xy / (n - 1)`. При `n < 2` повертає `0.0`.
- `welford_correlation` повертає вибірковий коефіцієнт кореляції Пірсона `r = C_xy / sqrt(M2_x * M2_y)`. Діапазон значень становить `[-1.0, 1.0]`. Якщо дисперсія хоча б однієї змінної дорівнює нулю, повертає `0.0`.

### 6. Функції отримання статистичних оцінок

Усі функції цієї групи є чистими (лише для читання) і не змінюють внутрішнього стану акумулятора.

:::tabs
```c
/* Отримання незміщеної вибіркової дисперсії (s²) */
double welford_sample_variance(const welford_acc_t *acc);

/* Отримання генеральної дисперсії (σ²) */
double welford_population_variance(const welford_acc_t *acc);

/* Отримання вибіркового середньоквадратичного відхилення (s) */
double welford_stddev(const welford_acc_t *acc);

/* Отримання коефіцієнта асиметрії вибірки (g1) */
double welford_skewness(const welford_acc_t *acc);

/* Отримання коефіцієнта ексцесу (g2, excess kurtosis) */
double welford_kurtosis(const welford_acc_t *acc);
```
```cpp
namespace stats {

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::sample_variance() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::population_variance() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::stddev() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::skewness() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::kurtosis() const noexcept;

} // namespace stats
```
:::

- `sample_variance`: повертає незміщену вибіркову дисперсію `s² = M2 / (n - 1)`. При `count < 2` повертає `0.0`.
- `population_variance`: повертає зміщену генеральну дисперсію `σ² = M2 / n`. При `count == 0` повертає `0.0`.
- `stddev`: повертає середньоквадратичне відхилення `s = sqrt(sample_variance)`. Завжди невід'ємне число.
- `skewness`: повертає коефіцієнт асиметрії `g1 = (M3 / n) / (M2 / n)^(3/2)`. При симетричному розподілі дорівнює `0.0`. Від'ємні значення відповідають довгому лівому хвосту, додатні — правому.
- `kurtosis`: повертає надлишковий ексцес `g2 = (M4 / n) / (M2 / n)² - 3.0`. Для стандартного гаусового розподілу дорівнює `0.0`. Додатні значення сигналізують про високу концентрацію навколо середнього та наявність важких хвостів.

### 7. Вимоги до апаратної платформи та вирівнювання

Для забезпечення найвищої продуктивності у багатопотокових обчисленнях рекомендується розміщувати екземпляри акумулятора за межами кеш-ліній із вирівнюванням на 64 байти:

:::tabs
```c
#if defined(__GNUC__) || defined(__clang__)
typedef struct __attribute__((aligned(64))) {
    uint64_t count;
    double mean;
    double M2;
    double M3;
    double M4;
    double min_val;
    double max_val;
} welford_aligned_acc_t;
#elif defined(_MSC_VER)
typedef __declspec(align(64)) struct {
    uint64_t count;
    double mean;
    double M2;
    double M3;
    double M4;
    double min_val;
    double max_val;
} welford_aligned_acc_t;
#endif
```
```cpp
#include <cstdint>
#include <new>

namespace stats {

template <typename FloatType = double>
struct alignas(64) AlignedAccumulatorState {
    std::uint64_t count{0};
    FloatType mean{0.0};
    FloatType M2{0.0};
    FloatType M3{0.0};
    FloatType M4{0.0};
    FloatType min_val{0.0};
    FloatType max_val{0.0};
};

} // namespace stats
```
:::

Це запобігає ефекту хибного спільного використання пам'яті (false sharing), коли два процесорні ядра одночасно інвалідують кеш-лінії одне одного під час оновлення сусідніх у пам'яті статистичних структур.

У неблокуючих односпрямованих кільцевих буферах (Single-Producer Single-Consumer чергах) передача знімка стану акумулятора між обчислювальним потоком і потоком візуалізації вимагає використання бар'єрів пам'яті:

- Потік-виробник виконує копіювання локальної структури `welford_acc_t` у спільний буфер і викликає інструкцію звільнення пам'яті (`atomic_thread_fence(memory_order_release)`).
- Потік-споживач зчитує індикатор оновлення з семантикою придбання (`memory_order_acquire`), гарантуючи узгодженість усіх числових полів без використання блокуючих м'ютексів.
- Такий підхід забезпечує обробку статистичних знімків телеметрії з нульовим часом очікування (zero-latency) у високошвидкісних системах збору даних.

# ⚙️ Реалізація потокового статистичного акумулятора для високих навантажень

<preknowlist>
- [Вибіркова дисперсія](root:math-probability/sample-variance) — базові статистичні характеристики вибірки.
- [Похибка машинної арифметики](root:math-numeric/float-arithmetic-error) — усунення катастрофічного скасування в числових алгоритмах.
</preknowlist>

У системах телеметрії реального часу, мережевих зондах та обробці сенсорних сигналів пам'ять пристрою суворо обмежена, а швидкість надходження даних може перевищувати мільйони відліків на секунду. Збереження всіх значень у динамічному масиві для наступного розрахунку статистик є неприйнятним як через перевитрату оперативної пам'яті (`O(N)`), так і через непередбачувані затримки виділення пам'яті (паузи алокатора або збирача сміття).

Потоковий акумулятор на основі алгоритму Велфорда та формул Чена розв'язує цю задачу з константною пам'яттю `O(1)` і константним часом `O(1)` на кожен елемент, підтримуючи обчислення середнього значення, вибіркової та генеральної дисперсії, середньоквадратичного відхилення, асиметрії, ексцесу та паралельне об'єднання часткових результатів із різних ядер процесора.

### Структура стану акумулятора та вирівнювання пам'яті

Для повного розрахунку перших чотирьох статистичних моментів стан акумулятора містить лише 5 числових полів подвійної точності (`double`), два поля для меж діапазону (`min`/`max`) та лічильник кількості спостережень `uint64_t`. Загальний обсяг структури становить 64 байти, що точно відповідає розміру одного стандартного кеш-рядка архітектури x86-64 та ARM64. Це виключає розщеплення структури між двома лініями кешу (cache line split) і гарантує максимальну пропускну здатність шини пам'яті під час послідовної обробки потоку.

Порядок оновлення змінних у функції додавання нового значення має критичне значення: обчислення суми четвертих (`M4`) та третіх (`M3`) степенів відхилень спирається на попередні значення `M2` та `M3`. Якщо оновити `M2` першим, старе значення буде втрачено, що призведе до спотворення коефіцієнтів ексцесу та асиметрії. Тому алгоритм спочатку оновлює середнє, потім використовує різницю для оновлення `M4` та `M3`, і лише наприкінці фіксує нове значення `M2`.

Нижче наведено повнофункціональну реалізацію потокового акумулятора мовами C та C++ з підтримкою поодиноких спостережень, пакетної обробки, зважених вибірок та паралельного злиття.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Потоковий статистичний акумулятор 1-4 моментів */
typedef struct {
    uint64_t count;      /* Кількість спостережень (n) */
    double mean;         /* Поточне вибіркове середнє (M1) */
    double M2;           /* Сума квадратів відхилень: ∑(x - μ)² */
    double M3;           /* Сума кубів відхилень: ∑(x - μ)³ */
    double M4;           /* Сума четвертих степенів: ∑(x - μ)⁴ */
    double min_val;      /* Мінімальне значення у вибірці */
    double max_val;      /* Максимальне значення у вибірці */
} welford_acc_t;

/* Ініціалізація або скидання акумулятора */
void welford_init(welford_acc_t *acc) {
    if (!acc) return;
    acc->count = 0;
    acc->mean = 0.0;
    acc->M2 = 0.0;
    acc->M3 = 0.0;
    acc->M4 = 0.0;
    acc->min_val = INFINITY;
    acc->max_val = -INFINITY;
}

/* Додавання одного спостереження за алгоритмом Велфорда-Пебея */
void welford_push(welford_acc_t *acc, double x) {
    if (!acc || isnan(x)) return;

    acc->count++;
    uint64_t n = acc->count;

    if (x < acc->min_val) acc->min_val = x;
    if (x > acc->max_val) acc->max_val = x;

    if (n == 1) {
        acc->mean = x;
        acc->M2 = 0.0;
        acc->M3 = 0.0;
        acc->M4 = 0.0;
        return;
    }

    double delta = x - acc->mean;
    double delta_n = delta / (double)n;
    double delta_n2 = delta_n * delta_n;
    double term1 = delta * delta_n * (double)(n - 1);

    /* Оновлення середнього */
    acc->mean += delta_n;

    /* Оновлення вищих моментів (від старших до молодших) */
    acc->M4 += term1 * delta_n2 * (double)(n * n - 3 * n + 3) +
               6.0 * delta_n2 * acc->M2 - 4.0 * delta_n * acc->M3;
    acc->M3 += term1 * delta_n * (double)(n - 2) - 3.0 * delta_n * acc->M2;
    acc->M2 += term1;

    /* Захист від машинного нуля нижче порогу точності */
    if (acc->M2 < 0.0) acc->M2 = 0.0;
    if (acc->M4 < 0.0) acc->M4 = 0.0;
}

/* Пакетне додавання масиву значень */
void welford_push_batch(welford_acc_t *acc, const double *data, size_t length) {
    if (!acc || !data) return;
    for (size_t i = 0; i < length; ++i) {
        welford_push(acc, data[i]);
    }
}

/* Паралельне об'єднання двох акумуляторів (формули Чена-Пебея) */
void welford_merge(welford_acc_t *dst, const welford_acc_t *src) {
    if (!dst || !src || src->count == 0) return;
    if (dst->count == 0) {
        *dst = *src;
        return;
    }

    uint64_t n_a = dst->count;
    uint64_t n_b = src->count;
    uint64_t n_ab = n_a + n_b;
    double delta = src->mean - dst->mean;
    double delta2 = delta * delta;
    double delta3 = delta2 * delta;
    double delta4 = delta3 * delta;

    double n_a_f = (double)n_a;
    double n_b_f = (double)n_b;
    double n_ab_f = (double)n_ab;

    /* Нове об'єднане середнє */
    dst->mean += delta * (n_b_f / n_ab_f);

    /* Нові об'єднані моменти */
    double new_m4 = dst->M4 + src->M4 +
                    delta4 * (n_a_f * n_b_f * (n_a_f * n_a_f - n_a_f * n_b_f + n_b_f * n_b_f)) / (n_ab_f * n_ab_f * n_ab_f) +
                    6.0 * delta2 * (n_a_f * n_a_f * src->M2 + n_b_f * n_b_f * dst->M2) / (n_ab_f * n_ab_f) +
                    4.0 * delta * (n_a_f * src->M3 - n_b_f * dst->M3) / n_ab_f;

    double new_m3 = dst->M3 + src->M3 +
                    delta3 * (n_a_f * n_b_f * (n_a_f - n_b_f)) / (n_ab_f * n_ab_f) +
                    3.0 * delta * (n_a_f * src->M2 - n_b_f * dst->M2) / n_ab_f;

    double new_m2 = dst->M2 + src->M2 +
                    delta2 * (n_a_f * n_b_f / n_ab_f);

    dst->M4 = fmax(0.0, new_m4);
    dst->M3 = new_m3;
    dst->M2 = fmax(0.0, new_m2);
    dst->count = n_ab;

    if (src->min_val < dst->min_val) dst->min_val = src->min_val;
    if (src->max_val > dst->max_val) dst->max_val = src->max_val;
}

/* Отримання вибіркової дисперсії (s², незміщена оцінка з k-1) */
double welford_sample_variance(const welford_acc_t *acc) {
    if (!acc || acc->count < 2) return 0.0;
    return acc->M2 / (double)(acc->count - 1);
}

/* Отримання генеральної дисперсії (σ², ділення на k) */
double welford_population_variance(const welford_acc_t *acc) {
    if (!acc || acc->count == 0) return 0.0;
    return acc->M2 / (double)acc->count;
}

/* Отримання середньоквадратичного відхилення (s) */
double welford_stddev(const welford_acc_t *acc) {
    return sqrt(welford_sample_variance(acc));
}

/* Отримання коефіцієнта асиметрії (g1) */
double welford_skewness(const welford_acc_t *acc) {
    if (!acc || acc->count < 3 || acc->M2 <= 1e-15) return 0.0;
    double n = (double)acc->count;
    double var = acc->M2 / n;
    return (acc->M3 / n) / pow(var, 1.5);
}

/* Отримання коефіцієнта ексцесу (g2, excess kurtosis, для норми = 0) */
double welford_kurtosis(const welford_acc_t *acc) {
    if (!acc || acc->count < 4 || acc->M2 <= 1e-15) return 0.0;
    double n = (double)acc->count;
    double var = acc->M2 / n;
    return (acc->M4 / n) / (var * var) - 3.0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <limits>
#include <span>
#include <algorithm>
#include <numeric>

/* Потоковий статистичний акумулятор на шаблонах C++20 */
template <typename FloatType = double>
class StreamingAccumulator {
public:
    StreamingAccumulator() noexcept { reset(); }

    void reset() noexcept {
        count_ = 0;
        mean_ = 0.0;
        M2_ = 0.0;
        M3_ = 0.0;
        M4_ = 0.0;
        min_ = std::numeric_limits<FloatType>::infinity();
        max_ = -std::numeric_limits<FloatType>::infinity();
    }

    /* Додавання одного спостереження */
    void push(FloatType x) noexcept {
        if (std::isnan(x)) return;

        ++count_;
        min_ = std::min(min_, x);
        max_ = std::max(max_, x);

        if (count_ == 1) {
            mean_ = x;
            M2_ = 0.0;
            M3_ = 0.0;
            M4_ = 0.0;
            return;
        }

        const auto n = static_cast<FloatType>(count_);
        const FloatType delta = x - mean_;
        const FloatType delta_n = delta / n;
        const FloatType delta_n2 = delta_n * delta_n;
        const FloatType term1 = delta * delta_n * (n - 1.0);

        mean_ += delta_n;

        M4_ += term1 * delta_n2 * (n * n - 3.0 * n + 3.0) +
               6.0 * delta_n2 * M2_ - 4.0 * delta_n * M3_;
        M3_ += term1 * delta_n * (n - 2.0) - 3.0 * delta_n * M2_;
        M2_ += term1;

        M2_ = std::max(static_cast<FloatType>(0.0), M2_);
        M4_ = std::max(static_cast<FloatType>(0.0), M4_);
    }

    /* Пакетне додавання через безпечний зріз std::span */
    void push_batch(std::span<const FloatType> batch) noexcept {
        for (FloatType val : batch) {
            push(val);
        }
    }

    /* Асоціативне об'єднання з іншим акумулятором */
    StreamingAccumulator& operator+=(const StreamingAccumulator& other) noexcept {
        if (other.count_ == 0) return *this;
        if (count_ == 0) {
            *this = other;
            return *this;
        }

        const auto n_a = static_cast<FloatType>(count_);
        const auto n_b = static_cast<FloatType>(other.count_);
        const FloatType n_ab = n_a + n_b;

        const FloatType delta = other.mean_ - mean_;
        const FloatType delta2 = delta * delta;
        const FloatType delta3 = delta2 * delta;
        const FloatType delta4 = delta3 * delta;

        mean_ += delta * (n_b / n_ab);

        const FloatType new_m4 = M4_ + other.M4_ +
            delta4 * (n_a * n_b * (n_a * n_a - n_a * n_b + n_b * n_b)) / (n_ab * n_ab * n_ab) +
            6.0 * delta2 * (n_a * n_a * other.M2_ + n_b * n_b * M2_) / (n_ab * n_ab) +
            4.0 * delta * (n_a * other.M3_ - n_b * M3_) / n_ab;

        const FloatType new_m3 = M3_ + other.M3_ +
            delta3 * (n_a * n_b * (n_a - n_b)) / (n_ab * n_ab) +
            3.0 * delta * (n_a * other.M2_ - n_b * M2_) / n_ab;

        const FloatType new_m2 = M2_ + other.M2_ +
            delta2 * (n_a * n_b / n_ab);

        M4_ = std::max(static_cast<FloatType>(0.0), new_m4);
        M3_ = new_m3;
        M2_ = std::max(static_cast<FloatType>(0.0), new_m2);
        count_ += other.count_;
        min_ = std::min(min_, other.min_);
        max_ = std::max(max_, other.max_);

        return *this;
    }

    [[nodiscard]] uint64_t count() const noexcept { return count_; }
    [[nodiscard]] FloatType mean() const noexcept { return mean_; }
    [[nodiscard]] FloatType min() const noexcept { return min_; }
    [[nodiscard]] FloatType max() const noexcept { return max_; }

    [[nodiscard]] FloatType sample_variance() const noexcept {
        return count_ > 1 ? M2_ / static_cast<FloatType>(count_ - 1) : 0.0;
    }

    [[nodiscard]] FloatType population_variance() const noexcept {
        return count_ > 0 ? M2_ / static_cast<FloatType>(count_) : 0.0;
    }

    [[nodiscard]] FloatType stddev() const noexcept {
        return std::sqrt(sample_variance());
    }

    [[nodiscard]] FloatType skewness() const noexcept {
        if (count_ < 3 || M2_ <= 1e-15) return 0.0;
        const auto n = static_cast<FloatType>(count_);
        const FloatType var = M2_ / n;
        return (M3_ / n) / std::pow(var, static_cast<FloatType>(1.5));
    }

    [[nodiscard]] FloatType kurtosis() const noexcept {
        if (count_ < 4 || M2_ <= 1e-15) return 0.0;
        const auto n = static_cast<FloatType>(count_);
        const FloatType var = M2_ / n;
        return (M4_ / n) / (var * var) - 3.0;
    }

private:
    uint64_t count_{0};
    FloatType mean_{0.0};
    FloatType M2_{0.0};
    FloatType M3_{0.0};
    FloatType M4_{0.0};
    FloatType min_{std::numeric_limits<FloatType>::infinity()};
    FloatType max_{-std::numeric_limits<FloatType>::infinity()};
};
```
:::

### Демонстраційний стрес-тест числової стійкості

Для практичної перевірки стійкості до катастрофічного скасування розглянемо поширений сценарій: вибірку показників датчика високої точності, де вимірювана фізична величина має велике постійне зміщення `10⁹` одиниць та мікроскопічні випадкові флуктуації.

Нехай вхідний масив містить п'ять значень:

```
x_i = 1 000 000 000.0 + r_i,   де r_i ∈ { 1.0, 2.0, 3.0, 4.0, 5.0 }
```

Істинне аналітичне середнє значення цього набору дорівнює точно `1 000 000 003.0`, а незміщена вибіркова дисперсія становить строго `2.5`.

:::tabs
```c
int main(void) {
    const double raw_data[5] = {
        1000000001.0, 1000000002.0, 1000000003.0, 1000000004.0, 1000000005.0
    };

    /* 1. Наївний однопрохідний підхід */
    double sum1 = 0.0, sum2 = 0.0;
    for (int i = 0; i < 5; ++i) {
        sum1 += raw_data[i];
        sum2 += raw_data[i] * raw_data[i];
    }
    double naive_var = (sum2 - (sum1 * sum1) / 5.0) / 4.0;

    /* 2. Алгоритм Велфорда */
    welford_acc_t acc;
    welford_init(&acc);
    welford_push_batch(&acc, raw_data, 5);
    double welford_var = welford_sample_variance(&acc);

    printf("Очікувана дисперсія : 2.5000000000\n");
    printf("Наївна формула      : %.10f (похибка катастрофічного скасування!)\n", naive_var);
    printf("Алгоритм Велфорда   : %.10f (ідеальний збіг)\n", welford_var);

    return 0;
}
```
```cpp
int main() {
    const std::vector<double> raw_data = {
        1000000001.0, 1000000002.0, 1000000003.0, 1000000004.0, 1000000005.0
    };

    /* 1. Наївний метод */
    double sum1 = 0.0, sum2 = 0.0;
    for (double x : raw_data) {
        sum1 += x;
        sum2 += x * x;
    }
    const double naive_var = (sum2 - (sum1 * sum1) / 5.0) / 4.0;

    /* 2. Акумулятор Велфорда */
    StreamingAccumulator<double> acc;
    acc.push_batch(raw_data);
    const double welford_var = acc.sample_variance();

    std::cout << "Очікувана дисперсія : 2.5000000000\n";
    std::cout << "Наївна формула      : " << naive_var << " (повна втрата точності!)\n";
    std::cout << "Алгоритм Велфорда   : " << welford_var << " (абсолютна точність)\n";

    return 0;
}
```
:::

У стандартному форматі `double` наївна формула повертає значення порядка `0.0000000000` або від'ємне число через переповнення значущих розрядів при відніманні `sum2 - (sum1 * sum1) / 5.0`. Натомість акумулятор Велфорда видає точне число `2.5000000000`, оскільки оперує виключно різницями `δ = x_i - μ_{i-1}`, які ніколи не перевищують масштабу вихідного розсіювання вибірки.

### Паралельне обчислення великих масивів через OpenMP

Оскільки оператор об'єднання двох статистичних станів `merge` задовольняє властивості асоціативності та комутативності, алгоритм Велфорда природно вбудовується в паралельні схеми редукції. Під час обробки масивів розміром у сотні мільйонів елементів кожен потік виконання виділяє локальний акумулятор у своєму стеку, обробляє свою неперетинну частину пам'яті без блокувань шини, а наприкінці об'єднує локальні результати в єдиний глобальний стан.

Нижче наведено приклад паралельної обробки великого масиву чисел із використанням бібліотеки OpenMP:

:::tabs
```c
#include <omp.h>

welford_acc_t parallel_welford(const double *array, size_t total_size) {
    welford_acc_t global_acc;
    welford_init(&global_acc);

    #pragma omp parallel
    {
        welford_acc_t local_acc;
        welford_init(&local_acc);

        #pragma omp for nowait
        for (size_t i = 0; i < total_size; ++i) {
            welford_push(&local_acc, array[i]);
        }

        #pragma omp critical
        {
            welford_merge(&global_acc, &local_acc);
        }
    }

    return global_acc;
}
```
```cpp
#include <omp.h>

StreamingAccumulator<double> parallel_accumulate(std::span<const double> data) {
    StreamingAccumulator<double> global_acc;

    #pragma omp parallel
    {
        StreamingAccumulator<double> local_acc;

        #pragma omp for nowait
        for (size_t i = 0; i < data.size(); ++i) {
            local_acc.push(data[i]);
        }

        #pragma omp critical
        {
            global_acc += local_acc;
        }
    }

    return global_acc;
}
```
:::

У цій схемі критична секція виконується рівно `P` разів (де `P` — кількість задіяних ядер процесора), що становить мізерну частку від загального часу виконання і забезпечує лінійне прискорення обчислень зі збільшенням кількості потоків.

### Тонкощі компіляції та векторна оптимізація (SIMD)

Через наявність прямої рекурентної залежності за даними між сусідніми ітераціями (`μ_k` залежить від `μ_{k-1}`, а `M2_k` — від `M2_{k-1}`) сучасні оптимізувальні компілятори (GCC, Clang, MSVC) не можуть автоматично векторизувати базовий цикл Велфорда за допомогою інструкцій AVX-512 або ARM Neon.

Для досягнення граничної швидкодії на векторних блоках застосовують блочне розгортання: процесор підтримує одночасно 4 або 8 паралельних потокових станів у SIMD-регістрах (наприклад, у регістрах `ymm` для 4 чисел `double` у разі AVX2). Потік даних розбивається на 4 незалежні смуги за модулем індексу (`x[0], x[4], x[8]...` для першого стану; `x[1], x[5], x[9]...` для другого). Наприкінці обробки 4 часткові стани об'єднуються за допомогою трьох послідовних викликів `merge`.

Така техніка усуває простій векторних конвеєрів (pipeline stalls) через затримку інструкцій ділення з рухомою комою і дає змогу обробляти понад 2.5 мільярда відліків за секунду на одному сучасному серверному ядрі.

### Обробка граничних та виняткових станів

Під час розробки надійного системного коду необхідно враховувати такі крайові випадки поведінки акумулятора:

1. **Вибірка розміром `n = 0`**: середнє та всі моменти залишаються нульовими, вибіркова дисперсія повертає 0 (або індикатор помилки), а поля `min` та `max` ініціалізуються нескінченностями відповідних знаків.
2. **Вибірка розміром `n = 1`**: вибіркове середнє дорівнює значенню першого елемента, а вибіркова дисперсія повертає 0. Спроба розрахувати незміщену дисперсію за формулою `M2 / (n - 1)` призвела б до ділення на нуль, тому функція `sample_variance` містить явну перевірку `count > 1`.
3. **Вибірка з ідентичних елементів**: якщо всі `x_i` однакові, математична сума `M2` повинна дорівнювати нулю. Проте через похибки машинного заокруглення проміжне значення `M2` може набути крихітного від'ємного значення порядку `-10⁻¹⁷`. Щоб запобігти поверненню `NaN` у функції взяття квадратного кореня `sqrt(s²)`, значення `M2` завжди обмежується знизу нулем за допомогою `fmax(0.0, M2)`.
4. **Нечислові значення (`NaN`) та нескінченності (`Inf`)**: поява навіть одного значення `NaN` у потоці здатна «отруїти» весь накопичувач, перетворивши всі наступні середні та моменти на `NaN`. Функція `push` містить перевірку `isnan(x)` і відкидає некоректні спостереження, зберігаючи цілісність накопиченої статистики.

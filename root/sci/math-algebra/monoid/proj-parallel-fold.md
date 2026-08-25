# ⚙️ Паралельна редукція та моноїди в обчисленнях

У сучасній розробці високонавантажених систем та обробці великих масивів даних — таких як MapReduce, Apache Spark, паралельні алгоритми C++ (`std::reduce`, `std::transform_reduce`, OpenMP) або GPU-обчислення на CUDA — однією з найчастіших операцій є агрегація мільйонів окремих записів у компактну підсумкову статистику.

Звичайний послідовний алгоритм виконує згортання елементів масиву один за одним в одному потоці:

```
acc = combine(acc, x)
```

Такий підхід має лінійну часову складність `O(N)`. Якщо масив містить сотні мільйонів значень, однопотокове згортання впирається в пропускну здатність одного процесорного ядра. Щоб задіяти всі доступні обчислювальні вузли, потік даних необхідно розділити між незалежними потоками виконання.

Математичною умовою, яка гарантує коректність довільного паралельного розбиття, є структура **моноїда**. Якщо операція об'єднання `combine` є асоціативною і має нейтральний елемент `empty`, алгоритм може безпечно розрізати масив на будь-яку кількість частин, порахувати проміжні підсумки в окремих потоках, а потім об'єднати результати у вигляді бінарного дерева. Часова глибина обчислення скорочується з лінійної `O(N)` до логарифмічної `O(log₂ N)`.

### Задача: багатопараметричний моноїд статистичних метрик

Припустимо, ми збираємо телеметрію з розподіленої мережі серверів (наприклад, час відгуку мережевих запитів або покази датчиків температури). Для кожного потоку подій нам потрібно паралельно обчислити одразу п'ять ключових показників:
1. Загальну кількість спостережень `count`.
2. Суму всіх значень `sum`.
3. Мінімальне зафіксоване значення `min`.
4. Максимальне зафіксоване значення `max`.
5. Вибіркову дисперсію або суму квадратів відхилень `M₂` для оцінки стабільності системи.

Обчислення середнього, мінімуму та максимуму є простим, але обчислення дисперсії в один прохід вимагає особливої обережності. Наївна формула `Var(X) = E[X²] − (E[X])²` страждає від катастрофічного скасування розрядів при відніманні двох близьких великих чисел. Тому ми застосуємо чисельно стійкий алгоритм попарного об'єднання Чана (*Tony Chan*), який узагальнює метод Велфорда (*B. P. Welford*) на випадок злиття двох довільних блоків даних.

#### Алгебра злиття двох блоків метрик (алгоритм Чана)

Нехай два незалежні потоки процесора обробили дві частини масиву й отримали проміжні акумулятори `A` та `B`:
- Кількість елементів: `N = N_A + N_B`
- Сума: `S = S_A + S_B`
- Мінімум: `min(A.min, B.min)`
- Максимум: `max(A.max, B.max)`
- Середні значення блоків: `μ_A = S_A / N_A`, `μ_B = S_B / N_B`
- Сума квадратів відхилень `M₂` комбінованого блоку:

```
δ = μ_B − μ_A
M₂ = M₂_A + M₂_B + δ² · (N_A · N_B) / (N_A + N_B)
```

Ця операція є строго асоціативною для довільних блоків даних. Нейтральним елементом `empty` є структура з `count = 0`, `sum = 0`, `min = +∞`, `max = −∞`, `M₂ = 0`. При злитті будь-якого блоку `A` з нейтральним елементом значення `A` залишається абсолютно незмінним.

---

### Робоча реалізація паралельної редукції

Нижче наведено робочі реалізації моноїдної структури та алгоритму паралельного деревоподібного згортання трьома мовами: чистим C (поділ масиву «розділяй і володарюй»), ідіоматичним C++20 (із використанням паралельних політик виконання `std::execution::par_unseq` та `std::transform_reduce`) та Python (наочна імітація рівнів дерева злиття).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <math.h>

/* Структура моноїда статистичних метрик */
typedef struct {
    long long count;
    double sum;
    double min_val;
    double max_val;
    double m2; /* сума квадратів відхилень для дисперсії */
} Metrics;

/* Нейтральний елемент моноїда e */
Metrics metrics_empty(void) {
    Metrics m;
    m.count = 0;
    m.sum = 0.0;
    m.min_val = DBL_MAX;
    m.max_val = -DBL_MAX;
    m.m2 = 0.0;
    return m;
}

/* Ініціалізація акумулятора з одного числового вимірювання */
Metrics metrics_from_value(double x) {
    Metrics m;
    m.count = 1;
    m.sum = x;
    m.min_val = x;
    m.max_val = x;
    m.m2 = 0.0;
    return m;
}

/* Асоціативна бінарна операція моноїда: combine(a, b) */
Metrics metrics_combine(Metrics a, Metrics b) {
    if (a.count == 0) return b;
    if (b.count == 0) return a;

    Metrics res;
    res.count = a.count + b.count;
    res.sum = a.sum + b.sum;
    res.min_val = (a.min_val < b.min_val) ? a.min_val : b.min_val;
    res.max_val = (a.max_val > b.max_val) ? a.max_val : b.max_val;

    double mean_a = a.sum / (double)a.count;
    double mean_b = b.sum / (double)b.count;
    double delta = mean_b - mean_a;

    double term = delta * delta * ((double)a.count * (double)b.count / (double)res.count);
    res.m2 = a.m2 + b.m2 + term;

    return res;
}

/* Рекурсивне бінарне дерево редукції (Divide and Conquer) */
Metrics reduce_range(const double* data, size_t left, size_t right) {
    if (left >= right) {
        return metrics_empty();
    }
    if (right - left == 1) {
        return metrics_from_value(data[left]);
    }
    size_t mid = left + (right - left) / 2;
    Metrics left_res = reduce_range(data, left, mid);
    Metrics right_res = reduce_range(data, mid, right);
    return metrics_combine(left_res, right_res);
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <limits>
#include <algorithm>
#include <numeric>
#include <execution>

struct Metrics {
    long long count{0};
    double sum{0.0};
    double min_val{std::numeric_limits<double>::infinity()};
    double max_val{-std::numeric_limits<double>::infinity()};
    double m2{0.0};

    [[nodiscard]] static constexpr Metrics empty() noexcept {
        return {};
    }

    [[nodiscard]] static constexpr Metrics from_value(double x) noexcept {
        return Metrics{1, x, x, x, 0.0};
    }

    [[nodiscard]] double mean() const noexcept {
        return count > 0 ? sum / static_cast<double>(count) : 0.0;
    }

    [[nodiscard]] double variance() const noexcept {
        return count > 1 ? m2 / static_cast<double>(count) : 0.0;
    }
};

/* Асоціативна моноїдна операція злиття */
[[nodiscard]] Metrics operator+(const Metrics& a, const Metrics& b) noexcept {
    if (a.count == 0) return b;
    if (b.count == 0) return a;

    const long long total_count = a.count + b.count;
    const double delta = b.mean() - a.mean();
    const double term = delta * delta * (static_cast<double>(a.count) * static_cast<double>(b.count) / static_cast<double>(total_count));

    return Metrics{
        .count = total_count,
        .sum = a.sum + b.sum,
        .min_val = std::min(a.min_val, b.min_val),
        .max_val = std::max(a.max_val, b.max_val),
        .m2 = a.m2 + b.m2 + term
    };
}

/* Узагальнене паралельне згортання за допомогою std::transform_reduce */
[[nodiscard]] Metrics parallel_metrics_reduce(std::span<const double> data) {
    return std::transform_reduce(
        std::execution::par_unseq,
        data.begin(), data.end(),
        Metrics::empty(),
        std::plus<Metrics>{},
        Metrics::from_value
    );
}
```
```python
from dataclasses import dataclass
import math
from functools import reduce
from typing import List

@dataclass(frozen=True)
class Metrics:
    count: int = 0
    sum_val: float = 0.0
    min_val: float = math.inf
    max_val: float = -math.inf
    m2: float = 0.0

    @classmethod
    def empty(cls) -> "Metrics":
        return cls()

    @classmethod
    def from_value(cls, x: float) -> "Metrics":
        return cls(count=1, sum_val=x, min_val=x, max_val=x, m2=0.0)

    def mean(self) -> float:
        return self.sum_val / self.count if self.count > 0 else 0.0

    def combine(self, other: "Metrics") -> "Metrics":
        if self.count == 0:
            return other
        if other.count == 0:
            return self

        total_count = self.count + other.count
        delta = other.mean() - self.mean()
        term = delta * delta * (self.count * other.count / total_count)

        return Metrics(
            count=total_count,
            sum_val=self.sum_val + other.sum_val,
            min_val=min(self.min_val, other.min_val),
            max_val=max(self.max_val, other.max_val),
            m2=self.m2 + other.m2 + term
        )

def parallel_tree_fold(data: List[float]) -> Metrics:
    """Імітація паралельного бінарного дерева редукції."""
    nodes = [Metrics.from_value(x) for x in data]
    if not nodes:
        return Metrics.empty()
    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                next_level.append(nodes[i].combine(nodes[i + 1]))
            else:
                next_level.append(nodes[i])
        nodes = next_level
    return nodes[0]
```
:::

---

### Чому планувальники завдань потребують нейтрального елемента

У сучасних багатопотокових середовищах із крадіжкою роботи (*work-stealing schedulers*, таких як Intel oneTBB або Rust Rayon) кількість паралельних задач не є фіксованою наперед. Планувальник динамічно розщеплює діапазон обробки щоразу, коли одне з ядер процесора звільняється від роботи.

У такій динамічній моделі кожен новостворений потік повинен негайно отримати початковий стан свого локального акумулятора. Якби операція не мала нейтрального елемента `empty`, системі довелося б заводити спеціальні прапорці `has_value` або повертати типи-обгортки `std::optional<T>`, що призводить до зайвих умовних переходів на кожній ітерації гарячого циклу. Наявність нейтрального елемента `e` дозволяє ініціалізувати акумулятор значенням `Metrics::empty()` без жодних накладних витрат і об'єднувати результати потоків за єдиним загальним шаблоном.

---

### Підводні камені та інженерні пастки

1. **Порушення асоціативності у числах з плаваючою комою (IEEE 754).**
   Математичне додавання дійсних чисел `(ℝ, +, 0)` є строго асоціативним: `(a + b) + c = a + (b + c)`. Проте апаратні числа `float` та `double` зберігаються з обмеженою точністю мантиси (24 біти для одинарної точності, 53 біти для подвійної).
   Якщо додати мале число `1e-16` до відносно великого числа `1.0`, воно повністю втрачається через обмеження сітки розрядів:
   ```
   (1.0 + 1e-16) + 1e-16 = 1.0 + 1e-16 = 1.0
   1.0 + (1e-16 + 1e-16) = 1.0 + 2e-16 = 1.0000000000000002
   ```
   *Наслідок:* Якщо великий масив чисел `double` обчислювати паралельно на різній кількості ядер (наприклад, 4 потоки замість 8), форма дерева редукції зміниться, і підсумковий результат може відрізнятися в останніх знаках. Якщо системі потрібна абсолютна бітова детермінованість (наприклад, у криптографії, реплікації ігрових рушіїв або фінансовому аудиті), порядок злиття фіксують статичним бінарним деревом або використовують цілочисельну арифметику фіксованої коми.

2. **Повторні пакети в мережі та вимога ідемпотентності.**
   У розподілених системах повідомлення між серверами можуть дублюватися через мережеві збої та механізми повторного надсилання (*retry policy*). Якщо моноїдна операція не є **ідемпотентною** (тобто `x · x ≠ x`), повторний пакет буде враховано двічі, що призведе до спотворення результату (наприклад, подвійного списання коштів або подвоєння лічильника кліків).
   Комутативні та ідемпотентні моноїди (де `a · b = b · a` та `a · a = a`), такі як взяття максимуму `max` чи об'єднання множин `∪`, називають **напіврешітками** (*semilattices*). Вони утворюють фундамент безконфліктних реплікованих типів даних (**CRDT**), які гарантують збіжність стану кластера навіть за умов дублювання та перестановки мережевих пакетів.

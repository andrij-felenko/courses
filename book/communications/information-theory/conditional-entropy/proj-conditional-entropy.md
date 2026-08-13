# ⚙️ Обчислення умовної ентропії з матриці спостережень

Ця вставка містить алгоритм та практичну реалізацію обчислення спільної ентропії `H(X,Y)`, умовних ентропій `H(X|Y)` та `H(Y|X)`, а також взаємної інформації `I(X;Y)` за даними експериментальної матриці сумісного випадання подій (або матриці плутанини каналу).

У реальних інженерних системах — від контролерів флеш-пам'яті до моніторингу завадостійкості бездротових ліній — вхідні дані надходять у вигляді лічильників сумісної появи двох подій. Матриця плутанини `N[i][j]` фіксує, скільки разів відправлений символ `x[i]` перетворився у прийнятий символ `y[j]`. На основі цих первинних даних розробник мусить обчислити повний спектр інформаційно-теоретичних метрик.

Обчислення умовної ентропії є фундаментальним етапом при моделюванні фізичного каналу зв'язку, підборі параметрів завадостійких кодів та оцінці точності моделей машинного навчання.

## Алгоритм і математичний підрахунок

Нехай матриця `N[i][j]` містить кількість спостережень, у яких вхідна величина `X` набула значення `x[i]` (`i = 0..n-1`), а вихідна `Y` — значення `y[j]` (`j = 0..m-1`).

Обчислення виконується у чотири послідовні кроки:

1. **Нормалізація та загальний підрахунок:** Обчислюється загальна кількість випробувань `N_total = ∑ᵢ,ⱼ N[i][j]` та оцінки спільних ймовірностей `p(x[i], y[j]) = N[i][j] / N_total`. Якщо сумарний лічильник дорівнює нулю або є від'ємним через збій лічильника hardware-статистики, функція має повертати помилку.
2. **Обчислення маргінальних розподілів:** 
   - `p(x[i]) = ∑ⱼ p(x[i], y[j])` — повна ймовірність появу символу `x[i]` на вході;
   - `p(y[j]) = ∑ᵢ p(x[i], y[j])` — повна ймовірність появу символу `y[j]` на виході.
3. **Обчислення часткових умовних ймовірностей:**
   - `p(x[i] | y[j]) = p(x[i], y[j]) / p(y[j])` — ймовірність того, що відправлено `x[i]`, якщо прийнято `y[j]`;
   - `p(y[j] | x[i]) = p(x[i], y[j]) / p(x[i])` — ймовірність того, що прийнято `y[j]`, якщо відправлено `x[i]`.
4. **Накопичення ентропійних сум:**
   - `H(X) = − ∑ᵢ p(x[i]) · log₂ p(x[i])` — початкова ентропія джерела;
   - `H(Y) = − ∑ⱼ p(y[j]) · log₂ p(y[j])` — ентропія виходу;
   - `H(X,Y) = − ∑ᵢ,ⱼ p(x[i], y[j]) · log₂ p(x[i], y[j])` — спільна ентропія пари;
   - `H(X|Y) = − ∑ᵢ,ⱼ p(x[i], y[j]) · log₂ p(x[i] | y[j])` — умовна ентропія входу за виходом (equivocation);
   - `H(Y|X) = − ∑ᵢ,ⱼ p(x[i], y[j]) · log₂ p(y[j] | x[i])` — умовна ентропія виходу за входом (шум каналу);
   - `I(X;Y) = H(X) − H(X|Y)` — взаємна інформація між входом і виходом.

Граничний випадок: якщо `p = 0`, доданок `p · log₂ p` дорівнює `0` (бо `lim_{p→0+} p · log₂ p = 0`). Код повинен явно перевіряти ймовірність на нуль перед викликом `log2()`, щоб уникнути невизначеностей `NaN` та обчислення логарифма від нуля.

## Архітектурні рішення та ефективність пам'яті

Для забезпечення максимальної швидкодії у системному програмуванні двовимірні матриці розміщуються у пам'яті у вигляді суцільного одновимірного масиву (row-major order). Це гарантує локальність даних за читанням та дозволяє ефективно використовувати кеш-пам'ять L1/L2 процесора при послідовному сумуванні елементів.

Використання лінійного масиву заважає виникненню фрагментації купи, що особливо критично при роботі у високопродуктивних мережевих драйверах та прошивках мікроконтролерів. Обчислення виконується за один прохід по елементах для маргіналізації та один додатковий прохід для сумування ентропійних логарифмів.

## Реалізація мовами C та C++

Наведена нижче реалізація демонструє обчислення метрик у системному коді. Для мови C надано очікуваний функціональний інтерфейс із явним керуванням пам'яттю, а для C++ — ідіоматичний варіант із використанням безнаслідкових контейнерів `std::vector`, перегляду буфера `std::span` та обробки помилок через `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double h_x;         /* Ентропія джерела H(X) */
    double h_y;         /* Ентропія приймача H(Y) */
    double h_xy;        /* Спільна ентропія H(X,Y) */
    double h_x_given_y; /* Умовна ентропія H(X|Y) (equivocation) */
    double h_y_given_x; /* Умовна ентропія H(Y|X) (шум каналу) */
    double mutual_info; /* Взаємна інформація I(X;Y) */
} EntropyMetrics;

/**
 * Обчислює інформаційні метрики за матрицею частот.
 * 
 * @param matrix Масив розміром rows * cols з лінійним розгортанням.
 * @param rows Кількість значень величини X.
 * @param cols Кількість значень величини Y.
 * @param out_metrics Вказівник на структуру для збереження результатів.
 * @return true у разі успіху, false при нульовій сумі випробувань або помилці виділення пам'яті.
 */
bool compute_entropy_metrics(const double *matrix, size_t rows, size_t cols, EntropyMetrics *out_metrics) {
    if (!matrix || !out_metrics || rows == 0 || cols == 0) {
        return false;
    }

    double total_count = 0.0;
    for (size_t i = 0; i < rows * cols; ++i) {
        total_count += matrix[i];
    }

    if (total_count <= 0.0) {
        return false;
    }

    double *px = (double *)calloc(rows, sizeof(double));
    double *py = (double *)calloc(cols, sizeof(double));

    if (!px || !py) {
        free(px);
        free(py);
        return false;
    }

    /* 1. Обчислення маргінальних ймовірностей */
    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix[r * cols + c] / total_count;
            px[r] += p_joint;
            py[c] += p_joint;
        }
    }

    double h_x = 0.0;
    for (size_t r = 0; r < rows; ++r) {
        if (px[r] > 0.0) {
            h_x -= px[r] * log2(px[r]);
        }
    }

    double h_y = 0.0;
    for (size_t c = 0; c < cols; ++c) {
        if (py[c] > 0.0) {
            h_y -= py[c] * log2(py[c]);
        }
    }

    double h_xy = 0.0;
    double h_x_given_y = 0.0;
    double h_y_given_x = 0.0;

    /* 2. Обчислення спільної та умовних ентропій */
    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix[r * cols + c] / total_count;
            if (p_joint > 0.0) {
                h_xy -= p_joint * log2(p_joint);

                double p_x_given_y = p_joint / py[c];
                h_x_given_y -= p_joint * log2(p_x_given_y);

                double p_y_given_x = p_joint / px[r];
                h_y_given_x -= p_joint * log2(p_y_given_x);
            }
        }
    }

    free(px);
    free(py);

    out_metrics->h_x = h_x;
    out_metrics->h_y = h_y;
    out_metrics->h_xy = h_xy;
    out_metrics->h_x_given_y = h_x_given_y;
    out_metrics->h_y_given_x = h_y_given_x;
    out_metrics->mutual_info = h_x - h_x_given_y;

    return true;
}

int main(void) {
    /* Приклад: зашумлений симетричний канал BSC із ймовірністю помилки p = 0.1 */
    /* Матриця частот: rows=2 (X in {0,1}), cols=2 (Y in {0,1}) */
    /* N(0,0)=450, N(0,1)=50, N(1,0)=50, N(1,1)=450 (разом 1000 випробувань) */
    double confusion_matrix[2][2] = {
        { 450.0,  50.0 },
        {  50.0, 450.0 }
    };

    EntropyMetrics res;
    if (compute_entropy_metrics((const double *)confusion_matrix, 2, 2, &res)) {
        printf("H(X)     = %.4f бітів\n", res.h_x);
        printf("H(Y)     = %.4f бітів\n", res.h_y);
        printf("H(X,Y)   = %.4f бітів\n", res.h_xy);
        printf("H(X|Y)   = %.4f бітів (equivocation)\n", res.h_x_given_y);
        printf("H(Y|X)   = %.4f бітів (шум)\n", res.h_y_given_x);
        printf("I(X;Y)   = %.4f бітів\n", res.mutual_info);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <string_view>
#include <iomanip>

struct EntropyMetrics {
    double h_x{0.0};          // Ентропія джерела H(X)
    double h_y{0.0};          // Ентропія приймача H(Y)
    double h_xy{0.0};         // Спільна ентропія H(X,Y)
    double h_x_given_y{0.0};    // Умовна ентропія H(X|Y) (equivocation)
    double h_y_given_x{0.0};    // Умовна ентропія H(Y|X)
    double mutual_info{0.0};    // Взаємна інформація I(X;Y)
};

enum class MatrixError {
    InvalidDimensions,
    EmptyData,
    ZeroTotalCount
};

/**
 * Обчислює інформаційні метрики для двовимірної матриці частот.
 * 
 * @param matrix_flat Плоский масив елементів матриці.
 * @param rows Кількість рядків (значень X).
 * @param cols Кількість стовпців (значень Y).
 */
[[nodiscard]] std::expected<EntropyMetrics, MatrixError> 
compute_entropy_metrics(std::span<const double> matrix_flat, size_t rows, size_t cols) {
    if (rows == 0 || cols == 0 || matrix_flat.size() != rows * cols) {
        return std::unexpected(MatrixError::InvalidDimensions);
    }

    double total_count = 0.0;
    for (double val : matrix_flat) {
        total_count += val;
    }

    if (total_count <= 0.0) {
        return std::unexpected(MatrixError::ZeroTotalCount);
    }

    std::vector<double> px(rows, 0.0);
    std::vector<double> py(cols, 0.0);

    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix_flat[r * cols + c] / total_count;
            px[r] += p_joint;
            py[c] += p_joint;
        }
    }

    EntropyMetrics m;

    for (double p : px) {
        if (p > 0.0) {
            m.h_x -= p * std::log2(p);
        }
    }

    for (double p : py) {
        if (p > 0.0) {
            m.h_y -= p * std::log2(p);
        }
    }

    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix_flat[r * cols + c] / total_count;
            if (p_joint > 0.0) {
                m.h_xy -= p_joint * std::log2(p_joint);

                double p_x_given_y = p_joint / py[c];
                m.h_x_given_y -= p_joint * std::log2(p_x_given_y);

                double p_y_given_x = p_joint / px[r];
                m.h_y_given_x -= p_joint * std::log2(p_y_given_x);
            }
        }
    }

    m.mutual_info = m.h_x - m.h_x_given_y;
    return m;
}

int main() {
    // Приклад: BSC з імовірністю помилки p = 0.1 (1000 випробувань)
    std::vector<double> confusion_matrix = {
        450.0,  50.0,
         50.0, 450.0
    };

    auto result = compute_entropy_metrics(confusion_matrix, 2, 2);

    if (result) {
        const auto& m = *result;
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "H(X)     = " << m.h_x << " бітів\n";
        std::cout << "H(Y)     = " << m.h_y << " бітів\n";
        std::cout << "H(X,Y)   = " << m.h_xy << " бітів\n";
        std::cout << "H(X|Y)   = " << m.h_x_given_y << " бітів (equivocation)\n";
        std::cout << "H(Y|X)   = " << m.h_y_given_x << " бітів (шум)\n";
        std::cout << "I(X;Y)   = " << m.mutual_info << " бітів\n";
    } else {
        std::cerr << "Помилка обчислення метрик!\n";
    }

    return 0;
}
```
:::

## Особливості чисельної реалізації та граничні випадки

При реалізації обчислень у реальному виробничому коді слід враховувати такі інженерні нюанси та особливості:

1. **Граничні значення логарифма:** У коді обов'язкова перевірка `p > 0.0`. Стандартні функції `log2(0.0)` повертають спеціальне значення `-INFINITY`, що при множенні на нуль дає нечислове значення `NaN`. Використання перевірки `if (p > 0.0)` гарантує коректне обчислення граничного значення `lim_{p→0+} p log₂ p = 0`.
2. **Чисельна стабільність та окліпинг:** При обробці експериментальних даних через накопичення похибок округлення чисел з плаваючою крапкою `double` сума `px[r]` або `py[c]` може дещо відрізнятися від фактичної суми рядка чи стовпця. Для запобігання ситуаціям, коли часткова ймовірність `p_joint / py[c]` виходить за межі одиниці `1.0`, умовне відношення слід обмежувати зверху значенням `1.0`.
3. **RAII та безпека ресурсів:** Реалізація мовою C++ спирається на семантику RAII (Resource Acquisition Is Initialization). Використання контейнерів `std::vector` усуває необхідність ручного виклику `free()`, а тип `std::expected` (доступний у стандарті C++23) забезпечує безпечну обробку помилок без застосування важких винятків (exceptions).
4. **Складність та масштабованість:** Алгоритм має часову складність `O(rows · cols)`, що робить його винятково швидким навіть для матрицій великої вимірності (наприклад, при обробці 256-позиційних сузір'їв значень у QAM-модемах). Необхідна додаткова пам'ять складає `O(rows + cols)` для зберігання вектора маргінальних ймовірностей.
5. **Векторизація SIMD:** При обробці матриць великого розміру (наприклад, у задачах обробки зображень чи аналізу великих мовних моделей) обчислення логарифмів можна векторизувати за допомогою інструкцій AVX2/AVX-512 або обчислювальних ядер GPU. У цьому випадку матрицю частот розбивають на блоки, які підсумовуються паралельно.
6. **Переповнення цілочисельних лічильників:** При зборі статистики в ядрах операційних систем лічильники пакетів можуть згортатися (overflow) після `2^64` випробувань. Функція обчислення повинна обробляти ситуації скидання лічильників за допомогою відносних приростів (deltas).

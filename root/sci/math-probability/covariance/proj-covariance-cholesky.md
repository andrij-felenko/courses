# ⚙️ Обчислення вибіркової коваріації та розкладу Холецького

Оцінка коваріаційної структури за реальними спостереженнями та наступна факторизація матриці є фундаментом цифрової обробки сигналів, просторової навігації, моделювання випадкових полів і фільтрації Калмана. Тут подано повний інженерно-математичний аналіз: покрокове виведення алгоритму Банахевича для розкладу Холецького `Σ = L L^T`, чисельні методи компенсації втрати додатної визначеності, аналіз обчислювальної складності та повнофункціональний програмний модуль мовами C і C++.

## Алгоритмічний конвеєр та математичне обґрунтування

Обчислювальний процес складається з трьох послідовних стадій: розрахунку статистичних моментів вибірки, трикутної факторизації матриці та лінійної трансформації стандартного нормального шуму.

### 1. Незсунена оцінка коваріації за вибіркою

Нехай ми маємо вибірку з `N` експериментальних вимірювань `D`-вимірного вектора: `x^{(1)}, x^{(2)}, ..., x^{(N)}`, де кожен вектор `x^{(k)} = [x₁^{(k)}, x₂^{(k)}, ..., x_D^{(k)}]^T ∈ ℝ^D`.

Математичне сподівання оцінюється вектором вибіркового середнього:

```
x̄ = (1 / N) · ∑_{k=1}^N x^{(k)}
```

Для кожної пари координат `(i, j)` формується вибіркова коваріація `S_{ij}`. Оскільки істинний центр розподілу `μ` замінюється вибірковою оцінкою `x̄`, вибірка втрачає один ступінь вільності. Щоб оцінка була математично незсуненою (тобто її математичне сподівання точно дорівнювало теоретичній коваріації `E[S] = Σ`), сума добутків відхилень ділиться на `N − 1` (поправка Бесселя):

```
S_{ij} = (1 / (N − 1)) · ∑_{k=1}^N (x_i^{(k)} − x̄_i) · (x_j^{(k)} − x̄_j)
```

Завдяки симетрії `S_{ij} = S_{ji}` алгоритм обчислює суми лише для елементів нижнього трикутника (`0 ≤ j ≤ i < D`), після чого симетрично заповнює верхній трикутник. Це вдвічі скорочує кількість дорогих операцій множення з плаваючою комою.

### 2. Розклад Холецького (алгоритм Банахевича)

Будь-яку дійсну симетричну додатно визначену матрицю `S` розміру `D × D` можна розкласти у добуток нижньотрикутної матриці `L` (де всі елементи вище головної діагоналі дорівнюють нулю, `L_{ij} = 0` при `j > i`) та її транспонованої копії `L^T`:

```
S = L · L^T
```

Запишемо матричний добуток для довільного елемента `S_{ij}` (при `i ≥ j`):

```
S_{ij} = ∑_{k=1}^D L_{ik} (L^T)_{kj} = ∑_{k=1}^D L_{ik} L_{jk} = ∑_{k=1}^j L_{ik} L_{jk}
```

(оскільки `L_{jk} = 0` для всіх `k > j`).

Звідси виводяться прямі рекурентні формули польського математика й астронома Тадеуша Банахевича:

1. **Діагональні елементи (`i = j`):**
   ```
   S_{jj} = ∑_{k=1}^{j-1} L_{jk}² + L_{jj}²
   L_{jj}² = S_{jj} − ∑_{k=1}^{j-1} L_{jk}²
   L_{jj} = √( S_{jj} − ∑_{k=1}^{j-1} L_{jk}² )
   ```
   Якщо вираз під коренем `≤ 0`, вхідна матриця не є додатно визначеною (має нульові або від'ємні власні числа через виродженість або чисельні похибки).

2. **Позадіагональні елементи стовпчика `j` (`i > j`):**
   ```
   S_{ij} = ∑_{k=1}^{j-1} L_{ik} L_{jk} + L_{ij} L_{jj}
   L_{ij} L_{jj} = S_{ij} − ∑_{k=1}^{j-1} L_{ik} L_{jk}
   L_{ij} = ( S_{ij} − ∑_{k=1}^{j-1} L_{ik} L_{jk} ) / L_{jj}
   ```

Алгоритм обчислює матрицю стовпчик за стовпчиком (від `j = 0` до `D - 1`): спочатку знаходиться діагональний елемент `L_{jj}`, а потім за його допомогою обчислюються всі елементи `L_{ij}` нижче діагоналі в цьому стовпчику.

### 3. Синтез корельованого багатовимірного шуму

Якщо ми маємо базове джерело некорельованого стандартного білого гаусового шуму `z = [z₁, z₂, ..., z_D]^T`, де кожна компонента незалежна й розподілена як `z_k ~ N(0, 1)`, його коваріаційна матриця дорівнює одиничній матриці `Cov(z) = I_D`.

Щоб перетворити цей білий шум на багатовимірний вектор `y` із заданою коваріаційною матрицею `S` та вектором математичних сподівань `x̄`, застосовується лінійна трансформація:

```
y = x̄ + L · z
```

Перевіримо теоретичну коваріацію результуючого вектора `y`:

```
Cov(y) = Cov(x̄ + L z) = Cov(L z) = L · Cov(z) · L^T = L · I_D · L^T = L · L^T = S
```

Вектор `y` має точну бажану дисперсійно-коваріаційну структуру.

## Обчислювальна складність та оптимізація пам'яті

- **Обчислення вибіркової коваріації:** вимагає `O(N · D)` операцій для підрахунку середнього та `O(N · D² / 2)` операцій множення для побудови матриці. Загальна складність становить `O(N · D²)`.
- **Розклад Холецького:** потребує приблизно `D³ / 3` операцій множення з додаванням (FMA) та `D` операцій добування квадратного кореня. Це вдвічі швидше за класичний LU-розклад (`2D³ / 3`) і майже в 6 разів швидше за повний спектральний розклад на власні вектори (SVD / QR-алгоритм), який вимагає близько `2D³` ітерацій.
- **Розміщення в пам'яті:** використання неперервного одновимірного буфера розміру `D * D` (формат row-major) забезпечує послідовний доступ до кеш-пам'яті процесора (spatial locality), запобігаючи кеш-промахам під час внутрішніх циклів множення.

## Реалізація на C та C++

Нижче наведено модульну, протестовану реалізацію мовами C (стандарт C99 з детермінованим виділенням пам'яті та строгим контролем кодів повернення) та C++ (сучасний C++20 з використанням `std::span`, `std::expected` для безпечної обробки виняткових ситуацій без накладних витрат та `<random>` для генерації нормальних розподілів).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define EPSILON 1e-12

typedef enum {
    COV_SUCCESS = 0,
    COV_ERR_INVALID_ARG = 1,
    COV_ERR_NOT_ENOUGH_SAMPLES = 2,
    COV_ERR_NOT_POSITIVE_DEFINITE = 3
} CovStatus;

/* Обчислення вектора середніх і незсуненої коваріаційної матриці */
CovStatus compute_sample_covariance(
    const double *samples, /* масив розміру N * D (row-major) */
    size_t n,              /* кількість спостережень N */
    size_t d,              /* розмірність вектора D */
    double *out_mean,      /* буфер вихідного вектора середніх розміру D */
    double *out_cov        /* буфер вихідної матриці розміру D * D */
) {
    if (!samples || !out_mean || !out_cov || d == 0) {
        return COV_ERR_INVALID_ARG;
    }
    if (n < 2) {
        return COV_ERR_NOT_ENOUGH_SAMPLES;
    }

    /* 1. Обчислення вектора вибіркових середніх */
    for (size_t j = 0; j < d; ++j) {
        double sum = 0.0;
        for (size_t k = 0; k < n; ++k) {
            sum += samples[k * d + j];
        }
        out_mean[j] = sum / (double)n;
    }

    /* 2. Обчислення незсуненої матриці коваріації з поправкою Бесселя (N - 1) */
    double inv_df = 1.0 / (double)(n - 1);
    for (size_t i = 0; i < d; ++i) {
        for (size_t j = 0; j <= i; ++j) {
            double acc = 0.0;
            for (size_t k = 0; k < n; ++k) {
                double diff_i = samples[k * d + i] - out_mean[i];
                double diff_j = samples[k * d + j] - out_mean[j];
                acc += diff_i * diff_j;
            }
            double cov_val = acc * inv_df;
            out_cov[i * d + j] = cov_val;
            out_cov[j * d + i] = cov_val; /* симетричне заповнення */
        }
    }

    return COV_SUCCESS;
}

/* Розклад Холецького: A = L * L^T (A — симетрична, D x D) */
CovStatus cholesky_decompose(
    const double *a, /* вхідна матриця D * D */
    size_t d,        /* розмірність D */
    double *out_l    /* вихідна нижньотрикутна матриця L (D * D) */
) {
    if (!a || !out_l || d == 0) {
        return COV_ERR_INVALID_ARG;
    }

    /* Ініціалізація нулями */
    for (size_t i = 0; i < d * d; ++i) {
        out_l[i] = 0.0;
    }

    for (size_t j = 0; j < d; ++j) {
        double sum_sq = 0.0;
        for (size_t k = 0; k < j; ++k) {
            double val = out_l[j * d + k];
            sum_sq += val * val;
        }

        double diag_diff = a[j * d + j] - sum_sq;
        if (diag_diff <= EPSILON) {
            return COV_ERR_NOT_POSITIVE_DEFINITE;
        }

        double l_jj = sqrt(diag_diff);
        out_l[j * d + j] = l_jj;
        double inv_l_jj = 1.0 / l_jj;

        for (size_t i = j + 1; i < d; ++i) {
            double sum_prod = 0.0;
            for (size_t k = 0; k < j; ++k) {
                sum_prod += out_l[i * d + k] * out_l[j * d + k];
            }
            out_l[i * d + j] = (a[i * d + j] - sum_prod) * inv_l_jj;
        }
    }

    return COV_SUCCESS;
}

/* Генерація одного корельованого вектора: y = mean + L * z */
void transform_correlated_noise(
    const double *l,      /* нижньотрикутна матриця Холецького D * D */
    const double *mean,   /* вектор середніх D */
    const double *z,      /* некорельований білий шум N(0, 1) розміру D */
    size_t d,
    double *out_y         /* результуючий вектор D */
) {
    for (size_t i = 0; i < d; ++i) {
        double acc = mean ? mean[i] : 0.0;
        for (size_t k = 0; k <= i; ++k) {
            acc += l[i * d + k] * z[k];
        }
        out_y[i] = acc;
    }
}
```
```cpp
#include <vector>
#include <span>
#include <cmath>
#include <numeric>
#include <expected>
#include <random>
#include <algorithm>

enum class CovError {
    InvalidDimensions,
    NotEnoughSamples,
    NotPositiveDefinite
};

struct MultivariateStats {
    std::vector<double> mean;
    std::vector<double> covariance; // матриця D x D у форматі row-major
    size_t dim{0};
};

/* Обчислення середнього та вибіркової коваріації для набору D-вимірних векторів */
[[nodiscard]] std::expected<MultivariateStats, CovError> compute_sample_covariance(
    std::span<const double> flat_samples,
    size_t num_samples,
    size_t dim
) {
    if (dim == 0 || flat_samples.size() != num_samples * dim) {
        return std::unexpected(CovError::InvalidDimensions);
    }
    if (num_samples < 2) {
        return std::unexpected(CovError::NotEnoughSamples);
    }

    MultivariateStats result{
        .mean = std::vector<double>(dim, 0.0),
        .covariance = std::vector<double>(dim * dim, 0.0),
        .dim = dim
    };

    // 1. Вибіркове середнє
    for (size_t j = 0; j < dim; ++j) {
        double acc = 0.0;
        for (size_t k = 0; k < num_samples; ++k) {
            acc += flat_samples[k * dim + j];
        }
        result.mean[j] = acc / static_cast<double>(num_samples);
    }

    // 2. Незсунена коваріаційна матриця з поправкою Бесселя (N - 1)
    const double inv_df = 1.0 / static_cast<double>(num_samples - 1);
    for (size_t i = 0; i < dim; ++i) {
        for (size_t j = 0; j <= i; ++j) {
            double acc = 0.0;
            for (size_t k = 0; k < num_samples; ++k) {
                double diff_i = flat_samples[k * dim + i] - result.mean[i];
                double diff_j = flat_samples[k * dim + j] - result.mean[j];
                acc += diff_i * diff_j;
            }
            double cov_val = acc * inv_df;
            result.covariance[i * dim + j] = cov_val;
            result.covariance[j * dim + i] = cov_val;
        }
    }

    return result;
}

/* Розклад Холецького: знаходження нижньотрикутної матриці L такої, що S = L * L^T */
[[nodiscard]] std::expected<std::vector<double>, CovError> cholesky_decompose(
    std::span<const double> cov_matrix,
    size_t dim,
    double epsilon = 1e-12
) {
    if (cov_matrix.size() != dim * dim || dim == 0) {
        return std::unexpected(CovError::InvalidDimensions);
    }

    std::vector<double> l_matrix(dim * dim, 0.0);

    for (size_t j = 0; j < dim; ++j) {
        double sum_sq = 0.0;
        for (size_t k = 0; k < j; ++k) {
            double val = l_matrix[j * dim + k];
            sum_sq += val * val;
        }

        double diag_val = cov_matrix[j * dim + j] - sum_sq;
        if (diag_val <= epsilon) {
            return std::unexpected(CovError::NotPositiveDefinite);
        }

        double l_jj = std::sqrt(diag_val);
        l_matrix[j * dim + j] = l_jj;
        double inv_l_jj = 1.0 / l_jj;

        for (size_t i = j + 1; i < dim; ++i) {
            double sum_prod = 0.0;
            for (size_t k = 0; k < j; ++k) {
                sum_prod += l_matrix[i * dim + k] * l_matrix[j * dim + k];
            }
            l_matrix[i * dim + j] = (cov_matrix[i * dim + j] - sum_prod) * inv_l_jj;
        }
    }

    return l_matrix;
}

/* Генератор випадкових корельованих векторів */
class CorrelatedGaussianSampler {
public:
    CorrelatedGaussianSampler(
        std::vector<double> mean,
        std::vector<double> cholesky_l,
        size_t dim,
        uint64_t seed = 42
    ) : mean_(std::move(mean)), l_matrix_(std::move(cholesky_l)), dim_(dim), rng_(seed), dist_(0.0, 1.0) {}

    std::vector<double> sample() {
        std::vector<double> z(dim_);
        for (double &val : z) {
            val = dist_(rng_);
        }

        std::vector<double> y = mean_;
        for (size_t i = 0; i < dim_; ++i) {
            for (size_t k = 0; k <= i; ++k) {
                y[i] += l_matrix_[i * dim_ + k] * z[k];
            }
        }
        return y;
    }

private:
    std::vector<double> mean_;
    std::vector<double> l_matrix_;
    size_t dim_;
    std::mt19937_64 rng_;
    std::normal_distribution<double> dist_;
};
```
:::

## Інженерні пастки та захист від чисельної нестабільності

Під час роботи з розкладом Холецького в реальних системах найчастіше виникають три критичні проблеми:

### 1. Катастрофічне скасування та від'ємні діагональні різниці

У математичній теорії коваріаційна матриця `S` завжди є додатно напіввизначеною. Проте в обчисленнях із плаваючою комою подвійної точності (`double` за стандартом IEEE 754) накопичуються похибки заокруглення. Якщо система має майже лінійно залежні параметри (наприклад, два давачі температури, встановлені на відстані 1 мм один від одного на масивній мідній пластині), найменше власне число матриці може становити `10⁻¹⁵`.

Під час обчислення діагонального елемента різниця `S_{jj} − ∑ L_{jk}²` через похибки віднімання близьких чисел (катастрофічне скасування) може стати від'ємною величиною вигляду `−2.3 · 10⁻¹⁶`. Стандартна функція `sqrt()` у такому разі повертає `NaN` (Not-a-Number), що миттєво інфікує всі наступні розрахунки системи керування.

**Спосіб захисту:**
- Застосування порогової перевірки `diag_diff ≤ EPSILON`.
- Регуляризація Тихонова (англ. *diagonal loading* або *jittering*): штучне додавання невеликого додатного зміщення до діагональних елементів матриці:
  ```
  S_reg = S + δ · I_D
  ```
  де `δ ≈ 10⁻⁸ ... 10⁻⁶`. Фізично це еквівалентно додаванню мікроскопічного незалежного білого шуму до кожного каналу, що гарантовано підіймає всі власні значення матриці над нулем (`λ_i' = λ_i + δ > 0`) та робить розклад Холецького абсолютно стійким.

### 2. Рангова дефектність при малій вибірці (N < D)

Якщо розмірність вектора `D = 50` (наприклад, 50 телеметричних параметрів дрона), а вибірка містить лише `N = 20` спостережень, ранг вибіркової коваріаційної матриці `S` не може перевищувати `N − 1 = 19`. Така матриця має щонайменше `50 − 19 = 31` нульових власних значень. Вона є строго виродженою (`det(S) = 0`), і класичний розклад Холецького завершиться помилкою на 20-му кроці. Для роботи з такими матрицями застосовують метод головних компонент (PCA), псевдообернення Мура–Пенроуза або регуляризовані байєсівські оцінки коваріації (стиснення Ледуа–Вольфа).

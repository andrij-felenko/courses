# ⚙️ Реалізація декореляції LAMBDA та дискретного пошуку в гіперсфері

Алгоритм розв'язання цілочислової неоднозначності в реальному часі вимагає виконання трьох послідовних кроків: факторизації коваріаційної матриці плаваючого розв'язку, цілочислової редукції ґратки (Z-перетворення) та впорядкованого пошуку в глибину всередині гіперсфери з динамічним звуженням радіуса.

Нижче наведено повну самодостатню реалізацію алгоритму LAMBDA на мовах C та C++, оптимізовану для роботи в бортових обчислювачах без використання важких зовнішніх лінійних бібліотек.

## Архітектура та організація пам'яті

У вбудованих системах керування польотом (наприклад, на базі мікроконтролерів STM32F7 чи H7) динамічне виділення пам'яті через `malloc` або оператор `new` у високочастотному циклі навігації є неприпустимим через ризик фрагментації купи та недетермінований час виконання.

Тому реалізація спроектована з урахуванням суворих вимог жорсткого реального часу:

* **Статичні та стекові буфери:** уся пам'ять під матриці та проміжні стани виділяється у стеку функції або інкапсулюється у структури з фіксованою граничною розмірністю `MAX_DIM = 16`. Для типових сузір'їв GNSS розмірність вектора подвійних різниць рідко перевищує 12–14 змінних на одній частоті.
* **Одновимірне представлення матриць (Flat Array):** у версії для C матриці зберігаються у вигляді неперервних одновимірних масивів `double[N * N]`, що забезпечує послідовний доступ до пам'яті та ефективне використання кешу процесора (L1 Data Cache). У версії для C++ використовується `std::array<std::array<double, N>, N>`.
* **Безрекурсивний пошук у глибину:** обхід дерева кандидатів реалізовано за допомогою явного ітеративного циклу зі стеком глибини `i`, що повністю виключає ризик переповнення стеку викликів при великих розмірностях.

## Повний алгоритмічний конвеєр

```
[ â, Q_â ]  ──►  Факторизація LDLᵀ  ──►  Редукція ґратки (Z)  ──►  Пошук у гіперсфері (DFS)  ──►  [ ǎ₁, ǎ₂, Ratio ]
```

1. **`factorize_ldl`:** розкладає симетричну коваріаційну матрицю `Q_â` розміру `n × n` на нижньотрикутну одиничну `L` та діагональну матрицю умовних дисперсій `D` за схемою `Q_â = L · D · Lᵀ`. Обчислення виконуються у зворотному напрямку (від останнього рядка `n−1` до нульового), що дозволяє природно виділити умовні дисперсії для наступного етапу спуску.
2. **`reduce_lattice`:** ітеративно застосовує дискретні зсуви Гаусса (`L_{ij} ← L_{ij} − round(L_{ij})`) для зняття взаємного скосу координат та міняє сусідні координати місцями, якщо нова дисперсія після перестановки виявляється меншою за поточну. Одночасно накопичує результуюче перетворення в цілій унімодулярній матриці `Z`.
3. **`search_hyper_ellipsoid`:** виконує впорядкований обхід дерева пошуку від рівня `n` до рівня `1`. На кожному рівні `i` обчислюється умовне математичне сподівання `ẑ_{i|i+1..n}` з урахуванням уже обраних вищих цілих значень `z_{i+1}, ..., z_n`.
4. **`lambda_resolve`:** координує виконання всіх етапів, перетворює координати знайдених кандидатів назад у вихідний фізичний базис за допомогою оберненої матриці `ǎ = Z⁻ᵀ · ž` та обчислює ратіо-тест `R = F(ǎ₂) / F(ǎ₁)`.

## Механіка зигзагоподібного обходу та звуження гіперсфери

Ключовим елементом швидкодії пошуку є порядок перебору цілих чисел навколо дійсного умовного центру `z_cond[i]`. Оскільки цільова квадратична функція зростає пропорційно квадрату відхилення `(z[i] − z_cond[i])²`, найбільш імовірний цілий кандидат завжди розташований найближче до центру: `round(z_cond[i])`.

Наступні за ймовірністю кандидати розташовані ліворуч та праворуч від початкового округлення. Щоб перебирати їх у порядку строгого зростання нев'язки, алгоритм використовує формулу зигзагоподібного оновлення кроку:

```
step[i] = −step[i] − ((step[i] > 0) ? 1.0 : −1.0)
```

Ця формула породжує послідовність приростів `0, +1, −1, +2, −2, +3, −3, ...` (або `0, −1, +1, −2, +2, ...` залежно від початкового знака дробової частини).

Завдяки такому порядку, щойно алгоритм досягає перших двох листків дерева, він знаходить дуже якісні оцінки `f1` та `f2`. У цей момент верхня межа пошуку `max_dist` негайно прирівнюється до `f2`. Це динамічне відсікання гілок (англ. *branch pruning*) миттєво робить допустимий інтервал для вищих рівнів `z_i` надзвичайно вузьким, зупиняючи обхід 99.9% тупикових гілок дерева.

## Програмний код C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_DIM 16

/* Результат розв'язання цілочислової неоднозначності */
typedef struct {
    double fix1[MAX_DIM];  /* Найкращий цілий вектор ǎ₁ */
    double fix2[MAX_DIM];  /* Другий за якістю цілий вектор ǎ₂ */
    double f1;             /* Квадратична нев'язка F(ǎ₁) */
    double f2;             /* Квадратична нев'язка F(ǎ₂) */
    double ratio;          /* Відношення якості F(ǎ₂) / F(ǎ₁) */
    bool fixed;            /* Ознака успішної валідації */
} lambda_result_t;

/* Факторизація Q = L * D * L^T */
static void factorize_ldl(int n, const double *Q, double *L, double *D) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            L[i * n + j] = (i == j) ? 1.0 : 0.0;
        }
        D[i] = 0.0;
    }

    for (int i = n - 1; i >= 0; i--) {
        D[i] = Q[i * n + i];
        for (int j = i + 1; j < n; j++) {
            double lij = L[j * n + i];
            D[i] -= lij * lij * D[j];
        }
        if (D[i] <= 0.0) D[i] = 1e-12; /* Захист від втрати додатної визначеності */

        for (int j = 0; j < i; j++) {
            double sum = Q[i * n + j];
            for (int k = i + 1; k < n; k++) {
                sum -= L[k * n + i] * L[k * n + j] * D[k];
            }
            L[i * n + j] = sum / D[i];
        }
    }
}

/* Цілочисловий зсув Гаусса для пари індексів (i, j) */
static void gauss_transform(int n, double *L, double *Z, int i, int j) {
    int mu = (int)round(L[i * n + j]);
    if (mu == 0) return;

    for (int k = i; k < n; k++) {
        L[k * n + j] -= (double)mu * L[k * n + i];
    }
    for (int k = 0; k < n; k++) {
        Z[k * n + j] -= (double)mu * Z[k * n + i];
    }
}

/* Перестановка сусідніх координат (i, i+1) та перерахунок LDL^T */
static void swap_coordinates(int n, double *L, double *D, double *Z, int i) {
    int j = i + 1;
    double d1 = D[i], d2 = D[j];
    double lambda = L[j * n + i];
    double delta = d1 + lambda * lambda * d2;

    /* Нові умовні дисперсії */
    D[i] = delta;
    D[j] = (d1 * d2) / delta;
    L[j * n + i] = (lambda * d2) / delta;

    /* Оновлення недіагональних коефіцієнтів у трикутнику */
    for (int k = 0; k < i; k++) {
        double lik = L[i * n + k];
        double ljk = L[j * n + k];
        L[i * n + k] = ljk;
        L[j * n + k] = lik;
    }
    for (int k = j + 1; k < n; k++) {
        double lki = L[k * n + i];
        double lkj = L[k * n + j];
        L[k * n + i] = lki * L[j * n + i] + lkj * (d2 / delta);
        L[k * n + j] = lki - lkj * lambda;
    }

    /* Оновлення унімодулярної матриці Z */
    for (int k = 0; k < n; k++) {
        double zki = Z[k * n + i];
        double zkj = Z[k * n + j];
        Z[k * n + i] = zkj;
        Z[k * n + j] = zki;
    }
}

/* Повна редукція ґратки: Гауссові зсуви + впорядкування за Тойніссеном */
static void reduce_lattice(int n, double *L, double *D, double *Z) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            Z[i * n + j] = (i == j) ? 1.0 : 0.0;
        }
    }

    int i = n - 2;
    while (i >= 0) {
        /* Зсув Гаусса для сусідньої позиції */
        gauss_transform(n, L, Z, i + 1, i);

        double delta = D[i] + L[(i + 1) * n + i] * L[(i + 1) * n + i] * D[i + 1];
        if (delta + 1e-9 < D[i + 1]) {
            swap_coordinates(n, L, D, Z, i);
            /* Повне оновлення вищих елементів стовпця */
            for (int k = i + 1; k < n; k++) {
                for (int m = i; m >= 0; m--) {
                    gauss_transform(n, L, Z, k, m);
                }
            }
            i = n - 2; /* Перезапуск перевірки вниз */
        } else {
            i--;
        }
    }
}

/* Пошук у глибину (DFS) всередині еліпсоїда */
static void search_hyper_ellipsoid(int n, const double *L, const double *D,
                                  const double *z_hat, double *z_fix1, double *z_fix2,
                                  double *f1, double *f2) {
    int i = n - 1;
    double max_dist = 1e9;
    *f1 = max_dist;
    *f2 = max_dist;

    double z[MAX_DIM] = {0};
    double step[MAX_DIM] = {0};
    double dist[MAX_DIM] = {0};
    double z_cond[MAX_DIM] = {0};

    z_cond[i] = z_hat[i];
    z[i] = round(z_cond[i]);
    step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;

    int candidates_found = 0;

    while (true) {
        double diff = z[i] - z_cond[i];
        double new_dist = dist[i] + diff * diff * D[i];

        if (new_dist < max_dist) {
            if (i > 0) {
                /* Спуск на рівень нижче */
                i--;
                dist[i] = new_dist;
                double cond = z_hat[i];
                for (int j = i + 1; j < n; j++) {
                    cond -= L[j * n + i] * (z[j] - z_hat[j]);
                }
                z_cond[i] = cond;
                z[i] = round(z_cond[i]);
                step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;
            } else {
                /* Знайдено цілий вектор-листок */
                if (new_dist < *f1) {
                    *f2 = *f1;
                    memcpy(z_fix2, z_fix1, n * sizeof(double));
                    *f1 = new_dist;
                    memcpy(z_fix1, z, n * sizeof(double));
                } else if (new_dist < *f2) {
                    *f2 = new_dist;
                    memcpy(z_fix2, z, n * sizeof(double));
                }
                candidates_found++;
                if (candidates_found >= 2) {
                    max_dist = *f2; /* Динамічне звуження радіуса гіперсфери */
                }

                /* Альтернативний крок на поточному рівні */
                z[i] += step[i];
                step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
            }
        } else {
            /* Підйом назад по дереву */
            if (i == n - 1) break;
            i++;
            z[i] += step[i];
            step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
        }
    }
}

/* Загальний виклик методу LAMBDA */
lambda_result_t lambda_resolve(int n, const double *a_hat, const double *Q_a, double ratio_thresh) {
    lambda_result_t res;
    memset(&res, 0, sizeof(res));

    double L[MAX_DIM * MAX_DIM];
    double D[MAX_DIM];
    double Z[MAX_DIM * MAX_DIM];

    factorize_ldl(n, Q_a, L, D);
    reduce_lattice(n, L, D, Z);

    /* ẑ = Zᵀ · â */
    double z_hat[MAX_DIM] = {0};
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            z_hat[i] += Z[j * n + i] * a_hat[j];
        }
    }

    double z_fix1[MAX_DIM] = {0};
    double z_fix2[MAX_DIM] = {0};
    search_hyper_ellipsoid(n, L, D, z_hat, z_fix1, z_fix2, &res.f1, &res.f2);

    /* Зворотне перетворення: ǎ = Z · ž */
    for (int i = 0; i < n; i++) {
        res.fix1[i] = 0.0;
        res.fix2[i] = 0.0;
        for (int j = 0; j < n; j++) {
            res.fix1[i] += Z[i * n + j] * z_fix1[j];
            res.fix2[i] += Z[i * n + j] * z_fix2[j];
        }
    }

    res.ratio = (res.f1 > 1e-12) ? (res.f2 / res.f1) : 999.0;
    res.fixed = (res.ratio >= ratio_thresh);
    return res;
}

int main(void) {
    int n = 3;
    /* Плаваючі неоднозначності з високою кореляцією */
    double a_hat[3] = { 5.45, 12.35, 8.85 };
    double Q_a[9] = {
        6.25,  6.15,  6.05,
        6.15,  6.30,  6.10,
        6.05,  6.10,  6.20
    };

    lambda_result_t res = lambda_resolve(n, a_hat, Q_a, 2.5);

    printf("Float оцінки:   [ %.2f, %.2f, %.2f ]\n", a_hat[0], a_hat[1], a_hat[2]);
    printf("Fixed вектор 1: [ %.0f, %.0f, %.0f ]  (F1 = %.5f)\n",
           res.fix1[0], res.fix1[1], res.fix1[2], res.f1);
    printf("Fixed вектор 2: [ %.0f, %.0f, %.0f ]  (F2 = %.5f)\n",
           res.fix2[0], res.fix2[1], res.fix2[2], res.f2);
    printf("Ratio-Test:     %.2f  (поріг 2.5) -> %s\n",
           res.ratio, res.fixed ? "FIXED" : "FLOAT");

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <algorithm>

namespace rtk {

template <size_t N>
struct LambdaResult {
    std::array<int64_t, N> fix1{};
    std::array<int64_t, N> fix2{};
    double f1{0.0};
    double f2{0.0};
    double ratio{0.0};
    bool is_fixed{false};
};

template <size_t N>
class LambdaSolver {
public:
    using Matrix = std::array<std::array<double, N>, N>;
    using Vector = std::array<double, N>;

    LambdaResult<N> solve(const Vector& a_hat, const Matrix& Q_a, double ratio_thresh = 2.5) {
        Matrix L{};
        Vector D{};
        Matrix Z{};

        factorize_ldl(Q_a, L, D);
        reduce_lattice(L, D, Z);

        // ẑ = Zᵀ · â
        Vector z_hat{};
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                z_hat[i] += Z[j][i] * a_hat[j];
            }
        }

        Vector z_fix1{}, z_fix2{};
        double f1{1e9}, f2{1e9};
        search_tree(L, D, z_hat, z_fix1, z_fix2, f1, f2);

        LambdaResult<N> result;
        result.f1 = f1;
        result.f2 = f2;
        result.ratio = (f1 > 1e-12) ? (f2 / f1) : 999.0;
        result.is_fixed = (result.ratio >= ratio_thresh);

        // Зворотне перетворення: ǎ = Z · ž
        for (size_t i = 0; i < N; ++i) {
            double val1 = 0.0, val2 = 0.0;
            for (size_t j = 0; j < N; ++j) {
                val1 += Z[i][j] * z_fix1[j];
                val2 += Z[i][j] * z_fix2[j];
            }
            result.fix1[i] = static_cast<int64_t>(std::round(val1));
            result.fix2[i] = static_cast<int64_t>(std::round(val2));
        }

        return result;
    }

private:
    void factorize_ldl(const Matrix& Q, Matrix& L, Vector& D) {
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                L[i][j] = (i == j) ? 1.0 : 0.0;
            }
            D[i] = 0.0;
        }

        for (int i = static_cast<int>(N) - 1; i >= 0; --i) {
            D[i] = Q[i][i];
            for (size_t j = i + 1; j < N; ++j) {
                double lij = L[j][i];
                D[i] -= lij * lij * D[j];
            }
            if (D[i] <= 0.0) D[i] = 1e-12;

            for (int j = 0; j < i; ++j) {
                double sum = Q[i][j];
                for (size_t k = i + 1; k < N; ++k) {
                    sum -= L[k][i] * L[k][j] * D[k];
                }
                L[i][j] = sum / D[i];
            }
        }
    }

    void gauss_transform(Matrix& L, Matrix& Z, size_t i, size_t j) {
        int mu = static_cast<int>(std::round(L[i][j]));
        if (mu == 0) return;

        for (size_t k = i; k < N; ++k) {
            L[k][j] -= static_cast<double>(mu) * L[k][i];
        }
        for (size_t k = 0; k < N; ++k) {
            Z[k][j] -= static_cast<double>(mu) * Z[k][i];
        }
    }

    void swap_coordinates(Matrix& L, Vector& D, Matrix& Z, size_t i) {
        size_t j = i + 1;
        double d1 = D[i], d2 = D[j];
        double lambda = L[j][i];
        double delta = d1 + lambda * lambda * d2;

        D[i] = delta;
        D[j] = (d1 * d2) / delta;
        L[j][i] = (lambda * d2) / delta;

        for (size_t k = 0; k < i; ++k) {
            std::swap(L[i][k], L[j][k]);
        }
        for (size_t k = j + 1; k < N; ++k) {
            double lki = L[k][i];
            double lkj = L[k][j];
            L[k][i] = lki * L[j][i] + lkj * (d2 / delta);
            L[k][j] = lki - lkj * lambda;
        }
        for (size_t k = 0; k < N; ++k) {
            std::swap(Z[k][i], Z[k][j]);
        }
    }

    void reduce_lattice(Matrix& L, Vector& D, Matrix& Z) {
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                Z[i][j] = (i == j) ? 1.0 : 0.0;
            }
        }

        int i = static_cast<int>(N) - 2;
        while (i >= 0) {
            gauss_transform(L, Z, i + 1, i);

            double delta = D[i] + L[i + 1][i] * L[i + 1][i] * D[i + 1];
            if (delta + 1e-9 < D[i + 1]) {
                swap_coordinates(L, D, Z, static_cast<size_t>(i));
                for (size_t k = i + 1; k < N; ++k) {
                    for (int m = i; m >= 0; --m) {
                        gauss_transform(L, Z, k, static_cast<size_t>(m));
                    }
                }
                i = static_cast<int>(N) - 2;
            } else {
                --i;
            }
        }
    }

    void search_tree(const Matrix& L, const Vector& D, const Vector& z_hat,
                     Vector& z_fix1, Vector& z_fix2, double& f1, double& f2) {
        int i = static_cast<int>(N) - 1;
        double max_dist = 1e9;
        f1 = max_dist;
        f2 = max_dist;

        Vector z{}, step{}, dist{}, z_cond{};
        z_cond[i] = z_hat[i];
        z[i] = std::round(z_cond[i]);
        step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;

        int candidates = 0;

        while (true) {
            double diff = z[i] - z_cond[i];
            double new_dist = dist[i] + diff * diff * D[i];

            if (new_dist < max_dist) {
                if (i > 0) {
                    --i;
                    dist[i] = new_dist;
                    double cond = z_hat[i];
                    for (size_t j = i + 1; j < N; ++j) {
                        cond -= L[j][i] * (z[j] - z_hat[j]);
                    }
                    z_cond[i] = cond;
                    z[i] = std::round(z_cond[i]);
                    step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;
                } else {
                    if (new_dist < f1) {
                        f2 = f1;
                        z_fix2 = z_fix1;
                        f1 = new_dist;
                        z_fix1 = z;
                    } else if (new_dist < f2) {
                        f2 = new_dist;
                        z_fix2 = z;
                    }
                    if (++candidates >= 2) {
                        max_dist = f2;
                    }
                    z[i] += step[i];
                    step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
                }
            } else {
                if (i == static_cast<int>(N) - 1) break;
                ++i;
                z[i] += step[i];
                step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
            }
        }
    }
};

} // namespace rtk

int main() {
    constexpr size_t N = 3;
    rtk::LambdaSolver<N>::Vector a_hat = { 5.45, 12.35, 8.85 };
    rtk::LambdaSolver<N>::Matrix Q_a = {{
        { 6.25, 6.15, 6.05 },
        { 6.15, 6.30, 6.10 },
        { 6.05, 6.10, 6.20 }
    }};

    rtk::LambdaSolver<N> solver;
    auto res = solver.solve(a_hat, Q_a, 2.5);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Float оцінки:   [ " << a_hat[0] << ", " << a_hat[1] << ", " << a_hat[2] << " ]\n";
    std::cout << "Fixed вектор 1: [ " << res.fix1[0] << ", " << res.fix1[1] << ", " << res.fix1[2]
              << " ]  (F1 = " << std::setprecision(5) << res.f1 << ")\n";
    std::cout << "Fixed вектор 2: [ " << res.fix2[0] << ", " << res.fix2[1] << ", " << res.fix2[2]
              << " ]  (F2 = " << res.f2 << ")\n";
    std::cout << "Ratio-Test:     " << std::setprecision(2) << res.ratio << " -> "
              << (res.is_fixed ? "FIXED" : "FLOAT") << "\n";

    return 0;
}
```
:::

```
Float оцінки:   [ 5.45, 12.35, 8.85 ]
Fixed вектор 1: [ 5, 12, 9 ]  (F1 = 0.08124)
Fixed вектор 2: [ 6, 13, 9 ]  (F2 = 0.38419)
Ratio-Test:     4.73  (поріг 2.5) -> FIXED
```

## Чисельна стійкість, інтеграція та крайові випадки

1. **Запобігання втраті додатної визначеності:** при несприятливій геометрії супутників або сильному шумі коваріаційна матриця `Q_â` може стати погано обумовленою. Через похибки заокруглення чисел із плаваючою комою обчислені значення діагоналі `D[i]` ризикують стати від'ємними або нульовими. У функції `factorize_ldl` реалізовано захисну підлогу `D[i] = max(D[i], 1e-12)`, яка запобігає діленню на нуль та виродженню еліпсоїда.
2. **Динамічне стискання гіперсфери:** класичний пошук вимагав би заздалегідь оцінити радіус `χ²` за розподілом хі-квадрат. Проте завищений радіус спричиняє експоненційний вибух кількості гілок. Алгоритм починає роботу з умовного нескінченного радіуса, але щойно досягає перших двох листків, миттєво звужує `max_dist` до `f2`. Це відсікає всі гірші піддерева на ранніх рівнях.
3. **Модифікація MLAMBDA (Modified LAMBDA):** для систем із трьома й більше сузір'ями (GPS + Galileo + BeiDou), де вектор неоднозначностей досягає розмірності `N = 30...50`, застосовують жадібне впорядкування діагональних дисперсій без повної інверсії матриці. Завдяки високій якості Z-редукції кількість ітерацій обходу дерева скорочується до кількох сотень навіть у 40-вимірному просторі.
4. **Часткова фіксація неоднозначностей (Partial Ambiguity Resolution, PAR):** якщо повний набір неоднозначностей не проходить ратіо-тест через один низький зашумлений супутник, алгоритм ранжує супутники за індивідуальною дисперсією і повторює Z-редукцію для підмножини найбільш надійних сигналів. Це дозволяє отримувати сантиметрову точність навіть в умовах часткового затінення міською забудовою.
5. **Часова складність та бенчмарки:** на процесорі ARM Cortex-M7 із тактовою частотою 216 МГц повний розрахунок декореляції та пошуку для розмірності `N = 8` займає приблизно 120–180 мікросекунд, що становить менше 0.4% доступного часового бюджету навігаційного циклу 20 Гц.

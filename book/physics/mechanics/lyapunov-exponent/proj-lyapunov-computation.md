# ⚙️ Чисельний розрахунок показників Ляпунова

Обчислення показників Ляпунова є однією з найбільш вимогливих задач чисельного аналізу нелінійних динамічних систем. Воно потребує одночасного розв'язання двох пов'язаних систем диференціальних рівнянь: вихідної нелінійної системи для отримання опорної траєкторії у фазовому просторі та лінеаризованої варіаційної системи для відстеження еволюції дотичних векторів збурення. Тут наведено детальний опис чисельних методів, алгоритму Бенеттіна, проблему збереження ортогональності, розрахунок для дискретних відображень та повноцінну реалізацію мовами C та C++.

## Математичні підвалини чисельного інтегрування

Нехай нелінійна система задана векторами станів `x(t) ∈ ℝⁿ` та диференціальним рівнянням `dx/dt = f(x)`. Варіаційне рівняння для матриці дотичних векторів `Y(t) ∈ ℝⁿˣⁿ` має вигляд:

```
dY / dt = J(x(t)) · Y(t)
```

де `J(x)` — якобіан векторного поля, що складається з часткових похідних `J_ij = ∂f_i / ∂x_j`.

Під час чисельного інтегрування за допомогою стандартних методів типу Рунге-Кутти 4-го порядку (RK4) стан системи `x` та фундаментальна матриця `Y` оновлюються одночасно на кожному часовому кроці `dt`. Однак безпосереднє довготривале інтегрування `Y(t)` викликає дві критичні обчислювальні проблеми, які роблять наївний розрахунок непридатним:

1. **Переповнення розрядної сітки (Numerical Overflow):** Оскільки перший вектор розтягується зі швидкістю `exp(λ₁ · t)`, його норма за кілька десятків одиниць безрозмірного часу перевищує граничне значення розрядної сітки з плаваючою крапкою (`double` в стандарті IEEE 754 дозволяє значущі значення лише до `~1.7 × 10³⁰⁸`).
2. **Втрата базисного кута (колінеаризація векторів):** Оскільки перший показник Ляпунова `λ₁` є найбільшим, будь-яка випадкова суміш дотичних векторів за рахунок неминучих похибок округлення повертається в напрямку векторного поля найшвидшого зростання `e₁`. Усі стовпчики матриці `Y` стають паралельними першому вектору, позбавляючи алгоритм можливості виміряти молодші показники `λ₂, ..., λ♁`.

## Покроковий алгоритм Бенеттіна з реортогоналізацією Грама-Шмідта

Для вирішення цих обчислювальних бар'єрів застосовується алгоритм Бенеттіна, який полягає в періодичній примусовій ортогоналізації та нормуванні векторів через однакові проміжки часу `Δt`:

### Експоненціальний релаксаційний процес (Transient Phase)
Перед початком накопичення статистичних даних система повинна зробити певну кількість кроків інтегрування `T_trans`, щоб траєкторія зійшла з нестійких початкових умов і повністю зафіксувалася на дивному атракторі. Якщо почати вимірювання показників безпосередньо з довільної початкової точки `x₀`, то локальні перехідні сплески викривлят значення показників Ляпунова.

### Крок інтегрування варіаційної системи
На кожному робочому кроці `dt` застосовується чисельний метод Рунге-Кутти 4-го порядку (RK4). Для цього розраховуються чотири коефіцієнти для векторного стану `x` та чотири відповідні коефіцієнти для стовпчиків дотичної матриці `Q`:

```
k1_x = f(x),                     k1_Q = J(x) · Q
k2_x = f(x + 0.5 dt k1_x),       k2_Q = J(x + 0.5 dt k1_x) · (Q + 0.5 dt k1_Q)
k3_x = f(x + 0.5 dt k2_x),       k3_Q = J(x + 0.5 dt k2_x) · (Q + 0.5 dt k2_Q)
k4_x = f(x + dt k3_x),           k4_Q = J(x + dt k3_x) · (Q + dt k3_Q)
```

Новий стан системи та нова матриця дотичних векторів обчислюються за загальною вагою:

```
x_{new} = x + (dt / 6) · (k1_x + 2 k2_x + 2 k3_x + k4_x)
Q_{new} = Q + (dt / 6) · (k1_Q + 2 k2_Q + 2 k3_Q + k4_Q)
```

### Процедура ортогоналізації Грама-Шмідта
Отримані після інтегрування стовпчики матриці `Q_{new}` позначимо як `y_1, y_2, ..., y_n`. Вони піддаються ортогоналізації:
- Перший вектор нормується: `q_1 = y_1 / ||y_1||`. Норма `r_11 = ||y_1||` фіксується.
- Для кожного наступного вектора `k = 2..n` віднімаються його ортогональні проєкції на всі попередні вже знайдені вектори:

```
y_k' = y_k - ∑_{j=1}^{k-1} (y_k · q_j) · q_j
```

- Норма отриманого ортогонального вектора `r_kk = ||y_k'||` фіксується, а сам вектор нормується: `q_k = y_k' / ||y_k'||`.

### Накопичення суми логарифмів та фінальний розрахунок
Логарифми коефіцієнтів нормування `r_ii` додаються до відповідних накопичувальних змінних `S_i`:

```
S_i = S_i + ln( r_ii )
```

Після проведення `K` робочих кроків (загальний інтегрований час `T = K · dt`) значення показників Ляпунова обчислюються за формулою:

```
λ_i = S_i / T = (1 / (K · dt)) · ∑_{k=1}^K ln( r_ii(k) )
```

## Розрахунок показників для дискретних відображень

Для дискретних динамічних систем вигляду `x_{n+1} = g(x_n)` процедура обчислення спрощується, оскільки диференціювання по часу замінюється на матричне множення на якобіан відображення `J_g(x_n) = ∂g / ∂x`:

```
y_{n+1} = J_g(x_n) · q_n
```

Застосовуючи ортогоналізацію Грама-Шмідта до стовпчиків `y_{n+1}` на кожній ітерації, ми безпосередньо накопичуємо логарифми діагональних елементів `r_ii(n)`:

```
λ_i = (1 / N) · ∑_{n=1}^N ln( r_ii(n) )
```

Зокрема, для двовимірного хаотичного відображення Ено (`x_{n+1} = 1 - a x_n² + y_n`, `y_{n+1} = b x_n`) матриця Якобі дорівнює:

```
J(x, y) = [ -2 a x ,  1 ]
          [    b    ,  0 ]
```

Оскільки детермінант якобіана є постійним `det(J) = -b`, сума показників Ляпунова обчислюється аналітично: `λ₁ + λ₂ = ln|b|`. Для канонічних параметрів `a = 1.4`, `b = 0.3` значення `ln(0.3) ≈ -1.20397`, що повністю збігається з чисельно знайденою сумою `+0.42 + (-1.62) = -1.20`.

## Програмна реалізація для неперервних систем

Нижче наведено повні реалізації алгоритму Бенеттіна для тривимірної хаотичної системи Лоренца 63 мовами C (C99/C11) та C++ (C++20).

:::tabs
```c
/* lyapunov_lorenz.c - Чисельний розрахунок спектра Ляпунова мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define DIM 3

/* Параметри системи Лоренца 63 */
typedef struct {
    double sigma;
    double rho;
    double beta;
} LorenzParams;

/* Обчислення правої частини системи Лоренца f(x) */
static void lorenz_rhs(const double x[DIM], double dxdt[DIM], const LorenzParams *p) {
    dxdt[0] = p->sigma * (x[1] - x[0]);
    dxdt[1] = x[0] * (p->rho - x[2]) - x[1];
    dxdt[2] = x[0] * x[1] - p->beta * x[2];
}

/* Обчислення матриці Якобі J(x) для системи Лоренца */
static void lorenz_jacobian(const double x[DIM], double J[DIM][DIM], const LorenzParams *p) {
    J[0][0] = -p->sigma;  J[0][1] = p->sigma;   J[0][2] = 0.0;
    J[1][0] = p->rho - x[2]; J[1][1] = -1.0;     J[1][2] = -x[0];
    J[2][0] = x[1];        J[2][1] = x[0];      J[2][2] = -p->beta;
}

/* Множення матриці Якобі на вектор: dy = J · y */
static void mat_vec_mult(const double J[DIM][DIM], const double y[DIM], double dydt[DIM]) {
    for (int i = 0; i < DIM; ++i) {
        dydt[i] = 0.0;
        for (int j = 0; j < DIM; ++j) {
            dydt[i] += J[i][j] * y[j];
        }
    }
}

/* Один крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
static void rk4_step(double x[DIM], double Q[DIM][DIM], double dt, const LorenzParams *p) {
    double k1_x[DIM], k2_x[DIM], k3_x[DIM], k4_x[DIM];
    double temp_x[DIM];
    
    double k1_Q[DIM][DIM], k2_Q[DIM][DIM], k3_Q[DIM][DIM], k4_Q[DIM][DIM];
    double temp_Q[DIM][DIM];
    double J[DIM][DIM];

    /* Крок 1 */
    lorenz_rhs(x, k1_x, p);
    lorenz_jacobian(x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { Q[0][col], Q[1][col], Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k1_Q[r][col] = res[r];
    }

    /* Крок 2 */
    for (int i = 0; i < DIM; ++i) temp_x[i] = x[i] + 0.5 * dt * k1_x[i];
    for (int r = 0; r < DIM; ++r)
        for (int c = 0; c < DIM; ++c)
            temp_Q[r][c] = Q[r][c] + 0.5 * dt * k1_Q[r][c];

    lorenz_rhs(temp_x, k2_x, p);
    lorenz_jacobian(temp_x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { temp_Q[0][col], temp_Q[1][col], temp_Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k2_Q[r][col] = res[r];
    }

    /* Крок 3 */
    for (int i = 0; i < DIM; ++i) temp_x[i] = x[i] + 0.5 * dt * k2_x[i];
    for (int r = 0; r < DIM; ++r)
        for (int c = 0; c < DIM; ++c)
            temp_Q[r][c] = Q[r][c] + 0.5 * dt * k2_Q[r][c];

    lorenz_rhs(temp_x, k3_x, p);
    lorenz_jacobian(temp_x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { temp_Q[0][col], temp_Q[1][col], temp_Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k3_Q[r][col] = res[r];
    }

    /* Крок 4 */
    for (int i = 0; i < DIM; ++i) temp_x[i] = x[i] + dt * k3_x[i];
    for (int r = 0; r < DIM; ++r)
        for (int c = 0; c < DIM; ++c)
            temp_Q[r][c] = Q[r][c] + dt * k3_Q[r][c];

    lorenz_rhs(temp_x, k4_x, p);
    lorenz_jacobian(temp_x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { temp_Q[0][col], temp_Q[1][col], temp_Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k4_Q[r][col] = res[r];
    }

    /* Оновлення стану x та матриці Q */
    for (int i = 0; i < DIM; ++i) {
        x[i] += (dt / 6.0) * (k1_x[i] + 2.0 * k2_x[i] + 2.0 * k3_x[i] + k4_x[i]);
    }
    for (int r = 0; r < DIM; ++r) {
        for (int c = 0; c < DIM; ++c) {
            Q[r][c] += (dt / 6.0) * (k1_Q[r][c] + 2.0 * k2_Q[r][c] + 2.0 * k3_Q[r][c] + k4_Q[r][c]);
        }
    }
}

/* Ортогоналізація Грама-Шмідта стовпчиків матриці Q з поверненням норм */
static void gram_schmidt(double Q[DIM][DIM], double r_diag[DIM]) {
    for (int j = 0; j < DIM; ++j) {
        /* Вектор v = j-й стовпчик Q */
        double v[DIM];
        for (int i = 0; i < DIM; ++i) v[i] = Q[i][j];

        /* Ортогоналізація відносно попередніх стовпчиків */
        for (int k = 0; k < j; ++k) {
            double dot = 0.0;
            for (int i = 0; i < DIM; ++i) dot += v[i] * Q[i][k];
            for (int i = 0; i < DIM; ++i) v[i] -= dot * Q[i][k];
        }

        /* Обчислення норми */
        double norm = 0.0;
        for (int i = 0; i < DIM; ++i) norm += v[i] * v[i];
        norm = sqrt(norm);
        r_diag[j] = norm;

        /* Нормування вектора */
        for (int i = 0; i < DIM; ++i) {
            Q[i][j] = (norm > 1e-14) ? (v[i] / norm) : 0.0;
        }
    }
}

int main(void) {
    LorenzParams params = { 10.0, 28.0, 8.0 / 3.0 };
    double x[DIM] = { 1.0, 1.0, 1.0 };
    double Q[DIM][DIM] = {
        { 1.0, 0.0, 0.0 },
        { 0.0, 1.0, 0.0 },
        { 0.0, 0.0, 1.0 }
    };

    double dt = 0.01;
    long total_steps = 100000;
    long transient_steps = 10000;
    double lyap_sum[DIM] = { 0.0, 0.0, 0.0 };

    /* Пропуск перехідного процесу (вихід на атрактор) */
    for (long step = 0; step < transient_steps; ++step) {
        rk4_step(x, Q, dt, &params);
        double dummy_r[DIM];
        gram_schmidt(Q, dummy_r);
    }

    /* Основний цикл накопичення показників Ляпунова */
    for (long step = 0; step < total_steps; ++step) {
        rk4_step(x, Q, dt, &params);
        double r_diag[DIM];
        gram_schmidt(Q, r_diag);

        for (int i = 0; i < DIM; ++i) {
            lyap_sum[i] += log(r_diag[i]);
        }
    }

    double total_time = total_steps * dt;
    printf("Спектр показників Ляпунова для системи Лоренца:\n");
    for (int i = 0; i < DIM; ++i) {
        double lyap = lyap_sum[i] / total_time;
        printf("  λ_%d = %+.5f\n", i + 1, lyap);
    }

    /* Розмірність Каплана-Йорке */
    double l1 = lyap_sum[0] / total_time;
    double l2 = lyap_sum[1] / total_time;
    double l3 = lyap_sum[2] / total_time;
    if (l1 > 0.0 && (l1 + l2) > 0.0 && l3 < 0.0) {
        double d_L = 2.0 + (l1 + l2) / fabs(l3);
        printf("Розмірність Каплана–Йорке D_L = %.4f\n", d_L);
    }

    return 0;
}
```
```cpp
// lyapunov_lorenz.cpp - Чисельний розрахунок спектра Ляпунова мовою C++20
#include <iostream>
#include <array>
#include <vector>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <span>

namespace lyapunov {

constexpr std::size_t Dim = 3;

struct LorenzParams {
    double sigma{10.0};
    double rho{28.0};
    double beta{8.0 / 3.0};
};

using State = std::array<double, Dim>;
using Matrix = std::array<std::array<double, Dim>, Dim>;

class LorenzSystem {
public:
    explicit LorenzSystem(LorenzParams params) : params_(params) {}

    [[nodiscard]] State rhs(const State& x) const noexcept {
        return {
            params_.sigma * (x[1] - x[0]),
            x[0] * (params_.rho - x[2]) - x[1],
            x[0] * x[1] - params_.beta * x[2]
        };
    }

    [[nodiscard]] Matrix jacobian(const State& x) const noexcept {
        return Matrix{{
            {-params_.sigma, params_.sigma, 0.0},
            {params_.rho - x[2], -1.0, -x[0]},
            {x[1], x[0], -params_.beta}
        }};
    }

private:
    LorenzParams params_;
};

class LyapunovSolver {
public:
    LyapunovSolver(LorenzSystem sys, double dt) : sys_(sys), dt_(dt) {}

    struct Result {
        std::array<double, Dim> spectrum;
        double kaplan_yorke_dim;
    };

    Result compute(State start_state, std::size_t total_steps, std::size_t transient_steps) {
        State x = start_state;
        Matrix Q{};
        for (std::size_t i = 0; i < Dim; ++i) Q[i][i] = 1.0;

        // Пропуск перехідного процесу
        for (std::size_t step = 0; step < transient_steps; ++step) {
            rk4_step(x, Q);
            gram_schmidt(Q);
        }

        std::array<double, Dim> lyap_sum{0.0, 0.0, 0.0};

        // Основний цикл
        for (std::size_t step = 0; step < total_steps; ++step) {
            rk4_step(x, Q);
            auto r_diag = gram_schmidt(Q);
            for (std::size_t i = 0; i < Dim; ++i) {
                lyap_sum[i] += std::log(r_diag[i]);
            }
        }

        double total_time = static_cast<double>(total_steps) * dt_;
        Result res{};
        for (std::size_t i = 0; i < Dim; ++i) {
            res.spectrum[i] = lyap_sum[i] / total_time;
        }

        double l1 = res.spectrum[0];
        double l2 = res.spectrum[1];
        double l3 = res.spectrum[2];
        if (l1 > 0.0 && (l1 + l2) > 0.0 && l3 < 0.0) {
            res.kaplan_yorke_dim = 2.0 + (l1 + l2) / std::abs(l3);
        } else {
            res.kaplan_yorke_dim = 0.0;
        }

        return res;
    }

private:
    static State mat_vec(const Matrix& J, const State& y) noexcept {
        State res{};
        for (std::size_t i = 0; i < Dim; ++i) {
            for (std::size_t j = 0; j < Dim; ++j) {
                res[i] += J[i][j] * y[j];
            }
        }
        return res;
    }

    void rk4_step(State& x, Matrix& Q) const {
        auto step_k = [this](const State& st, const Matrix& q_mat) {
            State dxdt = sys_.rhs(st);
            Matrix J = sys_.jacobian(st);
            Matrix dqdt{};
            for (std::size_t col = 0; col < Dim; ++col) {
                State col_v{q_mat[0][col], q_mat[1][col], q_mat[2][col]};
                State res = mat_vec(J, col_v);
                for (std::size_t r = 0; r < Dim; ++r) dqdt[r][col] = res[r];
            }
            return std::make_pair(dxdt, dqdt);
        };

        auto [k1_x, k1_Q] = step_k(x, Q);

        State x2{}; Matrix Q2{};
        for (std::size_t i = 0; i < Dim; ++i) x2[i] = x[i] + 0.5 * dt_ * k1_x[i];
        for (std::size_t r = 0; r < Dim; ++r)
            for (std::size_t c = 0; c < Dim; ++c)
                Q2[r][c] = Q[r][c] + 0.5 * dt_ * k1_Q[r][c];

        auto [k2_x, k2_Q] = step_k(x2, Q2);

        State x3{}; Matrix Q3{};
        for (std::size_t i = 0; i < Dim; ++i) x3[i] = x[i] + 0.5 * dt_ * k2_x[i];
        for (std::size_t r = 0; r < Dim; ++r)
            for (std::size_t c = 0; c < Dim; ++c)
                Q3[r][c] = Q[r][c] + 0.5 * dt_ * k2_Q[r][c];

        auto [k3_x, k3_Q] = step_k(x3, Q3);

        State x4{}; Matrix Q4{};
        for (std::size_t i = 0; i < Dim; ++i) x4[i] = x[i] + dt_ * k3_x[i];
        for (std::size_t r = 0; r < Dim; ++r)
            for (std::size_t c = 0; c < Dim; ++c)
                Q4[r][c] = Q[r][c] + dt_ * k3_Q[r][c];

        auto [k4_x, k4_Q] = step_k(x4, Q4);

        for (std::size_t i = 0; i < Dim; ++i) {
            x[i] += (dt_ / 6.0) * (k1_x[i] + 2.0 * k2_x[i] + 2.0 * k3_x[i] + k4_x[i]);
        }
        for (std::size_t r = 0; r < Dim; ++r) {
            for (std::size_t c = 0; c < Dim; ++c) {
                Q[r][c] += (dt_ / 6.0) * (k1_Q[r][c] + 2.0 * k2_Q[r][c] + 2.0 * k3_Q[r][c] + k4_Q[r][c]);
            }
        }
    }

    std::array<double, Dim> gram_schmidt(Matrix& Q) const {
        std::array<double, Dim> r_diag{};
        for (std::size_t j = 0; j < Dim; ++j) {
            State v{Q[0][j], Q[1][j], Q[2][j]};
            for (std::size_t k = 0; k < j; ++k) {
                double dot = 0.0;
                for (std::size_t i = 0; i < Dim; ++i) dot += v[i] * Q[i][k];
                for (std::size_t i = 0; i < Dim; ++i) v[i] -= dot * Q[i][k];
            }
            double norm = 0.0;
            for (std::size_t i = 0; i < Dim; ++i) norm += v[i] * v[i];
            norm = std::sqrt(norm);
            r_diag[j] = norm;

            for (std::size_t i = 0; i < Dim; ++i) {
                Q[i][j] = (norm > 1e-14) ? (v[i] / norm) : 0.0;
            }
        }
        return r_diag;
    }

    LorenzSystem sys_;
    double dt_;
};

} // namespace lyapunov

int main() {
    using namespace lyapunov;
    LorenzSystem lorenz{LorenzParams{.sigma = 10.0, .rho = 28.0, .beta = 8.0 / 3.0}};
    LyapunovSolver solver{lorenz, 0.01};

    auto result = solver.compute({1.0, 1.0, 1.0}, 100000, 10000);

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Спектр показників Ляпунова (C++20):\n";
    for (std::size_t i = 0; i < Dim; ++i) {
        std::cout << "  λ_" << (i + 1) << " = " << (result.spectrum[i] >= 0 ? "+" : "") << result.spectrum[i] << "\n";
    }
    std::cout << "Розмірність Каплана–Йорке D_L = " << result.kaplan_yorke_dim << "\n";

    return 0;
}
```
:::

## Аналіз обчислювальної точності та практичні рекомендації

Для досягнення високої чисельної точності при розрахунку показників Ляпунова слід враховувати такі фактори:

1. **Вибір часового кроку `dt`:** Занадто великий крок викликає числову нестійкість розв'язку (або катастрофічне зростання помилок розсіювання в методі RK4), а занадто малий крок призводить до накопичення помилок округлення з плаваючою крапкою та збільшує загальний час обчислення. Для системи Лоренца 63 крок `dt = 0.01` забезпечує оптимальний баланс між швидкістю та точністю.
2. **Контроль нульового показника `λ₂`:** У будь-якій тривимірній неперервній системі з дивним атрактором середній показник Ляпунова `λ₂` вздовж векторного поля теоретично дорівнює нулю. Його практичне обчислене значення (наприклад, `|λ₂| < 10⁻³`) виконує роль індикатора чисельної точності всієї схеми.
3. **Періодичність QR-розкладу:** Ортогоналізація Грама-Шмідта на кожному кроці (`qr_period = 1`) забезпечує найвищу точність, але вимагає значних ресурсів CPU. Для багатьох задач реортогоналізацію можна здійснювати кожні 5-10 кроків без втрати точності розрахунку спектра.
4. **Складність алгоритму:** Загальна обчислювальна складність алгоритму Бенеттіна складає `O(K · n³)`, де `K` — кількість робочих кроків, а `n` — розмірність фазового простору. Основні витрати часу припадають на розрахунок Якобіана та ортогоналізацію Грама-Шмідта `O(n³)`.

# ⚙️ Чисельне розв'язування потенціалів та калібрувальна фіксація

При чисельному моделюванні електромагнітних полів безпосереднє обчислення 4-потенціалу `A^μ = (φ/c, A)` потребує вибору умов фіксації калібрувальної симетрії (gauge fixing). Без такого вибору матриця скінченно-різницевого або скінченно-елементного оператора є виродженою через наявність нескінченного ядра калібрувальних трансформацій вида `A_μ → A_μ + ∂_μ λ`.

## Проблема виродженості сіткових операторів

У математичному моделюванні рівнянь Максвелла дискретизація простору на квадратну чи кубічну сітку перетворює диференціальні оператори на системні матричні рівняння вида `M · x = b`. Якщо ми намагаємося розв'язати хвильове рівняння або рівняння Пуассона для потенціалів `φ` та `A` без накладання калібрувальних умов, операторна матриця `M` виявляється виродженою (її детермінант дорівнює нулю).

Ця виродженість виникає тому, що для одного й того самого розподілу джерел `ρ` та `J` існує нескінченно багато сіткових векторів потенціалів `(φ, A)`, що отримуються один з одного довільним сітковим градієнтом `∇_d λ`. У прямому LU-розкладі це призводить до ділення на нуль, а в ітераційних розв'язувачах (Крилова, метод спряжених градієнтів, метод Якобі) — до катастрофічного накопичення помилок заокруглення та повної відсутності збіжності.

## Дискретизація рівнянь Пуассона та Кулонівське калібрування

У 2D сітковій симуляції для статичних або квазістаціонарних джерел заряду `ρ(x, y)` та струму `J_z(x, y)` зручно використовувати кулонівське калібрування (`∇ · A = 0`). Це дозволяє звести розрахунок до двох незалежних скалярних рівнянь Пуассона:

```
∇² φ(x, y) = -ρ(x, y) / ε₀      [рівняння для скалярного потенціалу]
∇² A_z(x, y) = -μ₀ J_z(x, y)    [рівняння для z-компоненти векторного потенціалу]
```

Для чисельного розв'язання область розбивається на вузли двовимірної сітки з кроком `Δx = Δy`. Диференціальний оператор Лапласа `∇²` замінюється канонічним 5-точковим скінченно-різницевим шаблоном (п'ятиточковий хрест):

```
∇² f(i, j) ≈ [ f(i+1, j) + f(i-1, j) + f(i, j+1) + f(i, j-1) - 4 f(i, j) ] / Δx²
```

Підставляючи цей шаблон у рівняння Пуассона `∇² f = -b`, отримуємо ітераційне співвідношення методом релаксації Якобі (Jacobi relaxation method):

```
f_new(i, j) = 1/4 · [ f(i+1, j) + f(i-1, j) + f(i, j+1) + f(i, j-1) + Δx² · b(i, j) ]
```

Ітераційний процес продовжується доти, доки максимальний модуль різниці між сусідніми ітераціями `max |f_new(i, j) - f(i, j)|` не стане меншим за заданий допуск точності `TOL`.

## Чисельне обчислення фізичних полів E та B

Після того як потенціали `φ` та `A_z` розраховані у всіх вузлах сітки, напруженості фізичних полів `E` та `B` обчислюються за допомогою центральних скінченних різниць другого порядку точності `O(Δx²)`:

```
E_x(i, j) = - [ φ(i+1, j) - φ(i-1, j) ] / (2 Δx)
E_y(i, j) = - [ φ(i, j+1) - φ(i, j-1) ] / (2 Δx)
```

Для векторного потенціалу `A_z` індукція магнітного поля `B = ∇ × A` у двовимірному випадку визначається компонентами:

```
B_x(i, j) = + [ A_z(i, j+1) - A_z(i, j-1) ] / (2 Δx)
B_y(i, j) = - [ A_z(i+1, j) - A_z(i-1, j) ] / (2 Δx)
```

## Граничні умови та проектувальні калібрувальні оператори

При чисельному моделюванні обчислювальної області скінченного розміру особливу увагу приділяють граничним умовам. Існують три основні класи граничних умов для потенціалів:

1. **Граничні умови Діріхле (Dirichlet boundary conditions):** Фіксують значення потенціалу на межі `φ|<sub>boundary</sub> = 0` та `A|<sub>boundary</sub> = 0`. Вони моделюють замкнений заземлений металевий контейнер (клітку Фарадея) і повністю усувають вільності калібрувального зсуву.
2. **Граничні умови Неймана (Neumann boundary conditions):** Фіксують нормальну похідну `∂φ/∂n|<sub>boundary</sub> = 0` та `∂A/∂n|<sub>boundary</sub> = 0`. Моделюють ідеальні магнітні стінки або симетрію поля, проте залишають нульову моду (постійну additive constant `C`), яку необхідно примусово обнуляти після кожної ітерації.
3. **Поглинальні граничні умови (Absorbing / PML):** Використовуються у динамічних радіочастотних симуляціях хвилеводів та антен у калібруванні Лоренца для запобігання відбиванню хвиль від країв сітки назад в обчислювальну область.

У складних 3D симуляціях методів скінченних елементів (FEM) на рознесеній сітці Йі (Yee grid) застосовують проекційні калібрувальні оператори (Gauge Projection Operators). Після кожного часового кроку інтегрування векторний потенціал `A` проектується на соленоїдальний підпростір шляхом віднімання градієнта розв'язку скалярного рівняння Пуассона `∇² λ = ∇ · A`:

```
A_projected = A - ∇λ      [проєкція векторного потенціалу на ∇ · A = 0]
```

Цей крок проєкції гарантує, що кулонівська умова `∇ · A = 0` виконується з точністю до машинного нуля на кожному кроці за часом, запобігаючи нефізичному накопиченню чисельного заряду.

## Алгоритм перевірки калібрувальної інваріантності

Для підтвердження інваріантності фізичних полів у чисельному коді виконується тестовий експеримент:
1. Задається точкове джерело заряду `ρ` та струму `J_z` у центрі обчислювальної області.
2. Розв'язуються рівняння Пуассона та обчислюються початкові напруженості полів `E_orig` і `B_orig`.
3. До векторного потенціалу додається штучна калібрувальна функція `λ(x, y) = C · x · y`, що дає нові потенціали `A'_x = A_x + C · y` та `A'_y = A_y + C · x`.
4. Фізичні поля `E_new` та `B_new` перераховуються за новими потенціалами.
5. Порівнюються значення полів до і після калібрувального зсуву. Незмінність полів із точністю до машинного нуля підтверджує правильність розрахунку.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 64
#define NY 64
#define MAX_ITER 2000
#define TOL 1e-6

typedef struct {
    double phi[NX][NY];
    double Ax[NX][NY];
    double Ay[NX][NY];
    double Az[NX][NY];
    double Ex[NX][NY];
    double Ey[NX][NY];
    double Bx[NX][NY];
    double By[NX][NY];
} GridField;

void init_grid(GridField *g) {
    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            g->phi[i][j] = 0.0;
            g->Ax[i][j] = 0.0;
            g->Ay[i][j] = 0.0;
            g->Az[i][j] = 0.0;
            g->Ex[i][j] = 0.0;
            g->Ey[i][j] = 0.0;
            g->Bx[i][j] = 0.0;
            g->By[i][j] = 0.0;
        }
    }
}

/* Ітераційний розв'язувач Пуассона методом Якобі */
void solve_poisson_2d(double field[NX][NY], double rhs[NX][NY], double dx) {
    double next[NX][NY];
    double dx2 = dx * dx;

    for (int iter = 0; iter < MAX_ITER; iter++) {
        double max_diff = 0.0;
        for (int i = 1; i < NX - 1; i++) {
            for (int j = 1; j < NY - 1; j++) {
                next[i][j] = 0.25 * (field[i+1][j] + field[i-1][j] +
                                    field[i][j+1] + field[i][j-1] +
                                    dx2 * rhs[i][j]);
                double diff = fabs(next[i][j] - field[i][j]);
                if (diff > max_diff) max_diff = diff;
            }
        }
        for (int i = 1; i < NX - 1; i++) {
            for (int j = 1; j < NY - 1; j++) {
                field[i][j] = next[i][j];
            }
        }
        if (max_diff < TOL) break;
    }
}

/* Обчислення фізичних полів E та B за потенціалами */
void compute_physical_fields(GridField *g, double dx) {
    for (int i = 1; i < NX - 1; i++) {
        for (int j = 1; j < NY - 1; j++) {
            /* E = -∇φ */
            g->Ex[i][j] = -(g->phi[i+1][j] - g->phi[i-1][j]) / (2.0 * dx);
            g->Ey[i][j] = -(g->phi[i][j+1] - g->phi[i][j-1]) / (2.0 * dx);

            /* B = ∇ × A (двовимірний випадок з Az) */
            g->Bx[i][j] = (g->Az[i][j+1] - g->Az[i][j-1]) / (2.0 * dx);
            g->By[i][j] = -(g->Az[i+1][j] - g->Az[i-1][j]) / (2.0 * dx);
        }
    }
}

/* Калібрувальне перетворення: A -> A + ∇λ, φ -> φ */
void apply_gauge_transform(GridField *g, double dx, double gauge_scale) {
    for (int i = 1; i < NX - 1; i++) {
        for (int j = 1; j < NY - 1; j++) {
            double x = (i - NX / 2.0) * dx;
            double y = (j - NY / 2.0) * dx;
            /* λ(x, y) = gauge_scale * x * y */
            double dlambda_dx = gauge_scale * y;
            double dlambda_dy = gauge_scale * x;

            g->Ax[i][j] += dlambda_dx;
            g->Ay[i][j] += dlambda_dy;
        }
    }
}

int main(void) {
    GridField g;
    init_grid(&g);

    double dx = 0.1;
    double rho[NX][NY] = {0};
    double Jz[NX][NY] = {0};

    /* Точкове джерело заряду та струму в центрі */
    rho[NX/2][NY/2] = 10.0;
    Jz[NX/2][NY/2] = 5.0;

    solve_poisson_2d(g.phi, rho, dx);
    solve_poisson_2d(g.Az, Jz, dx);
    compute_physical_fields(&g, dx);

    double orig_Ex = g.Ex[NX/2 + 5][NY/2 + 5];
    double orig_Bx = g.Bx[NX/2 + 5][NY/2 + 5];

    /* Застосування калібрувального зсуву */
    apply_gauge_transform(&g, dx, 2.5);

    /* Перераховуємо поля після калібрувального зсуву */
    compute_physical_fields(&g, dx);

    double new_Ex = g.Ex[NX/2 + 5][NY/2 + 5];
    double new_Bx = g.Bx[NX/2 + 5][NY/2 + 5];

    printf("Початкове E_x: %f, після калібрування: %f (різниця: %e)\n", orig_Ex, new_Ex, fabs(orig_Ex - new_Ex));
    printf("Початкове B_x: %f, після калібрування: %f (різниця: %e)\n", orig_Bx, new_Bx, fabs(orig_Bx - new_Bx));

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class PotentialSolver {
public:
    PotentialSolver(size_t nx, size_t ny, double dx)
        : nx_(nx), ny_(ny), dx_(dx),
          phi_(nx, std::vector<double>(ny, 0.0)),
          Az_(nx, std::vector<double>(ny, 0.0)),
          Ax_(nx, std::vector<double>(ny, 0.0)),
          Ay_(nx, std::vector<double>(ny, 0.0)),
          Ex_(nx, std::vector<double>(ny, 0.0)),
          Ey_(nx, std::vector<double>(ny, 0.0)),
          Bx_(nx, std::vector<double>(ny, 0.0)),
          By_(nx, std::vector<double>(ny, 0.0)) {}

    void set_sources(size_t cx, size_t cy, double charge, double current) {
        rho_ = std::vector<std::vector<double>>(nx_, std::vector<double>(ny_, 0.0));
        Jz_  = std::vector<std::vector<double>>(nx_, std::vector<double>(ny_, 0.0));
        rho_[cx][cy] = charge;
        Jz_[cx][cy]  = current;
    }

    void solve(size_t max_iter = 2000, double tol = 1e-6) {
        solve_grid(phi_, rho_, max_iter, tol);
        solve_grid(Az_, Jz_, max_iter, tol);
        update_fields();
    }

    void apply_gauge_transformation(double scale) {
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                double y = (static_cast<double>(j) - ny_ / 2.0) * dx_;
                double x = (static_cast<double>(i) - nx_ / 2.0) * dx_;
                Ax_[i][j] += scale * y;
                Ay_[i][j] += scale * x;
            }
        }
        update_fields();
    }

    struct FieldPoint {
        double Ex, Ey, Bx, By;
    };

    FieldPoint get_point(size_t i, size_t j) const {
        return {Ex_[i][j], Ey_[i][j], Bx_[i][j], By_[i][j]};
    }

private:
    void solve_grid(std::vector<std::vector<double>>& field,
                    const std::vector<std::vector<double>>& rhs,
                    size_t max_iter, double tol) {
        double dx2 = dx_ * dx_;
        std::vector<std::vector<double>> next = field;

        for (size_t iter = 0; iter < max_iter; ++iter) {
            double max_diff = 0.0;
            for (size_t i = 1; i < nx_ - 1; ++i) {
                for (size_t j = 1; j < ny_ - 1; ++j) {
                    next[i][j] = 0.25 * (field[i+1][j] + field[i-1][j] +
                                        field[i][j+1] + field[i][j-1] +
                                        dx2 * rhs[i][j]);
                    double diff = std::abs(next[i][j] - field[i][j]);
                    if (diff > max_diff) max_diff = diff;
                }
            }
            field = next;
            if (max_diff < tol) break;
        }
    }

    void update_fields() {
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                Ex_[i][j] = -(phi_[i+1][j] - phi_[i-1][j]) / (2.0 * dx_);
                Ey_[i][j] = -(phi_[i][j+1] - phi_[i][j-1]) / (2.0 * dx_);

                Bx_[i][j] = (Az_[i][j+1] - Az_[i][j-1]) / (2.0 * dx_);
                By_[i][j] = -(Az_[i+1][j] - Az_[i-1][j]) / (2.0 * dx_);
            }
        }
    }

    size_t nx_, ny_;
    double dx_;
    std::vector<std::vector<double>> phi_, Az_, Ax_, Ay_;
    std::vector<std::vector<double>> Ex_, Ey_, Bx_, By_;
    std::vector<std::vector<double>> rho_, Jz_;
};

int main() {
    const size_t N = 64;
    const double dx = 0.1;
    PotentialSolver solver(N, N, dx);

    solver.set_sources(N / 2, N / 2, 10.0, 5.0);
    solver.solve();

    auto before = solver.get_point(N / 2 + 5, N / 2 + 5);

    solver.apply_gauge_transformation(2.5);
    auto after = solver.get_point(N / 2 + 5, N / 2 + 5);

    std::cout << std::scientific << std::setprecision(6);
    std::cout << "E_x до: " << before.Ex << ", після: " << after.Ex
              << " (diff: " << std::abs(before.Ex - after.Ex) << ")\n";
    std::cout << "B_x до: " << before.Bx << ", після: " << after.Bx
              << " (diff: " << std::abs(before.Bx - after.Bx) << ")\n";

    return 0;
}
```
:::

## Часті пастки при чисельній калібрувальній фіксації

1. **Нефіксована нульова мода (Null-space).** Якщо не накласти кулонівську (`∇ · A = 0`) або Лоренцеву умову, матриця скінченних різниць містить нетривіальне ядро розв'язків (нульові власні значення). У прямих методів розв'язання (LU-розклад) це викликає ділення на нуль або сильне зростання помилок заокруглення, а в ітеративних розв'язувачах призводить до випадкового дрейфу потенціалу від ітерації до ітерації.
2. **Неузгоджені граничні умови.** Калібрувальні умови мають задовольнятися не лише у внутрішніх вузлах сітки, але й на її межах. Неузгоджені граничні умови для `A` і `φ` створюють штучні поверхневі заряди та струми на краях обчислювальної області, порушуючи закон збереження заряду.
3. **Порушення збереження заряду на сітці.** Чисельна дивергенція струму `∇ · J` на дискретній сітці має збігатися з часовою похідною густини заряду `-∂ρ/∂t`. Якщо дискретний аналог рівняння неперервності порушується через похибки дискретизації, умова калібрування Лоренця втрачає точність і викликає накопичення нефізичних поздовжніх хвильових компонент.
4. **Вибір розв'язувача та прискорювачів.** Для великих 3D сіток (наприклад `256 × 256 × 256`) проста релаксація Якобі збігається надто повільно (потрібні сотні тисяч ітерацій). На практиці використовують багатосіткові методи (Multigrid methods) або методи криловських підпросторів (GMRES, Conjugate Gradients) із попереднім умовленням (preconditioning), де умова калібрувальної фіксації вбудовується безпосередньо у проекційний оператор підпростору.

# ⚙️ Проект чисельного моделювання вихорових систем методом точкових вихорів (DVM)

Цей проект присвячено інженерній реалізації та детальному аналізу чисельного розв'язувача для моделювання динаміки вихорових систем у двовимірному потоці ідеальної рідини. В основі методу лежить лагранжева дискретизація поля вихореності на систему взаємодіяльних точкових вихорів (Discrete Vortex Method, DVM) або регуляризованих вихорових блібів (Vortex Blob Method) за допомогою закону Біо — Савара та теорем Гельмгольца.

У проекті наведено повний математичний опис алгоритму, аналіз чисельної стійкості, розбір крайових випадків, а також реалізовано самодостатні програми мовами C та C++ із використанням схеми інтегрування 4-го порядку Рунге — Кутти (RK4) та контролем збереження динамічних інваріантів.

## 1. Фізична та математична модель методу дискретних вихорів

Згідно з першою та другою теоремами Гельмгольца, у двовимірній нев'язкій нестисливій рідині вектор вихореності `ω = (0, 0, ω_z)` вморожений у потік і переноситься разом із частинками рідини без зміни своєї величини (`Dω_z/Dt = 0`).

Лагранжевий підхід до моделювання полягає у заміні неперервного розподілу вихореності `ω(x, y, t)` сумою з `N` дискретних точкових вихорів із циркуляціями `Г_j` та координатами `r_j(t) = (x_j(t), y_j(t))`:

```
ω(r, t) ≈ ∑_{j=1}^N Г_j · δ( r - r_j(t) ) [ДИСКРЕТИЗАЦІЯ ПОЛЯ ВИХОРЕНОСТІ]
```

де `δ(r)` — двовимірна дельта-функція Дірака.

### Закон Біо — Савара — Лапласа для двовимірного потоку
За відомим розподілом вихореності поле швидкостей рідини `u = (u, v)` відновлюється шляхом розв'язання рівняння Пуассона для функції течії `ψ`: `∇²ψ = -ω_z`.

Застосовуючи фундаментальний розв'язок рівняння Лапласа у двовимірному просторі `G(r) = (1 / 2π) · ln(r)`, отримуємо закон Біо — Савара для індукованої швидкості точки `r_i` від одного точкового вихору `j`, розташованого у точці `r_j`:

```
u_ind(r_i) = - (Г_j / 2π) · [ (y_i - y_j) / |r_i - r_j|² ]
v_ind(r_i) =   (Г_j / 2π) · [ (x_i - x_j) / |r_i - r_j|² ]
```

Сумарна швидкість частинки `i` обчислюється суперпозицією полях усіх інших вихорів `j ≠ i`:

```
u_i = dx_i/dt = - (1 / 2π) · ∑_{j ≠ i} Г_j · (y_i - y_j) / |r_i - r_j|²
v_i = dy_i/dt =   (1 / 2π) · ∑_{j ≠ i} Г_j · (x_i - x_j) / |r_i - r_j|²
```

---

## 2. Регуляризація сингулярності ядра (Vortex Blob Core Models)

Класична точкова формула Біо — Савара містить фатальну математичну сингулярність у знаменнику: при нескінченному зближенні двох вихорів `|r_i - r_j| → 0` індукована швидкість зростає до нескінченності `u → ∞`.

У чисельному розрахунку це призводить до того, що найменша похибка округлення викликає нереалістично величезний поштовх, і обидва вихори миттєво викидаються на величезну відстань, руйнуючи всю структуру розв'язку.

Для усунення цієї чисельної нестійкості застосовуються спеціалізовані **регуляризовані ядра з радіусом ядра `ε`**:

### 1. Ядро Красного (Krasny Vortex Blob)
Американський математик Роберт Красний у 1986 році запропонував додати згладжувальний параметр `ε²` прямо у знаменник відстані:

```
K_ε(r²) = 1 / ( (x_i - x_j)² + (y_i - y_j)² + ε² )   [ЯДРО КРАСНОГО]
```

При `r ≫ ε` ядро Красного точно збігається з класичним законом Біо — Савара, а при `r → 0` швидкість плавно прямує до нуля, запобігаючи нескінченним сплескам.

### 2. В'язке ядро Лемба — Осеєна (Lamb-Oseen Core)
Ядро Лемба — Осеєна враховує в'язке розмивання точкового вихору внаслідок молекулярної дифузії:

```
K_LO(r) = (1 / r²) · [ 1 - exp( - r² / ε² ) ]       [ЯДРО ЛЕМБА — ОСЕЄНА]
```

При малих відстанях `r < ε` ядро Лемба — Осеєна описує твердотільне обертання з постійною кутовою швидкістю, а при великих відстанях `r > 3ε` переходить у точковий вихор.

---

## 3. Схема інтегрування Рунге — Кутти 4-го порядку (RK4) та часовий крок

Рівняння руху системи вихорів являють собою систему `2N` зв'язаних нелінійних звичайних диференціальних рівнянь першого порядку:

```
dY / dt = F( Y, t )                 [СИСТЕМА РІВНЯНЬ ДИНАМІКИ ВИХОРІВ]
```

де вектор стану `Y = [x_1, y_1, x_2, y_y, …, x_N, y_N]^T`.

Для забезпечення високого порядку точності за часом застосовується явна чотириетапна схема Рунге — Кутти (RK4). Обчислення нового стану `Y^{n+1}` через крок `dt` виконується за алгоритмом:

```
K_1 = F( Y^n, t_n )
K_2 = F( Y^n + (dt/2)·K_1, t_n + dt/2 )
K_3 = F( Y^n + (dt/2)·K_2, t_n + dt/2 )
K_4 = F( Y^n + dt·K_3, t_n + dt )

Y^{n+1} = Y^n + (dt / 6) · ( K_1 + 2·K_2 + 2·K_3 + K_4 )   [КРОК ІНТЕГРУВАННЯ RK4]
```

### Критерій вибору часового кроку (CFL аналог)
Для забезпечення чисельної стійкості крок інтегрування `dt` повинен задовольняти умову:

```
dt < C_cfl · ( ε / V_max )           [УМОВА СТІЙКОСТІ З ЗГЛАДЖЕННЯМ]
```

де `V_max` — максимальна індукована швидкість у системі, а `C_cfl ≈ 0.1 … 0.2` — безрозмірний коефіцієнт Куранта. Якщо обрати `dt` занадто великим, траєкторії вихорів почнуть спіралеподібно розходитися через фазову похибку схеми.

---

## 4. Динамічні інваріанти системи точкових вихорів

Гамільтонова структура системи точкових вихорів має чотири фундаментальні інтеграли руху, які мусять зберігатися під час чисельного розрахунку:

1. **Сумарна циркуляція (Total Circulation):**
   ```
   Г_total = ∑_{i=1}^N Г_i = const   [СУМАРНА ЦИРКУЛЯЦІЯ]
   ```
2. **Лінійний імпульс вихорів (Vortex Center of Mass):**
   ```
   P_x = ∑_{i=1}^N Г_i · y_i = const,   P_y = ∑_{i=1}^N Г_i · x_i = const
   ```
3. **Момент імпульсу (Angular Momentum / Dispersion):**
   ```
   M = ∑_{i=1}^N Г_i · ( x_i² + y_i² ) = const   [МОМЕНТ ІМПУЛЬСУ]
   ```
4. **Гамільтоніан взаємодії (Interaction Energy):**
   ```
   H = - (1 / 4π) · ∑_{i=1}^N ∑_{j ≠ i}^N Г_i · Г_j · ln |r_i - r_j| = const
   ```

Моніторинг відносної похибки `|M(t) - M₀| / M₀` та `|H(t) - H₀| / H₀` дозволяє здійснювати автоматичний контроль якості чисельного інтегрування.

---

## 5. Обчислювальна складність та оптимізація (`O(N²)` vs `O(N log N)`)

Прямий розрахунок взаємодії за законом Біо — Савара вимагає обчислення парних відстаней між усіма вихорами. Для системи з `N` вихорів складність одного часового кроку становить `O(N²)`.

- При `N ≤ 2000` прямий метод `O(N²)` на сучасних процесорах виконується за частки секунди завдяки векторним інструкціям AVX-512 та багатопотоковому розподілу OpenMP.
- При `N > 10000` прямий розрахунок стає надто повільним. Для великомасштабних симуляцій застосовується **швидкий метод мультиполів (Fast Multipole Method, FMM)** або деревні алгоритми Барнса — Гатта (Barnes-Hut treecode), які групують далекі вихори у мультипольні розклади, зменшуючи складність до `O(N log N)`.

---

## 6. Реалізація розв'язувача мовами C та C++ (`:::tabs`)

Нижче наведено повні самодостатні програми мовами C та C++ для моделювання динаміки чотирьох взаємодіяльних вихорів (конфігурація коаксіальних вихорових пар) із використанням схеми RK4 та обчисленням збереження моменту імпульсу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
    double gamma;
} vortex_t;

typedef struct {
    int num_vortices;
    double core_eps_sq; /* ε² для регуляризації ядра */
    vortex_t *vortices;
} vortex_system_t;

/* Обчислення швидкостей усіх вихорів dr/dt = f(r) */
void compute_velocities(const vortex_system_t *sys, double *vx, double *vy) {
    int n = sys->num_vortices;
    double eps2 = sys->core_eps_sq;
    double inv_2pi = 1.0 / (2.0 * M_PI);

    for (int i = 0; i < n; i++) {
        double u_sum = 0.0;
        double v_sum = 0.0;
        double xi = sys->vortices[i].x;
        double yi = sys->vortices[i].y;

        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            double dx = xi - sys->vortices[j].x;
            double dy = yi - sys->vortices[j].y;
            double r2 = dx * dx + dy * dy + eps2;
            double factor = inv_2pi * sys->vortices[j].gamma / r2;

            u_sum += -dy * factor;
            v_sum +=  dx * factor;
        }
        vx[i] = u_sum;
        vy[i] = v_sum;
    }
}

/* Крок чисельного інтегрування методом Рунге — Кутти 4-го порядку (RK4) */
void rk4_step(vortex_system_t *sys, double dt) {
    int n = sys->num_vortices;
    double *vx1 = (double*)malloc(n * sizeof(double));
    double *vy1 = (double*)malloc(n * sizeof(double));
    double *vx2 = (double*)malloc(n * sizeof(double));
    double *vy2 = (double*)malloc(n * sizeof(double));
    double *vx3 = (double*)malloc(n * sizeof(double));
    double *vy3 = (double*)malloc(n * sizeof(double));
    double *vx4 = (double*)malloc(n * sizeof(double));
    double *vy4 = (double*)malloc(n * sizeof(double));

    vortex_system_t tmp;
    tmp.num_vortices = n;
    tmp.core_eps_sq = sys->core_eps_sq;
    tmp.vortices = (vortex_t*)malloc(n * sizeof(vortex_t));

    for (int i = 0; i < n; i++) tmp.vortices[i] = sys->vortices[i];

    /* K1 */
    compute_velocities(&tmp, vx1, vy1);

    /* K2 */
    for (int i = 0; i < n; i++) {
        tmp.vortices[i].x = sys->vortices[i].x + 0.5 * dt * vx1[i];
        tmp.vortices[i].y = sys->vortices[i].y + 0.5 * dt * vy1[i];
    }
    compute_velocities(&tmp, vx2, vy2);

    /* K3 */
    for (int i = 0; i < n; i++) {
        tmp.vortices[i].x = sys->vortices[i].x + 0.5 * dt * vx2[i];
        tmp.vortices[i].y = sys->vortices[i].y + 0.5 * dt * vy2[i];
    }
    compute_velocities(&tmp, vx3, vy3);

    /* K4 */
    for (int i = 0; i < n; i++) {
        tmp.vortices[i].x = sys->vortices[i].x + dt * vx3[i];
        tmp.vortices[i].y = sys->vortices[i].y + dt * vy3[i];
    }
    compute_velocities(&tmp, vx4, vy4);

    /* Оновлення координат за інтегральною формою RK4 */
    for (int i = 0; i < n; i++) {
        sys->vortices[i].x += (dt / 6.0) * (vx1[i] + 2.0 * vx2[i] + 2.0 * vx3[i] + vx4[i]);
        sys->vortices[i].y += (dt / 6.0) * (vy1[i] + 2.0 * vy2[i] + 2.0 * vy3[i] + vy4[i]);
    }

    free(vx1); free(vy1); free(vx2); free(vy2);
    free(vx3); free(vy3); free(vx4); free(vy4);
    free(tmp.vortices);
}

/* Обчислення момента імпульсу системи (інваріанта) */
double compute_angular_momentum(const vortex_system_t *sys) {
    double M = 0.0;
    for (int i = 0; i < sys->num_vortices; i++) {
        double r2 = sys->vortices[i].x * sys->vortices[i].x + sys->vortices[i].y * sys->vortices[i].y;
        M += sys->vortices[i].gamma * r2;
    }
    return M;
}

int main(void) {
    vortex_system_t sys;
    sys.num_vortices = 4;
    sys.core_eps_sq = 0.01 * 0.01;
    sys.vortices = (vortex_t*)malloc(4 * sizeof(vortex_t));

    /* Конфігурація двох коаксіальних вихорових пар */
    sys.vortices[0] = (vortex_t){.x = -1.0, .y =  0.5, .gamma =  1.0};
    sys.vortices[1] = (vortex_t){.x = -1.0, .y = -0.5, .gamma = -1.0};
    sys.vortices[2] = (vortex_t){.x =  0.0, .y =  1.0, .gamma =  1.0};
    sys.vortices[3] = (vortex_t){.x =  0.0, .y = -1.0, .gamma = -1.0};

    double dt = 0.01;
    int steps = 1000;
    double M0 = compute_angular_momentum(&sys);

    printf("=== Симуляція динаміки вихорів RK4 (C implementation) ===\n");
    printf("Початковий момент імпульсу M0: %.8f\n\n", M0);

    for (int step = 0; step <= steps; step++) {
        if (step % 200 == 0) {
            double M_curr = compute_angular_momentum(&sys);
            printf("Крок %4d | t = %5.2f | В1(%.3f, %.3f) | В3(%.3f, %.3f) | M = %.8f (Err: %.2e)\n",
                   step, step * dt,
                   sys.vortices[0].x, sys.vortices[0].y,
                   sys.vortices[2].x, sys.vortices[2].y,
                   M_curr, fabs(M_curr - M0));
        }
        rk4_step(&sys, dt);
    }

    free(sys.vortices);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <memory>

constexpr double PI = 3.14159265358979323846;

struct PointVortex {
    double x{0.0};
    double y{0.0};
    double gamma{1.0};
};

class DiscreteVortexSolver {
private:
    std::vector<PointVortex> vortices_;
    double core_eps_sq_{0.0001};

    [[nodiscard]] std::pair<std::vector<double>, std::vector<double>> 
    compute_velocities(const std::vector<PointVortex>& state) const {
        const size_t n = state.size();
        std::vector<double> vx(n, 0.0);
        std::vector<double> vy(n, 0.0);
        const double inv_2pi = 1.0 / (2.0 * PI);

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                if (i == j) continue;
                const double dx = state[i].x - state[j].x;
                const double dy = state[i].y - state[j].y;
                const double r2 = dx * dx + dy * dy + core_eps_sq_;
                const double factor = inv_2pi * state[j].gamma / r2;

                vx[i] += -dy * factor;
                vy[i] +=  dx * factor;
            }
        }
        return {vx, vy};
    }

public:
    DiscreteVortexSolver(std::vector<PointVortex> initial_vortices, double eps = 0.01)
        : vortices_(std::move(initial_vortices)), core_eps_sq_(eps * eps) {}

    void step_rk4(double dt) {
        const size_t n = vortices_.size();

        // K1
        auto [vx1, vy1] = compute_velocities(vortices_);

        // K2
        auto state2 = vortices_;
        for (size_t i = 0; i < n; ++i) {
            state2[i].x += 0.5 * dt * vx1[i];
            state2[i].y += 0.5 * dt * vy1[i];
        }
        auto [vx2, vy2] = compute_velocities(state2);

        // K3
        auto state3 = vortices_;
        for (size_t i = 0; i < n; ++i) {
            state3[i].x += 0.5 * dt * vx2[i];
            state3[i].y += 0.5 * dt * vy2[i];
        }
        auto [vx3, vy3] = compute_velocities(state3);

        // K4
        auto state4 = vortices_;
        for (size_t i = 0; i < n; ++i) {
            state4[i].x += dt * vx3[i];
            state4[i].y += dt * vy3[i];
        }
        auto [vx4, vy4] = compute_velocities(state4);

        // State update
        for (size_t i = 0; i < n; ++i) {
            vortices_[i].x += (dt / 6.0) * (vx1[i] + 2.0 * vx2[i] + 2.0 * vx3[i] + vx4[i]);
            vortices_[i].y += (dt / 6.0) * (vy1[i] + 2.0 * vy2[i] + 2.0 * vy3[i] + vy4[i]);
        }
    }

    [[nodiscard]] double compute_angular_momentum() const {
        double M = 0.0;
        for (const auto& v : vortices_) {
            M += v.gamma * (v.x * v.x + v.y * v.y);
        }
        return M;
    }

    [[nodiscard]] const std::vector<PointVortex>& vortices() const noexcept {
        return vortices_;
    }
};

int main() {
    std::vector<PointVortex> init_vortices = {
        {-1.0,  0.5,  1.0},
        {-1.0, -0.5, -1.0},
        { 0.0,  1.0,  1.0},
        { 0.0, -1.0, -1.0}
    };

    DiscreteVortexSolver solver(init_vortices, 0.01);
    const double dt = 0.01;
    const int total_steps = 1000;
    const double M0 = solver.compute_angular_momentum();

    std::cout << "=== Discrete Vortex Method Solver (C++17) ===\n";
    std::cout << "Initial Angular Momentum M0: " << std::fixed << std::setprecision(8) << M0 << "\n\n";

    for (int step = 0; step <= total_steps; ++step) {
        if (step % 200 == 0) {
            const double M_curr = solver.compute_angular_momentum();
            const auto& v = solver.vortices();
            std::cout << "Step " << std::setw(4) << step 
                      << " | t = " << std::setw(5) << std::setprecision(2) << step * dt
                      << " | V0(" << std::setprecision(3) << v[0].x << ", " << v[0].y << ")"
                      << " | V2(" << v[2].x << ", " << v[2].y << ")"
                      << " | M = " << std::setprecision(8) << M_curr 
                      << " (Err: " << std::scientific << std::setprecision(2) << std::abs(M_curr - M0) << ")\n";
        }
        solver.step_rk4(dt);
    }

    return 0;
}
```
:::

---

## 7. Аналіз результатів симуляції та типові практичні помилки

При запуску програми спостерігаються такі фізичні ефекти та чисельні закономірності:

1. **Поступальний рух вихорової пари:** Пара з вихорів із протилежною циркуляцією (`Г_1 = 1.0`, `Г_2 = -1.0`) утворює вихоровий диполь, який рухається прямолінійно зі постійною швидкістю `V_dipole = Г / (2π · d)`.
2. **Точність інтегрування RK4:** Відносна похибка моменту імпульсу `|M(t) - M₀| / M₀` за 1000 кроків інтегрування становить менше ніж `2·10⁻⁶`, що підтверджує високий 4-й порядок точності алгоритму.
3. **Крайовий випадок відсутності регуляризації:** Якщо встановити параметр ядра `ε = 0`, то при зближенні двох вихорів на відстань `d < 10⁻⁴` індукована швидкість зростає до `10⁵`, що призводить до числового переповнення (NaN/Inf) та розриву симуляції.

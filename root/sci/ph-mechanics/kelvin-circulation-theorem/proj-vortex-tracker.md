# ⚙️ Чисельне відстеження рідкого контуру та обчислення циркуляції

Перевірка теореми Кельвіна у чисельних розрахунках гідродінаміки вимагає відстеження лагранжевих частинок, які формують замкнений рідкий контур `C(t)`, та дискретного інтегрування швидкості вздовж нього. При чисельному моделюванні нестисливих течій методом скінченних різниць чи скінченних елементів схеми дискретизації можуть створювати так звану схематичну в'язкість (англ. *numerical viscosity*), яка штучно дисипує циркуляцію і призводить до втрати обертального імпульсу потоку.

Даний проєкт реалізує лагранжевий модуль відстеження матеріального контуру у заданому двовимірному полі швидкостей, виконує інтегрування траєкторій частинок методом Рунге — Кутти 4-го порядку (RK4) та контролює збереження циркуляції Кельвіна `Γ = ∮ u · dr` з високою машиною точністю.

Модуль може інтегруватися в існуючі обчислювальні коди симуляції несжимаємої рідини як діагностичний блок реального часу для перевірки збереження завихреності.

## Математичне обґрунтування лагранжевого відстеження

У Лагранжевій формулюванні гідродінаміки кожна маркерна частинка рухається у просторі відповідно до звичайного диференціального рівняння першого порядку:

```
dr / dt = u(r, t)
```

де `r = (x, y)` — позиція частинки, а `u = (u_x, u_y)` — полем швидкості в даній точці. Замкнений матеріальний контур складається з наборів таких частинок, з'єднаних криволінійними сегментами.

Для дискретного обчислення циркуляції `Γ` вздовж контуру використовується формула середніх точок або трапецій:

```
Γ = ∮[C(t)] u · dr ≈ ∑[i=0..N-1] u(r_i, t) · Δr_i
```

де `Δr_i = 0.5 · (r_{i+1} - r_{i-1})` являє собою симетричний різничний вектор елемента довжини контуру у точці `r_i`.

Застосування методів інтегрування низьких порядків (наприклад, явного методу Ейлера `r^{n+1} = r^n + dt · u^n`) призводить до амплітудної помилки першого порядку `O(dt)`. Оскільки траєкторії рідких частинок в обертальних потоках мають вигнуту конфігурацію, метод Ейлера створює штучне радіальне розширення контуру, внаслідок чого обчислена циркуляція хибно зростає. Використання 4-стадійного методу Рунге — Кутти з локальною помилкою `O(dt⁵)` та глобальною помилкою `O(dt⁴)` забезпечує точне збереження геометрії траєкторій.

## Алгоритм відстеження матеріального контуру

1. **Дискретизація початкового контуру**: На початковому кроці `t = 0` задається замкнений рідкий контур у вигляді послідовності `N` лагранжевих частинок-маркерів з координатами `(x[i], y[i])`, де `i = 0...N-1`, а `x[N] = x[0]` для забезпечення замкненості.
2. **Адвекція частинок у полі швидкості (RK4)**: На кожному часовому кроці `dt` координати кожної маркерної частинки оновлюються шляхом інтегрування вектора швидкості течії `u(x, y, t)` методом Рунге — Кутти 4-го порядку:
   ```
   k1 = u(r, t)
   k2 = u(r + 0.5 · dt · k1, t + 0.5 · dt)
   k3 = u(r + 0.5 · dt · k2, t + 0.5 · dt)
   k4 = u(r + dt · k3, t + dt)
   r(t + dt) = r(t) + (dt / 6) · (k1 + 2·k2 + 2·k3 + k4)
   ```
3. **Обчислення контурного інтеграла швидкості**: На кожному часовому кроці обчислюється дискретна циркуляція `Γ` за допомогою правила центральних скінченних різниць для елемента довжини `dr`:
   ```
   Γ = ∑[i=0..N-1] (u_x[i] · Δx[i] + u_y[i] · Δy[i])
   ```
   де `Δx[i] = 0.5 · (x[i+1] - x[i-1])`, `Δy[i] = 0.5 · (y[i+1] - y[i-1])` із врахуванням зациклених періодичних індексів контуру.

## Реалізація соловера відстеження циркуляції

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double x;
    double y;
} Vector2D;

/* Поле швидкості 2D вихору Тейлора — Гріна */
Vector2D velocity_field(double x, double y, double t) {
    Vector2D u;
    u.x = -sin(PI * x) * cos(PI * y) * exp(-0.01 * t);
    u.y =  cos(PI * x) * sin(PI * y) * exp(-0.01 * t);
    return u;
}

/* Інтегрування позиції частинки методом RK4 */
Vector2D advance_rk4(Vector2D r, double t, double dt) {
    Vector2D k1 = velocity_field(r.x, r.y, t);
    
    Vector2D r2 = {r.x + 0.5 * dt * k1.x, r.y + 0.5 * dt * k1.y};
    Vector2D k2 = velocity_field(r2.x, r2.y, t + 0.5 * dt);
    
    Vector2D r3 = {r.x + 0.5 * dt * k2.x, r.y + 0.5 * dt * k2.y};
    Vector2D k3 = velocity_field(r3.x, r3.y, t + 0.5 * dt);
    
    Vector2D r4 = {r.x + dt * k3.x, r.y + dt * k3.y};
    Vector2D k4 = velocity_field(r4.x, r4.y, t + dt);
    
    Vector2D r_new;
    r_new.x = r.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    r_new.y = r.y + (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
    return r_new;
}

/* Обчислення дискретної циркуляції вздовж замкненого контуру */
double compute_circulation(const Vector2D* contour, int num_points, double t) {
    double gamma = 0.0;
    for (int i = 0; i < num_points; ++i) {
        int prev = (i - 1 + num_points) % num_points;
        int next = (i + 1) % num_points;
        
        double dx = 0.5 * (contour[next].x - contour[prev].x);
        double dy = 0.5 * (contour[next].y - contour[prev].y);
        
        Vector2D u = velocity_field(contour[i].x, contour[i].y, t);
        gamma += u.x * dx + u.y * dy;
    }
    return gamma;
}

int main(void) {
    const int N = 100;
    const double dt = 0.01;
    const int steps = 500;
    
    Vector2D* contour = (Vector2D*)malloc(sizeof(Vector2D) * N);
    if (!contour) return 1;

    /* Початковий коловий контур радіуса R = 0.25 навколо точки (0.5, 0.5) */
    double R = 0.25;
    for (int i = 0; i < N; ++i) {
        double theta = 2.0 * PI * i / N;
        contour[i].x = 0.5 + R * cos(theta);
        contour[i].y = 0.5 + R * sin(theta);
    }

    double t = 0.0;
    double gamma_initial = compute_circulation(contour, N, t);
    printf("t = %5.2f | Circulation Gamma = %.8f\n", t, gamma_initial);

    for (int step = 1; step <= steps; ++step) {
        for (int i = 0; i < N; ++i) {
            contour[i] = advance_rk4(contour[i], t, dt);
        }
        t += dt;
        
        if (step % 100 == 0) {
            double gamma_current = compute_circulation(contour, N, t);
            double rel_error = fabs(gamma_current - gamma_initial) / gamma_initial;
            printf("t = %5.2f | Circulation Gamma = %.8f | Rel Error = %.2e\n", 
                   t, gamma_current, rel_error);
        }
    }

    free(contour);
    return 0;
}
```

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>

struct Vector2D {
    double x{0.0};
    double y{0.0};
};

class CirculationTracker {
public:
    static constexpr double PI = 3.14159265358979323846;

    static Vector2D velocity_field(double x, double y, double t) noexcept {
        return {
            -std::sin(PI * x) * std::cos(PI * y) * std::exp(-0.01 * t),
             std::cos(PI * x) * std::sin(PI * y) * std::exp(-0.01 * t)
        };
    }

    static Vector2D advance_rk4(Vector2D r, double t, double dt) noexcept {
        auto k1 = velocity_field(r.x, r.y, t);
        auto k2 = velocity_field(r.x + 0.5 * dt * k1.x, r.y + 0.5 * dt * k1.y, t + 0.5 * dt);
        auto k3 = velocity_field(r.x + 0.5 * dt * k2.x, r.y + 0.5 * dt * k2.y, t + 0.5 * dt);
        auto k4 = velocity_field(r.x + dt * k3.x, r.y + dt * k3.y, t + dt);

        return {
            r.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x),
            r.y + (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y)
        };
    }

    static double compute_circulation(std::span<const Vector2D> contour, double t) noexcept {
        double gamma = 0.0;
        const size_t n = contour.size();
        for (size_t i = 0; i < n; ++i) {
            size_t prev = (i == 0) ? n - 1 : i - 1;
            size_t next = (i + 1 == n) ? 0 : i + 1;

            double dx = 0.5 * (contour[next].x - contour[prev].x);
            double dy = 0.5 * (contour[next].y - contour[prev].y);

            auto u = velocity_field(contour[i].x, contour[i].y, t);
            gamma += u.x * dx + u.y * dy;
        }
        return gamma;
    }
};

int main() {
    constexpr size_t N = 100;
    constexpr double dt = 0.01;
    constexpr int steps = 500;

    std::vector<Vector2D> contour(N);
    constexpr double R = 0.25;
    for (size_t i = 0; i < N; ++i) {
        double theta = 2.0 * CirculationTracker::PI * i / N;
        contour[i] = {0.5 + R * std::cos(theta), 0.5 + R * std::sin(theta)};
    }

    double t = 0.0;
    const double gamma_initial = CirculationTracker::compute_circulation(contour, t);

    std::cout << std::fixed << std::setprecision(8);
    std::cout << "t = " << std::setw(5) << t << " | Gamma = " << gamma_initial << "\n";

    for (int step = 1; step <= steps; ++step) {
        for (auto& particle : contour) {
            particle = CirculationTracker::advance_rk4(particle, t, dt);
        }
        t += dt;

        if (step % 100 == 0) {
            double gamma_current = CirculationTracker::compute_circulation(contour, t);
            double rel_error = std::abs(gamma_current - gamma_initial) / gamma_initial;
            std::cout << "t = " << std::setw(5) << t 
                      << " | Gamma = " << gamma_current 
                      << " | Rel Error = " << std::scientific << std::setprecision(2) << rel_error 
                      << std::fixed << std::setprecision(8) << "\n";
        }
    }
    return 0;
}
```

```py
import numpy as np

def velocity_field(x, y, t):
    """Поле швидкостей двовимірного потоку."""
    u_x = -np.sin(np.pi * x) * np.cos(np.pi * y) * np.exp(-0.01 * t)
    u_y =  np.cos(np.pi * x) * np.sin(np.pi * y) * np.exp(-0.01 * t)
    return u_x, u_y

def advance_rk4(x, y, t, dt):
    """Інтегрування координат маркетингових частинок методом RK4."""
    k1_x, k1_y = velocity_field(x, y, t)
    k2_x, k2_y = velocity_field(x + 0.5 * dt * k1_x, y + 0.5 * dt * k1_y, t + 0.5 * dt)
    k3_x, k3_y = velocity_field(x + 0.5 * dt * k2_x, y + 0.5 * dt * k2_y, t + 0.5 * dt)
    k4_x, k4_y = velocity_field(x + dt * k3_x, y + dt * k3_y, t + dt)
    
    x_new = x + (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
    y_new = y + (dt / 6.0) * (k1_y + 2.0 * k2_y + 2.0 * k3_y + k4_y)
    return x_new, y_new

def compute_circulation(x, y, t):
    """Обчислення замкненого контурного інтеграла ∮ u · dr."""
    dx = 0.5 * (np.roll(x, -1) - np.roll(x, 1))
    dy = 0.5 * (np.roll(y, -1) - np.roll(y, 1))
    u_x, u_y = velocity_field(x, y, t)
    return np.sum(u_x * dx + u_y * dy)

# Параметри розрахунку
N = 100
dt = 0.01
steps = 500

theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
x = 0.5 + 0.25 * np.cos(theta)
y = 0.5 + 0.25 * np.sin(theta)

t = 0.0
gamma_0 = compute_circulation(x, y, t)
print(f"t = {t:.2f} | Gamma = {gamma_0:.8f}")

for step in range(1, steps + 1):
    x, y = advance_rk4(x, y, t, dt)
    t += dt
    if step % 100 == 0:
        gamma = compute_circulation(x, y, t)
        err = abs(gamma - gamma_0) / gamma_0
        print(f"t = {t:.2f} | Gamma = {gamma:.8f} | Rel Error = {err:.2e}")
```
:::

## Оцінка чисельної точності, алгоритмічні пастки та ресемплінг

При практичній чисельній реалізації алгоритмів відстеження контурів у складних симуляціях слід ураховувати декілька фундаментальних джерел чисельних помилок:

- **Геометричний зсув маркерних частинок (англ. *particle clustering*)**: У регіонах потоку з сильним розтягненням або зсувом рідкі частинки накопичуються в окремих зонах і рідшають на інших. Це призводить до втрати роздільної здатності контурного інтегрування. Для запобігання цій деградації застосовується процедура динамічного адаптивного ресемплінгу (англ. *adaptive contour resampling*): коли відстань між сусідніми маркерними частинками перевищує `1.5 · Δs_0`, між ними вставляється нова частинка за допомогою кубічного сплайна. Якщо ж відстань падає нижче `0.5 · Δs_0`, дві сусідні частинки зливаються в одну.
- **Вибір порядку часового інтегрування**: Застосування схеми Ейлера першого порядку (`O(dt)`) призводить до штучного розширення замкнених траєкторій частинок і неконтрольованого зростання циркуляції. Використання схем високих порядків точності (RK4 або симплектичних інтеграторів) є обов'язковою умовою збереження дискретного фазового об'єму та циркуляційного інваріанта.
- **Вплив інтерполяційної в'язкості на сітці**: Якщо поле швидкості заздалегідь розраховане на Ейлеровій сітці (наприклад, методом Marker-and-Cell), інтерполяція швидкості в позиції частинок методом білінійної інтерполяції створює штучну дифузію завихреності зі швидкістю `dΓ/dt ∝ Δx²`. Для високої точності слід застосовувати кубічну сплайнову інтерполяцію або методи спектральних елементів.
- **Перевірка періодичності індексів**: При обчисленні дискретного контурного інтеграла перша та остання точки мають замикатися без утворення геометричних розривів або повторного подвійного врахування крайового вузла.
- **Збереження топології в тривимірних потоках**: У 3D симуляціях контур описується замкненим просторовим полігоном. Ресемплінг повинен зберігати тривимірну кривину та закрученість (англ. *torsion*) контурної лінії для точного обчислення циркуляційного інваріанта.
- **Паралелізація та потокобезпечність**: Обчислення інтегрування траєкторій лагранжевих маркерних частинок у C++ реалізації можна легко паралелізувати за допомогою бібліотеки OpenMP (`#pragma omp parallel for`), оскільки частинки адвектуються незалежно одна від одної.
- **Моніторинг чисельної енстрофії**: Оцінка зміни циркуляції з часом `|Γ(t) - Γ(0)| / Γ(0)` дає можливість автоматично контролювати стійкість гідродинамічного соловера та виявляти області локального виникнення дисипативних помилок.

Крім того, при моделюванні течій зі вільними межами або твердими перешкодами маркерні частинки контуру при наближенні до твердої стінки повинні оброблятися дзеркальним відображенням або проектуванням швидкості для дотримання умови непроникності.

Завдяки реалізації лагранжевого відстеження маркерів розробник отримує точний інструмент діагностики чисельних симуляцій, який дозволяє відрізнити фізичні процеси генерації завихреності (наприклад, бароклінний момент чи в'язке прилипання) від артефактів обчислювальних схем.

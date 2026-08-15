# ⚙️ Практична реалізація чисельного розв'язувача осцилятора Дуффінга: інтегрування методом Рунге-Кутти RK4 та побудова перерізів Пуанкаре

Практична чисельна реалізація розв'язання нелінійного диференціального рівняння Дуффінга вимагає побудови стійких обчислювальних алгоритмів інтегрування високого порядку точності, ефективної організації пам'яті для тривалих розрахунків та точного стробоскопічного збору точок для формування фрактальних перерізів Пуанкаре.

У цьому практичному проєкті розглядається повна архітектура обчислювального двигуна, математичне обґрунтування вибору чисельного методу, порівняння RK4 із симплектичними інтеграторами, особливості реалізації трьома мовами програмування (C99, C++20 та Python 3), а також аналіз інженерних підводних каменів.

---

### Математичне обґрунтування та розгортання чисельного алгоритму

Вихідне нелінійне диференціальне рівняння осцилятора Дуффінга другого порядку з періодичним зовнішнім збудженням описується виразом:

```
d²x/dt² + δ·(dx/dt) + α·x + β·x³ = γ·cos(ω·t)
```

Для застосування стандартних чисельних методів інтегрування диференціальне рівняння другого порядку необхідно звести до еквівалентної системи двох зв'язаних диференціальних рівнянь першого порядку. Ввівши вектор фазового стану системи `S = (x, v)`, де `x` — узагальнена координата зміщення, а `v = dx/dt` — миттєва швидкість, отримуємо канонічну систему:

```
dx/dt = f₁(t, x, v) = v
dv/dt = f₂(t, x, v) = - δ·v - α·x - β·x³ + γ·cos(ω·t)
```

#### Вибір чисельного методу: RK4 проти симплектичних інтеграторів

При виборі чисельного методу для нелінійного осцилятора виникає фундаментальна інженерна дилема між класичними методами Рунге-Кутти та симплектичними інтеграторами:

1. **Класичний метод Рунге-Кутти 4-го порядку (RK4):**
   - **Переваги:** Має високий локальний порядок точності `O(h⁵)` та сумарну похибку `O(h⁴)`. Метод є універсальним і чудово працює як для консервативних, так і для дисипативних систем із явним згасанням `δ > 0` та зовнішньою силою `γ·cos(ω·t)`.
   - **Обмеження:** Не зберігає фазовий об'єм (теорема Ліувілля) при нескінченно тривалому інтегруванні консервативних систем без згасання, що може викликати повільний чисельний дрейф енергії.

2. **Симплектичні інтегратори (Velocity Verlet / Symplectic Euler):**
   - **Переваги:** Точно зберігають симплектичну структуру фазового простору та фазовий об'єм у консервативних системах (`δ = 0`, `γ = 0`).
   - **Обмеження:** Мають нижчий порядок точності (`O(h²)` для Verlet) і потребують значно дрібнішого кроку часу для збереження високої гладкості траєкторій при наявності швидких нелінійних коливань.

Для вимушеного дисипативного осцилятора Дуффінга метод RK4 є найкращим інженерним вибором, оскільки наявність фізичної дисипації `δ·v` робить систему несимпликтичною, а висока точність `O(h⁴)` забезпечує точне відтворення тонкої фрактальної структури дивного атрактора.

#### Детальний крок методу RK4

На кожному кроці за часом `h = t_{n+1} - t_n` обчислюються чотири векторних нахили `k₁, k₂, k₃, k₄`:

```
k₁ = f(t_n, S_n)
k₂ = f(t_n + h/2, S_n + (h/2)·k₁)
k₃ = f(t_n + h/2, S_n + (h/2)·k₂)
k₄ = f(t_n + h, S_n + h·k₃)

S_{n+1} = S_n + (h/6) · (k₁ + 2·k₂ + 2·k₃ + k₄)
```

Для вимушеного осцилятора Дуффінга компоненти нахилів розгортаються у вирази:
- `k₁.x = v_n`
- `k₁.v = - δ·v_n - α·x_n - β·x_n³ + γ·cos(ω·t_n)`
- `k₂.x = v_n + (h/2)·k₁.v`
- `k₂.v = - δ·(v_n + (h/2)·k₁.v) - α·(x_n + (h/2)·k₁.x) - β·(x_n + (h/2)·k₁.x)³ + γ·cos(ω·(t_n + h/2))`
- `k₃.x = v_n + (h/2)·k₂.v`
- `k₃.v = - δ·(v_n + (h/2)·k₂.v) - α·(x_n + (h/2)·k₂.x) - β·(x_n + (h/2)·k₂.x)³ + γ·cos(ω·(t_n + h/2))`
- `k₄.x = v_n + h·k₃.v`
- `k₄.v = - δ·(v_n + h·k₃.v) - α·(x_n + h·k₃.x) - β·(x_n + h·k₃.x)³ + γ·cos(ω·(t_n + h))`

---

### Побудова стробоскопічного перерізу Пуанкаре

Вимушений осцилятор Дуффінга має тривимірний фазовий простір станів `(x, v, t mod T)`, де `T = 2π/ω` — період зовнішньої збуджуючої сили. Для візуалізації хаотичної структури дивного атрактора використовується метод стробоскопічного зрізу (переріз Пуанкаре).

Послідовність обчислювальних кроків генерації перерізу Пуанкаре:

1. **Параметризація кроку:** Крок інтегрування `h` вибирається як точна частка від періоду сили: `h = T / N_steps`, де `N_steps` (наприклад, 400 або 500) — ціле число кроків на один період. Це гарантує, що після `N_steps` кроків час `t` збільшується точно на один період `T`.
2. **Усунення перехідних процесів (Transient Elimination):** Системі дають можливість еволюціонувати протягом `N_transient` періодів (зазвичай від 200 до 1000 періодів). Усі згасаючі власні коливання, зумовлені довільністю початкових умов `(x₀, v₀)`, повністю розсіюються, і траєкторія лягає на сталий атрактор.
3. **Стробоскопічний відбір точок (Poincare Sampling):** Після завершення перехідного режиму стан системи `(x, v)` фіксується і записується у файл або вектор суворо кожні `N_steps` кроків (тобто у моменти часу `t = k · T`).

---

### Повний багатомовний вихідний код проєкту

Нижче наведено три повністю функціональні реалізації обчислювального двигуна осцилятора Дуффінга мовами C99, C++20 та Python 3. Кожен приклад є автономним і готовим до компіляції та запуску.

:::tabs
```c
/* duffing_sim.c — Чисельне інтегрування осцилятора Дуффінга на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double alpha; /* лінійна жорсткість */
    double beta;  /* кубічна жорсткість */
    double delta; /* коефіцієнт згасання */
    double gamma; /* амплітуда зовнішньої сили */
    double omega; /* частота зовнішньої сили */
} duffing_params_t;

typedef struct {
    double x;
    double v;
} state_t;

/* Обчислення правих частин системи диференціальних рівнянь */
static inline state_t duffing_derivatives(state_t s, double t, const duffing_params_t *p) {
    state_t d;
    d.x = s.v;
    d.v = - p->delta * s.v - p->alpha * s.x - p->beta * s.x * s.x * s.x + p->gamma * cos(p->omega * t);
    return d;
}

/* Одиничний крок методом Рунге-Кутти 4-го порядку (RK4) */
state_t rk4_step(state_t s, double t, double h, const duffing_params_t *p) {
    state_t k1 = duffing_derivatives(s, t, p);
    
    state_t s2 = { s.x + 0.5 * h * k1.x, s.v + 0.5 * h * k1.v };
    state_t k2 = duffing_derivatives(s2, t + 0.5 * h, p);
    
    state_t s3 = { s.x + 0.5 * h * k2.x, s.v + 0.5 * h * k2.v };
    state_t k3 = duffing_derivatives(s3, t + 0.5 * h, p);
    
    state_t s4 = { s.x + h * k3.x, s.v + h * k3.v };
    state_t k4 = duffing_derivatives(s4, t + h, p);
    
    state_t next_s;
    next_s.x = s.x + (h / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    next_s.v = s.v + (h / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v);
    return next_s;
}

int main(void) {
    /* Параметри двоямного хаотичного осцилятора (Атрактор Уеди / Муна) */
    duffing_params_t params = {
        .alpha = -1.0,
        .beta  =  1.0,
        .delta =  0.2,
        .gamma =  0.3,
        .omega =  1.2
    };

    state_t current_state = { .x = 0.1, .v = 0.0 };
    double t = 0.0;
    
    /* Період зовнішньої сили T_period та крок інтегрування */
    double period = 2.0 * M_PI / params.omega;
    int steps_per_period = 500;
    double h = period / steps_per_period;
    
    int transient_periods = 200;  /* Пропускаємо перехідні процеси */
    int total_poincare_pts = 2000; /* Кількість точок у перерізі Пуанкаре */
    
    FILE *fp_poincare = fopen("poincare_c.dat", "w");
    if (!fp_poincare) {
        perror("Не вдалося відкрити файл poincare_c.dat");
        return EXIT_FAILURE;
    }
    
    /* 1. Пропускаємо перехідний режим */
    long transient_steps = (long)transient_periods * steps_per_period;
    for (long step = 0; step < transient_steps; ++step) {
        current_state = rk4_step(current_state, t, h, params);
        t += h;
    }
    
    /* 2. Запис стробоскопічних точок перерізу Пуанкаре (кожен період T) */
    for (int pt = 0; pt < total_poincare_pts; ++pt) {
        fprintf(fp_poincare, "%.8f\t%.8f\n", current_state.x, current_state.v);
        for (int step = 0; step < steps_per_period; ++step) {
            current_state = rk4_step(current_state, t, h, params);
            t += h;
        }
    }
    
    fclose(fp_poincare);
    printf("Обчислення завершено успішно. Записано %d точок у poincare_c.dat\n", total_poincare_pts);
    return EXIT_SUCCESS;
}
```
```cpp
// duffing_sim.cpp — Обчислювальний клас та переріз Пуанкаре на сучасній C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <numbers>
#include <stdexcept>

struct DuffingParams {
    double alpha{ -1.0 };
    double beta{   1.0 };
    double delta{  0.2 };
    double gamma{  0.3 };
    double omega{  1.2 };
};

struct Point2D {
    double x{ 0.0 };
    double v{ 0.0 };
};

class DuffingSolver {
public:
    explicit DuffingSolver(DuffingParams params) : params_(params) {}

    [[nodiscard]] Point2D rk4Step(Point2D s, double t, double h) const noexcept {
        const auto k1 = derivatives(s, t);
        const auto k2 = derivatives({ s.x + 0.5 * h * k1.x, s.v + 0.5 * h * k1.v }, t + 0.5 * h);
        const auto k3 = derivatives({ s.x + 0.5 * h * k2.x, s.v + 0.5 * h * k2.v }, t + 0.5 * h);
        const auto k4 = derivatives({ s.x + h * k3.x,       s.v + h * k3.v },       t + h);

        return {
            s.x + (h / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x),
            s.v + (h / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v)
        };
    }

    [[nodiscard]] std::vector<Point2D> generatePoincareSection(
        Point2D initialState,
        std::size_t transientPeriods,
        std::size_t poincarePoints,
        std::size_t stepsPerPeriod) const 
    {
        std::vector<Point2D> poincareData;
        poincareData.reserve(poincarePoints);

        const double period = 2.0 * std::numbers::pi / params_.omega;
        const double h = period / static_cast<double>(stepsPerPeriod);
        
        Point2D state = initialState;
        double t = 0.0;

        // Пропуск перехідного процесу (transient)
        const std::size_t totalTransientSteps = transientPeriods * stepsPerPeriod;
        for (std::size_t i = 0; i < totalTransientSteps; ++i) {
            state = rk4Step(state, t, h);
            t += h;
        }

        // Стробоскопічний відбір точок
        for (std::size_t i = 0; i < poincarePoints; ++i) {
            poincareData.push_back(state);
            for (std::size_t step = 0; step < stepsPerPeriod; ++step) {
                state = rk4Step(state, t, h);
                t += h;
            }
        }

        return poincareData;
    }

private:
    [[nodiscard]] Point2D derivatives(Point2D s, double t) const noexcept {
        return {
            s.v,
            -params_.delta * s.v - params_.alpha * s.x - params_.beta * s.x * s.x * s.x + params_.gamma * std::cos(params_.omega * t)
        };
    }

    DuffingParams params_;
};

int main() {
    try {
        DuffingParams params{ .alpha = -1.0, .beta = 1.0, .delta = 0.2, .gamma = 0.3, .omega = 1.2 };
        DuffingSolver solver(params);

        const auto poincarePoints = solver.generatePoincareSection({ 0.1, 0.0 }, 200, 2000, 500);

        std::ofstream outFile("poincare_cpp.dat");
        if (!outFile) {
            throw std::runtime_error("Не вдалося створити файл poincare_cpp.dat");
        }

        for (const auto& [x, v] : poincarePoints) {
            outFile << x << "\t" << v << "\n";
        }

        std::cout << "Успішно збережено " << poincarePoints.size() << " точок перерізу Пуанкаре (C++20)\n";
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
```py
# duffing_sim.py — Чисельне інтегрування та візуалізація мовою Python
import numpy as np
import matplotlib.pyplot as plt

def duffing_derivatives(state, t, alpha, beta, delta, gamma, omega):
    x, v = state
    dxdt = v
    dvdt = -delta * v - alpha * x - beta * x**3 + gamma * np.cos(omega * t)
    return np.array([dxdt, dvdt])

def rk4_step(state, t, h, params):
    k1 = duffing_derivatives(state, t, *params)
    k2 = duffing_derivatives(state + 0.5 * h * k1, t + 0.5 * h, *params)
    k3 = duffing_derivatives(state + 0.5 * h * k2, t + 0.5 * h, *params)
    k4 = duffing_derivatives(state + h * k3, t + h, *params)
    return state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

# Параметри системи
params = (-1.0, 1.0, 0.2, 0.3, 1.2)  # alpha, beta, delta, gamma, omega
alpha, beta, delta, gamma, omega = params

period = 2.0 * np.pi / omega
steps_per_period = 400
h = period / steps_per_period

state = np.array([0.1, 0.0])
t = 0.0

# 1. Пропуск перехідного процесу
for _ in range(200 * steps_per_period):
    state = rk4_step(state, t, h, params)
    t += h

# 2. Збір точок перерізу Пуанкаре
poincare_pts = []
for _ in range(3000):
    poincare_pts.append(state.copy())
    for _ in range(steps_per_period):
        state = rk4_step(state, t, h, params)
        t += h

poincare_pts = np.array(poincare_pts)

# Побудова графіка
plt.figure(figsize=(8, 6))
plt.scatter(poincare_pts[:, 0], poincare_pts[:, 1], s=0.8, color='crimson', alpha=0.7)
plt.title("Переріз Пуанкаре для хаотичного осцилятора Дуффінга")
plt.xlabel("Координата x")
plt.ylabel("Швидкість v")
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig("poincare_python.png", dpi=300)
print("Графік збережено як poincare_python.png")
```
:::

---

### Покроковий розбір реалізації та порівняльний аналіз мов

#### Специфіка реалізації на мові C99
У C-версії застосовано підхід із використанням простих структур даних `state_t` та `duffing_params_t`, що дозволяє передавати стан системи за значенням (оскільки структура містить лише два числа `double` і легко вміщується в регістри процесора `xmm0`, `xmm1`). Функція `duffing_derivatives` позначена як `static inline`, що виключає накладні витрати на виклик функції всередині гарячого циклу інтегрування.

#### Специфіка реалізації на мові C++20
У C++ версії реалізовано клас `DuffingSolver`, який інкапсулює параметри системи та надає безпечний публічний інтерфейс. Використання виразів `[[nodiscard]]` запобігає випадковому ігноруванню повернутих результатів. Параметри часу беруться з нового стандарту `std::numbers::pi`. Для уникнення динамічного перевиділення пам'яті при збереженні точок перерізу Пуанкаре використовується метод `poincareData.reserve(poincarePoints)`.

#### Специфіка реалізації мовою Python 3
Python-версія орієнтована на швидку візуалізацію та аналіз даних. Завдяки масивам NumPy обчислення векторів `[dxdt, dvdt]` виконуються компактно, а бібліотека Matplotlib створює готову публікаційну графіку з високою роздільною здатністю.

---

### Пастки реалізації та інженерні підводні камені

Під час практичного програмування чисельних методів для нелінійних осциляторів легко припуститися прикростей, які спотворюють результати:

1. **Накопичення похибки фази при додаванні кроку `t += h`:**
   Через обмежену точність чисел із плаваючою комою `double` (53 біти мантиси) багаторазове додавання дрібного кроку `t += h` протягом мільйонів ітерацій призводить до накопичення систематичної похибки фази. У результаті вибірка точок для перерізу Пуанкаре проводиться не точно в моменти `t_k = k · (2π / ω)`, а з постійно зростаючим кутовим зсувом.
   *Рішення:* Виражати час через точний цілочисельний індекс ітерації `t = step_index * h` або періодично виконувати редукцію фази за модулем `t = fmod(t, 2.0 * M_PI / omega)`.

2. **Недостатня тривалість відкидання перехідного процесу (transient):**
   При старті з довільних початкових умов система потребує часу для того, щоб фазова траєкторія «впала» на атрактор. Якщо почати зберігати точки надто рано, переріз Пуанкаре буде розмитий хаотичними слідами перехідного процесу.
   *Рішення:* Відкидати не менше 100–300 повних періодів зовнішньої сили перед початком фіксації точок.

3. **Вибір занадто великого кроку `h`:**
   У нелінійних системах із кубічним членом `β·x³` при великих відхиленнях відновлювальна сила зростає надзвичайно швидко. Якщо крок `h` завеликий, алгоритм RK4 чисельно «вибухає» (`x → ∞`).
   *Рішення:* Крок інтегрування має задовольняти умову `h ≤ (2π / 100·ω)` для гарантії стійкості.

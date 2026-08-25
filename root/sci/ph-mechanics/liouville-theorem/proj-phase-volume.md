# ⚙️ Чисельне моделювання збереження фазового об'єму: симплектичні проти несимплектичних інтеграторів

Чисельне розв'язання рівнянь гамільтонової динаміки є одним із найпоширеніших практичних завдань сучасної обчислювальної фізики. Воно лежить в основі розрахунку довготривалої стійкості орбіт планет Сонячної системи, траєкторій супутників, молекулярної динаміки складних білкових молекул, а також моделювання руху згустків плазми у магнітних пастках токамаків.

Проте ззвичайні числові інтегратори (такі як стандартний явний метод Ейлера, неявний метод Ейлера або класичний метод Рунге-Кутти 4-го порядку) мають приховану математичну ваду: вони не поважають теорему Ліувілля й не зберігають фазовий об'єм.

У цьому практичному проєкті ми розробимо комп'ютерну модель, яка прямо обчислює якобіан трансформації та відстежує зміну фазового об'єму для трьох різних алгоритмів чисельного інтегрування.

```
                  ПОРІВНЯННЯ ЧИСЕЛЬНИХ ІНТЕГРАТОРІВ
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      │                           │                           │
      ▼                           ▼                           ▼
Явний Ейлер                 Неявний Ейлер               Симплектичний Ейлер
(Explicit Euler)            (Implicit Euler)            (Symplectic Euler / Verlet)
det J = 1 + ω²Δt² > 1       det J = 1/(1 + ω²Δt²) < 1   det J ≡ 1.000000
Фазове вибухання            Штучне згасання             Точне збереження об'єму
```

## 1. Проблема числового дрейфу у гамільтоновій механіці

Коли ми розв'язуємо систему звичайних диференціальних рівнянь на комп'ютері, неперервний фізичний час `t` замінюється дискретною сіткою кроків `t_n = n · Δt`. Звичайні методи аналізу (зокрема явні алгоритми сімейства Рунге-Кутти) будуються так, щоб мінімізувати локальну помилку апроксимації на одного кроці `O(Δtᵖ)`.

Проте для гамільтонових систем мінімізація локальної помилки є недостатньою. Оскільки справжній гамільтонів потік зберігає симплектичну структуру `ω = ∑ dq ∧ dp` та фазовий об'єм `det J = 1.0`, несимплектичний інтегратор на кожному кроці робить мікроскопічну деформацію фазового об'єму.

При моделюванні на мільйони кроків (наприклад, при розрахунку руху планет Сонячної системи на 4.5 мільярдів років) ці мікроскопічні помилки фазового об'єму систематично накопичуються:
- Якщо `det J > 1.0`, фазовий об'єм штучно зростає, що призводить до нефізичного чисельного вибуху енергії та вильоту планет зі своїх орбіт.
- Якщо `det J < 1.0`, фазовий об'єм штучно стискається, що створює неіснуюче чисельне тертя (дисипацію), і планети падають на Сонце.

Симплектичні інтегратори (такі як метод Верле, схеми Стормера-Верле або симплектичний метод Ейлера-Кромера) будуються на принципово іншому фундаменті. Вони гарантують точне збереження симплектичної форми та фазового об'єму `det J ≡ 1.0` **строго й тотожно** для будь-якого кроку сітки `Δt`.

## 2. Фізична модель: Одиничний гармонічний осцилятор

Розглянемо класичний гармонічний осцилятор із одиничною масою `m = 1.0` та одиничною частотою `ω = 1.0`. Рівняння руху системи у фазовому просторі `(q, p)` мають вигляд:

```
dq/dt = p
dp/dt = -q
```

За один крок інтегрування за часом `Δt` ми переходимо від стану `(q_n, p_n)` до стану `(q_{n+1}, p_{n+1})`. Зміна фазової площі описується числовою матрицею Якобі `J`:

```
J = ┌                                              ┐
    │  ∂q_{n+1}/∂q_n            ∂q_{n+1}/∂p_n      │
    │                                              │
    │  ∂p_{n+1}/∂q_n            ∂p_{n+1}/∂p_n      │
    └                                              ┘
```

Теорема Ліувілля вимагає, щоб для справжньої консервативної системи визначник `det J` на кожному кроці дорівнював **строго 1.0**.

## 3. Математичний аналіз кроків інтегрування

1. **Явний метод Ейлера (Explicit Euler):**
   ```
   q_{n+1} = q_n + p_n · Δt
   p_{n+1} = p_n - q_n · Δt
   ```
   Матриця Якобі: `J = [[1, Δt], [-Δt, 1]]`.
   Обчислюємо визначник: `det J = 1 · 1 - (Δt)·(-Δt) = 1 + Δt² > 1`.
   **Наслідок:** З кожним кроком фазовий об'єм штучно розширюється у `(1 + Δt²)` разів. За `N` кроків площа роздувається у `(1 + Δt²)^N` разів. Повна енергія системи безмежно зростає, спричиняючи чисельний вибух.

2. **Неявний метод Ейлера (Implicit Euler):**
   ```
   q_{n+1} = q_n + p_{n+1} · Δt
   p_{n+1} = p_n - q_{n+1} · Δt
   ```
   Розв'язок системи відносно нових точок дає матрицю Якобі: `J = 1/(1 + Δt²) · [[1, Δt], [-Δt, 1]]`.
   Обчислюємо визначник: `det J = 1 / (1 + Δt²) < 1`.
   **Наслідок:** Фазовий об'єм штучно стискається. Модель демонструє фальшиве числове тертя (дисипацію), і осцилятор нефізично зупиняється.

3. **Симплектичний метод Ейлера-Кромера (Symplectic Euler / Euler-Cromer):**
   ```
   p_{n+1} = p_n - q_n · Δt           [спочатку оновлюємо імпульс]
   q_{n+1} = q_n + p_{n+1} · Δt       [потім координату новим імпульсом]
   ```
   Матриця Якобі: `J = [[1 - Δt², Δt], [-Δt, 1]]`.
   Обчислюємо визначник: `det J = (1 - Δt²) · 1 - (Δt)·(-Δt) = 1 - Δt² + Δt² = 1.000000`.
   **Наслідок:** Визначник `det J ≡ 1` виконується **строго й тотожно** для будь-якого кроку `Δt`! Фазовий об'єм зберігається абсолютно точно.

## 4. Метод геометричного обчислення площі фазової хмари

Для числової перевірки теореми Ліувілля ми створюємо ансамбль із `N` фазових точок, які у початковий момент часу утворюють правильне коло радіуса `R = 0.2` у фазовій площині `(q, p)`.

Для обчислення площі замкненого контуру у фазовому просторі використовується формула Гаусса для площі багатокутника (формула галасових шнурків, англ. *shoelace formula*):

```
S = ½ · | ∑ᵢ₌₁ⁿ ( qᵢ · p_{i+1} − q_{i+1} · pᵢ ) |
```

Оскільки фазовий потік збереже неперервність контуру, зміна цієї обчисленої площі `S(t)` прямо виражає коефіцієнт деформації фазового об'єму під дією чисельного алгоритму.

## 5. Програмне моделювання еволюції фазової хмари

Нижче наведено ідіоматичні реалізації трьох методів числового інтегрування мовами Python, C та C++. Програма моделює еволюцію початкової кругової хмари з `N = 500` частинок у фазовому просторі й обчислює її площу за допомогою алгоритму Гаусса.

:::tabs
```py
import math
import numpy as np

def simulate_phase_volume(steps=1000, dt=0.05, num_particles=500):
    # Початковий хмара точок у фазовому просторі: коло радіуса R = 0.2 біля (1.0, 0.0)
    angles = np.linspace(0, 2 * math.pi, num_particles, endpoint=False)
    r = 0.2
    
    # Створюємо початкові координати та імпульси
    q_explicit = 1.0 + r * np.cos(angles)
    p_explicit = 0.0 + r * np.sin(angles)
    
    q_implicit = np.copy(q_explicit)
    p_implicit = np.copy(p_explicit)
    
    q_sympl = np.copy(q_explicit)
    p_sympl = np.copy(p_explicit)
    
    def calculate_area(q, p):
        # Площа полігона у фазовому просторі за формулою Гаусса (галасових шнурків)
        return 0.5 * np.abs(np.dot(q, np.roll(p, 1)) - np.dot(p, np.roll(q, 1)))

    initial_area = calculate_area(q_explicit, p_explicit)
    print(f"Початкова площа фазової хмари Ω₀ = {initial_area:.6f}\n")
    print(f"{'Крок':>5} | {'Явний Ейлер':>14} | {'Неявний Ейлер':>14} | {'Симплектичний':>14}")
    print("-" * 55)

    for step in range(1, steps + 1):
        # 1. Явний Ейлер
        q_exp_new = q_explicit + p_explicit * dt
        p_exp_new = p_explicit - q_explicit * dt
        q_explicit, p_explicit = q_exp_new, p_exp_new

        # 2. Неявний Ейлер
        denom = 1.0 + dt * dt
        q_imp_new = (q_implicit + dt * p_implicit) / denom
        p_imp_new = (p_implicit - dt * q_implicit) / denom
        q_implicit, p_implicit = q_imp_new, p_imp_new

        # 3. Симплектичний Ейлер-Кромер
        p_sym_new = p_sympl - q_sympl * dt
        q_sym_new = q_sympl + p_sym_new * dt
        q_sympl, p_sympl = q_sym_new, p_sym_new

        if step % 200 == 0:
            area_exp = calculate_area(q_explicit, p_explicit)
            area_imp = calculate_area(q_implicit, p_implicit)
            area_sym = calculate_area(q_sympl, p_sympl)
            print(f"{step:5d} | {area_exp:14.6f} | {area_imp:14.6f} | {area_sym:14.6f}")

if __name__ == '__main__':
    simulate_phase_volume()
```
```c
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#define NUM_PARTICLES 500
#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double q[NUM_PARTICLES];
    double p[NUM_PARTICLES];
} PhaseEnsemble;

double calculate_area(const PhaseEnsemble *ens) {
    double area = 0.0;
    for (int i = 0; i < NUM_PARTICLES; ++i) {
        int j = (i + 1) % NUM_PARTICLES;
        area += (ens->q[i] * ens->p[j]) - (ens->p[i] * ens->q[j]);
    }
    return 0.5 * fabs(area);
}

int main(void) {
    PhaseEnsemble exp_ens, imp_ens, sym_ens;
    double r = 0.2;
    double dt = 0.05;
    int steps = 1000;

    for (int i = 0; i < NUM_PARTICLES; ++i) {
        double angle = 2.0 * M_PI_VAL * i / NUM_PARTICLES;
        double q0 = 1.0 + r * cos(angle);
        double p0 = 0.0 + r * sin(angle);
        
        exp_ens.q[i] = imp_ens.q[i] = sym_ens.q[i] = q0;
        exp_ens.p[i] = imp_ens.p[i] = sym_ens.p[i] = p0;
    }

    double init_area = calculate_area(&exp_ens);
    printf("Початкова площа фазової хмари: %.6f\n\n", init_area);
    printf("%5s | %14s | %14s | %14s\n", "Крок", "Явний Ейлер", "Неявний Ейлер", "Симплектичний");
    printf("-------------------------------------------------------\n");

    for (int step = 1; step <= steps; ++step) {
        for (int i = 0; i < NUM_PARTICLES; ++i) {
            // Явний Ейлер
            double q_exp_next = exp_ens.q[i] + exp_ens.p[i] * dt;
            double p_exp_next = exp_ens.p[i] - exp_ens.q[i] * dt;
            exp_ens.q[i] = q_exp_next; exp_ens.p[i] = p_exp_next;

            // Неявний Ейлер
            double denom = 1.0 + dt * dt;
            double q_imp_next = (imp_ens.q[i] + dt * imp_ens.p[i]) / denom;
            double p_imp_next = (imp_ens.p[i] - dt * imp_ens.q[i]) / denom;
            imp_ens.q[i] = q_imp_next; imp_ens.p[i] = p_imp_next;

            // Симплектичний Ейлер
            double p_sym_next = sym_ens.p[i] - sym_ens.q[i] * dt;
            double q_sym_next = sym_ens.q[i] + p_sym_next * dt;
            sym_ens.q[i] = q_sym_next; sym_ens.p[i] = p_sym_next;
        }

        if (step % 200 == 0) {
            printf("%5d | %14.6f | %14.6f | %14.6f\n",
                   step, calculate_area(&exp_ens), calculate_area(&imp_ens), calculate_area(&sym_ens));
        }
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct PhasePoint {
    double q{0.0};
    double p{0.0};
};

class PhaseEnsemble {
public:
    explicit PhaseEnsemble(std::size_t count, double radius, double center_q = 1.0, double center_p = 0.0) {
        m_points.reserve(count);
        for (std::size_t i = 0; i < count; ++i) {
            double angle = 2.0 * std::numbers::pi * i / count;
            m_points.push_back({center_q + radius * std::cos(angle), center_p + radius * std::sin(angle)});
        }
    }

    [[nodiscard]] double calculate_phase_area() const noexcept {
        double area = 0.0;
        const std::size_t n = m_points.size();
        for (std::size_t i = 0; i < n; ++i) {
            std::size_t j = (i + 1) % n;
            area += (m_points[i].q * m_points[j].p) - (m_points[i].p * m_points[j].q);
        }
        return 0.5 * std::abs(area);
    }

    void step_explicit_euler(double dt) noexcept {
        for (auto& pt : m_points) {
            double q_next = pt.q + pt.p * dt;
            double p_next = pt.p - pt.q * dt;
            pt.q = q_next;
            pt.p = p_next;
        }
    }

    void step_implicit_euler(double dt) noexcept {
        const double denom = 1.0 + dt * dt;
        for (auto& pt : m_points) {
            double q_next = (pt.q + dt * pt.p) / denom;
            double p_next = (pt.p - dt * pt.q) / denom;
            pt.q = q_next;
            pt.p = p_next;
        }
    }

    void step_symplectic_euler(double dt) noexcept {
        for (auto& pt : m_points) {
            pt.p -= pt.q * dt;       // Оновлення імпульсу
            pt.q += pt.p * dt;       // Оновлення координати з новим імпульсом
        }
    }

private:
    std::vector<PhasePoint> m_points;
};

int main() {
    constexpr std::size_t particles = 500;
    constexpr double dt = 0.05;
    constexpr int total_steps = 1000;

    PhaseEnsemble explicit_ens(particles, 0.2);
    PhaseEnsemble implicit_ens(particles, 0.2);
    PhaseEnsemble symplectic_ens(particles, 0.2);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Початкова площа фазової хмари: " << symplectic_ens.calculate_phase_area() << "\n\n";
    std::cout << std::setw(5) << "Крок" << " | "
              << std::setw(14) << "Явний Ейлер" << " | "
              << std::setw(14) << "Неявний Ейлер" << " | "
              << std::setw(14) << "Симплектичний" << "\n";
    std::cout << "-------------------------------------------------------\n";

    for (int step = 1; step <= total_steps; ++step) {
        explicit_ens.step_explicit_euler(dt);
        implicit_ens.step_implicit_euler(dt);
        symplectic_ens.step_symplectic_euler(dt);

        if (step % 200 == 0) {
            std::cout << std::setw(5) << step << " | "
                      << std::setw(14) << explicit_ens.calculate_phase_area() << " | "
                      << std::setw(14) << implicit_ens.calculate_phase_area() << " | "
                      << std::setw(14) << symplectic_ens.calculate_phase_area() << "\n";
        }
    }

    return 0;
}
```
:::

## 6. Аналіз результатів та фізичні висновки

Результати моделювання демонструють фундаментальну відмінність між різними математичними методами:

1. **Явний метод Ейлера:** За 1000 кроків площа фазової хмари зростає у понад 12 разів (`det J = (1 + 0.05²)^1000 ≈ 12.1`). Початковий круг деформується й роздувається, що відповідає нефізичному вибуховому зростанню повної енергії системи.
2. **Неявний метод Ейлера:** За 1000 кроків площа фазової хмари спадає у понад 12 разів (`det J = (1 / (1 + 0.05²))^1000 ≈ 0.082`). Метод вносить штучну дисипацію, згашуючи коливання навіть за відсутності справжнього тертя.
3. **Симплектичний метод Ейлера-Кромера:** За всі 1000 кроків площа фазової хмари зберігається з точністю до машинного нуля (`0.125664`). Кругова хмара деформується в нахилений еліпс, але її точна фазова площа за теоремою Ліувілля залишається абсолютно постійною.

У комп'ютерному моделюванні фізичних систем (зокрема у вивченні термодинамічної рівноваги та канонічних ансамблів Ґіббса) збереження фазової міри Ліувілля через використання симплектичних інтеграторів є обов'язковою умовою адекватності чисельного експерименту.

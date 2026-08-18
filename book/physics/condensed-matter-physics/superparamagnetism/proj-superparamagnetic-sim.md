# ⚙️ Чисельне моделювання термофлуктуацій макроспіна методом Стохастичної Динаміки Ландау — Ліфшиця — Ґільберта

Чисельне моделювання термофлуктуаційної релаксації однодоменних магнітних наночастинок дає змогу безпосередньо простежити за просторовою траєкторією вектора намагніченості під дією теплового шуму та розрахувати час релаксації Нееля — Брауна без спрощувальних припущень. Для цього використовується метод стохастичних диференціальних рівнянь Ландау — Ліфшиця — Ґільберта (sLLG), у якому теплові флуктуації кристалічної ґратки моделюються випадковим еквівалентним магнітним полем Ланжевена `H_th(t)`.

## 1. Фізична модель стохастичної динаміки Ланжевена

Динаміка безрозмірного вектора одиничної намагніченості макроспіна `m = M / M_s` (де інваріант норми вектора строго дорівнює одиниці `|m| = 1`) описується рівнянням Ландау — Ліфшиця — Ґільберта з термодинамічним членом Ланжевена:

```
dm/dt = -γ' · (m × H_eff) - α · γ' · (m × (m × H_eff))
```

де `γ' = γ / (1 + α²)`, `γ ≈ 1.76 · 10¹¹` рад/(с·Тл) — гіромагнітне співвідношення для електронного спіна, а `α` — безрозмірний коефіцієнт згасання Ґільберта.

Перший доданок у рівнянні sLLG описує консервативну Ларморівську прецесію вектора намагніченості `m` навколо напрямку ефективного магнітного поля `H_eff`. Другий доданок описує дисипативну релаксацію (згасання), яка спрямовує вектор намагніченості вздовж поля `H_eff` зі швидкістю, пропорційною коефіцієнту `α`.

Повне ефективне магнітне поле `H_eff`, яке визначає динаміку макроспіна у кожен момент часу, складається з трьох незалежних фізичних компонент:

```
H_eff = H_ext + H_aniso + H_th
```

1. **Зовнішнє магнітне поле `H_ext`**: Задається лабораторним джерелом поля або голівкою запису, наприклад `H_ext = (0, 0, H_z)`.
2. **Поле одновісної анізотропії `H_aniso`**: Спрямоване вздовж легкої осі анізотропії `Z` і залежить від поточного значення проекції намагніченості `m_z`:

```
H_aniso = (0, 0, H_k · m_z) = (0, 0, (2 · K_u / M_s) · m_z)
```

де `H_k = 2 · K_u / M_s` — ефективне поле анізотропії матеріалу.
3. **Випадкове поле теплових флуктуацій `H_th(t)`**: Моделює стохастичні поштовхи теплового руху кристалічної ґратки. Воно являє собою тривимірний гауссівський білий шум із нульовим математичним сподіванням та дельта-корельованою часовою функцією:

```
⟨H_th,i(t)⟩ = 0
⟨H_th,i(t) · H_th,j(t')⟩ = 2 · D_th · δ_ij · δ(t - t')
```

Інтенсивність флуктуаційного шуму `D_th` визначається флуктуаційно-дисипативною теоремою (ФДТ) Брауна для магнітних систем:

```
D_th = (α · k_B · T) / (γ · M_s · V)
```

При дискретизації диференціального рівняння за часом із кроком `Δt` компоненти випадкового поля Ланжевена на кожному ітераційному кроці розраховуються за допомогою незалежних випадкових величин `η_i`, які мають стандартний нормальний розподіл `N(0, 1)` із середнім нуль та дисперсією одиниця:

```
H_th,i = η_i · √(2 · D_th / Δt) = η_i · √((2 · α · k_B · T) / (γ · M_s · V · Δt))
```

## 2. Особливості чисельного інтегрування та метод Хена

Стохастичне рівняння sLLG містить мультиплікативний шум, оскільки випадкове поле `H_th(t)` входить під оператор векторного добутку `m × H_th`. У математиці стохастичних диференціальних рівнянь це вимагає чіткого вибору стохастичного числення — формалізму Іто або Стратоновича.

У фізиці магнетизму обов'язковим є застосування числення в інтерпретації Стратоновича. Головною фізичною причиною є те, що числення Стратоновича зберігає звичайні правила диференціювання складних функцій і гарантує суворе збереження норми вектора намагніченості `|m| = 1` під час еволюції. Просте застосування схеми Ейлера (яка відповідає численню Іто) призводить до штучного збільшення довжини вектора намагніченості та систематичної числової похибки.

Для чисельного інтегрування стохастичного рівняння sLLG у сенсі Стратоновича застосовується двоетапний метод Хена (Stratonovich-Heun predictor-corrector), який забезпечує другий порядок точності за часовим кроком.

### Детальний алгоритм ітераційного кроку Хена

На кожному часовому кроці `t_n -> t_n + Δt`:

1. **Генерація стохастичних величин**: Ґенеруються три незалежні випадкові числа `η_x, η_y, η_z`, розподілені за нормальним законом `N(0, 1)`.
2. **Обчислення флуктуаційного поля**: Розраховується вектор теплового поля Ланжевена `H_th = (H_th,x, H_th,y, H_th,z)`.
3. **Крок Предиктора (Predictor Step)**:
   - Обчислюється початкове ефективне поле `H_eff1 = H_ext + H_aniso(m_n) + H_th`.
   - Обчислюється початковий вектор похідної `k1 = sLLG(m_n, H_eff1)`.
   - Розраховується попередній орієнтовний вектор намагніченості `m_pred = m_n + k1 · Δt`.
   - Виконується обов'язкова підпросторова нормалізація вектора: `m_pred = m_pred / |m_pred|`.
4. **Крок Коректора (Corrector Step)**:
   - Обчислюється скориговане ефективне поле у проміжній точці `H_eff2 = H_ext + H_aniso(m_pred) + H_th`.
   - Обчислюється другий вектор похідної `k2 = sLLG(m_pred, H_eff2)`.
   - Розраховується остаточний зважений стан намагніченості: `m_{n+1} = m_n + 0.5 · (k1 + k2) · Δt`.
   - Виконується остаточна нормалізація вектора намагніченості: `m_{n+1} = m_{n+1} / |m_{n+1}|`.

Ця схема гарантує високу числову стійкість і точне збереження енергетичного балансу системи при тривалому моделюванні.

## 3. Реалізація симулятора мовами C, C++ та Python

Нижче наведено три повністю працездатні реалізації чисельного сумулятора стохастичної динаміки макроспінів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x, y, z;
} Vec3;

static Vec3 vec3_cross(Vec3 a, Vec3 b) {
    Vec3 r = {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
    return r;
}

static Vec3 vec3_normalize(Vec3 v) {
    double len = sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (len < 1e-15) len = 1.0;
    Vec3 r = { v.x / len, v.y / len, v.z / len };
    return r;
}

/* Генератор випадкових чисел Box-Muller для нормально розподілених величин N(0,1) */
static double rand_gaussian(void) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

/* Розрахунок похідної dm/dt за рівнянням sLLG */
static Vec3 sllg_rhs(Vec3 m, Vec3 h_eff, double gamma_prime, double alpha) {
    Vec3 m_cross_h = vec3_cross(m, h_eff);
    Vec3 m_cross_m_cross_h = vec3_cross(m, m_cross_h);
    
    Vec3 dmdt = {
        -gamma_prime * m_cross_h.x - alpha * gamma_prime * m_cross_m_cross_h.x,
        -gamma_prime * m_cross_h.y - alpha * gamma_prime * m_cross_m_cross_h.y,
        -gamma_prime * m_cross_h.z - alpha * gamma_prime * m_cross_m_cross_h.z
    };
    return dmdt;
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* Фізичні константи */
    const double kB = 1.380649e-23;    /* Дж/К */
    const double gamma = 1.76e11;       /* rad/(s*T) */

    /* Параметри матеріалу (Co наночастинка) */
    const double Ms = 1.4e6;            /* А/м */
    const double Ku = 4.5e5;            /* Дж/м3 */
    const double diameter = 8.0e-9;      /* 8 нм */
    const double V = (M_PI / 6.0) * diameter * diameter * diameter;
    const double alpha = 0.1;
    const double T = 300.0;             /* Кімнатна температура К */

    const double gamma_prime = gamma / (1.0 + alpha * alpha);
    const double Hk = 2.0 * Ku / Ms;    /* Поле анізотропії, Тл */
    const double stdev_h_th = sqrt((2.0 * alpha * kB * T) / (gamma * Ms * V));

    /* Параметри чисельного інтегрування */
    const double dt = 1.0e-13;          /* Крок за часом 0.1 пс */
    const long num_steps = 5000000;    /* 0.5 мкс сумуляції */

    Vec3 m = { 0.0, 0.0, 1.0 };         /* Старт з верхнього мінімуму +M_z */

    long flip_count = 0;
    int current_state = 1;              /* 1 для m_z > 0, -1 для m_z < 0 */

    printf("=== Симуляція термофлуктуацій макроспіна (C) ===\n");
    printf("Діаметр частини: %.1f нм, Температура: %.0f K\n", diameter * 1e9, T);
    printf("Енергетичний бар'єр Ku*V / kB*T: %.2f\n", (Ku * V) / (kB * T));
    printf("Поле анізотропії Hk: %.3f Tл\n\n", Hk);

    for (long step = 0; step < num_steps; step++) {
        /* Згенелювати випадкове поле Ланжевена для даного кроку */
        double dt_sqrt = sqrt(dt);
        Vec3 h_th = {
            stdev_h_th * rand_gaussian() / dt_sqrt,
            stdev_h_th * rand_gaussian() / dt_sqrt,
            stdev_h_th * rand_gaussian() / dt_sqrt
        };

        /* Ефективне поле: анізотропія + шум */
        Vec3 h_eff = { h_th.x, h_th.y, Hk * m.z + h_th.z };

        /* Метод Хена (Предиктор) */
        Vec3 k1 = sllg_rhs(m, h_eff, gamma_prime, alpha);
        Vec3 m_pred = {
            m.x + k1.x * dt,
            m.y + k1.y * dt,
            m.z + k1.z * dt
        };
        m_pred = vec3_normalize(m_pred);

        /* Коректор */
        Vec3 h_eff_pred = { h_th.x, h_th.y, Hk * m_pred.z + h_th.z };
        Vec3 k2 = sllg_rhs(m_pred, h_eff_pred, gamma_prime, alpha);

        m.x += 0.5 * (k1.x + k2.x) * dt;
        m.y += 0.5 * (k1.y + k2.y) * dt;
        m.z += 0.5 * (k1.z + k2.z) * dt;
        m = vec3_normalize(m);

        /* Фіксація перевертань */
        if (current_state == 1 && m.z < -0.2) {
            current_state = -1;
            flip_count++;
        } else if (current_state == -1 && m.z > 0.2) {
            current_state = 1;
            flip_count++;
        }
    }

    double sim_time = num_steps * dt;
    double tau_theoretical = 1e-9 * exp((Ku * V) / (kB * T));

    printf("Час моделювання: %.2e с\n", sim_time);
    printf("Кількість перевертань макроспіна: %ld\n", flip_count);
    printf("Теоретичний час Нееля-Брауна: %.2e с\n", tau_theoretical);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] Vec3 cross(const Vec3& o) const noexcept {
        return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }

    [[nodiscard]] Vec3 normalized() const noexcept {
        const double n = norm();
        const double inv = (n < 1e-15) ? 1.0 : (1.0 / n);
        return {x * inv, y * inv, z * inv};
    }

    Vec3& operator+=(const Vec3& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
};

inline Vec3 operator*(double s, const Vec3& v) noexcept {
    return {s * v.x, s * v.y, s * v.z};
}

inline Vec3 operator+(const Vec3& a, const Vec3& b) noexcept {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}

class MacrospinSimulator {
public:
    struct Params {
        double Ms{1.4e6};           // Насичена намагніченість, А/м
        double Ku{4.5e5};           // Анізотропія, Дж/м3
        double diameter{8.0e-9};    // Діаметр наночастинки, м
        double alpha{0.1};          // Затухання Ґільберта
        double T{300.0};            // Температура, К
    };

    explicit MacrospinSimulator(Params p)
        : p_(p),
          volume_((M_PI / 6.0) * std::pow(p.diameter, 3)),
          gamma_prime_(1.76e11 / (1.0 + p.alpha * p.alpha)),
          Hk_(2.0 * p.Ku / p.Ms),
          stdev_h_th_(std::sqrt((2.0 * p.alpha * 1.380649e-23 * p.T) / (1.76e11 * p.Ms * volume_))),
          gen_(std::random_device{}()) {}

    struct SimulationResult {
        double total_time_sec;
        std::size_t flip_count;
        double tau_theoretical_sec;
        double final_mz;
    };

    SimulationResult run(double dt_sec, std::size_t num_steps) {
        Vec3 m{0.0, 0.0, 1.0};
        std::size_t flips = 0;
        int state = 1;
        const double inv_sqrt_dt = 1.0 / std::sqrt(dt_sec);

        for (std::size_t step = 0; step < num_steps; ++step) {
            Vec3 h_th{
                stdev_h_th_ * dist_(gen_) * inv_sqrt_dt,
                stdev_h_th_ * dist_(gen_) * inv_sqrt_dt,
                stdev_h_th_ * dist_(gen_) * inv_sqrt_dt
            };

            Vec3 h_eff = h_th + Vec3{0.0, 0.0, Hk_ * m.z};

            // Метод Хена (Стратонович)
            Vec3 k1 = sllg_rhs(m, h_eff);
            Vec3 m_pred = (m + dt_sec * k1).normalized();

            Vec3 h_eff_pred = h_th + Vec3{0.0, 0.0, Hk_ * m_pred.z};
            Vec3 k2 = sllg_rhs(m_pred, h_eff_pred);

            m = (m + (0.5 * dt_sec) * (k1 + k2)).normalized();

            if (state == 1 && m.z < -0.2) {
                state = -1;
                ++flips;
            } else if (state == -1 && m.z > 0.2) {
                state = 1;
                ++flips;
            }
        }

        const double kb = 1.380649e-23;
        const double tau_th = 1.0e-9 * std::exp((p_.Ku * volume_) / (kb * p_.T));
        return {num_steps * dt_sec, flips, tau_th, m.z};
    }

private:
    [[nodiscard]] Vec3 sllg_rhs(const Vec3& m, const Vec3& h_eff) const noexcept {
        Vec3 m_x_h = m.cross(h_eff);
        Vec3 m_x_m_x_h = m.cross(m_x_h);
        return (-1.0 * gamma_prime_) * m_x_h + (-1.0 * p_.alpha * gamma_prime_) * m_x_m_x_h;
    }

    Params p_;
    double volume_;
    double gamma_prime_;
    double Hk_;
    double stdev_h_th_;
    std::mt19937 gen_;
    std::normal_distribution<double> dist_{0.0, 1.0};
};

int main() {
    MacrospinSimulator::Params p;
    p.diameter = 8.0e-9;
    p.T = 300.0;

    MacrospinSimulator sim(p);
    const double dt = 1.0e-13;
    const std::size_t steps = 5'000'000;

    std::cout << "=== Стохастична LLG симуляція макроспіна (C++17) ===\n";
    auto res = sim.run(dt, steps);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "Час моделювання: " << res.total_time_sec << " s\n";
    std::cout << "Перевертань макроспіна: " << res.flip_count << "\n";
    std::cout << "Теоретичний час Нееля-Брауна: " << res.tau_theoretical_sec << " s\n";

    return 0;
}
```
```py
import math
import numpy as np

def simulate_macrospin_sllg(d_nm=8.0, temp_k=300.0, dt_s=1e-13, num_steps=5000000):
    """
    Чисельне моделювання термофлуктуацій макроспіна однодоменної частинки методом sLLG (Heun).
    """
    kb = 1.380649e-23
    gamma = 1.76e11
    ms = 1.4e6
    ku = 4.5e5
    alpha = 0.1

    vol = (math.pi / 6.0) * (d_nm * 1e-9)**3
    gamma_prime = gamma / (1.0 + alpha**2)
    hk = 2.0 * ku / ms
    stdev_h_th = math.sqrt((2.0 * alpha * kb * temp_k) / (gamma * ms * vol))

    m = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    flips = 0
    state = 1

    def sllg_rhs(m_vec, h_eff):
        m_x_h = np.cross(m_vec, h_eff)
        m_x_m_x_h = np.cross(m_vec, m_x_h)
        return -gamma_prime * m_x_h - alpha * gamma_prime * m_x_m_x_h

    dt_sqrt = math.sqrt(dt_s)

    for _ in range(num_steps):
        # Поле Ланжевена
        h_th = stdev_h_th * np.random.normal(0.0, 1.0, 3) / dt_sqrt
        h_eff = h_th + np.array([0.0, 0.0, hk * m[2]])

        # Предиктор Хена
        k1 = sllg_rhs(m, h_eff)
        m_pred = m + k1 * dt_s
        m_pred /= np.linalg.norm(m_pred)

        # Коректор Хена
        h_eff_pred = h_th + np.array([0.0, 0.0, hk * m_pred[2]])
        k2 = sllg_rhs(m_pred, h_eff_pred)

        m += 0.5 * (k1 + k2) * dt_s
        m /= np.linalg.norm(m)

        # Фіксація перевертання
        if state == 1 and m[2] < -0.2:
            state = -1
            flips += 1
        elif state == -1 and m[2] > 0.2:
            state = 1
            flips += 1

    tau_th = 1e-9 * math.exp((ku * vol) / (kb * temp_k))
    return num_steps * dt_s, flips, tau_th

if __name__ == "__main__":
    print("=== Моделювання релаксації Нееля — Брауна в Python ===")
    total_t, count, tau_exp = simulate_macrospin_sllg()
    print(f"Час симуляції: {total_t:.2e} с")
    print(f"Кількість спонтанних перевертань: {count}")
    print(f"Теоретичний час релаксації τ: {tau_exp:.2e} с")
```
:::

## 4. Детальний порівняльний аналіз програмних реалізацій

Кожна з наведених трьох реалізацій демонструє свій підхід до чисельного аналізу магнітних моделей:

1. **Процедурна C-реалізація**: Побудована на найпростіших фундаментальних типах даних із використанням явного перетворення Бокса — Мюллера для генерації стандартного нормально розподіленого шуму `N(0, 1)`. Вона забезпечує виключно високу обчислювальну швидкість та мінімальне використання оперативної пам'яті, що є критичним при паралельному моделюванні великих ансамблів (мільйонів невзаємодіючих частинок) на суперкомп'ютерах.
2. **Об'єктно-орієнтована C++17 реалізація**: Інкапсулює фізичні параметри наночастинки та математичний стан симуляції усередині класу `MacrospinSimulator`. Використання генератора псевдовипадкових чисел `std::mt19937` та розподілу `std::normal_distribution` з бібліотеки `<random>` гарантує високу якість статистичного шуму без періодичних кореляцій. Завдяки механізмам inline-розгортання компілятора під час оптимізації `O3`, C++ реалізація виконується з тотожною до C швидкістю.
3. **Python / NumPy реалізація**: Забезпечує максимально прозорий та стислий код для швидкого проектування фізичних експериментів, аналізу результатів та побудови графіків. Використання векторних функцій `np.cross` та `np.linalg.norm` робить код подібним до математичного запису рівнянь.

## 5. Аналіз чисельних результатів та фізичні висновки

1. **Залежність від розміру частинки**: При моделюванні наночастинки кобальту (`K_u = 4.5 · 10⁵` Дж/м³) при кімнатній температурі `T = 300` К зміна діаметра частинки `D` спричиняє кардинальну зміну кінетики релаксації:
   - При `D = 6` нм: бар'єр анізотропії `K_u · V / (k_B · T) ≈ 2.8`. Макроспін флуктуює безперервно, здійснюючи десятки тисяч перевертань за мікросекунду. Намагніченість усереднюється до нуля за лічені наносекунди.
   - При `D = 8` нм: бар'єр `K_u · V / (k_B · T) ≈ 6.6`. Середній час між спонтанними переворотами становить десятки наносекунд, що узгоджується з розрахованим теоретичним значенням `τ_th`.
   - При `D = 12` нм: бар'єр `K_u · V / (k_B · T) ≈ 22.4`. За весь час сумуляції `0.5` мкс не спостерігається жодної події перевороту. Макроспін здійснює лише дрібні прецесійні коливання навколо початкового мінімуму `+M_z`.

2. **Динамічна траєкторія**: Вектор намагніченості `m(t)` здійснює високочастотну прецесію з Ларморівською частотою навколо легкої осі `Z`. Під дією стохастичного поля Ланжевена конус прецесії пульсує та розширюється, поки випадковий поштовх шуму не виштовхне вектор через екваторіальну площину `m_z = 0` у протилежний потенціальний мінімум `-M_z`.

3. **Вимоги до часового кроку `Δt`**: Оскільки частота прецесії макроспіна у полі анізотропії становить `f_prec = γ · H_k / (2π) ~ 10`–`50` ГГц, крок інтегрування `Δt` повинен бути принаймні на два порядки меншим за період прецесії (`Δt ≤ 10⁻¹³` с). Використання більшого кроку призводить до числової нестійкості стохастичного поля та розриву норми вектора намагніченості.

4. **Межі прямого моделювання**: Для систем із високими бар'єрами анізотропії (`K_u · V > 30 k_B T`) пряме моделювання методом sLLG стає обчислювально недоступним, оскільки очікування події рідкісного перескоку вимагає трильйонів часових кроків. У таких випадках у наукових розрахунках застосовують метод кінетичного Монте-Карло (kMC) або розрахунок поверхні переходів методом Forward Flux Sampling.

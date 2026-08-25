# ⚙️ Чисельне моделювання язиків Арнольда та драбини диявола

Чисельне моделювання є основним інструментом дослідження нелінійних відображень, оскільки аналітичні розв'язки для меж язиків Арнольда вищих порядків та фрактальної драбини диявола отримати неможливо. На цій сторінці подано алгоритми, практичну архітектуру, програмні моделі та робочі реалізації мовами C та C++ для обчислення числа обертання, побудови карти резонансних областей у просторі параметрів, обчислення показника Ляпунова та виявлення режиму фазового захоплення.

## Постановка обчислювальної задачі

Чисельне моделювання синус-кругового відображення Арнольда полягає у послідовному обчисленні ітерацій підйому дійсної фазової координати `x ∈ ℝ`:

```
x[n+1] = x[n] + Ω - (K / (2·π)) · sin(2·π·x[n])
```

Для кожної точки простору параметрів `(Ω, K)` на двовимірній сітці розміром `N_Ω × N_K` необхідно розрахувати число обертання `W`:

```
W = lim[N → ∞] (x[N] - x[0]) / N
```

Процес чисельного розрахунку складається з трьох послідовних етапів:

1. **Перехідний процес (англ. *transient phase*):** Перші `N_transient` ітерацій (типово від `10³` до `10⁵`) відкидаються, щоб фазова точка вийшла з довільного початкового стану `x₀` і осіла на стійкому атракторі (граничному циклі або квазіперіодичному торі). Завдяки відкиданню початкових кроків розрахунок не залежить від вибору початкової фази при `K ≤ 1`. Якщо не відкинути перехідний процес, початкове відхилення викривить обчислене число обертання, створивши фальшиві коливання на графіку.
2. **Вимірювальна фаза (англ. *measurement phase*):** Виконується `N_measure` ітерацій, під час яких відстежується повне накопичене відхилення фази `Δx = x[N_measure] - x[0]`. Число обертання обчислюється як `W = Δx / N_measure`. Для досягнення високої точності обчислень значення `N_measure` обирається значно більшим за максимальний передбачуваний період `q`. Чим більша кількість вимірювальних кроків, тим вища роздільна здатність розрізнення раціональних плато.
3. **Ідентифікація резонансу (англ. *mode-locking detection*):** Отримане число обертання `W` порівнюється з раціональними дробами `p/q` із заданим допустимим відхиленням `ε` (наприклад `10⁻⁴`). Якщо `|W - p/q| < ε`, режим класифікується як фазове захоплення на резонансі `p/q`. Для пошуку раціонального дробу використовується алгоритм перебору знаменників від `1` до `max_q` із вибором чисельника `p = round(W · q)`.

## Архітектура алгоритму та оптимізація обчислень

Основним обчислювальним вузлом алгоритму є функція виклику тригонометричного синуса `sin()`. При обчисленні карт високої роздільної здатності (наприклад `1000 × 1000` точок) кількість ітерацій відображення може досягати `10¹⁰`. Для забезпечення максимальної продуктивності виконання та запобігання втраті точності застосовуються спеціальні інженерні рішення.

### Захист від втрати точності плаваючої крапки

При тривалому моделюванні фазова координата `x[n]` зростає до великих чисельних значень (наприклад `x[n] > 10⁵`). Оскільки формат `double` має обмежену кількість розрядів мантиси (53 біти), додавання малого зсуву `Ω` до великого числа `x[n]` призводить до катастрофічної втрати точності (англ. *loss of significance*).

Для запобігання цій похибці використовується методика нормалізації:
* На кожному кроці або через фіксовану кількість ітерацій ціла частина фази `floor(x)` віднімається від дробової, а кількість повних обертів накопичується в окремому цілочисельному лічильнику `long long turns`.
* Розрахунок аргументу синуса виконується виключно від дробової частини phase `x - floor(x) ∈ [0, 1)`, що гарантує максимальну точність тригонометричних викликів.
* Наприкінці вимірювальної фази повний зсув обчислюється як сума лічильника обертів та залишку дробових частин: `Δx = turns + (x_final - x_start)`.

### Оптимізація обчислювального ядра та паралелізація

Для прискорення розрахунків застосовуються наступні методи:
* **Попередній розрахунок констант:** Величини `2·π` та `1 / (2·π)` обчислюються один раз під час ініціалізації та зберігаються у регістрах або константній пам'яті процесора.
* **Векторизація SIMD:** Сучасні процесори з підтримкою інструкцій AVX2 / AVX-512 здатні обчислювати по 4 або 8 синусів одночасно при використанні векторних математичних бібліотек (наприклад Intel SVML або SLEEF).
* **Багатопотокова паралелізація сітки:** Оскільки обчислення кожної точки `(Ω, K)` є абсолютно незалежним від інших точок (задача за своєю природою є паралельною, англ. *embarrassingly parallel*), завдання розподіляється між ядрами процесора за допомогою OpenMP directives `#pragma omp parallel for` або стандартних потоків виконання `std::thread`.

### Паралельне сканування за допомогою OpenMP та std::jthread

При скануванні сіток високої роздільної здатності `1000 × 1000` для максимальної утилізації всіх ядер центрального процесора застосовується паралельний обчислювальний конвеєр.

У мові C паралельний цикл по рядках сітки параметрів `K` реалізується прагмою OpenMP:

```
#pragma omp parallel for collapse(2) schedule(dynamic)
for (int y = 0; y < grid_h; ++y) {
    for (int x = 0; x < grid_w; ++x) {
        /* обчислення точки (omega, k) */
    }
}
```

Директива `schedule(dynamic)` забезпечує високе вирівнювання завантаження обчислювальних ядер (англ. *load balancing*), оскільки точки поблизу меж язиків вимагають більше часу через сповільнення збіжності, ніж точки у центрі резонансних плато.

У C++20 для досягнення аналогічного ефекту використовується пул потоків `std::jthread` або паралельні алгоритми стандартної бібліотеки `std::for_each(std::execution::par, ...)`, що усуває потребу у зовнішніх залежностях.

### Аналіз часової складності та кеш-локальності

Часова складність сканування прямокутної сітки розміром `N_Ω × N_K` становить `O(N_Ω · N_K · (N_transient + N_measure))`. Для стандартної карти `1000 × 1000` при `N_transient = 5000` та `N_measure = 10000` загальна кількість крок-ітерацій становить `1.5 × 10¹⁰`.

Просторова складність збереження підсумкового масиву становить `O(N_Ω · N_K)`. При збереженні чисел обертання у форматі `double` масив `1000 × 1000` займає всього 8 МБ оперативної пам'яті, що повністю вміщується у L3-кеш сучасних процесорів, забезпечуючи високу локальність даних по пам'яті (англ. *cache locality*).

## Алгоритм прямого пошуку меж язиків методом бісекції

Замість повного сканування двовимірної сітки параметрів для знаходження точних геодезичних меж язика Арнольда `T[p/q]` при зафіксованому `K` застосовується метод ділення навпіл (бісекції).

Оскільки число обертання `W(Ω)` є неперервною та монотонно неспадною функцією від `Ω`, ліва межа `Ω_left` визначається як точка, у якій `W(Ω) = p/q`, але при зменшенні `Ω` число обертання знижується.

Алгоритм пошуку лівої межі:
1. Задається початковий інтервал `[Ω_a, Ω_b]`, де `W(Ω_a) < p/q` та `W(Ω_b) = p/q`.
2. Обчислюється середина інтервалу `Ω_mid = (Ω_a + Ω_b) / 2`.
3. Для точки `Ω_mid` розраховується точне число обертання `W(Ω_mid)`.
4. Якщо `W(Ω_mid) < p/q`, нова ліва межа `Ω_a = Ω_mid`; інакше нова права межа `Ω_b = Ω_mid`.
5. Покроковий процес триває до досягнення точності `|Ω_b - Ω_a| < 10⁻⁶`.

Аналогічно обчислюється права межа `Ω_right`. Цей підхід зменшує кількість розрахункових точок із `10⁶` до кількох сотень, дозволяючи будувати гладкі контурні графіки язиків з високою точністю.

## Чисельний розрахунок старшого показника Ляпунова

Для розрізнення хаотичних та квазіперіодичних режимів у системі при `K > 1` паралельно з числом обертання розраховується старший показник Ляпунова `λ`.

Алгоритм обчислення показника Ляпунова:
1. Ініціалізується змінна-накопичувач `lyapunov_sum = 0.0`.
2. На кожному кроці вимірювальної фази обчислюється значення похідної `f̄'(x[i]) = 1 - K · cos(2·π·x[i])`.
3. Для запобігання взяттю логарифма від нуля при випадковому потраплянні в суперстійку точку додається захисне значення `eps_guard = 10⁻¹²`: `val = max(|1 - K · cos(2·π·x[i])|, eps_guard)`.
4. До накопичувача додається натуральний логарифм: `lyapunov_sum += ln(val)`.
5. Після завершення `N_measure` кроків показник Ляпунова дорівнює `λ = lyapunov_sum / N_measure`.

Якщо `λ < 0`, траєкторія притягується до стійкого періодичного циклу всередині язика. Якщо `λ = 0`, рух є квазіперіодичним. Якщо `λ > 0`, траєкторія є хаотичною.

## Пошук нерухомих точок методом Ньютона — Рафсона

Для точного знаходження періодичних точок періоду `q` всередині язика `T[p/q]` використовується багатовимірний метод Ньютона — Рафсона для рівняння `F(x) = f̄⁹(x) - x - p = 0`.

Ітераційна формула Ньютона має вигляд:

```
x[k+1] = x[k] - F(x[k]) / F'(x[k])
```

де похідна `F'(x) = (d/dx f̄⁹(x)) - 1` обчислюється за ланцюговим правилом диференціювання композиції функцій:

```
d/dx f̄⁹(x) = ∏[i=0..q-1] f̄'(x[i])
```

Цей метод збігається з квадратичною швидкістю `|x[k+1] - x*| ∼ |x[k] - x*|²`, дозволяючи знаходити розташування та стійкість періодичних орбіт за 4–6 ітерацій.

## Файловий експорт результатів у CSV та бінарні формати

Для подальшого аналізу та побудови високоякісних двовимірних діаграм (наприклад за допомогою пакета Gnuplot, Python Matplotlib або паралельних візуалізаторів VTK/ParaView) обчислені результати експортуються у текстові файли формату CSV або бінарні файли прямого доступу.

У C++ для експорту даних використовується клас `std::ofstream` з буферизованим виводом:

```cpp
void export_to_csv(std::string_view filename, std::span<const StaircasePoint> points) {
    std::ofstream out(filename.data());
    out << "omega,rotation_number,derivative\n";
    for (const auto& pt : points) {
        out << pt.omega << "," << pt.rotation_number << "," << pt.derivative << "\n";
    }
}
```

Використання `std::span<const StaircasePoint>` з стандарту C++20 забезпечує безпечний доступ до послідовності елементів без створення копій пам'яті.

## Профілювання продуктивності та тестування продуктивності

Для оцінки ефективності розроблених чисельних ядер проводиться профільне тестування продуктивності (англ. *benchmarking*) за допомогою системних утиліт профілювання (таких як `perf` у Linux або Intel VTune Profiler).

Метрики оцінки продуктивності обчислювального ядра:
* **Мільйони ітерацій за секунду (M-Iter/s):** Кількість виконаних крок-ітерацій кругового відображення за 1 секунду на один потік процесора. Оптимізоване C/C++ ядро з використанням інструкцій AVX2 досягає понад 400 M-Iter/s на одноядерному обчислювачі.
* **Ефективність використання L1/L2 кешу:** Завдяки локальному збереженню фазової координати у регістровій пам'яті кількість промахів кешу пам'яті (англ. *cache misses*) на етапі моделювання траєкторії прямує до нуля `L1 Miss Rate < 0.1%`.
* **Масштабованість на багатоядерних системах:** Коефіцієнт прискорення (англ. *speedup factor*) при виклику OpenMP на 8-ядерному процесорі досягає `S_8 ≈ 7.6`, що свідчить про високу лінійну масштабованість паралельного алгоритму.

## Моделювання підсистем ФАПЧ (Digital Phase-Locked Loop)

Програмні моделі кругових відображень безпосередньо застосовуються при розробці систем цифрово-аналогової фазової автопідстройки частоти (ФАПЧ / DPLL).

У таких системах підйом відображення дискретизує динаміку вихідного фазового детектора та керованого напругою генератора (ГУН / VCO).

Особливості програмної реалізації DPLL на основі кругового відображення:
* **Фільтр нижніх частот (ФНЧ):** Рівняння відображення доповнюється другою змінною стану `v[n]` (керуюча напруга фільтра):
  ```
  v[n+1] = α · v[n] + (1 - α) · (K / (2·π)) · sin(2·π·x[n])
  x[n+1] = x[n] + Ω - v[n+1]
  ```
* **Захоплення частоти в широкому діапазоні:** Моделювання дозволяє обчислити максимальну смугу захоплення (англ. *pull-in range*) та смугу утримання (англ. *hold-in range*) при довільних коефіцієнтах підсилення петлі `K`.
* **Тестування стабільності фазового шуму:** Крок-відображення модифікується додаванням випадкової величини з нормальним розподілом (гауссівський фазовий шум `ξ[n]`), що дозволяє чисельно розраховувати середній час виходу системи зі стану захоплення під дією завад.

## Інтерактивна візуалізація на графічних процесорах (GPGPU / Compute Shaders)

Для досягнення інтерактивної частоти оновлення кадрів (60 FPS) при інтерактивному дослідженні простору параметрів `(Ω, K)` обчислення синус-кругового відображення переноситься на графічний процесор (GPU) за допомогою обчислювальних шейдерів (англ. *Compute Shaders* у OpenGL / Vulkan / Direct3D) або технології CUDA / OpenCL.

Принцип реалізації на GPU:
* Кожен піксель екранного буфера розміром `1920 × 1080` обробляється окремим потоком шейдера (англ. *thread / work-item*).
* Координати пікселя `(x, y)` масштабуються у фізичні параметри `Ω ∈ [0, 1]` та `K ∈ [0, 1.2]`.
* Усередині шейдера виконується цикл із `N_transient + N_measure` ітерацій у регістровій пам'яті графічного ядра.
* Знайдене число обертання `W` перетворюється на колір пікселя за допомогою палітри (колірне кодування резонансів).

Завдяки паралелізму тисяч обчислювальних ядер GPU повне обчислення карти з 2 мільйонів точок виконується за 10–15 мілісекунд, що дозволяє користувачеві в реальному часі змінювати масштаб (зумувати фрактальні межі язиків Арнольда) без затримок.

## Реалізація алгоритму обчислення числа обертання

Нижче подано паралельні ідіоматичні реалізації алгоритму аналізу кругового відображення мовами C та C++.

Версія C використовує традиційну процедурну структуру з явним управлінням пам'яттю, вбудованими інлайн-функціями `static inline` для крок-відображення та передачею конфігураційних структур через вказівники на стакові дані. У функції `compute_circle_map` крок за кроком моделюється проходження перехідного процесу та вимірювальної фази. Утиліта `find_closest_rational` шукає найближчий раціональний дріб `p/q` зі знаменником `q ≤ max_q` і перевіряє, чи не перевищує похибка заданий поріг `tol`.

Версія C++ написана за сучасним стандартом C++20: вона застосовує інкапсуляцію у клас `CircleMapSimulator`, простори імен `physics::nonlinear`, засоби `std::numbers::pi`, тип `std::optional` для безпечного повернення результату ідентифікації резонансу та кваліфікатори `constexpr` і `[[nodiscard]]`. Використання `std::optional<ResonanceInfo>` гарантує, що якщо режим не є резонансним, об'єкт виклику явно сигналізує про відсутність фазового захоплення без використання нульових вказівників чи магічних чисел.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double omega;
    double k;
    size_t transient_steps;
    size_t measure_steps;
    double initial_x;
} circle_map_config_t;

typedef struct {
    double rotation_number;
    int numerator;
    int denominator;
    bool is_mode_locked;
} circle_map_result_t;

/* Обчислення підйому синус-кругового відображення */
static inline double circle_map_step(double x, double omega, double k) {
    const double two_pi = 2.0 * M_PI;
    return x + omega - (k / two_pi) * sin(two_pi * x);
}

/* Пошук найближчого раціонального дробу p/q з обмеженням знаменника max_q */
static void find_closest_rational(double w, int max_q, double tol, int *out_p, int *out_q, bool *out_locked) {
    w = w - floor(w); // нормалізація до [0, 1)
    int best_p = 0;
    int best_q = 1;
    double min_diff = fabs(w);

    for (int q = 1; q <= max_q; ++q) {
        int p = (int)round(w * q);
        double diff = fabs(w - (double)p / (double)q);
        if (diff < min_diff) {
            min_diff = diff;
            best_p = p;
            best_q = q;
        }
    }

    *out_p = best_p;
    *out_q = best_q;
    *out_locked = (min_diff <= tol);
}

/* Основна функція моделювання траєкторії та обчислення W */
circle_map_result_t compute_circle_map(const circle_map_config_t *cfg, int max_q, double tol) {
    double x = cfg->initial_x;
    const double omega = cfg->omega;
    const double k = cfg->k;

    /* 1. Фаза перехідного процесу */
    for (size_t i = 0; i < cfg->transient_steps; ++i) {
        x = circle_map_step(x, omega, k);
    }

    /* 2. Вимірювальна фаза */
    const double start_x = x;
    for (size_t i = 0; i < cfg->measure_steps; ++i) {
        x = circle_map_step(x, omega, k);
    }

    const double delta_x = x - start_x;
    const double rot_num = delta_x / (double)cfg->measure_steps;

    /* 3. Ідентифікація резонансного режиму */
    circle_map_result_t res;
    res.rotation_number = rot_num;
    find_closest_rational(rot_num, max_q, tol, &res.numerator, &res.denominator, &res.is_mode_locked);

    return res;
}

int main(void) {
    circle_map_config_t cfg = {
        .omega = 0.33333333,
        .k = 0.8,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.1
    };

    circle_map_result_t res = compute_circle_map(&cfg, 16, 1e-4);

    printf("Параметри: Omega = %.4f, K = %.4f\n", cfg.omega, cfg.k);
    printf("Число обертання W = %.6f\n", res.rotation_number);
    if (res.is_mode_locked) {
        printf("Стан: Фазове захоплення на резонансі %d/%d\n", res.numerator, res.denominator);
    } else {
        printf("Стан: Квазіперіодичний рух (поза язиками)\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <optional>
#include <string_view>
#include <iomanip>

namespace physics::nonlinear {

struct CircleMapConfig {
    double omega{0.0};
    double k{0.0};
    std::size_t transient_steps{10000};
    std::size_t measure_steps{50000};
    double initial_x{0.0};
};

struct ResonanceInfo {
    int numerator{0};
    int denominator{1};
    double error{0.0};
};

struct SimulationResult {
    double rotation_number{0.0};
    std::optional<ResonanceInfo> resonance{};
};

class CircleMapSimulator {
public:
    explicit constexpr CircleMapSimulator(CircleMapConfig config) noexcept
        : config_{config} {}

    [[nodiscard]] SimulationResult run(int max_denominator = 16, double tolerance = 1e-4) const {
        double x = config_.initial_x;
        const double two_pi = 2.0 * std::numbers::pi;

        // 1. Пропускаємо перехідний процес
        for (std::size_t i = 0; i < config_.transient_steps; ++i) {
            x = step(x, two_pi);
        }

        // 2. Вимірюємо точний зсув фази
        const double start_x = x;
        for (std::size_t i = 0; i < config_.measure_steps; ++i) {
            x = step(x, two_pi);
        }

        const double delta_x = x - start_x;
        const double rot_num = delta_x / static_cast<double>(config_.measure_steps);

        // 3. Шукаємо найближчий резонансний дріб
        SimulationResult result;
        result.rotation_number = rot_num;
        result.resonance = detect_resonance(rot_num, max_denominator, tolerance);

        return result;
    }

private:
    [[nodiscard]] constexpr double step(double x, double two_pi) const noexcept {
        return x + config_.omega - (config_.k / two_pi) * std::sin(two_pi * x);
    }

    [[nodiscard]] static std::optional<ResonanceInfo> detect_resonance(
        double w, int max_q, double tol) noexcept 
    {
        const double norm_w = w - std::floor(w);
        int best_p = 0;
        int best_q = 1;
        double min_diff = std::abs(norm_w);

        for (int q = 1; q <= max_q; ++q) {
            const int p = static_cast<int>(std::round(norm_w * static_cast<double>(q)));
            const double diff = std::abs(norm_w - static_cast<double>(p) / static_cast<double>(q));
            if (diff < min_diff) {
                min_diff = diff;
                best_p = p;
                best_q = q;
            }
        }

        if (min_diff <= tol) {
            return ResonanceInfo{.numerator = best_p, .denominator = best_q, .error = min_diff};
        }
        return std::nullopt;
    }

    CircleMapConfig config_;
};

} // namespace physics::nonlinear

int main() {
    using namespace physics::nonlinear;

    const CircleMapConfig config{
        .omega = 0.33333333,
        .k = 0.8,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.1
    };

    const CircleMapSimulator simulator{config};
    const auto result = simulator.run(16, 1e-4);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Параметри: Omega = " << config.omega << ", K = " << config.k << "\n";
    std::cout << "Число обертання W = " << result.rotation_number << "\n";

    if (result.resonance) {
        std::cout << "Стан: Фазове захоплення на резонансі "
                  << result.resonance->numerator << "/" << result.resonance->denominator
                  << " (абсолютна похибка: " << result.resonance->error << ")\n";
    } else {
        std::cout << "Стан: Квазіперіодичний рух (поза язиками)\n";
    }

    return 0;
}
```
:::

## Сканування двовимірної карти язиків Арнольда

Для розрахунку двовимірної карти параметрів `(Ω, K)` створюється двовимірний масив чисел обертання. Візуалізація результатів у тестових консольних утилітах виконується за допомогою символьної карти ASCII, де кожному основному резонансному язику призначається власний текстовий символ (наприклад `'0'` для `0/1`, `'H'` для `1/2`, `'3'` для `1/3` та `2/3`).

Нижче подано дві паралельні реалізації консольного рендерера для двовимірної карти параметрів.

У C++ версії клас `ArnoldMapRenderer` узагальнює обчислення і вивід, використовуючи строгу інкапсуляцію та незмінні члени класу.

Функція `select_symbol` аналізує число обертання `w` і зіставляє його з основними раціональними плато в межах допуску. Якщо число обертання не потрапляє в жодне з перелічених плато, виводиться символ крапки `'.'`, що сигналізує про квазіперіодичний рух або язик високого порядку.

Програма виконує подвійний цикл по висоті `grid_h` (значення `K`) та ширині `grid_w` (значення `Ω`). У кожній точці сітки викликом приватного методу `compute_rotation_number` розраховується число обертання і виводиться відповідний ASCII-символ.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void render_ascii_arnold_tongues(int grid_w, int grid_h, size_t steps) {
    const double two_pi = 2.0 * M_PI;

    for (int y = grid_h - 1; y >= 0; --y) {
        double k = 1.2 * ((double)y / (double)(grid_h - 1));
        printf("%4.1f |", k);

        for (int x = 0; x < grid_w; ++x) {
            double omega = (double)x / (double)(grid_w - 1);
            double phase = 0.1;

            /* Ітерації відображення */
            for (size_t i = 0; i < steps; ++i) {
                phase = phase + omega - (k / two_pi) * sin(two_pi * phase);
            }

            double start_p = phase;
            size_t m_steps = steps;
            for (size_t i = 0; i < m_steps; ++i) {
                phase = phase + omega - (k / two_pi) * sin(two_pi * phase);
            }

            double w = (phase - start_p) / (double)m_steps;
            w = w - floor(w);

            /* Символьне позначення резонансів */
            char symbol = '.';
            if (fabs(w - 0.0) < 0.02 || fabs(w - 1.0) < 0.02) symbol = '0';
            else if (fabs(w - 0.5) < 0.02) symbol = 'H'; // 1/2
            else if (fabs(w - 1.0/3.0) < 0.015 || fabs(w - 2.0/3.0) < 0.015) symbol = '3';
            else if (fabs(w - 1.0/4.0) < 0.01 || fabs(w - 3.0/4.0) < 0.01) symbol = '4';
            else if (fabs(w - 1.0/5.0) < 0.008 || fabs(w - 2.0/5.0) < 0.008 ||
                     fabs(w - 3.0/5.0) < 0.008 || fabs(w - 4.0/5.0) < 0.008) symbol = '5';

            putchar(symbol);
        }
        putchar('\n');
    }

    printf("     +");
    for (int x = 0; x < grid_w; ++x) putchar('-');
    printf("\n      0.0");
    for (int x = 0; x < grid_w - 8; ++x) putchar(' ');
    printf("1.0 (Omega)\n");
}

int main(void) {
    printf("=== Двовимірна карта язиків Арнольда (ASCII) ===\n");
    render_ascii_arnold_tongues(60, 20, 2000);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <string_view>
#include <memory>
#include <span>

namespace physics::visualization {

class ArnoldMapRenderer {
public:
    ArnoldMapRenderer(std::size_t width, std::size_t height, std::size_t steps)
        : width_{width}, height_{height}, steps_{steps} {}

    void render_to_console() const {
        const double two_pi = 2.0 * std::numbers::pi;

        for (std::size_t y = height_; y > 0; --y) {
            const double k = 1.2 * static_cast<double>(y - 1) / static_cast<double>(height_ - 1);
            std::cout << std::fixed << std::setprecision(1) << k << " |";

            for (std::size_t x = 0; x < width_; ++x) {
                const double omega = static_cast<double>(x) / static_cast<double>(width_ - 1);
                const double w = compute_rotation_number(omega, k, two_pi);
                std::cout << select_symbol(w);
            }
            std::cout << "\n";
        }

        std::cout << "    +";
        for (std::size_t x = 0; x < width_; ++x) std::cout << "-";
        std::cout << "\n     0.0" << std::string(width_ > 8 ? width_ - 8 : 0, ' ') << "1.0 (Omega)\n";
    }

private:
    [[nodiscard]] double compute_rotation_number(double omega, double k, double two_pi) const noexcept {
        double phase = 0.1;
        for (std::size_t i = 0; i < steps_; ++i) {
            phase = phase + omega - (k / two_pi) * std::sin(two_pi * phase);
        }

        const double start_phase = phase;
        for (std::size_t i = 0; i < steps_; ++i) {
            phase = phase + omega - (k / two_pi) * std::sin(two_pi * phase);
        }

        const double rot = (phase - start_phase) / static_cast<double>(steps_);
        return rot - std::floor(rot);
    }

    [[nodiscard]] static constexpr char select_symbol(double w) noexcept {
        if (std::abs(w - 0.0) < 0.02 || std::abs(w - 1.0) < 0.02) return '0';
        if (std::abs(w - 0.5) < 0.02) return 'H'; // 1/2
        if (std::abs(w - 1.0 / 3.0) < 0.015 || std::abs(w - 2.0 / 3.0) < 0.015) return '3';
        if (std::abs(w - 1.0 / 4.0) < 0.01 || std::abs(w - 3.0 / 4.0) < 0.01) return '4';
        if (std::abs(w - 1.0 / 5.0) < 0.008 || std::abs(w - 2.0 / 5.0) < 0.008 ||
            std::abs(w - 3.0 / 5.0) < 0.008 || std::abs(w - 4.0 / 5.0) < 0.008) return '5';
        return '.';
    }

    std::size_t width_;
    std::size_t height_;
    std::size_t steps_;
};

} // namespace physics::visualization

int main() {
    const physics::visualization::ArnoldMapRenderer renderer{60, 20, 2000};
    renderer.render_to_console();
    return 0;
}
```
:::

## Обчислення драбини диявола та чисельне диференціювання

Для побудови драбини диявола при критичному значенні `K = 1` функція `W(Ω)` обчислюється на одновимірній сітці з високою роздільною здатністю по `Ω` (наприклад `10⁴` точок).

Окрім власне числа обертання, програма розраховує його числову похідну `dW/dΩ` методом центральних скінченних різниць:

```
dW/dΩ ≈ (W(Ω + ΔΩ) - W(Ω - ΔΩ)) / (2 · ΔΩ)
```

На горизонтальних плато (всередині язиків Арнольда) числова похідна дорівнює нулю `dW/dΩ = 0`. На межах між плато похідна приймає великі сплескоподібні значення, що дозволяє чисельно фіксувати фрактальну структуру Кантора.

Отриманий вектор даних дозволяє будувати сумарну міру горизонтальних сходинок та чисельно оцінювати фрактальну розмірність покриття Гаусдорфа.

Класи `staircase_point_t` (C) та `StaircasePoint` (C++) містять три тривіальні поля: значення `omega`, число обертання `rotation_number` та похідну `derivative`. Завдяки компактному розташуванню у пам'яті масив структур зручно передавати у графічні пакети візуалізації (наприклад Gnuplot або Matplotlib) чи зберігати у файлі формату CSV.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double omega;
    double rotation_number;
    double derivative;
} staircase_point_t;

void compute_devils_staircase(double k_val, size_t num_points, size_t steps, staircase_point_t *out_points) {
    const double two_pi = 2.0 * M_PI;

    for (size_t i = 0; i < num_points; ++i) {
        double omega = (double)i / (double)(num_points - 1);
        double x = 0.1;

        /* Перехідний процес */
        for (size_t s = 0; s < steps; ++s) {
            x = x + omega - (k_val / two_pi) * sin(two_pi * x);
        }

        /* Вимірювання */
        double start_x = x;
        for (size_t s = 0; s < steps; ++s) {
            x = x + omega - (k_val / two_pi) * sin(two_pi * x);
        }

        double w = (x - start_x) / (double)steps;
        out_points[i].omega = omega;
        out_points[i].rotation_number = w;
        out_points[i].derivative = 0.0;
    }

    /* Числове диференціювання методом центральних різниць */
    double d_omega = 1.0 / (double)(num_points - 1);
    for (size_t i = 1; i < num_points - 1; ++i) {
        out_points[i].derivative = (out_points[i + 1].rotation_number - out_points[i - 1].rotation_number) / (2.0 * d_omega);
    }
}

int main(void) {
    const size_t n_pts = 11;
    staircase_point_t points[11];

    compute_devils_staircase(1.0, n_pts, 5000, points);

    printf("=== Таблиця драбини диявола (K = 1.0) ===\n");
    printf("   Omega  |  W(Omega) |   dW/dOmega\n");
    printf("-----------------------------------\n");
    for (size_t i = 0; i < n_pts; ++i) {
        printf("  %6.4f  |  %8.6f |  %10.4f\n", points[i].omega, points[i].rotation_number, points[i].derivative);
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
#include <span>

namespace physics::numerical {

struct StaircasePoint {
    double omega{0.0};
    double rotation_number{0.0};
    double derivative{0.0};
};

class DevilsStaircaseCalculator {
public:
    DevilsStaircaseCalculator(double k, std::size_t points_count, std::size_t steps)
        : k_{k}, points_count_{points_count}, steps_{steps} {}

    [[nodiscard]] std::vector<StaircasePoint> calculate() const {
        std::vector<StaircasePoint> points(points_count_);
        const double two_pi = 2.0 * std::numbers::pi;
        const double d_omega = 1.0 / static_cast<double>(points_count_ - 1);

        for (std::size_t i = 0; i < points_count_; ++i) {
            const double omega = static_cast<double>(i) * d_omega;
            double x = 0.1;

            // Перехідний процес
            for (std::size_t s = 0; s < steps_; ++s) {
                x = x + omega - (k_ / two_pi) * std::sin(two_pi * x);
            }

            // Вимірювання
            const double start_x = x;
            for (std::size_t s = 0; s < steps_; ++s) {
                x = x + omega - (k_ / two_pi) * std::sin(two_pi * x);
            }

            const double w = (x - start_x) / static_cast<double>(steps_);
            points[i] = StaircasePoint{.omega = omega, .rotation_number = w, .derivative = 0.0};
        }

        // Центральні різниці для похідної
        for (std::size_t i = 1; i < points_count_ - 1; ++i) {
            points[i].derivative = (points[i + 1].rotation_number - points[i - 1].rotation_number) / (2.0 * d_omega);
        }

        return points;
    }

private:
    double k_;
    std::size_t points_count_;
    std::size_t steps_;
};

} // namespace physics::numerical

int main() {
    using namespace physics::numerical;

    const DevilsStaircaseCalculator calc{1.0, 11, 5000};
    const auto points = calc.calculate();

    std::cout << "=== Таблиця драбини диявола (K = 1.0) ===\n";
    std::cout << "   Omega  |  W(Omega) |   dW/dOmega\n";
    std::cout << "-----------------------------------\n";
    std::cout << std::fixed << std::setprecision(4);

    for (const auto& pt : points) {
        std::cout << "  " << pt.omega << "  |  " << std::setprecision(6) << pt.rotation_number
                  << " |  " << std::setprecision(4) << pt.derivative << "\n";
    }

    return 0;
}
```
:::

## Обчислювальні пастки та крайні випадки

При практицій чисельній реалізації моделювання язиків Арнольда виникають наступні важливі інженерні проблеми та крайні випадки:

1. **Уповільнення збіжності поблизу меж язика (англ. *critical slowing down*):** При наближенні параметрів `(Ω, K)` до геометрії меж язика Арнольда час релаксації фази до стійкої періодичної орбіти експоненційно зростає `τ ∼ 1 / |K - K_c|`. Якщо число ітерацій `N_transient` недостатнє, обчислене значення `W` може виявитися помилковим. Для таких точок потрібно збільшувати кількість ітерацій `N_transient` у 10–100 разів.
2. **Чисельне накопичення похибок плаваючої крапки:** При тривалому підсумовуванні `x[N] = x[0] + ∑ Δx` виникає втрата точності типу `double`. Щоб її уникнути, цілу частину фази `floor(x)` періодично віднімають і накопичують у окремому 64-бітному цілому лічильнику обертів `long long turns`.
3. **Залежність від початкових умов у закритичному режимі (`K > 1`):** У зоні перекриття язиків співіснують кілька стійких атракторів. Початок моделювання з невірно обраної точки `x₀` призводить до потрапляння у сусідній резонансний режим. Для повного аналізу мультистабільності виконується сканування з різними початковими фазами `x₀ ∈ [0, 1)`.
4. **Виявлення хаотичних траєкторій:** Всередині хаотичних зон `K > 1` границя числа обертання флуктуює при зміні тривалості моделювання. Для надійного відділення хаосу від квазіперіодичності додатково розраховується старший показник Ляпунова `λ`: якщо `λ > 0`, режим класифікується як детермінований хаос.

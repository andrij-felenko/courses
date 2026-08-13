# ⚙️ Реалізація інтерполяції та відновлення сигналу мовами C і C++

У цифровий обробці сигналів (DSP), вбудованих системах керування та програмних звукових рушіях безперервний сигнал часто доводиться відновлювати у довільні моменти часу між дискретними відліками. Така потреба виникає при передискретизації (*resampling*), зміні частоти кадрів у відео, керуванні прецизійними приводами та формуванні аналогових вихідних сигналів за допомогою ЦАП.

Залежно від вимог до обчислювальної швидкодії, доступної пам'яті та припустимого рівня високочастотних спотворень у DSP-практиці застосовують три основні класи методів відновлення:
1. **Фіксатор нульового порядку (ZOH / Zero-Order Hold):** алгоритм найближчого сусіда, що утримує постійне значення відліку протягом усього періоду.
2. **Лінійна інтерполяція (FOH / First-Order Hold):** з'єднання сусідніх точок похилими лінійними відрізками.
3. **Віконна Sinc-інтерполяція (Windowed Sinc / Lanczos Interpolation):** згортка масиву відліків зі зваженою віконною функцією кардинального синуса, яка максимально наближається до теоретичної формули Котельникова-Шеннона.

Нижче детально розібрано алгоритмічну будову кожного методу, їхні країні випадки (*edge cases*) та подано робочі компільовані реалізації мовами C та C++.

---

## 1. Алгоритмічний розбір методів відновлення

### Фіксатор нульового порядку (ZOH)

Фіксатор нульового порядку є найпростішим можливим способом відновлення. Для будь-якого моменту часу `t` алгоритм обчислює дробовий індекс у масиві відліків `idx = floor(t · fs)` і повертає значення `x[idx]`.

```
Складність: O(1) операцій
Операції: 1 множення, 1 округлення floor, 1 читання з пам'яті
```

*Крайові випадки:* При `t < 0` алгоритм повертає перший відлік `x[0]`; при `t >= N / fs` повертає останній відлік `x[N-1]`.

*Спектральний відгук:* ZOH утворює ступенчасту напругу з великою кількістю високочастотних дзеркальних гармонік (образів). Модуль спектральної обвідної згасає повільно за законом `sinc(f·Ts)`, затухаючи на `-3.92 дБ` на межі Найквіста `fs/2`. ZOH застосовують у найпростіших дисплеях, індикаторах та швидких інструментальних контролерах, де обчислювальні ресурси жорстко обмежені.

### Лінійна інтерполяція (FOH)

Лінійна інтерполяція обчислює похилий відрізок між двома сусідніми відліками `x[i]` та `x[i+1]`. Для моменту часу `t` визначається ціла частина індексу `i = floor(t · fs)` та дробовий залишок `frac = t · fs - i`.

```
x_lin(t) = (1 - frac) · x[i] + frac · x[i+1]
```

```
Складність: O(1) операцій
Операції: 1 множення для індексу, 1 floor, 1 віднімання, 2 множення, 1 додавання
```

*Крайові випадки:* Якщо `i+1` виходить за межі масиву `N`, алгоритм обрізає індекс до останньої доступної точки `x[N-1]`, не допускаючи виходу за межі буфера.

*Спектральний відгук:* Амплітудно-частотна характеристика лінійної інтерполяції пропорційна `sinc²(f·Ts)`. Вона усуває розриви першого роду (значення напруги стають неперервними), проте призводить до помітного згладжування високих частот (згасання досягає `-7.84 дБ` на межі Найквіста). Лінійну інтерполяцію активно використовують у давачах контролерів моторів, обробці аудіо в реальному часі та простому масштабуванні графіки.

### Віконна Sinc-інтерполяція Ланцоша (Lanczos Interpolation)

Для досягнення високої спектральної чистоти відновлений сигнал обчислюється як зважена сума сусідніх відліків із ядрами Ланцоша радіуса `a` (зазвичай `a = 3` або `a = 4` відліки в один бік, всього `2·a` точок):

```
L(x) = sinc(x) · sinc(x / a)   для |x| < a, і 0 для |x| ≥ a
```

Для моменту часу `t` обчислюється дробова позиція `sample_pos = t · fs` та її ціла частина `center_idx = floor(sample_pos)`. Інтерполятор підсумовує `2·a` відліків у діапазоні від `center_idx - a + 1` до `center_idx + a`:

```
x_sinc(t) = ∑ x[i] · L(sample_pos - i) / ∑ L(sample_pos - i)
```

```
Складність: O(a) операцій на кожен відновлений відлік
Операції: 2·a обчислень sinc, 2·a множень та накопичення у суматорі
```

*Крайові випадки:* Поблизу меж масиву (`i < 0` або `i >= N`) відсутні відліки ігноруються, а підсумкова сума ділиться на фактичну суму нормалізуючих вагових коефіцієнтів `weight_sum`. Це запобігає виникненню паразитичних зсувів постійної складової (DC offset) біля країв сигналу.

*Спектральний відгук:* Забезпечує пригнічення дзеркальних образотворчих частот понад `-80...-100 дБ` із мінімальними пульсаціями Гіббса. Віконну `sinc`-інтерполяцію використовують у студійній обробці звуку, генераторах тестових сигналів, SDR-трансиверах та прецизійному цифровому перетворюванні частот.

---

## 2. Реалізація мовами C та C++

У наведеному нижче контейнері `:::tabs` подано паралельні ідіоматичні реалізації трьох методів відновлення сигналу мовами C (C99) та C++ (C++20).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура опису масиву дискретних відліків */
typedef struct {
    const double *data;
    size_t length;
    double sample_rate; /* Частота дискретизації fs (Гц) */
} signal_samples_t;

/* 1. Фіксатор нульового порядку (ZOH / Найближчий сусід) */
double interpolate_zoh(const signal_samples_t *sig, double t) {
    if (t < 0.0) return sig->data[0];
    
    double sample_index = t * sig->sample_rate;
    size_t idx = (size_t)floor(sample_index);
    
    if (idx >= sig->length) {
        return sig->data[sig->length - 1];
    }
    return sig->data[idx];
}

/* 2. Лінійна інтерполяція (FOH) */
double interpolate_linear(const signal_samples_t *sig, double t) {
    if (t <= 0.0) return sig->data[0];
    
    double sample_pos = t * sig->sample_rate;
    size_t idx0 = (size_t)floor(sample_pos);
    size_t idx1 = idx0 + 1;
    
    if (idx1 >= sig->length) {
        return sig->data[sig->length - 1];
    }
    
    double frac = sample_pos - (double)idx0;
    return (1.0 - frac) * sig->data[idx0] + frac * sig->data[idx1];
}

/* Нормована функція sinc(x) = sin(pi*x) / (pi*x) */
static inline double sinc(double x) {
    if (fabs(x) < 1e-9) return 1.0;
    double px = M_PI * x;
    return sin(px) / px;
}

/* Ядро Ланцоша радіуса a */
static inline double lanczos_kernel(double x, int a) {
    if (fabs(x) >= (double)a) return 0.0;
    return sinc(x) * sinc(x / (double)a);
}

/* 3. Віконна Sinc-інтерполяція Ланцоша радіуса a */
double interpolate_sinc_lanczos(const signal_samples_t *sig, double t, int radius) {
    double sample_pos = t * sig->sample_rate;
    long center_idx = (long)floor(sample_pos);
    
    double sum = 0.0;
    double weight_sum = 0.0;
    
    for (long i = center_idx - radius + 1; i <= center_idx + radius; i++) {
        if (i >= 0 && i < (long)sig->length) {
            double dx = sample_pos - (double)i;
            double w = lanczos_kernel(dx, radius);
            sum += sig->data[i] * w;
            weight_sum += w;
        }
    }
    
    /* Нормалізація суми ваг проти коливань постійної складової */
    return (weight_sum > 1e-9) ? (sum / weight_sum) : 0.0;
}

int main(void) {
    /* Синтез тестового сигналу: сума синусоїд 2 Гц та 5 Гц */
    const double fs = 20.0; /* Частота дискретизації 20 Гц */
    const size_t num_samples = 40;
    double samples[40];
    
    for (size_t i = 0; i < num_samples; i++) {
        double t = (double)i / fs;
        samples[i] = sin(2.0 * M_PI * 2.0 * t) + 0.5 * sin(2.0 * M_PI * 5.0 * t);
    }
    
    signal_samples_t sig = { .data = samples, .length = num_samples, .sample_rate = fs };
    
    printf("--- Тестування відновлення сигналу на C у точці t = 0.355 с ---
");
    double test_t = 0.355;
    double true_val = sin(2.0 * M_PI * 2.0 * test_t) + 0.5 * sin(2.0 * M_PI * 5.0 * test_t);
    
    double zoh_val = interpolate_zoh(&sig, test_t);
    double lin_val = interpolate_linear(&sig, test_t);
    double sinc_val = interpolate_sinc_lanczos(&sig, test_t, 4);
    
    printf("Справжнє значення:           %f
", true_val);
    printf("ZOH (ступінь):               %f (похибка: %.6f)
", zoh_val, fabs(zoh_val - true_val));
    printf("FOH (лінійна):               %f (похибка: %.6f)
", lin_val, fabs(lin_val - true_val));
    printf("Sinc-інтерполяція (Ланцош4): %f (похибка: %.6f)
", sinc_val, fabs(sinc_val - true_val));
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <stdexcept>
#include <algorithm>

class SignalReconstructor {
public:
    enum class Method {
        ZeroOrderHold,
        Linear,
        WindowedSincLanczos
    };

    explicit SignalReconstructor(std::vector<double> samples, double sample_rate)
        : m_samples(std::move(samples)), m_sample_rate(sample_rate) {
        if (m_sample_rate <= 0.0) {
            throw std::invalid_argument("Sample rate must be positive");
        }
    }

    [[nodiscard]] double reconstruct_at(double t, Method method = Method::WindowedSincLanczos, int sinc_radius = 4) const {
        if (m_samples.empty()) return 0.0;

        switch (method) {
            case Method::ZeroOrderHold:
                return interpolate_zoh(t);
            case Method::Linear:
                return interpolate_linear(t);
            case Method::WindowedSincLanczos:
                return interpolate_sinc_lanczos(t, sinc_radius);
        }
        return 0.0;
    }

private:
    std::vector<double> m_samples;
    double m_sample_rate;

    [[nodiscard]] static constexpr double sinc(double x) noexcept {
        if (std::abs(x) < 1e-9) return 1.0;
        const double px = std::numbers::pi * x;
        return std::sin(px) / px;
    }

    [[nodiscard]] static double lanczos_kernel(double x, int a) noexcept {
        if (std::abs(x) >= static_cast<double>(a)) return 0.0;
        return sinc(x) * sinc(x / static_cast<double>(a));
    }

    [[nodiscard]] double interpolate_zoh(double t) const noexcept {
        if (t <= 0.0) return m_samples.front();
        const double sample_pos = t * m_sample_rate;
        const auto idx = static_cast<std::size_t>(std::floor(sample_pos));
        if (idx >= m_samples.size()) return m_samples.back();
        return m_samples[idx];
    }

    [[nodiscard]] double interpolate_linear(double t) const noexcept {
        if (t <= 0.0) return m_samples.front();
        const double sample_pos = t * m_sample_rate;
        const auto idx0 = static_cast<std::size_t>(std::floor(sample_pos));
        const std::size_t idx1 = idx0 + 1;

        if (idx1 >= m_samples.size()) return m_samples.back();

        const double frac = sample_pos - static_cast<double>(idx0);
        return (1.0 - frac) * m_samples[idx0] + frac * m_samples[idx1];
    }

    [[nodiscard]] double interpolate_sinc_lanczos(double t, int radius) const noexcept {
        const double sample_pos = t * m_sample_rate;
        const auto center_idx = static_cast<std::ptrdiff_t>(std::floor(sample_pos));
        const auto n_samples = static_cast<std::ptrdiff_t>(m_samples.size());

        double sum = 0.0;
        double weight_sum = 0.0;

        for (std::ptrdiff_t i = center_idx - radius + 1; i <= center_idx + radius; ++i) {
            if (i >= 0 && i < n_samples) {
                const double dx = sample_pos - static_cast<double>(i);
                const double w = lanczos_kernel(dx, radius);
                sum += m_samples[static_cast<std::size_t>(i)] * w;
                weight_sum += w;
            }
        }

        return (weight_sum > 1e-9) ? (sum / weight_sum) : 0.0;
    }
};

int main() {
    constexpr double fs = 20.0;
    constexpr std::size_t num_samples = 40;
    std::vector<double> samples(num_samples);

    for (std::size_t i = 0; i < num_samples; ++i) {
        const double t = static_cast<double>(i) / fs;
        samples[i] = std::sin(2.0 * std::numbers::pi * 2.0 * t) + 0.5 * std::sin(2.0 * std::numbers::pi * 5.0 * t);
    }

    SignalReconstructor reconstructor(std::move(samples), fs);

    constexpr double test_t = 0.355;
    const double true_val = std::sin(2.0 * std::numbers::pi * 2.0 * test_t) + 0.5 * std::sin(2.0 * std::numbers::pi * 5.0 * test_t);

    std::cout << "--- C++ Signal Reconstruction Test at t = " << test_t << " s ---
";
    std::cout << "True value:      " << true_val << "
";
    std::cout << "ZOH value:       " << reconstructor.reconstruct_at(test_t, SignalReconstructor::Method::ZeroOrderHold) << "
";
    std::cout << "Linear value:    " << reconstructor.reconstruct_at(test_t, SignalReconstructor::Method::Linear) << "
";
    std::cout << "Sinc (Lanczos4): " << reconstructor.reconstruct_at(test_t, SignalReconstructor::Method::WindowedSincLanczos, 4) << "
";

    return 0;
}
```
:::

---

## 3. Інженерний аналіз та практична оптимізація DSP

При реалізації відновлення сигналів у реальних DSP-процесорах, FPGA та мікроконтролерах безпосереднє обчислення функцій `sin()` для кожного відліку є занадто дорогим. Для прискорення використовуються такі оптимізації:

### 1. Таблична `sinc`-інтерполяція (Look-Up Table / LUT)
Значення ядра Ланцоша `L(x)` обчислюють заздалегідь із високою роздільністю (наприклад, 256 або 1024 точок на один період `Ts`) і зберігають у константній пам'яті (Flash/ROM). Під час роботи дробовий залишок індексу `frac` використовується як адресний зсув у таблиці, зменшуючи обчислення до прямого читання з пам'яті.

### 2. Поліфазні банківські КІХ-фільтри (Polyphase FIR Filter Bank)
При фіксованому коефіцієнті передискретизації (наприклад, підвищення частоти в 8 разів) інтерполяцію реалізують у вигляді `M` паралельних підфільтрів (поліфазної структури). Кожен підфільтр обчислює свій дробовий зсув за допомогою фіксованого набору КІХ-коефіцієнтів, що дозволяє виконувати фільтрацію за допомогою конвеєрних векторних інструкцій (SIMD / AVX2 / ARM NEON).

### 3. Цілочислова арифметика з фіксованою комою (Fixed-Point Q15 / Q31)
На мікроконтролерах без апаратного блоку плаваючої коми (FPU) відліки сигналу та коефіцієнти `sinc` мастштабують у формат Q15 (16-бітні цілі числа) або Q31 (32-бітні цілі). Множення виконується за один такт процесора за допомогою швидких DSP-інструкцій (наприклад, `SMLABB` або `__SMLAD` у ядрах ARM Cortex-M4/M7).

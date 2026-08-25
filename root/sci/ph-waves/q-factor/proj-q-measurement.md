# ⚙️ Алгоритми та реалізація вимірювання добротності за згасанням і смугою

Ця проектна вставка містить практичні алгоритми та ідіоматичні реалізації мовами C і C++ для обчислення добротності Q за двома основними методами: аналізом експоненційного згасання коливань (*ringdown decay*) та за шириною резонансного піка на рівні половинної потужності (-3 дБ).

## 1. Детальний покроковий аналіз обчислювальних методів

У вимірювальних приладах, діагностиці матеріалів, радіоелектроніці та акустичних випробуваннях застосовують два принципово різні обчислювальні підходи до оцінки добротності `Q`. Кожен з них має власну область застосовності, джерела системних похибок та вимоги до чисельної стійкості.

### Метод 1. Часовий аналіз «дзвону» (Ringdown Decay Analysis)

Коли осцилятор виводять із стану рівноваги коротким імпульсним збудженням (наприклад, удар молоточка по камертону або електричний імпульс у LC-контур) і залишають вільно згасати, амплітуда огинаючої спадає за експоненційним законом:

```
A(t) = A₀ · e^( − (π · f₀ / Q) · t )
```

Зняття добротності безпосередньо за сирими осцилограмами ускладнене наявністю високочастотного осцилювального заповнення. Тому першим кроком обчислювача є виділення огинаючої. Прологарифмуємо обидві частини рівняння огинаючої:

```
ln( A(t) ) = ln(A₀) − ( (π · f₀ / Q) ) · t
```

Це рівняння має вигляд класичної прямої лінії `y = a + b·t` у напівлогарифмічних координатах, де залежною змінною є `y = ln(A(t))`, незалежною змінною — час `t`, а кутовий коефіцієнт нахилу прямої дорівнює:

```
b = − (π · f₀ / Q)
```

**Покроковий алгоритмічний процес:**

1. **Фільтрація та виявлення локальних екстремумів:**
   Для дискретизованого масиву відліків `x[n]` із частотою дискретизації `f_s` виконується пошук строго локальних максимумів (точок, де `x[i] > x[i-1]` та `x[i] > x[i+1]`). Пошук максимуму у цифровому масиві може ускладнюватися високочастотним шумом АЦП, тому у промислових вимірювачах перед шукачем піків часто ставлять цифровий згладжувальний фільтр Савицького-Голея або ковзне середнє.

2. **Відсікання шуму та некоректних відліків:**
   Напруга або амплітуда на хвості дзвону неминуче опускається до рівня власних шумів АЦП чи вимірювального тракту. Додавання шумових відліків до логарифмування призведе до катастрофічного викривлення прямої (логарифм малих чисел прямує до мінус нескінченності). Тому всі піки з амплітудою нижче заданого порогу `noise_floor` відсікаються.

3. **Логарифмування амплітуд:**
   Обчислюються значення `y_k = ln(A_k)` та відповідні моменти часу `t_k = k / f_s`.

4. **Лінійна регресія методом найменших квадратів (МНК / OLS):**
   Обчислюються суми `∑ t_k`, `∑ y_k`, `∑ (t_k²)`, `∑ (t_k · y_k)` та знаходяться параметри регресії `b` (нахил) і `a` (початкова амплітуда):
   ```
   b = ( N·∑(t_k · y_k) − ∑t_k · ∑y_k ) / ( N·∑(t_k²) − (∑t_k)² )
   ```

5. **Оцінка якості апроксимації (Коефіцієнт детермінації R²):**
   Для виключення випадкових завад обчислюється `R²`. Якщо `R² < 0.85`, це означає, що загасання не є чисто експоненційним (наприклад, наявне нелінійне тертя або біполярні биття двох близьких мод), і вимірювання маркується як недостірне.

6. **Фінальний розрахунок добротності:**
   ```
   Q = − (π · f₀) / b
   ```

---

### Метод 2. Спектральний аналіз смуги 3 дБ (3dB Bandwidth Method)

При свіпуванні частоти гармонічним сигналом або при спектральному аналізі відгуку за допомогою швидкого перетворення Фур'є (ШПФ / FFT) будується амплітудно-частотна характеристика `A(f)`.

**Покроковий алгоритмічний процес:**

1. **Пошук піка та резонансної частоти:**
   У масиві амплітуд спектра знаходиться максимум `A_max` на частоті `f₀`. Для запобігання розтіканню спектра (*spectral leakage*) вихідний дискретний сигнал у часовій області попередньо зважується вікном Гіннінґа або Блекмана.

2. **Обчислення порогового рівня половинної потужності:**
   Порогове значення амплітуди дорівнює:
   ```
   A_3db = A_max / √2 ≈ 0.70710678 · A_max
   ```

3. **Субпіксельна інтерполяція частот зрізу f₁ та f₂:**
   Оскільки сітка частот FFT або свіпування має скінченний крок `Δf_bin`, точки перетину з порогом `A_3db` майже ніколи не потрапляють точно на дискретний відлік. Для підвищення точності застосовується лінійна або квадратична інтерполяція між сусідніми відліками:
   ```
   f_cut = f_left + (A_3db − A_left) · (f_right − f_left) / (A_right − A_left)
   ```

4. **Обчислення підсумкової добротності:**
   ```
   Q = f₀ / (f₂ − f₁)
   ```

---

## 2. Оптимізація обчислень та практичні рекомендації з калібрування

Під час практичної реалізації вимірювача добротності у вбудованому ПЗ або лабораторних вимірювальних комплексах необхідно враховувати три основні чисельні фактори:

### 1. Вибір частоти дискретизації АЦП (`f_s`)
Для точного виділення піків огинаючої метода Ringdown частота дискретизації `f_s` повинна перевищувати резонансну частоту принаймні у 8–10 разів (`f_s >= 10 f₀`). При менших частотах (близьких до межі Найквіста `2 f₀`) дискретний максимум АЦП відхилятиметься від реального максимуму синусоїди на різний фазовий кут, створюючи хибні флуктуації амплітуди.

### 2. Попередня обробка та видалення постійної складової (DC Offset)
Будь-який постійний зсув нуля в аналоговому тракті `V_dc` перетворить експоненту `A e^(−α t)` на `A e^(−α t) + V_dc`. При прологарифмуванні це призводить до викривлення прямої на хвості спаду. Перед початком МНК-регресії обов'язково віднімається математичне сподівання сигналу: `x[n] = raw[n] − mean(raw)`.

### 3. Робота з високими добротностями (`Q > 10 000`)
Для високодобротних резонаторів (кварц, MEMS у вакуумі) часова тривалість спаду вимагає збереження масивів з мільйонами відліків. У такому разі вимірювач не зберігає всі відліки в оперативну пам'ять, а обробляє сигнал «на льоту» у потоковому режимі, вираховуючи суми для МНК-регресії в режимі реального часу.

---

## 3. Повна кодова реалізація вимірювача добротності (C та C++)

Нижче наведено повністю працездатні реалізації обох алгоритмів. Версія мовою C строго дотримується стандарту C99, використовує пряму передачу масивів та покажчиків і не вимагає динамічного виділення пам'яті в купі (heap). Вона ідеально підходить для вбудованих мікроконтролерів (STM32, ESP32, AVR). Версія мовою C++ написана за сучасним стандартом C++20, спирається на `std::span`, `std::vector`, `std::optional` для безпечної обробки помилок без винятків та математичні константи з `<numbers>`.

:::tabs
```c
/* q_measurement.h — C-бібліотека обчислення добротності */
#ifndef Q_MEASUREMENT_H
#define Q_MEASUREMENT_H

#include <stddef.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double q_factor;
    double r_squared;      /* Коефіцієнт детермінації R² для оцінки якості апроксимації */
    double initial_amp;
    bool valid;
} q_ringdown_result_t;

typedef struct {
    double q_factor;
    double f0_hz;
    double bandwidth_hz;
    bool valid;
} q_bandwidth_result_t;

/* Обчислення Q методом МНК-регресії логарифма огинаючої спаду */
q_ringdown_result_t measure_q_ringdown(
    const double *samples, 
    size_t count, 
    double sample_rate_hz, 
    double f0_hz,
    double noise_floor
) {
    q_ringdown_result_t res = {0.0, 0.0, 0.0, false};
    if (!samples || count < 10 || sample_rate_hz <= 0.0 || f0_hz <= 0.0) {
        return res;
    }

    /* Знаходження локальних піків */
    size_t peak_count = 0;
    double sum_t = 0.0, sum_y = 0.0, sum_tt = 0.0, sum_ty = 0.0;

    for (size_t i = 1; i < count - 1; ++i) {
        if (samples[i] > samples[i - 1] && samples[i] > samples[i + 1] && samples[i] > noise_floor) {
            double t = (double)i / sample_rate_hz;
            double y = log(samples[i]);

            sum_t += t;
            sum_y += y;
            sum_tt += t * t;
            sum_ty += t * y;
            peak_count++;
        }
    }

    if (peak_count < 3) {
        return res; /* Занадто мало піків для регресії */
    }

    double n = (double)peak_count;
    double denom = (n * sum_tt - sum_t * sum_t);
    if (fabs(denom) < 1e-12) {
        return res;
    }

    double slope = (n * sum_ty - sum_t * sum_y) / denom;
    double intercept = (sum_y - slope * sum_t) / n;

    if (slope >= 0.0) {
        return res; /* Нахил має бути від'ємним для загасання */
    }

    /* Обчислення R² */
    double mean_y = sum_y / n;
    double ss_tot = 0.0, ss_res = 0.0;

    for (size_t i = 1; i < count - 1; ++i) {
        if (samples[i] > samples[i - 1] && samples[i] > samples[i + 1] && samples[i] > noise_floor) {
            double t = (double)i / sample_rate_hz;
            double y = log(samples[i]);
            double y_pred = intercept + slope * t;
            ss_tot += (y - mean_y) * (y - mean_y);
            ss_res += (y - y_pred) * (y - y_pred);
        }
    }

    res.q_factor = -(M_PI * f0_hz) / slope;
    res.initial_amp = exp(intercept);
    res.r_squared = (ss_tot > 0.0) ? (1.0 - (ss_res / ss_tot)) : 0.0;
    res.valid = (res.r_squared > 0.85);

    return res;
}

/* Обчислення Q за спектром методом -3 дБ */
q_bandwidth_result_t measure_q_bandwidth(
    const double *spectrum_amp, 
    const double *freqs_hz, 
    size_t count
) {
    q_bandwidth_result_t res = {0.0, 0.0, 0.0, false};
    if (!spectrum_amp || !freqs_hz || count < 5) {
        return res;
    }

    /* Пошук максимуму */
    size_t max_idx = 0;
    double max_amp = spectrum_amp[0];
    for (size_t i = 1; i < count; ++i) {
        if (spectrum_amp[i] > max_amp) {
            max_amp = spectrum_amp[i];
            max_idx = i;
        }
    }

    if (max_amp <= 0.0 || max_idx == 0 || max_idx == count - 1) {
        return res;
    }

    double target_amp = max_amp / sqrt(2.0);

    /* Ліва точка f1 */
    double f1 = freqs_hz[0];
    for (size_t i = max_idx; i > 0; --i) {
        if (spectrum_amp[i - 1] <= target_amp) {
            double a1 = spectrum_amp[i - 1];
            double a2 = spectrum_amp[i];
            double f_left = freqs_hz[i - 1];
            double f_right = freqs_hz[i];
            f1 = f_left + (target_amp - a1) * (f_right - f_left) / (a2 - a1);
            break;
        }
    }

    /* Права точка f2 */
    double f2 = freqs_hz[count - 1];
    for (size_t i = max_idx; i < count - 1; ++i) {
        if (spectrum_amp[i + 1] <= target_amp) {
            double a1 = spectrum_amp[i];
            double a2 = spectrum_amp[i + 1];
            double f_left = freqs_hz[i];
            double f_right = freqs_hz[i + 1];
            f2 = f_left + (target_amp - a1) * (f_right - f_left) / (a2 - a1);
            break;
        }
    }

    double bw = f2 - f1;
    if (bw <= 0.0) {
        return res;
    }

    res.f0_hz = freqs_hz[max_idx];
    res.bandwidth_hz = bw;
    res.q_factor = res.f0_hz / bw;
    res.valid = true;

    return res;
}
#endif
```
```cpp
// q_measurement.hpp — Ідіоматична C++20 реалізація
#pragma once

#include <vector>
#include <span>
#include <optional>
#include <cmath>
#include <numeric>
#include <numbers>
#include <algorithm>

namespace physics::oscillations {

struct RingdownResult {
    double q_factor{0.0};
    double r_squared{0.0};
    double initial_amplitude{0.0};
};

struct BandwidthResult {
    double q_factor{0.0};
    double f0_hz{0.0};
    double bandwidth_hz{0.0};
};

class QMeter {
public:
    static std::optional<RingdownResult> measureRingdown(
        std::span<const double> samples,
        double sample_rate_hz,
        double f0_hz,
        double noise_floor = 1e-4
    ) {
        if (samples.size() < 10 || sample_rate_hz <= 0.0 || f0_hz <= 0.0) {
            return std::nullopt;
        }

        struct Peak { double time; double log_amp; };
        std::vector<Peak> peaks;
        peaks.reserve(samples.size() / 10);

        for (size_t i = 1; i < samples.size() - 1; ++i) {
            if (samples[i] > samples[i - 1] && samples[i] > samples[i + 1] && samples[i] > noise_floor) {
                double t = static_cast<double>(i) / sample_rate_hz;
                peaks.push_back({t, std::log(samples[i])});
            }
        }

        if (peaks.size() < 3) {
            return std::nullopt;
        }

        double n = static_cast<double>(peaks.size());
        double sum_t = 0.0, sum_y = 0.0, sum_tt = 0.0, sum_ty = 0.0;

        for (const auto& p : peaks) {
            sum_t += p.time;
            sum_y += p.log_amp;
            sum_tt += p.time * p.time;
            sum_ty += p.log_amp * p.time;
        }

        double denom = n * sum_tt - sum_t * sum_t;
        if (std::abs(denom) < 1e-12) {
            return std::nullopt;
        }

        double slope = (n * sum_ty - sum_t * sum_y) / denom;
        double intercept = (sum_y - slope * sum_t) / n;

        if (slope >= 0.0) {
            return std::nullopt;
        }

        double mean_y = sum_y / n;
        double ss_tot = 0.0, ss_res = 0.0;
        for (const auto& p : peaks) {
            double y_pred = intercept + slope * p.time;
            ss_tot += (p.log_amp - mean_y) * (p.log_amp - mean_y);
            ss_res += (p.log_amp - y_pred) * (p.log_amp - y_pred);
        }

        double r_sq = (ss_tot > 0.0) ? (1.0 - (ss_res / ss_tot)) : 0.0;
        if (r_sq < 0.80) {
            return std::nullopt;
        }

        return RingdownResult{
            .q_factor = -(std::numbers::pi * f0_hz) / slope,
            .r_squared = r_sq,
            .initial_amplitude = std::exp(intercept)
        };
    }

    static std::optional<BandwidthResult> measure3dB(
        std::span<const double> spectrum_amp,
        std::span<const double> freqs_hz
    ) {
        if (spectrum_amp.size() != freqs_hz.size() || spectrum_amp.size() < 5) {
            return std::nullopt;
        }

        auto max_it = std::max_element(spectrum_amp.begin(), spectrum_amp.end());
        size_t max_idx = std::distance(spectrum_amp.begin(), max_it);
        double max_amp = *max_it;

        if (max_amp <= 0.0 || max_idx == 0 || max_idx == spectrum_amp.size() - 1) {
            return std::nullopt;
        }

        double target_amp = max_amp / std::numbers::sqrt2;

        double f1 = freqs_hz.front();
        for (size_t i = max_idx; i > 0; --i) {
            if (spectrum_amp[i - 1] <= target_amp) {
                double a1 = spectrum_amp[i - 1], a2 = spectrum_amp[i];
                f1 = freqs_hz[i - 1] + (target_amp - a1) * (freqs_hz[i] - freqs_hz[i - 1]) / (a2 - a1);
                break;
            }
        }

        double f2 = freqs_hz.back();
        for (size_t i = max_idx; i < spectrum_amp.size() - 1; ++i) {
            if (spectrum_amp[i + 1] <= target_amp) {
                double a1 = spectrum_amp[i], a2 = spectrum_amp[i + 1];
                f2 = freqs_hz[i] + (target_amp - a1) * (freqs_hz[i + 1] - freqs_hz[i]) / (a2 - a1);
                break;
            }
        }

        double bw = f2 - f1;
        if (bw <= 0.0) {
            return std::nullopt;
        }

        return BandwidthResult{
            .q_factor = freqs_hz[max_idx] / bw,
            .f0_hz = freqs_hz[max_idx],
            .bandwidth_hz = bw
        };
    }
};

} // namespace physics::oscillations
```
:::

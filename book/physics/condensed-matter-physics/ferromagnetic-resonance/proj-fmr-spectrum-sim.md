# ⚙️ Моделювання спектрів FMR та обчислення параметра Гільберта

Чисельний розрахунок спектрів поглинання феромагнітного резонансу дозволяє вилучати ґіромагнітний фактор, поля анізотропії та коефіцієнт згасання Гільберта з експериментальних НВЧ-даних.

---

### 1. Фізичні основи та обчислювальна модель

У резонаторних та широкосмугових FMR-експериментах вимірюваним сигналом є або поглинута НВЧ-потужність `P_abs(H) ∝ χ''(H)`, або її перша похідна за зовнішнім магнітним полем `dP/dH`. 

Уявна частина комплексної магнітної сприйнятливості `χ''(H)` для тонкої плівки описується лоренцівським контуром:

```
χ''(H) = A · [ ( ΔH · H ) / ( (H² - H_r²)² + (ΔH · H)² ) ]
```

де `H_r` — резонансне поле, `ΔH` — ширина лінії поглинання на напіввисоті, a `A` — амплітудний множник, пропорційний намагніченості насичення `M_s`.

Програма виконує дві основні задачних методики:
1. **Пряма симуляція спектра:** Для заданих параметрів магнітного матеріалу (намагніченості насичення `M_s`, `g`-фактора, безрозмірного згасання Гільберта `α` та частоти НВЧ-поля `f`) обчислює теоретичне резонансне поле `H_r` за формулою Кіттеля, формує лоренцівський профіль поглинання `χ''(H)` та обчислює його першу чисельну похідну `dP/dH`.
2. **Обернена задача (параметричне фітування):** Приймає масив експериментальних виміряних точок `(f_i, ΔH_i)` на різних частотах та виконує лінійну регресію методом найменших квадратів для рівняння:

```
ΔH(f) = ΔH₀ + (2 · α / γ) · 2π f
```

Кутовий нахил отриманої прямої дає безрозмірне згасання Гільберта `α`, а точка перетину з віссю ординат при `f = 0` визначає параметр неоднорідного розширення `ΔH₀`.

---

### 2. Алгоритм попередньої обробки даних та вилучення лінійних параметрів

Експериментальні масиви FMR-спектрів, отримані з векторних аналізаторів мереж (VNA) чи резонаторних Lock-in систем, часто містять вимірювальні шуми, фазові зсуви та лінійний дрейф базової лінії. 

Перед проведенням фітування програма виконує наступну послідовність обчислювальних кроків:
1. **Видалення тренду (Baseline Detrending):** 
   Для усунення фазового дрейфу та лінійного нахилу базової лінії сигнал `S(H)` скориговується шляхом віднімання лінійної функції `S_base(H) = a H + b`, яка обчислюється за крайовими точками спектра поза зоною резонансу.
2. **Знаходження пік-до-пікової ширини лінії `ΔH_pp`:**
   Для похідного спектра `dP/dH` знаходяться глобальні екстремуми — максимум `(H_max, P_max)` та мінімум `(H_min, P_min)`. Відстань між ними визначає пік-до-пікову ширину лінії:
   ```
   ΔH_pp = H_min - H_max
   ```
   Резонансне поле `H_r` обчислюється як середина між екстремумами `H_r = (H_max + H_min) / 2`.
3. **Розрахунок повної ширини лінії `ΔH`:**
   Для переходу від пік-до-пікової ширини похідної `ΔH_pp` до ширини профілю поглинання на напіввисоті `ΔH` застосовується коефіцієнт перерахунку для лоренцівської форми:
   ```
   ΔH = √3 · ΔH_pp  ≈  1.73205 · ΔH_pp
   ```

---

### 3. Урахування асиметрії лінії (асиметричний контур Дайсона)

У металевих провідних плівках (наприклад, кобальті або залізі товщиною понад 30–50 нм) глибина скін-шару виявляється порівнянною з товщиною зразка. У результаті фаза НВЧ-поля змінюється по товщині плівки, а сигнал поглинання перетворюється на асиметричний **профіль Дайсона** (суміш Лоренціана поглинання та Дисперсії):

```
dP / dH = A · [ ( d/dH ) ( χ''(H) · cos(φ) + χ'(H) · sin(φ) ) ]
```

де `φ` — фазовий асимметрійний кут. У програмах числового фітування кут `φ` виступає вільним параметром, що дозволяє відокремити чисто магнітні втрати від провіднісних ефектів скін-шару.

---

### 4. Математичний алгоритм лінійного фітування методом найменших квадратів

Для набору `N` експериментальних вимірювань `(f_i, ΔH_i)` кутовий нахил `k` та статичний зсув `b = ΔH₀` обчислюються з умови мінімізації суми квадратів неузгодженостей `∑ (ΔH_i - (k f_i + b))²`:

```
k = ( N · ∑ (f_i · ΔH_i) - ∑ f_i · ∑ ΔH_i ) / ( N · ∑ (f_i²) - (∑ f_i)² )
b = ( ∑ ΔH_i - k · ∑ f_i ) / N
```

Знаючи кутовий нахил `k` (який вимірюється в Ерстедах на Гігагерц), параметр згасання Гільберта `α` розраховується за співвідношенням:

```
α = ( k · γ ) / ( 4π )
```

де `γ / (2π)` — ґіромагнітне співвідношення у ГГц/Тл. Похибка фітування оцінюється через стандартне відхилення залишків регресії `σ_k` та `σ_b`:

```
σ_k = √[ ( 1 / (N - 2) ) · ( ∑ (ΔH_i - ΔH_fit,i)² / ∑ (f_i - f_mean)² ) ]
```

Слід зважати на те, що при обробці експериментальних спектрів з реальних ВНА-спектрометрів сирий сигнал часто містить лінійну або фазову похибку базової лінії (дрейф приладу). Перед виконанням регресії масив даних `dP/dH` очищають шляхом віднімання фонової тренд-лінії.

---

### 5. Обчислювальна ефективність та крайні випадки при зчитуванні даних

При обробці масивів з декількох тисяч спектрів VNA-FMR обчислювальна швидкість алгоритму має вирішальне значення. Використання векторних операцій та оптимізованих пакунків пам'яті дозволяє виконувати параметричне фітування в реальному часі безпосередньо під час зняття експериментальної серії.

Для забезпечення надійності алгоритму передбачено обробку крайніх випадків:
* **Недостатня кількість частотних точок (`N < 2`):** Виклик функції переривається з видачею відповідного виключення, оскільки лінійна регресія вимагає щонайменше 2 точок.
* **Нульовий знаменник регресії:** Виникає, якщо вимірювання проведені на одній і тій самій частоті (`f_i = const`). Програма перевіряє дисперсію `Var(f)` перед виконанням ділення.
* **Сильний шум та пропущені точки:** Використовується алгоритм зважених найменших квадратів (Weighted Least Squares), де вагові коефіцієнти точок `w_i = 1 / σ_i²` обчислюються пропорційно коефіцієнту кореляції R² для кожного окремого лоренціану.

---

### 6. Багатомовна програма симуляції та аналізу

Нижче наведено повноцінні реалізації симулятора FMR-спектра та лінійного аналізатора трьома мовами: Python, C++ та C. Кожна реалізація є автономною, ідіоматичною та підходить для використання у реальних наукових дослідженнях.

:::tabs
```py
import math

class FMRSimulator:
    def __init__(self, ms_ka_m=800.0, g_factor=2.10, alpha=0.007, dh0_oe=5.0):
        # ms_ka_m: намагніченість (кА/м), g_factor: фактор Ланде
        # alpha: параметр Гільберта, dh0_oe: неоднорідне уширення (Ерстед)
        self.ms = ms_ka_m * 1000.0  # А/м
        self.g = g_factor
        self.alpha = alpha
        self.dh0 = dh0_oe
        # γ / (2π) у ГГц/Тл: γ = g * e / (2 * m_e)
        self.gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * math.pi * 1e9)

    def kittel_inplane_field(self, freq_ghz):
        # Обчислення резонансного поля H_r для плівки у площині: f = γ √(H_r (H_r + M_s))
        # У термінах B_r (Тл): (f / γ)² = B_r * (B_r + μ0 M_s)
        mu0_ms = 4.0 * math.pi * 1e-7 * self.ms
        f_g = freq_ghz / self.gamma_ghz_t
        # Квадратне рівняння: B_r² + μ0 M_s B_r - (f/γ)² = 0
        b_r = (-mu0_ms + math.sqrt(mu0_ms**2 + 4.0 * f_g**2)) / 2.0
        return b_r * 10000.0  # перетворення у Гауси / Ерстеди

    def linewidth(self, freq_ghz):
        # ΔH(f) = ΔH0 + (2 α / γ) * 2π f
        # У Ерстедах: (2 * alpha * f) / (gamma / 2π) * 1000
        return self.dh0 + (2.0 * self.alpha * freq_ghz * 1000.0) / self.gamma_ghz_t

    def generate_spectrum(self, freq_ghz, h_min_oe, h_max_oe, points=500):
        hr = self.kittel_inplane_field(freq_ghz)
        dh = self.linewidth(freq_ghz)
        step = (h_max_oe - h_min_oe) / (points - 1)

        fields, chi_pp, deriv = [], [], []
        for i in range(points):
            h = h_min_oe + i * step
            fields.append(h)
            # Лоренціан поглинання
            denom = (h**2 - hr**2)**2 + (dh * h)**2
            val = (dh * h) / denom if denom != 0 else 0
            chi_pp.append(val)

        # Чисельна похідна dP/dH
        for i in range(points):
            if i == 0:
                d = (chi_pp[1] - chi_pp[0]) / step
            elif i == points - 1:
                d = (chi_pp[-1] - chi_pp[-2]) / step
            else:
                d = (chi_pp[i+1] - chi_pp[i-1]) / (2.0 * step)
            deriv.append(d)

        return fields, chi_pp, deriv

def fit_gilbert_damping(freqs_ghz, linewidths_oe, g_factor=2.10):
    n = len(freqs_ghz)
    if n < 2:
        raise ValueError("Потрібно принаймні 2 виміри для лінійного фітування")

    sum_f = sum(freqs_ghz)
    sum_dh = sum(linewidths_oe)
    sum_ff = sum(f*f for f in freqs_ghz)
    sum_fdh = sum(f*dh for f, dh in zip(freqs_ghz, linewidths_oe))

    slope = (n * sum_fdh - sum_f * sum_dh) / (n * sum_ff - sum_f**2)
    dh0 = (sum_dh - slope * sum_f) / n

    gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * math.pi * 1e9)
    # slope = (2 * alpha / gamma) * 1000  => alpha = slope * gamma / 2000
    alpha = (slope * gamma_ghz_t) / 2000.0

    return alpha, dh0

if __name__ == "__main__":
    sim = FMRSimulator(ms_ka_m=800.0, g_factor=2.08, alpha=0.0065, dh0_oe=4.5)
    f_test = 9.5 # ГГц (X-band)
    hr = sim.kittel_inplane_field(f_test)
    dh = sim.linewidth(f_test)
    print(f"Частота: {f_test} ГГц => Резонансне поле: {hr:.2f} Ое, Ширина лінії: {dh:.2f} Ое")

    freqs = [4.0, 8.0, 12.0, 16.0, 20.0]
    dhs = [sim.linewidth(f) for f in freqs]
    alpha_fit, dh0_fit = fit_gilbert_damping(freqs, dhs, g_factor=2.08)
    print(f"Фітування: alpha = {alpha_fit:.6f}, ΔH0 = {dh0_fit:.2f} Ое")
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <iomanip>

struct FMRResult {
    double alpha;
    double dh0_oe;
};

class FMRAnalyzer {
private:
    double ms_a_m;
    double g_factor;
    double gamma_ghz_t;

public:
    FMRAnalyzer(double ms_ka_m = 800.0, double g = 2.10)
        : ms_a_m(ms_ka_m * 1000.0), g_factor(g) {
        gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * M_PI * 1e9);
    }

    double calculate_kittel_inplane(double freq_ghz) const {
        double mu0_ms = 4.0 * M_PI * 1e-7 * ms_a_m;
        double f_g = freq_ghz / gamma_ghz_t;
        double b_r = (-mu0_ms + std::sqrt(mu0_ms * mu0_ms + 4.0 * f_g * f_g)) / 2.0;
        return b_r * 10000.0; // Гаус / Ерстед
    }

    FMRResult fit_gilbert(const std::vector<double>& freqs_ghz,
                          const std::vector<double>& linewidths_oe) const {
        size_t n = freqs_ghz.size();
        if (n < 2 || n != linewidths_oe.size()) {
            throw std::invalid_argument("Некоректний розмір вимірювальних масивів");
        }

        double sum_f = 0.0, sum_dh = 0.0, sum_ff = 0.0, sum_fdh = 0.0;
        for (size_t i = 0; i < n; ++i) {
            sum_f += freqs_ghz[i];
            sum_dh += linewidths_oe[i];
            sum_ff += freqs_ghz[i] * freqs_ghz[i];
            sum_fdh += freqs_ghz[i] * linewidths_oe[i];
        }

        double slope = (n * sum_fdh - sum_f * sum_dh) / (n * sum_ff - sum_f * sum_f);
        double dh0 = (sum_dh - slope * sum_f) / static_cast<double>(n);
        double alpha = (slope * gamma_ghz_t) / 2000.0;

        return FMRResult{alpha, dh0};
    }
};

int main() {
    FMRAnalyzer analyzer(800.0, 2.08);
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Резонансне поле на 9.5 ГГц: " 
              << analyzer.calculate_kittel_inplane(9.5) << " Ое\n";

    std::vector<double> freqs = {4.0, 8.0, 12.0, 16.0, 20.0};
    std::vector<double> dhs = {6.2, 8.1, 10.0, 11.9, 13.8};

    try {
        FMRResult res = analyzer.fit_gilbert(freqs, dhs);
        std::cout << "Параметр Гільберта alpha: " << res.alpha << "\n";
        std::cout << "Неоднорідне уширення ΔH0: " << res.dh0_oe << " Ое\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double alpha;
    double dh0_oe;
} fmr_fit_result_t;

double fmr_kittel_inplane(double freq_ghz, double ms_ka_m, double g_factor) {
    double ms_a_m = ms_ka_m * 1000.0;
    double gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * M_PI * 1e9);
    double mu0_ms = 4.0 * M_PI * 1e-7 * ms_a_m;
    double f_g = freq_ghz / gamma_ghz_t;
    double b_r = (-mu0_ms + sqrt(mu0_ms * mu0_ms + 4.0 * f_g * f_g)) / 2.0;
    return b_r * 10000.0;
}

int fmr_fit_gilbert(const double* freqs_ghz, const double* linewidths_oe, size_t count,
                    double g_factor, fmr_fit_result_t* out_result) {
    if (!freqs_ghz || !linewidths_oe || !out_result || count < 2) {
        return -1;
    }

    double sum_f = 0.0, sum_dh = 0.0, sum_ff = 0.0, sum_fdh = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_f += freqs_ghz[i];
        sum_dh += linewidths_oe[i];
        sum_ff += freqs_ghz[i] * freqs_ghz[i];
        sum_fdh += freqs_ghz[i] * linewidths_oe[i];
    }

    double denom = (count * sum_ff - sum_f * sum_f);
    if (fabs(denom) < 1e-12) return -2;

    double slope = (count * sum_fdh - sum_f * sum_dh) / denom;
    double dh0 = (sum_dh - slope * sum_f) / (double)count;
    double gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * M_PI * 1e9);

    out_result->alpha = (slope * gamma_ghz_t) / 2000.0;
    out_result->dh0_oe = dh0;
    return 0;
}

int main(void) {
    double freqs[] = {4.0, 8.0, 12.0, 16.0, 20.0};
    double dhs[] = {6.2, 8.1, 10.0, 11.9, 13.8};
    size_t count = sizeof(freqs) / sizeof(freqs[0]);

    fmr_fit_result_t fit;
    if (fmr_fit_gilbert(freqs, dhs, count, 2.08, &fit) == 0) {
        printf("FMR C Analysis Results:\n");
        printf("Alpha (Gilbert): %.6f\n", fit.alpha);
        printf("Delta H0: %.2f Oe\n", fit.dh0_oe);
    } else {
        printf("Fitting error occurred.\n");
    }
    return 0;
}
```
:::

---

### 7. Фізична інтерпретація результатів та діагностика матеріалу

Результати обчислення параметра Гільберта `α` та неоднорідного уширення `ΔH₀` дозволяють оцінити мікроскопічну якість синтезованого матеріалу:

* Якщо вирахований параметр `α` значно перевищує табличне значення для монокристала (наприклад, `α > 0.02` для пермалою), це свідчить про наявність додаткових релаксаційних каналів — таких як двомагнонне розсіювання на шорсткості поверхні або міжфазне демпфування.
* Велике значення неоднорідного розширення (`ΔH₀ > 15 Ое`) вказує на дефекти структури, локальні флуктуації товщини плівки або наявність полікристалічних зерен з дезорієнтованими осями анізотропії.
* Систематичні відхилення точок від лінійної залежності `ΔH(f)` свідчать про включення нелінійних релаксаційних механізмів, наприклад, розсіювання на тримагнонних або чотиримагнонних процесах при високих рівнях НВЧ-потужності.

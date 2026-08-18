# ⚙️ Алгоритм розрахунку втрат у сердечнику для синусоїдального та PWM сигналів

У цій вставці наведено практичний алгоритм чисельного розрахунку питомих та сумарних втрат у магнітному сердечнику за класичним рівнянням Штейнмеця (OSE) та розширеним покращеним рівнянням (iSE). Подано розбір інженерної методики, опис крайових випадків при дискретизації виміряних осцилограм, аналітичний розкрив параметрів для трикутних сигналів, рекомендації щодо векторної оптимізації обчислень, а також реалізації алгоритму трьома мовами програмування: C, C++20 та Python.

---

## 1. Інженерна постановка задачі чисельного розрахунку

У сучасній силовій електроніці форми напруги та струму у магнітних компонентах рідко бувають чисто синусоїдальними. У мостових інверторах, Buck/Boost перетворювачах та резонансних LLC-контурах магнітна індукція `B(t)` має складну трапецеподібну, пилоподібну або piecewise-лінійну форму з крутими фронтами та паузами ("мертвим часом").

Для обчислення втрат у таких умовах аналітичні формули стають занадто громіздкими, тому інженери застосовують чисельне інтегрування масивів вибірок `B[i]`, отриманих із симуляторів схемотехніки (LTspice, PLECS, PSIM) або зацифрованих осцилограм з реального осцилографа.

### Кроки чисельного алгоритму iSE:
1. **Зчитування вибірок:** Масив вибірок магнітної індукції `B[i]` розміром `N` за один повний період `T`.
2. **Знаходження розмаху індукції `ΔB`:** Обчислення різниці між максимальним та мінімальним значенням у масиві: `ΔB = B_max - B_min`.
3. **Чисельне диференціювання:** Розрахунок миттєвої швидкості зміни індукції `dB/dt` на кожному інтервалі дискретизації `dt = T / (N - 1)` за допомогою різницевої схеми першого порядку:
   ```
   (dB / dt)[i] = (B[i + 1] - B[i]) / dt
   ```
4. **Чисельне інтегрування:** Накопичення суми миттєвих втрат, піднесених до ступеня `α`:
   ```
   Integral = ∑ ( |(dB/dt)[i]|^α · dt )
   ```
5. **Обчислення коефіцієнта матеріалу `k_i`:** Розрахунок модифікованого коефіцієнта за Бета-функцією Ейлера із паспортних параметрів Штейнмеця `(k, α, β)`.
6. **Остаточний розрахунок `P_v`:** Множення накопиченого інтеграла на `k_i` та на фактор розмаху `ΔB^(β - α)`.

---

## 2. Аналітичний розрахунок для PWM трикутних сигналів

Для найбільш поширеного випадку силової електроніки — трикутної індукції `B(t)` у дроселі Buck/Boost перетворювача з коефіцієнтом заповнення `D` (де робочий хід триває `t_on = D · T`, а зворотний хід `t_off = (1 - D) · T`) — числове інтегрування iSE можна виконати в аналітичному вигляді.

На інтервалі робочого ходу `t_on` швидкість зміни індукції є постійною:
```
(dB / dt)_on = ΔB / (D · T)
```

На інтервалі зворотного ходу `t_off`:
```
(dB / dt)_off = - ΔB / ((1 - D) · T)
```

Підставляючи ці швидкості в інтеграл iSE:
```
∫₀ᵀ |dB/dt|^α dt = [ (ΔB / (D · T))^α · D · T ] + [ (ΔB / ((1 - D) · T))^α · (1 - D) · T ]
                 = (ΔB / T)^α · T · [ (1 / D^(α - 1)) + (1 / (1 - D)^(α - 1)) ]
```

Поділивши на період `T` та підставивши частоту `f = 1/T`, отримуємо аналітичну формулу питомих втрат iSE для трикутного PWM сигналу:

```
P_v_PWM = k_i · f^α · ΔB^β · [ (1 / D^(α - 1)) + (1 / (1 - D)^(α - 1)) ]
```

Ця формула чітко показує:
- При симетричному PWM (`D = 0.5`) вираз у дужках набуває мінімального значення `2^α`.
- При сильному відхиленні коефіцієнта заповнення від 0.5 (наприклад, при `D = 0.05` або `D = 0.95` у високовольтних перетворювачах) сума у дужках стрімко зростає, і втрати в сердечнику збільшуються у 2–4 рази при тому самому розмаху індукції `ΔB`.

---

## 3. Крайові випадки, шуми осцилограм та обробка даних

При практичній реалізації чисельного розрахунку на даних із цифрових осцилографів виникають наступні важливі інженерні нюанси:

- **Дискретизаційний шум вимірювань:** Високочастотний шум осцилографа при чисельному диференціюванні створить хибні гігантські сплески `dB/dt`. Для запобігання цьому масив вибірок `B[i]` перед розрахунком iSE піддають цифровому згладжуванню фільтром Савицького — Ґолея або низькочастотним фільтром Баттерворта.
- **Вибір кроку дискретизації `dt`:** Кількість точок на період `N` має бути достатньо великою, щоб точно передати круті фронти перемикання транзисторів. Для імпульсних сигналів з часом наростання `t_r = 20 нс` на частоті `100 кГц` рекомендовано використовувати не менше `1000–2000` вибірок на період.
- **Нульовий розмах (`ΔB = 0`):** Якщо сигнал відсутній або індукція стала, формула iSE містить невизначеність. Код повинен явним чином перевіряти умову `ΔB > 0` і повертати `0.0`.
- **Обробка пауз (`dB/dt = 0`):** Під час інтервалів із постійною індукцією похідна дорівнює нулю. Алгоритм не повинен накопичувати хибних значень у суму інтеграла.

---

## 4. Продуктивність та SIMD-векторизація

При виконанні оптимізаційного перебору сотень варіантів сердечників у САПР (наприклад, при розрахунку термодинаміки в реальному часі на серверах симуляцій) обчислення степеня `pow(fabs(db_dt), alpha)` у циклі з мільйонами точок може стати обчислювальним вузьким місцем.

Для прискорення розрахунків у високопродуктивних бібліотеках C++ застосовують:
1. **Табуляцію та підгонку:** Заміну піднесення до дробового ступеня `pow(x, α)` на локальну аппроксимацію поліномами Чебишова або виклики SIMD-інструкцій (AVX-512 / ARM NEON `vpowq_f32`).
2. **Паралельне інтегрування OpenMP:** Розпаралелювання розрахунку iSE для декількох обмоток та різних періодів по незалежних потоках CPU, оскільки обчислення для кожного періоду є повністю незалежним.

---

## 5. Програмна реалізація алгоритму

:::tabs
```c
/* Steinmetz Core Loss Calculator (C implementation) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double k;     /* Коефіцієнт Штейнмеця (для f в Гц, B у Тл) */
    double alpha; /* Експонента по частоті */
    double beta;  /* Експонента по індукції */
} SteinmetzParams;

/* Обчислення Бета-функції B(x, y) = Gamma(x)*Gamma(y)/Gamma(x+y) */
static double beta_func(double x, double y) {
    return (tgamma(x) * tgamma(y)) / tgamma(x + y);
}

/* Обчислення коефіцієнта k_i для iSE */
double calculate_k_i(const SteinmetzParams *p) {
    double term1 = pow(2.0 * M_PI, p->alpha - 1.0);
    double term2 = pow(2.0, p->beta - p->alpha + 1.0);
    double beta_val = beta_func((p->alpha + 1.0) / 2.0, 0.5);
    
    return p->k / (term1 * term2 * beta_val);
}

/* Розрахунок втрат OSE для синусоїди: P_v = k * f^alpha * B_m^beta */
double calculate_ose_loss(const SteinmetzParams *p, double freq_hz, double b_peak_tesla) {
    return p->k * pow(freq_hz, p->alpha) * pow(b_peak_tesla, p->beta);
}

/* Розрахунок втрат iSE для довільного часового сигналу B(t) */
double calculate_ise_loss(const SteinmetzParams *p, const double *b_samples, 
                           size_t num_samples, double period_sec) {
    if (num_samples < 2 || period_sec <= 0.0) return 0.0;
    
    double dt = period_sec / (double)(num_samples - 1);
    double b_min = b_samples[0];
    double b_max = b_samples[0];
    
    /* Знаходимо розмах індукції ΔB */
    for (size_t i = 1; i < num_samples; ++i) {
        if (b_samples[i] < b_min) b_min = b_samples[i];
        if (b_samples[i] > b_max) b_max = b_samples[i];
    }
    double delta_b = b_max - b_min;
    if (delta_b <= 0.0) return 0.0;
    
    double k_i = calculate_k_i(p);
    double integral_sum = 0.0;
    
    /* Числове інтегрування |dB/dt|^alpha */
    for (size_t i = 0; i < num_samples - 1; ++i) {
        double db_dt = (b_samples[i + 1] - b_samples[i]) / dt;
        integral_sum += pow(fabs(db_dt), p->alpha) * dt;
    }
    
    double avg_integral = integral_sum / period_sec;
    double p_v = k_i * avg_integral * pow(delta_b, p->beta - p->alpha);
    
    return p_v;
}

int main(void) {
    /* Параметри матеріалу N87 (Epcos): k=16.9, alpha=1.25, beta=2.55 */
    SteinmetzParams n87 = {16.9, 1.25, 2.55};
    double freq = 100000.0;   /* 100 кГц */
    double b_pk = 0.1;        /* 100 мТл */
    
    double ose_p_v = calculate_ose_loss(&n87, freq, b_pk);
    printf("OSE Power Loss Density: %.2f W/m^3 (%.2f mW/cm^3)\n", 
           ose_p_v, ose_p_v / 1000.0);
           
    return 0;
}
```
```cpp
// Steinmetz Core Loss Calculator (C++20 implementation)
#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <format>

struct SteinmetzParams {
    double k{16.9};     // Material constant k
    double alpha{1.25}; // Frequency exponent
    double beta{2.55};  // Flux density exponent

    [[nodiscard]] double calculate_k_i() const noexcept {
        const double term1 = std::pow(2.0 * std::numbers::pi, alpha - 1.0);
        const double term2 = std::pow(2.0, beta - alpha + 1.0);
        const double beta_val = (std::tgamma((alpha + 1.0) / 2.0) * std::tgamma(0.5)) / 
                                 std::tgamma(alpha / 2.0 + 1.0);
        return k / (term1 * term2 * beta_val);
    }
};

class CoreLossCalculator {
public:
    explicit CoreLossCalculator(SteinmetzParams params) : params_(params) {}

    // Calculate OSE loss density (W/m^3) for pure sine wave
    [[nodiscard]] double calculate_ose(double freq_hz, double b_peak_tesla) const noexcept {
        return params_.k * std::pow(freq_hz, params_.alpha) * std::pow(b_peak_tesla, params_.beta);
    }

    // Calculate iSE loss density (W/m^3) for discrete B(t) sample span
    [[nodiscard]] double calculate_ise(std::span<const double> b_samples, double period_sec) const {
        if (b_samples.size() < 2 || period_sec <= 0.0) {
            return 0.0;
        }

        const double dt = period_sec / static_cast<double>(b_samples.size() - 1);
        const auto [min_it, max_it] = std::minmax_element(b_samples.begin(), b_samples.end());
        const double delta_b = *max_it - *min_it;
        if (delta_b <= 0.0) return 0.0;

        const double k_i = params_.calculate_k_i();
        double integral_sum = 0.0;

        for (size_t i = 0; i < b_samples.size() - 1; ++i) {
            const double db_dt = (b_samples[i + 1] - b_samples[i]) / dt;
            integral_sum += std::pow(std::abs(db_dt), params_.alpha) * dt;
        }

        const double avg_integral = integral_sum / period_sec;
        return k_i * avg_integral * std::pow(delta_b, params_.beta - params_.alpha);
    }

private:
    SteinmetzParams params_;
};

int main() {
    SteinmetzParams n87_ferrite{.k = 16.9, .alpha = 1.25, .beta = 2.55};
    CoreLossCalculator calc(n87_ferrite);

    constexpr double freq = 100'000.0; // 100 kHz
    constexpr double b_peak = 0.1;     // 100 mT

    const double ose_loss = calc.calculate_ose(freq, b_peak);
    std::cout << std::format("OSE Loss: {:.2f} W/m^3 ({:.2f} mW/cm^3)\n", 
                              ose_loss, ose_loss / 1000.0);

    // Generate triangular B(t) waveform for 50% duty PWM
    constexpr size_t num_pts = 1000;
    std::vector<double> b_triangular(num_pts);
    const double period = 1.0 / freq;
    for (size_t i = 0; i < num_pts; ++i) {
        double t_rel = static_cast<double>(i) / (num_pts - 1); // 0.0 to 1.0
        if (t_rel < 0.5) {
            b_triangular[i] = -b_peak + 4.0 * b_peak * t_rel;
        } else {
            b_triangular[i] = b_peak - 4.0 * b_peak * (t_rel - 0.5);
        }
    }

    const double ise_loss = calc.calculate_ise(b_triangular, period);
    std::cout << std::format("iSE Loss (PWM Triangle): {:.2f} W/m^3 ({:.2f} mW/cm^3)\n", 
                              ise_loss, ise_loss / 1000.0);

    return 0;
}
```
```py
# Steinmetz Core Loss Calculator (Python implementation)
import math
import scipy.special

class SteinmetzCalculator:
    def __init__(self, k: float, alpha: float, beta: float):
        self.k = k
        self.alpha = alpha
        self.beta = beta

    def get_k_i(self) -> float:
        """Calculate modified material parameter k_i for iSE"""
        term1 = (2.0 * math.pi) ** (self.alpha - 1.0)
        term2 = 2.0 ** (self.beta - self.alpha + 1.0)
        beta_val = scipy.special.beta((self.alpha + 1.0) / 2.0, 0.5)
        return self.k / (term1 * term2 * beta_val)

    def calculate_ose(self, freq_hz: float, b_peak_tesla: float) -> float:
        """Calculate classic OSE loss density (W/m^3)"""
        return self.k * (freq_hz ** self.alpha) * (b_peak_tesla ** self.beta)

    def calculate_ise(self, b_samples: list[float], period_sec: float) -> float:
        """Calculate iSE loss density (W/m^3) for arbitrary B(t) array"""
        if len(b_samples) < 2 or period_sec <= 0:
            return 0.0
            
        dt = period_sec / (len(b_samples) - 1)
        delta_b = max(b_samples) - min(b_samples)
        if delta_b <= 0:
            return 0.0

        k_i = self.get_k_i()
        integral_sum = 0.0
        for i in range(len(b_samples) - 1):
            db_dt = (b_samples[i + 1] - b_samples[i]) / dt
            integral_sum += (abs(db_dt) ** self.alpha) * dt

        avg_integral = integral_sum / period_sec
        return k_i * avg_integral * (delta_b ** (self.beta - self.alpha))

# Приклад використання
if __name__ == "__main__":
    calc = SteinmetzCalculator(k=16.9, alpha=1.25, beta=2.55)
    f_hz = 100000.0
    b_pk = 0.1
    
    p_ose = calc.calculate_ose(f_hz, b_pk)
    print(f"OSE Loss Density: {p_ose:.2f} W/m^3 ({p_ose/1000:.2f} mW/cm^3)")
```
:::

---

## 6. Порівняльний аналіз реалізацій

1. **Мобільність C-коду:** Мова C використовує стандартизовану функцію `tgamma()` з бібліотеки `math.h` для обчислення Бета-функції `B(x, y) = Γ(x)Γ(y)/Γ(x+y)`. Це дозволяє інтегрувати розрахунок безпосередньо у прошивки мікроконтролерів (STM32, ESP32, TI C2000) для адаптивного керування силовим перетворювачем у реальному часі.
2. **Безпека та виразність C++20:** Використання `std::span<const double>` запобігає виходу за межі буфера масиву вибірок без копіювання даних. Модифікатори `[[nodiscard]]` та `constexpr` дозволяють обчислювати коефіцієнт `k_i` на етапі компіляції для відомих матеріалів.
3. **Гнучкість Python:** Версія на Python є ідеальною для пост-обробки файлів осцилограм у форматах CSV або HDF5 після проведення лабораторних випробувань або симуляцій в LTspice.

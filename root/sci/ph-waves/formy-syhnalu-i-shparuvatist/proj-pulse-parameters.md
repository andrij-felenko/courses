# ⚙️ Вимірювання параметрів імпульсу та генерація ШІМ у коді

Програмне вимірювання часових інтервалів (періоду `T`, тривалості імпульсу `t_h`, коефіцієнта заповнення `D` та шпаруватості `S`) за допомогою блоків апаратного захоплення таймера (Input Capture), а також розрахунок діючого значення (True RMS) дискретизованого сигналу демонструють, як аналітичні інтеграли та часові межі перетворюються на надійний машинний код без втрати точності через переповнення лічильників, двоїстість порогів чи шуми квантування.

### Апаратне захоплення фронтів таймером (Input Capture)

Вимірювання параметрів імпульсного сигналу шляхом програмного опитування вхідних портів мікроконтролера («polling» у нескінченному циклі або обробка звичайних переривань GPIO) страждає від непереборного джитера: час реакції ядра на переривання, затримка конвеєра інструкцій та виконання інших пріоритетних завдань вносять випадкову похибку в десятки й сотні тактів. Якщо період сигналу становить одиниці мікросекунд, така програмна похибка робить вимірювання абсолютно беззмістовним.

Тому для прецизійного аналізу застосовують апаратний периферійний блок **Input Capture** (модуль захоплення таймера).

Принцип апаратного захоплення полягає у прямому апаратному зв'язку між вхідним фізичним піном та внутрішнім регістром таймера, який тактується стабільною опорною частотою `f_timer` (наприклад, 100 МГц, що забезпечує апаратну роздільну здатність у 10 наносекунд на один відлік лічильника):

1. **Передній фронт (Rising Edge)**: поява логічної одиниці на контакті апаратно копіює поточне значення лічильника таймера `CNT` у регістр захоплення `CCR1` (`t_rise`) без будь-якої затримки ядра.
2. **Задній фронт (Falling Edge)**: спад сигналу в логічний нуль копіює `CNT` у другий канал захоплення `CCR2` (`t_fall`).
3. **Наступний передній фронт**: фіксує початок наступного періоду `t_rise_next`.

За трьома послідовними апаратними відліками обчислюються всі часові параметри:

```
t_h   = (t_fall − t_rise) / f_timer

T     = (t_rise_next − t_rise) / f_timer

D     = (t_fall − t_rise) / (t_rise_next − t_rise)

S     = 1 / D
```

Критичним моментом у низькорівневих обчисленнях є коректна обробка переповнення (rollover) апаратного лічильника таймера. Якщо лічильник 16-розрядний (`0 .. 65535`), таймер скидається в 0 після досягнення вершини. В апаратній двійковій арифметиці мов C та C++ беззнакове віднімання `(uint16_t)(t_now - t_prev)` на рівні комп'ютерної логіки доповняльного коду автоматично дає правильну циклічну різницю без жодних умовних операторів `if`, доки вимірюваний інтервал не перевищує повного діапазону лічильника `2¹⁶ - 1`.

---

### Обчислення діючого значення (True RMS) у ковзному вікні

Якщо сигнал надходить з аналого-цифрового перетворювача (АЦП) як послідовність дискретних відліків напруги `v[0], v[1], ..., v[N-1]`, його діюче значення (True RMS), постійна складова (DC) та пік-фактор обчислюються дискретними аналогами неперервних інтегралів:

```
V_dc   = (1 / N) · ∑[i=0..N-1] v[i]

V_rms  = √( (1 / N) · ∑[i=0..N-1] v[i]² )

k_c    = V_peak / V_rms
```

При практичній реалізації алгоритму на вбудованих платформах виникають три типові проблеми:

1. **Чисельне переповнення акумулятора**: піднесення 12- або 16-бітних відліків АЦП до квадрата та їхнє підсумовування у 32-розрядному регістрі швидко переповнює розрядну сітку (`65535² · 1000 ≈ 4.3 · 10¹² > 2³²`). Тому сума квадратів обов'язково повинна накопичуватися у 64-розрядному цілому типі `uint64_t` або числі з рухомою комою подвійної точності `double`.
2. **Низька швидкість операції квадратного кореня**: виконання функції `sqrt()` у циклі переривання АЦП блокує процесор. Для високочастотних сигналів оптимізований код обчислює суму квадратів у швидкому перериванні, а витяг кореня `sqrt()` виносить у фоновий потік із меншою частотою оновлення.
3. **Синхронізація вікна усереднення**: якщо вікно з `N` відліків не містить строго цілу кількість періодів вхідного коливання, виникає похибка розриву фази (витік спектра). Для високоточного вимірювання розмір вікна `N` динамічно прив'язують до періоду `T`, виміряного таймером захоплення.

---

### Програмна реалізація: C та ідіоматичний C++

Нижче наведено модуль обробки подій захоплення таймера та розрахунку параметрів імпульсного сигналу й True RMS для вбудованих систем.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stddef.h>

/* Результати вимірювання параметрів імпульсного сигналу */
typedef struct {
    double frequency_hz;   /* Частота сигналу f = 1 / T */
    double period_s;       /* Період сигналу T */
    double pulse_width_s;  /* Тривалість імпульсу th */
    double duty_cycle;     /* Коефіцієнт заповнення D (0.0 .. 1.0) */
    double duty_factor;    /* Шпаруватість S = 1 / D */
    bool is_valid;         /* Ознака валідності розрахунку */
} PulseMetrics;

/* Стан кінцевого автомата подвійного захоплення таймера */
typedef struct {
    uint32_t timer_clock_hz; /* Тактова частота лічильника таймера */
    uint32_t last_rise_tick; /* Відлік лічильника останнього наростання */
    uint32_t last_fall_tick; /* Відлік лічильника останнього спаду */
    bool has_prev_rise;      /* Зафіксовано попередній передній фронт */
    bool has_fall;           /* Зафіксовано задній фронт у поточному циклі */
} TimerCaptureFSM;

/* Ініціалізація автомата захоплення */
void pulse_fsm_init(TimerCaptureFSM *fsm, uint32_t timer_clock_hz) {
    if (!fsm) return;
    fsm->timer_clock_hz = timer_clock_hz;
    fsm->last_rise_tick = 0;
    fsm->last_fall_tick = 0;
    fsm->has_prev_rise = false;
    fsm->has_fall = false;
}

/* Обробник події переднього фронту (Rising Edge Interrupt) */
bool pulse_fsm_on_rising(TimerCaptureFSM *fsm, uint32_t tick, PulseMetrics *out_metrics) {
    if (!fsm || !out_metrics) return false;
    out_metrics->is_valid = false;

    if (fsm->has_prev_rise && fsm->has_fall) {
        /* Беззнакове віднімання автоматично враховує циклічне переповнення */
        uint32_t period_ticks = tick - fsm->last_rise_tick;
        uint32_t high_ticks   = fsm->last_fall_tick - fsm->last_rise_tick;

        if (period_ticks > 0 && high_ticks <= period_ticks && fsm->timer_clock_hz > 0) {
            double clk = (double)fsm->timer_clock_hz;
            out_metrics->period_s = (double)period_ticks / clk;
            out_metrics->pulse_width_s = (double)high_ticks / clk;
            out_metrics->frequency_hz = clk / (double)period_ticks;
            out_metrics->duty_cycle = (double)high_ticks / (double)period_ticks;
            out_metrics->duty_factor = (high_ticks > 0) ? (1.0 / out_metrics->duty_cycle) : 0.0;
            out_metrics->is_valid = true;
        }
    }

    fsm->last_rise_tick = tick;
    fsm->has_prev_rise = true;
    fsm->has_fall = false; /* Очікуємо спад у новому періоді */
    return out_metrics->is_valid;
}

/* Обробник події заднього фронту (Falling Edge Interrupt) */
void pulse_fsm_on_falling(TimerCaptureFSM *fsm, uint32_t tick) {
    if (!fsm) return;
    if (fsm->has_prev_rise) {
        fsm->last_fall_tick = tick;
        fsm->has_fall = true;
    }
}

/* Розрахунок True RMS та інтегральних норм для масиву вибірок АЦП */
void calculate_discrete_rms(const float *samples, size_t count,
                            float *out_dc, float *out_rms,
                            float *out_crest, float *out_form) {
    if (!samples || count == 0 || !out_dc || !out_rms || !out_crest || !out_form) return;

    double sum = 0.0;
    double sum_sq = 0.0;
    double sum_abs = 0.0;
    float peak = 0.0f;

    for (size_t i = 0; i < count; ++i) {
        float val = samples[i];
        sum += val;
        sum_sq += (double)val * (double)val;
        float abs_val = fabsf(val);
        sum_abs += (double)abs_val;
        if (abs_val > peak) {
            peak = abs_val;
        }
    }

    double mean = sum / (double)count;
    double mean_sq = sum_sq / (double)count;
    double rms = sqrt(mean_sq);
    double rectified_avg = sum_abs / (double)count;

    *out_dc = (float)mean;
    *out_rms = (float)rms;
    *out_crest = (rms > 1e-9) ? (peak / (float)rms) : 0.0f;
    *out_form  = (rectified_avg > 1e-9) ? ((float)rms / (float)rectified_avg) : 0.0f;
}
```
```cpp
#include <cmath>
#include <cstdint>
#include <chrono>
#include <span>
#include <optional>
#include <expected>
#include <concepts>
#include <algorithm>

namespace signal_dsp {

/* Метрики імпульсного сигналу */
struct PulseMetrics {
    double frequency_hz{0.0};
    std::chrono::duration<double> period{0.0};
    std::chrono::duration<double> pulse_width{0.0};
    double duty_cycle{0.0};   // D = th / T
    double duty_factor{0.0};  // S = 1 / D
    double crest_factor{0.0}; // Kc = Vpeak / Vrms
};

/* Коди помилок аналізу */
enum class PulseError {
    ZeroPeriod,
    PulseWidthExceedsPeriod,
    InvalidClockRate,
    NoData
};

/* Концепт для беззнакових цілих типів лічильника таймера */
template <typename T>
concept UnsignedIntegral = std::unsigned_integral<T>;

/* Шаблонний клас обробки подій захоплення таймера */
template <UnsignedIntegral TickType = uint32_t>
class PulseCaptureAnalyzer {
public:
    constexpr explicit PulseCaptureAnalyzer(uint32_t timer_clock_hz) noexcept
        : clock_hz_(timer_clock_hz) {}

    void on_falling_edge(TickType tick) noexcept {
        if (has_rising_) {
            last_fall_ = tick;
            has_falling_ = true;
        }
    }

    [[nodiscard]] std::expected<PulseMetrics, PulseError> on_rising_edge(TickType tick) noexcept {
        if (clock_hz_ == 0) {
            return std::unexpected(PulseError::InvalidClockRate);
        }

        std::optional<PulseMetrics> result;

        if (has_rising_ && has_falling_) {
            // Беззнакове віднімання автоматично враховує переповнення лічильника
            const TickType period_ticks = tick - last_rise_;
            const TickType high_ticks = last_fall_ - last_rise_;

            if (period_ticks == 0) {
                return std::unexpected(PulseError::ZeroPeriod);
            }
            if (high_ticks > period_ticks) {
                return std::unexpected(PulseError::PulseWidthExceedsPeriod);
            }

            const double clk = static_cast<double>(clock_hz_);
            const double period_s = static_cast<double>(period_ticks) / clk;
            const double width_s  = static_cast<double>(high_ticks) / clk;
            const double duty     = static_cast<double>(high_ticks) / static_cast<double>(period_ticks);

            PulseMetrics m{
                .frequency_hz = clk / static_cast<double>(period_ticks),
                .period = std::chrono::duration<double>(period_s),
                .pulse_width = std::chrono::duration<double>(width_s),
                .duty_cycle = duty,
                .duty_factor = (high_ticks > 0) ? (1.0 / duty) : 0.0,
                .crest_factor = (duty > 0.0) ? (1.0 / std::sqrt(duty)) : 0.0
            };
            result = m;
        }

        last_rise_ = tick;
        has_rising_ = true;
        has_falling_ = false;

        if (result) {
            return *result;
        }
        return std::unexpected(PulseError::NoData);
    }

    void reset() noexcept {
        has_rising_ = false;
        has_falling_ = false;
    }

private:
    uint32_t clock_hz_{0};
    TickType last_rise_{0};
    TickType last_fall_{0};
    bool has_rising_{false};
    bool has_falling_{false};
};

/* Структура результату аналізу дискретних вибірок */
struct WaveformStatistics {
    float mean_dc{0.0f};
    float rms{0.0f};
    float crest_factor{0.0f};
    float form_factor{0.0f};
};

/* Розрахунок інтегральних норм через std::span без зайвого копіювання пам'яті */
[[nodiscard]] inline std::expected<WaveformStatistics, PulseError>
calculate_statistics(std::span<const float> samples) noexcept {
    if (samples.empty()) {
        return std::unexpected(PulseError::NoData);
    }

    double sum = 0.0;
    double sum_sq = 0.0;
    double sum_abs = 0.0;
    float peak = 0.0f;

    for (const float val : samples) {
        const double dval = static_cast<double>(val);
        sum += dval;
        sum_sq += dval * dval;
        const float abs_val = std::abs(val);
        sum_abs += static_cast<double>(abs_val);
        peak = std::max(peak, abs_val);
    }

    const double n = static_cast<double>(samples.size());
    const double mean = sum / n;
    const double rms = std::sqrt(sum_sq / n);
    const double rectified_avg = sum_abs / n;

    WaveformStatistics stats{
        .mean_dc = static_cast<float>(mean),
        .rms = static_cast<float>(rms),
        .crest_factor = (rms > 1e-9) ? static_cast<float>(peak / rms) : 0.0f,
        .form_factor = (rectified_avg > 1e-9) ? static_cast<float>(rms / rectified_avg) : 0.0f
    };

    return stats;
}

} // namespace signal_dsp
```
:::

---

### Апаратні пастки та захист від збоїв

1. **Неузгодженість хвильового опору та дзвони (Ringing)**: коли вхідний сигнал має крутий фронт (`t_r < 2` нс), доріжка друкованої плати завдовжки понад 5 см поводиться як довга лінія з розподіленими параметрами. Хвиля відбивається від високого вхідного опору піна мікроконтролера, утворюючи згасаючі коливання. Якщо амплітуда дзвону перетинає поріг спрацьовування тригера Шмітта, таймер фіксує кілька хибних фронтів поспіль. Це усувається послідовним демпфуючим резистором (damping resistor 33..50 Ом) безпосередньо біля виходу джерела або ввімкненням цифрового фільтра захоплення таймера (Input Filter на 4–8 тактів).
2. **Крайові випадки 0% та 100% заповнення**: при постійному нульовому рівні фронти не виникають взагалі; при 100% заповненні виникає лише один передній фронт, після чого лінія залишається у верхньому стані. Автомат захоплення ніколи не отримує заднього фронту. Для запобігання «зависанню» вимірювальної системи таймер повинен мати окреме переривання за тайм-аутом переповнення (Update Interrupt): якщо після переднього фронту таймер переповнився двічі без спаду, алгоритм примусово фіксує стан `D = 1.0` (100%).
3. **Квантування та фазовий шум (Jitter)**: якщо період імпульсу становить лише 100 тактів таймера, крок квантування за коефіцієнтом заповнення складає `1%`. Для вимірювання високочастотного ШІМ (наприклад, 1 МГц із точністю 0.1%) тактова частота таймера має становити не менше 1 ГГц, або ж застосовують блоки високої роздільної здатності (High-Resolution Timer — HRTIM) із внутрішніми фазовими лініями затримки (DLL).

# ⚙️ Цифрова фільтрація та розпізнавання патернів PIR-сенсора

Просте зчитування логічного рівня з компаратора або пряме порогове порівняння сирих відліків АЦП неминуче призводить до помилкових спрацьовувань охоронних систем та автоматики освітлення. Короткі імпульсні завади від комутації індуктивних навантажень (реле, пускачі), електромагнітні наведення від радіопередавачів (Wi-Fi, GSM) та повільний тепловий дрейф напруги зміщення здатні перевищити статичний поріг компаратора за відсутності реального руху. Створення надійної системи вимагає цифрової фільтрації потоку АЦП та синтаксичного розпізнавання форми сигналу (патерну чергування напівхвиль) за допомогою автомата станів.

### Архітектура цифрового тракту обробки

Сигнал надходить з частотою дискретизації `f_s = 50 Гц` (інтервал вибірки `Δt = 20 мс`) з внутрішнього 14-бітного АЦП цифрового сенсора або зовнішнього аналого-цифрового каналу мікроконтролера.

Обробка виконується послідовно в чотири етапи:
1. **Смугова IIR-фільтрація (Direct Form II Transposed Biquad):** Каскадний цифровий фільтр 2-го порядку зі смугою пропускання `0.5 ... 4.0 Гц`. Він повністю пригнічує постійну складову (дрейф робочої точки JFET), високочастотний шум квантування та мережеві наведення 50 Гц.
2. **Адаптивне стеження за базовою лінією та рівнем шуму (DC & Noise Floor Tracker):** Обчислення повільного експоненційного ковзного середнього (EMA) для фонового шуму дозволяє динамічно підлаштовувати поріг детекції під температуру та електромагнітну обстановку.
3. **Двопороговий віконний аналізатор:** Визначення виходу сигналу за межі коридору `[V_base - V_th, V_base + V_th]`.
4. **Скінченний автомат розпізнавання хвильового пакета (Pattern FSM):** Справжній рух людини крізь фасетку лінзи Френеля породжує пару почергових напівхвиль протилежної полярності (позитивний сплеск, перехід через нуль, негативний сплеск або навпаки). Одиничні некорельовані імпульси від завад ігноруються.

### Розрахунок та дискретна передавальна функція смугового фільтра

Для виділення характерних частот руху людини (`0.5–4.0 Гц`) при частоті дискретизації `f_s = 50 Гц` застосовують біквадратний смуговий фільтр Баттерворта 2-го порядку. Передавальна функція в Z-області має вигляд:

```
H(z) = (b0 + b1 · z⁻¹ + b2 · z⁻²) / (1 + a1 · z⁻¹ + a2 · z⁻²)
```

Застосування білінійного перетворення аналогового прототипу на частоти зрізу `f_L = 0.5 Гц` та `f_H = 4.0 Гц` дає такі нормовані коефіцієнти:
- `b0 =  0.1983`
- `b1 =  0.0000`
- `b2 = -0.1983`
- `a1 = -1.5422`
- `a2 =  0.6034`

Фільтр реалізується у транспонованій прямій формі 2 (Direct Form II Transposed). На відміну від прямої форми 1, ця топологія потребує лише двох змінних стану (`d1, d2`), мінімізує кількість операцій читання/запису в оперативній пам'яті мікроконтролера та володіє максимальною стійкістю до накопичення похибок округлення чисел із рухомою або фіксованою комою.

Різницеві рівняння обчислення вибірки мають вигляд:

```
y[n]  = b0 · x[n] + d1[n-1]
d1[n] = b1 · x[n] - a1 · y[n] + d2[n-1]
d2[n] = b2 · x[n] - a2 · y[n]
```

### Динамічний поріг та експоненційне стеження за шумом

Статичний поріг спрацьовування стає непридатним при зміні сезонів: взимку сенсор має менший власний шум, а влітку зі зростанням температури тепловий шум Джонсона напівпровідникового кристала та JFET-каналу зростає майже на 30–50%.

Для підтримання постійної ймовірності хибної тривоги алгоритм оцінює середнє абсолютне відхилення фону в стані спокою (`IDLE`):

```
σ_noise[n] = (1 - α) · σ_noise[n-1] + α · |y[n]|
```

Коефіцієнт згладжування обирається `α = 0.005`, що за частоти 50 Гц відповідає сталій часу інтегрування `τ_noise ≈ 4 секунди`. Поточний поріг детекції обчислюється динамічно:

```
V_th[n] = k_sens · σ_noise[n]
```

де множник чутливості `k_sens = 3.5 ... 5.0` задає кратність перевищення сигналу над середньоквадратичним шумом (забезпечуючи надійне детектування за критерієм Неймана — Пірсона).

### Програмна реалізація алгоритму на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PIR_SAMPLE_RATE_HZ     50
#define PIR_MIN_WINDOW_TICKS   (PIR_SAMPLE_RATE_HZ * 0.15f) // 150 мс
#define PIR_MAX_WINDOW_TICKS   (PIR_SAMPLE_RATE_HZ * 1.50f) // 1.5 с
#define PIR_DEADTIME_TICKS     (PIR_SAMPLE_RATE_HZ * 1.00f) // 1.0 с після тривоги

typedef enum {
    PIR_STATE_IDLE = 0,
    PIR_STATE_POS_PEAK_DETECTED,
    PIR_STATE_NEG_PEAK_DETECTED,
    PIR_STATE_DEADTIME
} pir_fsm_state_t;

typedef struct {
    // Коефіцієнти смугового IIR-фільтра (0.5–4.0 Гц при Fs = 50 Гц)
    float b0, b1, b2;
    float a1, a2;
    // Змінні стану фільтра (Direct Form II Transposed)
    float d1;
    float d2;

    // Адаптивний рівень шуму та поріг
    float baseline;
    float noise_sigma;
    float threshold_multiplier;

    // Стан FSM
    pir_fsm_state_t state;
    uint32_t timer_ticks;
    bool motion_detected;
} pir_processor_t;

void pir_init(pir_processor_t *p, float sensitivity_k) {
    // Коефіцієнти розраховані для Butterworth Bandpass 0.5-4.0 Гц, Fs=50 Гц
    p->b0 =  0.1983f;
    p->b1 =  0.0000f;
    p->b2 = -0.1983f;
    p->a1 = -1.5422f;
    p->a2 =  0.6034f;

    p->d1 = 0.0f;
    p->d2 = 0.0f;
    p->baseline = 0.0f;
    p->noise_sigma = 15.0f; // Початкова оцінка шуму в LSB
    p->threshold_multiplier = sensitivity_k; // Типово 3.5 - 5.0

    p->state = PIR_STATE_IDLE;
    p->timer_ticks = 0;
    p->motion_detected = false;
}

static float pir_filter_step(pir_processor_t *p, float raw_sample) {
    // Реалізація транспонованої форми Direct Form II
    float out = p->b0 * raw_sample + p->d1;
    p->d1 = p->b1 * raw_sample - p->a1 * out + p->d2;
    p->d2 = p->b2 * raw_sample - p->a2 * out;
    return out;
}

bool pir_process_sample(pir_processor_t *p, float raw_adc_sample) {
    p->motion_detected = false;

    // 1. Смугова фільтрація
    float filtered = pir_filter_step(p, raw_adc_sample);

    // 2. Адаптивне оновлення базової лінії шуму в стані спокою
    if (p->state == PIR_STATE_IDLE) {
        float abs_val = fabsf(filtered);
        // Повільне експоненційне згладжування шуму: alpha = 0.005 (~4 сек)
        p->noise_sigma = 0.995f * p->noise_sigma + 0.005f * abs_val;
        if (p->noise_sigma < 5.0f) p->noise_sigma = 5.0f; // Нижній обмежувач
    }

    float current_threshold = p->noise_sigma * p->threshold_multiplier;

    // 3. Автомат станів розпізнавання патерну
    switch (p->state) {
        case PIR_STATE_IDLE:
            if (filtered > current_threshold) {
                p->state = PIR_STATE_POS_PEAK_DETECTED;
                p->timer_ticks = 0;
            } else if (filtered < -current_threshold) {
                p->state = PIR_STATE_NEG_PEAK_DETECTED;
                p->timer_ticks = 0;
            }
            break;

        case PIR_STATE_POS_PEAK_DETECTED:
            p->timer_ticks++;
            // Очікуємо зворотного негативного піку (підтвердження руху)
            if (filtered < -current_threshold && p->timer_ticks >= PIR_MIN_WINDOW_TICKS) {
                p->motion_detected = true;
                p->state = PIR_STATE_DEADTIME;
                p->timer_ticks = 0;
            } else if (p->timer_ticks > PIR_MAX_WINDOW_TICKS) {
                // Таймаут вікна: одинична завада без другої напівхвилі
                p->state = PIR_STATE_IDLE;
            }
            break;

        case PIR_STATE_NEG_PEAK_DETECTED:
            p->timer_ticks++;
            // Очікуємо зворотного позитивного піку
            if (filtered > current_threshold && p->timer_ticks >= PIR_MIN_WINDOW_TICKS) {
                p->motion_detected = true;
                p->state = PIR_STATE_DEADTIME;
                p->timer_ticks = 0;
            } else if (p->timer_ticks > PIR_MAX_WINDOW_TICKS) {
                p->state = PIR_STATE_IDLE;
            }
            break;

        case PIR_STATE_DEADTIME:
            p->timer_ticks++;
            // Період блокування повторних спрацьовувань після тривоги
            if (p->timer_ticks >= PIR_DEADTIME_TICKS) {
                p->state = PIR_STATE_IDLE;
            }
            break;
    }

    return p->motion_detected;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>

class PirDspProcessor {
public:
    enum class State : uint8_t {
        Idle,
        PosPeakDetected,
        NegPeakDetected,
        DeadTime
    };

    explicit constexpr PirDspProcessor(float sensitivityMultiplier = 4.0f) noexcept
        : thresholdMultiplier_{sensitivityMultiplier} {}

    [[nodiscard]] bool processSample(float rawAdcSample) noexcept {
        bool triggered = false;

        // 1. Пряма фільтрація (Direct Form II Transposed)
        const float filtered = filterStep(rawAdcSample);

        // 2. Адаптивне оновлення фонового шуму в стані спокою
        if (state_ == State::Idle) {
            const float absVal = std::fabs(filtered);
            noiseSigma_ = 0.995f * noiseSigma_ + 0.005f * absVal;
            noiseSigma_ = std::max(noiseSigma_, 5.0f);
        }

        const float threshold = noiseSigma_ * thresholdMultiplier_;

        // 3. Автомат розпізнавання чергування фаз
        switch (state_) {
            case State::Idle:
                if (filtered > threshold) {
                    state_ = State::PosPeakDetected;
                    timerTicks_ = 0;
                } else if (filtered < -threshold) {
                    state_ = State::NegPeakDetected;
                    timerTicks_ = 0;
                }
                break;

            case State::PosPeakDetected:
                ++timerTicks_;
                if (filtered < -threshold && timerTicks_ >= kMinWindowTicks) {
                    triggered = true;
                    state_ = State::DeadTime;
                    timerTicks_ = 0;
                } else if (timerTicks_ > kMaxWindowTicks) {
                    state_ = State::Idle;
                }
                break;

            case State::NegPeakDetected:
                ++timerTicks_;
                if (filtered > threshold && timerTicks_ >= kMinWindowTicks) {
                    triggered = true;
                    state_ = State::DeadTime;
                    timerTicks_ = 0;
                } else if (timerTicks_ > kMaxWindowTicks) {
                    state_ = State::Idle;
                }
                break;

            case State::DeadTime:
                ++timerTicks_;
                if (timerTicks_ >= kDeadTimeTicks) {
                    state_ = State::Idle;
                }
                break;
        }

        return triggered;
    }

    void processBlock(std::span<const float> inputBuffer, std::span<bool> outputEvents) noexcept {
        const size_t count = std::min(inputBuffer.size(), outputEvents.size());
        for (size_t i = 0; i < count; ++i) {
            outputEvents[i] = processSample(inputBuffer[i]);
        }
    }

    [[nodiscard]] State currentState() const noexcept { return state_; }
    [[nodiscard]] float currentNoiseFloor() const noexcept { return noiseSigma_; }

    void reset() noexcept {
        d1_ = 0.0f;
        d2_ = 0.0f;
        noiseSigma_ = 15.0f;
        timerTicks_ = 0;
        state_ = State::Idle;
    }

private:
    static constexpr uint32_t kSampleRateHz    = 50;
    static constexpr uint32_t kMinWindowTicks  = static_cast<uint32_t>(kSampleRateHz * 0.15f);
    static constexpr uint32_t kMaxWindowTicks  = static_cast<uint32_t>(kSampleRateHz * 1.50f);
    static constexpr uint32_t kDeadTimeTicks   = static_cast<uint32_t>(kSampleRateHz * 1.00f);

    // Коефіцієнти фільтра Butterworth Bandpass (0.5–4.0 Гц, Fs = 50 Гц)
    static constexpr float kB0 =  0.1983f;
    static constexpr float kB1 =  0.0000f;
    static constexpr float kB2 = -0.1983f;
    static constexpr float kA1 = -1.5422f;
    static constexpr float kA2 =  0.6034f;

    float d1_{0.0f};
    float d2_{0.0f};
    float noiseSigma_{15.0f};
    float thresholdMultiplier_{4.0f};

    uint32_t timerTicks_{0};
    State state_{State::Idle};

    [[nodiscard]] float filterStep(float x) noexcept {
        const float y = kB0 * x + d1_;
        d1_ = kB1 * x - kA1 * y + d2_;
        d2_ = kB2 * x - kA2 * y;
        return y;
    }
};
```
:::

### Покроковий аналіз проходження хвилі через FSM

Розглянемо траєкторію внутрішнього стану детектора при проходженні людини на дистанції 4 метри:

1. **Фаза спокою (`IDLE`):** Сигнал на виході смугового фільтра флуктує в межах `±12 LSB`. Адаптивний рівень шуму стабілізується на значенні `noise_sigma ≈ 14.5 LSB`. При `threshold_multiplier = 4.0` порогове вікно становить `±58 LSB`.
2. **Вхід у зону активного кристала A (t = 0.20 с):** Людина входить у промінь. Фільтрований сигнал стрімко зростає до `+140 LSB`, перевищуючи поріг `+58 LSB`. Автомат фіксує передній пік, переходить у стан `POS_PEAK_DETECTED` та скидає таймер `timer_ticks = 0`. Оновлення дисперсії шуму миттєво блокується, щоб уникнути завищення порогу хвилею руху.
3. **Перетин сліпої зони та перехід через нуль (t = 0.45 с):** Сигнал спадає з `+140 LSB` до `0 LSB`. Лічильник `timer_ticks` досягає значення 12 відліків (240 мс). Оскільки `timer_ticks >= PIR_MIN_WINDOW_TICKS` (150 мс), вікно валідації відкрито.
4. **Вхід у зону компенсаційного кристала B (t = 0.70 с):** Сигнал падає до `-165 LSB`, перетинаючи від'ємний поріг `-58 LSB`. Автомат констатує наявність повної пари протифазних напівхвиль у дозволеному часовому вікні (`150 мс ≤ Δt ≤ 1500 мс`). Прапорець `motion_detected` встановлюється в `true`, а FSM переходить у захисний стан `DEADTIME`.
5. **Фаза мертвого часу (t = 0.70 ... 1.70 с):** Протягом 1 секунди система блокує обробку нових подій, дозволяючи залишковій коливальній реакції IIR-фільтра затухнути, а зовнішньому реле — завершити комутацію контактів. Після закінчення `DEADTIME` автомат повертається в стан `IDLE`.

### Крайові випадки та практичні пастки

1. **Ефект теплового удару (Thermal Shock):** При раптовому увімкненні потужного обігрівача чи протягу з відчиненого вікна виникає перепад температури, що заганяє АЦП у насичення (clipping). Програма повинна детектувати стан насичення (`ADC == 0` або `ADC == MAX_VALUE`) і примусово переводити FSM у стан блокування `DeadTime`, скидаючи лінії затримки фільтра `d1 = d2 = 0`, щоб уникнути тривалого дзвону IIR-фільтра після виходу з насичення.
2. **Комутаційні перешкоди силових реле:** Момент спрацьовування вихідного силового реле супроводжується іскровим розрядом на контактах та магнітною наводкою на котушку. Без обов'язкового тайм-ауту блокування `PIR_DEADTIME_TICKS` (1–2 секунди після фіксації руху) реле здатне самозбуджуватися, сприймаючи власну комутацію як новий рух.
3. **Заморожування рівня шуму під час руху:** Оцінка дисперсії шуму `noise_sigma` повинна оновлюватися **виключно у стані спокою (`PIR_STATE_IDLE`)**. Якщо оновлювати шум під час проходження активної хвилі від людини, алгоритм завищить поріг і втратить чутливість до наступних кроків об'єкта.

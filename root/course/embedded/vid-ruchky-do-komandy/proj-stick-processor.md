# ⚙️ Бібліотека обробки сигналів стіка керування

Аналоговий сигнал ручки керування проходить довгий обчислювальний шлях: від сирих відліків АЦП (або цифрових каналів пакетних протоколів CRSF/SBUS) до фізичної уставки кутової швидкості в градусах за секунду (`deg/s`). Бібліотека реалізує автономний обчислювальний конвеєр, що включає триточкове калібрування, плавну неперервну мертву зону, кубічно-степеневу експоненту, модель кутових швидкостей `Actual Rates` та низькочастотний фільтр `PT1` для усунення сходинок квантування в часі.

```
+-----------+     +------------+     +----------+     +--------------+     +--------------+
| RAW (ADC) | --> | Normalize  | --> | Deadband | --> | Actual Rates | --> | RC Smoothing | --> Rate (deg/s)
+-----------+     | (Calibrate)|     | (Smooth) |     | (Expo+Curve) |     |  (PT1 LPF)   |
                  +------------+     +----------+     +--------------+     +--------------+
```

## Архітектура та етапи обробки

Конвеєр обробки складається з чотирьох послідовних математичних перетворень:

1. **Етап 1: Триточкова нормалізація (`stick_normalize`).**
   Сирий вхідний сигнал (`raw_min .. raw_max`) перетворюється у симетричний безрозмірний діапазон `[-1.0 .. +1.0]`. Оскільки фізичний центр `raw_center` через допуски пружин ніколи не ділить діапазон навпіл, ліве та праве плече нормалізуються окремими коефіцієнтами. Це виключає зміщення нуля у стані спокою та гарантує досягнення повного діапазону в обидва боки без паразитного насичення або недольоту.

2. **Етап 2: Неперервна мертва зона (`stick_apply_deadband`).**
   Сигнал очищається від механічного гістерезису повернення пружини в центрі (`center_deadband`) та обмежується від механічного бруду й розкиду на кінцевих упорах (`end_deadband`). На відміну від наївного обнулення, алгоритм ремасштабує активний робочий діапазон, гарантуючи C⁰-неперервність: вихід починає плавно наростати від нуля без сходинок і стрибків похідної, що захищає диференціальний контур PID від ударів струму.

3. **Етап 3: Розрахунок кутової швидкості (`stick_calc_actual_rate`).**
   Положення стіка масштабується за моделлю `Actual Rates` з використанням степеневого полінома 5-го порядку. Параметри `center_rate` (чутливість у нулі) та `max_rate` (максимальна швидкість на упорі) є повністю незалежними, а коефіцієнт `expo` плавно регулює кривину переходу між ними без взаємного деформування шкал.

4. **Етап 4: RC Smoothing фільтрація (`stick_filter_pt1`).**
   Дискретні сходинки радіопакетів (які надходять з частотою 50–500 Гц) згладжуються низькочастотним фільтром першого порядку (PT1). Це запобігає появі дельта-сплесків у диференціальній складовій PID-регулятора (`D-term kick`), усуваючи високочастотний нагрів моторів та паразитний розряд батареї.

## Реалізація бібліотеки на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Конфігурація калібрування та мертвої зони для однієї осі */
typedef struct {
    float raw_min;         /* мінімальний відлік АЦП (наприклад, 1000.0f) */
    float raw_center;      /* центральний відлік у стані спокою (наприклад, 1500.0f) */
    float raw_max;         /* максимальний відлік АЦП (наприклад, 2000.0f) */
    float center_deadband; /* відносна мертва зона центру [0.0 .. 0.15] (наприклад, 0.04f) */
    float end_deadband;    /* відносна мертва зона упору [0.0 .. 0.10] (наприклад, 0.02f) */
} stick_calib_config_t;

/* Налаштування моделі швидкості Actual Rates */
typedef struct {
    float center_rate;     /* чутливість біля центру (deg/s), наприклад 200.0f */
    float max_rate;        /* максимальна кутова швидкість (deg/s), наприклад 850.0f */
    float expo;            /* ступінь пом'якшення кривої [0.0 .. 1.0], наприклад 0.55f */
} actual_rates_config_t;

/* Стан фільтра згладжування RC Smoothing (PT1) */
typedef struct {
    float state;           /* накопичений стан фільтра */
    float cutoff_hz;       /* частота зрізу фільтра (Гц), наприклад 45.0f */
} rc_filter_state_t;

/* Повний об'єкт обробки осі стіка */
typedef struct {
    stick_calib_config_t calib;
    actual_rates_config_t rates;
    rc_filter_state_t filter;
} stick_axis_processor_t;

/* Ініціалізація стану процесора осі */
void stick_processor_init(stick_axis_processor_t *proc,
                          const stick_calib_config_t *calib,
                          const actual_rates_config_t *rates,
                          float cutoff_hz)
{
    if (proc != NULL) {
        if (calib != NULL) proc->calib = *calib;
        if (rates != NULL) proc->rates = *rates;
        proc->filter.state = 0.0f;
        proc->filter.cutoff_hz = (cutoff_hz > 0.0f) ? cutoff_hz : 45.0f;
    }
}

/* 1. Нормалізація вхідного сирого сигналу в діапазон [-1.0 .. +1.0] */
static float stick_normalize(const stick_calib_config_t *calib, float raw_value)
{
    float norm = 0.0f;
    if (raw_value >= calib->raw_center) {
        float span = calib->raw_max - calib->raw_center;
        if (span > 1e-3f) {
            norm = (raw_value - calib->raw_center) / span;
        }
    } else {
        float span = calib->raw_center - calib->raw_min;
        if (span > 1e-3f) {
            norm = (raw_value - calib->raw_center) / span;
        }
    }

    /* Жорстке затискання в межі [-1.0 .. +1.0] */
    if (norm > 1.0f) norm = 1.0f;
    if (norm < -1.0f) norm = -1.0f;
    return norm;
}

/* 2. Застосування мертвої зони центру та кінцевих упорів без розривів */
static float stick_apply_deadband(const stick_calib_config_t *calib, float norm_value)
{
    float sign = (norm_value >= 0.0f) ? 1.0f : -1.0f;
    float abs_val = fabsf(norm_value);

    float db_c = calib->center_deadband;
    float db_e = calib->end_deadband;

    /* Перевірка перебування всередині мертвої зони центру */
    if (abs_val <= db_c) {
        return 0.0f;
    }

    /* Досягнення кінцевого упору */
    if (abs_val >= (1.0f - db_e)) {
        return sign * 1.0f;
    }

    /* Лінійне ремасштабування робочого діапазону від 0.0 до 1.0 */
    float active_range = 1.0f - db_c - db_e;
    if (active_range < 1e-3f) {
        return 0.0f;
    }

    float rescaled = (abs_val - db_c) / active_range;
    return sign * rescaled;
}

/* 3. Розрахунок цільової кутової швидкості за моделлю Actual Rates */
static float stick_calc_actual_rate(const actual_rates_config_t *rates, float stick_pos)
{
    float sign = (stick_pos >= 0.0f) ? 1.0f : -1.0f;
    float x = fabsf(stick_pos);

    /* Степенева крива 5-го порядку: x · (1 - e) + x⁵ · e */
    float x5 = x * x * x * x * x;
    float curve = x * (1.0f - rates->expo) + x5 * rates->expo;

    /* Розрахунок кутової швидкості (deg/s) */
    float center_contrib = x * rates->center_rate;
    float max_contrib = (rates->max_rate - rates->center_rate) * curve;
    float rate_deg_s = center_contrib + max_contrib;

    return sign * rate_deg_s;
}

/* 4. Фільтр низьких частот PT1 (RC Smoothing) */
static float stick_filter_pt1(rc_filter_state_t *filt, float target_rate, float dt_seconds)
{
    if (dt_seconds <= 0.0f || filt->cutoff_hz <= 0.0f) {
        filt->state = target_rate;
        return filt->state;
    }

    /* Розрахунок коефіцієнта alpha: dt / (RC + dt) */
    float rc = 1.0f / (2.0f * 3.1415926535f * filt->cutoff_hz);
    float alpha = dt_seconds / (rc + dt_seconds);

    if (alpha > 1.0f) alpha = 1.0f;
    if (alpha < 0.0f) alpha = 0.0f;

    filt->state += alpha * (target_rate - filt->state);
    return filt->state;
}

/* Головна функція повного циклу обробки осі */
float stick_process_axis(stick_axis_processor_t *proc, float raw_input, float dt_seconds)
{
    if (proc == NULL) {
        return 0.0f;
    }

    /* Крок 1: Нормалізація */
    float norm = stick_normalize(&proc->calib, raw_input);

    /* Крок 2: Мертва зона */
    float active_stick = stick_apply_deadband(&proc->calib, norm);

    /* Крок 3: Модель швидкості Actual Rates */
    float target_rate = stick_calc_actual_rate(&proc->rates, active_stick);

    /* Крок 4: RC Smoothing */
    float smoothed_rate = stick_filter_pt1(&proc->filter, target_rate, dt_seconds);

    return smoothed_rate;
}
```
```cpp
#include <cmath>
#include <algorithm>
#include <span>
#include <array>
#include <numbers>

namespace flight_control {

struct StickCalibration {
    float raw_min{1000.0f};
    float raw_center{1500.0f};
    float raw_max{2000.0f};
    float center_deadband{0.04f}; // 4% мертва зона в нулі
    float end_deadband{0.02f};    // 2% мертва зона на упорах
};

struct ActualRatesConfig {
    float center_rate{200.0f};    // Чутливість біля нуля (deg/s)
    float max_rate{850.0f};       // Максимальна кутова швидкість (deg/s)
    float expo{0.55f};            // Кривина переходу [0.0 .. 1.0]
};

class RcSmoothingFilter {
public:
    constexpr explicit RcSmoothingFilter(float cutoff_hz = 45.0f) noexcept
        : cutoff_hz_{cutoff_hz} {}

    [[nodiscard]] float process(float target, float dt_seconds) noexcept {
        if (dt_seconds <= 0.0f || cutoff_hz_ <= 0.0f) {
            state_ = target;
            return state_;
        }
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        const float rc = 1.0f / (two_pi * cutoff_hz_);
        const float alpha = std::clamp(dt_seconds / (rc + dt_seconds), 0.0f, 1.0f);

        state_ += alpha * (target - state_);
        return state_;
    }

    void reset(float initial_value = 0.0f) noexcept {
        state_ = initial_value;
    }

    [[nodiscard]] float state() const noexcept { return state_; }
    void set_cutoff(float hz) noexcept { cutoff_hz_ = (hz > 0.0f) ? hz : 45.0f; }

private:
    float state_{0.0f};
    float cutoff_hz_{45.0f};
};

class StickAxisProcessor {
public:
    constexpr StickAxisProcessor(StickCalibration calib, ActualRatesConfig rates, float cutoff_hz = 45.0f) noexcept
        : calib_{calib}, rates_{rates}, filter_{cutoff_hz} {}

    [[nodiscard]] float process(float raw_input, float dt_seconds) noexcept {
        const float norm = normalize(raw_input);
        const float active_stick = apply_deadband(norm);
        const float target_rate = calculate_actual_rate(active_stick);
        return filter_.process(target_rate, dt_seconds);
    }

    void reset() noexcept {
        filter_.reset(0.0f);
    }

    [[nodiscard]] const StickCalibration& calibration() const noexcept { return calib_; }
    [[nodiscard]] const ActualRatesConfig& rates() const noexcept { return rates_; }
    void set_rates(const ActualRatesConfig& r) noexcept { rates_ = r; }
    void set_cutoff(float hz) noexcept { filter_.set_cutoff(hz); }

private:
    [[nodiscard]] float normalize(float raw) const noexcept {
        float norm = 0.0f;
        if (raw >= calib_.raw_center) {
            const float span = calib_.raw_max - calib_.raw_center;
            if (span > 1e-3f) {
                norm = (raw - calib_.raw_center) / span;
            }
        } else {
            const float span = calib_.raw_center - calib_.raw_min;
            if (span > 1e-3f) {
                norm = (raw - calib_.raw_center) / span;
            }
        }
        return std::clamp(norm, -1.0f, 1.0f);
    }

    [[nodiscard]] float apply_deadband(float norm) const noexcept {
        const float sign = (norm >= 0.0f) ? 1.0f : -1.0f;
        const float abs_val = std::abs(norm);

        if (abs_val <= calib_.center_deadband) {
            return 0.0f;
        }
        if (abs_val >= (1.0f - calib_.end_deadband)) {
            return sign * 1.0f;
        }

        const float active_range = 1.0f - calib_.center_deadband - calib_.end_deadband;
        if (active_range < 1e-3f) {
            return 0.0f;
        }
        return sign * ((abs_val - calib_.center_deadband) / active_range);
    }

    [[nodiscard]] float calculate_actual_rate(float stick_pos) const noexcept {
        const float sign = (stick_pos >= 0.0f) ? 1.0f : -1.0f;
        const float x = std::abs(stick_pos);

        const float x5 = x * x * x * x * x;
        const float curve = x * (1.0f - rates_.expo) + x5 * rates_.expo;

        const float center_part = x * rates_.center_rate;
        const float max_part = (rates_.max_rate - rates_.center_rate) * curve;
        return sign * (center_part + max_part);
    }

    StickCalibration calib_;
    ActualRatesConfig rates_;
    RcSmoothingFilter filter_;
};

} // namespace flight_control
```
:::

## Інженерні пастки та обробка крайових випадків

Під час розробки та інтеграції бібліотеки в прошивку реального часу необхідно враховувати типові пастки:

1. **Асиметрія плечей калібрування:**
   Наївна нормалізація виду `(raw - 1500) / 500` призводить до несиметричної поведінки. Через механічні допуски лівий упор може бути на відліку 985, а правий — на 2018. За єдиного знаменника в один бік стик ніколи не досягне 100% (недоліт), а в інший — насититься за 5% до упору (рання мертва зона на краю). Роздільне масштабування лівого та правого напівдіапазонів є обов'язковим.

2. **Нульове ділення в мертвій зоні:**
   Якщо сума `center_deadband + end_deadband >= 1.0`, активний робочий діапазон `active_range` перетворюється на нуль або від'ємне число. Будь-яка спроба ділення без перевірки порогу `active_range > 1e-3f` призведе до генерації нескінченності `inf` або `NaN`, що миттєво зруйнує обчислення в контурі PID.

3. **Стрибки інтервалу часу `dt` при втраті радіопакетів:**
   Якщо радіолінк втрачає пакети або працює в адаптивному режимі динамічної зміни частоти (наприклад, ExpressLRS при переході з 500 Гц на 250 Гц чи 50 Гц), період `dt` між новими даними збільшується у 2–10 разів. Якщо фільтр PT1 використовує статичний захардкоджений коефіцієнт `alpha`, сигнал почне запізнюватися або пропускати сходинки. Динамічний перерахунок `alpha` від реального `dt_seconds` є ключовим для стабільності траєкторії.

## Оптимізація обчислювальної складності на мікроконтролерах

На 32-бітних мікроконтролерах без апаратного блоку FPU (наприклад, ARM Cortex-M0+ або Cortex-M3) операції з числами з плаваючою комою `float` виконуються програмною емуляцією, що забирає десятки тактів процесора на кожне множення.

Для мінімізації навантаження у критичних циклах контуру керування застосовують такі оптимізації:

- **Піднесення до 5-го степеня через послідовні множення:**
  Вираз `x⁵` обчислюється через збереження проміжних квадратів:
  ```
  x2 = x * x
  x4 = x2 * x2
  x5 = x4 * x
  ```
  Це скорочує кількість операцій множення до трьох замість виклику важкої бібліотечної функції `powf(x, 5.0f)`, яка потребує сотень тактів і може підтягувати важкі таблиці трансцендентних функцій у флеш-пам'ять.

- **Попередній розрахунок констант фільтра:**
  Якщо частота дискретизації контуру PID є фіксованою (наприклад, 4 кГц, dt = 250 мкс), коефіцієнт `alpha` можна розраховувати лише під час зміни частоти зрізу в меню налаштувань, усуваючи операцію ділення з кожного циклу обробки.

## Методика тестування та валідація на симуляторі

Перед інтеграцією алгоритму в польотний контролер бібліотека проходить верифікацію за допомогою набору синтетичних тестів:

1. **Тест нульового спокою (Zero Rest Test):**
   На вхід подаються відліки в діапазоні `raw_center ± deadband`. Тест перевіряє, що вихідна кутова швидкість строго дорівнює `0.000 deg/s` без жодного числового дрейфу чи втрати молодших бітів.

2. **Тест граничного насичення (Boundary Saturation Test):**
   На вхід подаються значення з екстремальними шумами поза межами діапазону (наприклад, `raw = -500` або `raw = 5000`). Тест гарантує, що функція повертає рівно `±max_rate` без переповнення змінних чи генерації `NaN`.

3. **Тест перехідної характеристики (Step Response Test):**
   Подається миттєвий стрибок стіка з 0 у +1.0. Аналізується реакція фільтра PT1: час наростання до рівня 63.2% повинен строго відповідати теоретичній постійній часу `τ = 1 / (2π · f_cutoff)`, а перерегулювання (overshoot) має бути строго відсутнім.

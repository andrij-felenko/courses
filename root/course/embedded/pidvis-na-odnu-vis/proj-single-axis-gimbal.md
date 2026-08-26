# ⚙️ Стендовий стабілізатор горизонту на одну вісь: повна прошивка на C та C++

Одноосьовий стабілізуючий підвіс (англ. *single-axis gimbal stabilizer*) вимагає детермінованого контуру реального часу. Навіть найточніший алгоритм фільтрації та розрахунку ПІД виявиться марним, якщо виклик функції запізнюється на кілька мілісекунд, нуль гіроскопа не відкалібровано перед пуском, або інтегратор регулятора загнано в насичення під час механічного упору.

Тут наведено закінчений стендовий проєкт керування одноосьовим підвісом: зчитування сирих даних 6-осьового IMU, процедура калібрування зсуву гіроскопа з контролем нерухомості, дискретний комплементарний фільтр, ПІД-регулятор із динамічним затисканням інтегратора (Anti-Windup Clamping) та фільтрацією похідної за вимірюванням (Derivative on Measurement), а також перетворення виходу в тривалість імпульсу ШІМ для сервоприводу.

## Архітектура модулів та обчислювальний конвеєр

Прошивка розділена на ізольовані структури даних та послідовні кроки обчислювального конвеєра:

```
[Сирі покази IMU] ──> [Віднімання зсуву гіроскопа] ──> [Комплементарний фільтр]
                                                               │
                                                               ▼ (кут θ_filt, швидкість ω)
[Цільовий кут 0°] ───────────────────────────────────> [ПІД з Anti-Windup & LPF D]
                                                               │
                                                               ▼ (кут керування серво)
                                                       [Генератор ШІМ 1.0–2.0 мс]
```

1. **Калібрування нуля та дисперсійний тест (`gimbal_calibrate_gyro`):** під час запуску апарат перебуває у стані спокою протягом 1–2 секунд. Алгоритм накопичує 500 вибірок кутової швидкості гіроскопа, обчислює середнє арифметичне значення постійного зміщення (bias `b_0`) та перевіряє дисперсію вибірки: якщо дисперсія перевищує поріг шуму спокою, калібрування бракується як спроба старту в русі.
2. **Оцінка орієнтації (`comp_filter_update`):** зчитуються кутова швидкість осі обертання `ω` (з відніманням `b_0`) та проєкції вектора прискорення `a_y, a_z`. Розраховується нахил за акселерометром через `atan2f(a_y, a_z)`. Комплементарний фільтр поєднує інтегрування гіроскопа та поправку акселерометра з коефіцієнтом `α ≈ 0.98` на частоті 200 Гц (`Δt = 0.005` с).
3. **Регулювання (`pid_update`):** помилка положення обчислюється як `e = θ_target - θ_filt`. Пропорційна складова формує миттєвий відгук. Диференціальна ланка спирається на виміряну швидкість гіроскопа `-ω`, згладжену фільтром низьких частот першого порядку. Інтегральна складова накопичує статичну похибку, проте блокує інтегрування (Clamping), якщо вихід регулятора досяг межі ходу сервоприводу.
4. **Виконавчий привід (`servo_output_map`):** вихідний кут обмежується фізичним діапазоном сервоприводу ([−45°, +45°] або [0°, 180°]) та транслюється у тривалість імпульсу стандарту RC-серво (1000…2000 мкс).

## Покрокове чисельне простеження одного такту керування

Розглянемо числовий стан системи на одному конкретному такті керування (`k = 100`, період `Δt = 0.005 с`):

- **Вхідні дані давача:** кутова швидкість гіроскопа `raw_gyro = +12.3°/с`, каліброване зміщення `b_0 = +0.3°/с`, прискорення `a_y = 0.1736 g`, `a_z = 0.9848 g`.
- **Попередній стан фільтра:** `θ_filt[k-1] = -1.20°`.
- **Крок 1 (Очищення швидкості):** `ω = 12.3 - 0.3 = +12.0°/с`.
- **Крок 2 (Передбачення інтегралом):** `θ_pred = -1.20 + 12.0 · 0.005 = -1.14°`.
- **Крок 3 (Кут за акселерометром):** `θ_acc = atan2(0.1736, 0.9848) · (180 / π) = 10.00°`.
- **Крок 4 (Комплементарне злиття, α = 0.98):**
  `θ_filt[k] = 0.98 · (-1.14°) + 0.02 · (+10.00°) = -1.1172° + 0.2000° = -0.9172°`.
- **Крок 5 (Похибка ПІД, ціль 0°):** `e[k] = 0.0 - (-0.9172) = +0.9172°`.
- **Крок 6 (П-ланка, Kp = 2.0):** `P = 2.0 · 0.9172 = +1.8344°`.
- **Крок 7 (Д-ланка за гіроскопом, Kd = 0.08, швидкість +12.0°/с):** `D = -0.08 · 12.0 = -0.9600°`.
- **Крок 8 (І-ланка, Ki = 0.5, I_prev = 0.10°):** `ΔI = 0.5 · 0.9172 · 0.005 = +0.00229°`, новий `I = 0.1023°`.
- **Крок 9 (Сумарний вихід):** `u = 1.8344 + 0.1023 - 0.9600 = +0.9767°`.
- **Крок 10 (ШІМ-мапування):** тривалість імпульсу `pulse = 1500 + 0.9767 · (500 / 45) = 1500 + 10.85 = 1511 мкс`.

Привід отримує імпульс 1511 мкс і повертає вал рівно настільки, щоб компенсувати відхилення без перерегулювання.

## Реалізація прошивки

:::tabs
```c
/* ============================================================================
 * gimbal_controller.h / gimbal_controller.c
 * Модуль одноосьового гіроскопічного підвісу на чистому C (C99/C11)
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define GIMBAL_DT_SEC          0.005f   /* Крок такту 200 Гц (5 мс) */
#define GIMBAL_SERVO_MIN_US    1000.0f  /* Мінімальний імпульс ШІМ (мкс) */
#define GIMBAL_SERVO_MID_US    1500.0f  /* Нейтральне положення 0° (мкс) */
#define GIMBAL_SERVO_MAX_US    2000.0f  /* Максимальний імпульс ШІМ (мкс) */
#define GIMBAL_MAX_ANGLE_DEG   45.0f    /* Межа ходу шарніра ±45° */
#define GIMBAL_MAX_BIAS_VAR    0.25f    /* Максимальна допустима дисперсія шуму (°/с)² */

/* Стан комплементарного фільтра */
typedef struct {
    float angle_deg;    /* Відфільтрована оцінка кута (градуси) */
    float alpha;        /* Ваговий коефіцієнт довіри до гіроскопа */
} CompFilter;

/* Стан та налаштування ПІД-регулятора */
typedef struct {
    /* Коефіцієнти підсилення */
    float kp;
    float ki;
    float kd;

    /* Межі насичення керування */
    float out_min;
    float out_max;

    /* Стан інтегратора та фільтра похідної */
    float integrator;
    float d_lpf_state;
    float d_lpf_alpha;  /* Коефіцієнт ФНЧ для D-терму */
} GimbalPID;

/* Головна структура одноосьового стабілізатора */
typedef struct {
    CompFilter filter;
    GimbalPID  pid;
    float      gyro_bias_dps;  /* Зсув нуля гіроскопа (°/с) */
    bool       is_calibrated;
} SingleAxisGimbal;

/* Ініціалізація компонентів підвісу */
void gimbal_init(SingleAxisGimbal *gimbal, float alpha, float kp, float ki, float kd, float d_cutoff_hz)
{
    gimbal->filter.angle_deg = 0.0f;
    gimbal->filter.alpha     = alpha;

    gimbal->pid.kp = kp;
    gimbal->pid.ki = ki;
    gimbal->pid.kd = kd;
    gimbal->pid.out_min = -GIMBAL_MAX_ANGLE_DEG;
    gimbal->pid.out_max =  GIMBAL_MAX_ANGLE_DEG;
    gimbal->pid.integrator = 0.0f;
    gimbal->pid.d_lpf_state = 0.0f;

    /* Розрахунок коефіцієнта ФНЧ 1-го порядку для D-ланки: beta = dt / (dt + RC) */
    if (d_cutoff_hz > 0.0f) {
        float rc = 1.0f / (2.0f * 3.14159265f * d_cutoff_hz);
        gimbal->pid.d_lpf_alpha = GIMBAL_DT_SEC / (GIMBAL_DT_SEC + rc);
    } else {
        gimbal->pid.d_lpf_alpha = 1.0f; /* Без фільтрації */
    }

    gimbal->gyro_bias_dps = 0.0f;
    gimbal->is_calibrated = false;
}

/* Калібрування зміщення гіроскопа з перевіркою стаціонарності вибірки */
bool gimbal_calibrate_gyro(SingleAxisGimbal *gimbal, const float *gyro_samples, uint32_t count)
{
    if (count < 10) return false;

    float sum = 0.0f;
    for (uint32_t i = 0; i < count; ++i) {
        sum += gyro_samples[i];
    }
    float mean = sum / (float)count;

    /* Обчислення дисперсії для перевірки нерухомості датчика */
    float var_sum = 0.0f;
    for (uint32_t i = 0; i < count; ++i) {
        float diff = gyro_samples[i] - mean;
        var_sum += diff * diff;
    }
    float variance = var_sum / (float)(count - 1);

    if (variance > GIMBAL_MAX_BIAS_VAR) {
        /* Давач рухався під час калібрування: відхиляємо результат */
        gimbal->is_calibrated = false;
        return false;
    }

    gimbal->gyro_bias_dps = mean;
    gimbal->is_calibrated = true;
    return true;
}

/* Крок комплементарної фільтрації */
float comp_filter_update(CompFilter *f, float raw_gyro_dps, float gyro_bias_dps,
                         float ay, float az, float dt)
{
    /* 1. Компенсована кутова швидкість гіроскопа */
    float rate_dps = raw_gyro_dps - gyro_bias_dps;

    /* 2. Передбачення інтегруванням */
    float pred_angle = f->angle_deg + rate_dps * dt;

    /* 3. Кут нахилу за вектором тяжіння акселерометра */
    float acc_angle_deg = atan2f(ay, az) * (180.0f / 3.14159265f);

    /* 4. Комплементарне злиття */
    f->angle_deg = f->alpha * pred_angle + (1.0f - f->alpha) * acc_angle_deg;

    return f->angle_deg;
}

/* Крок розрахунку ПІД з динамічним Anti-Windup Clamping */
float pid_update(GimbalPID *pid, float setpoint_deg, float current_angle_deg,
                 float measured_rate_dps, float dt)
{
    /* 1. Похибка кута */
    float error = setpoint_deg - current_angle_deg;

    /* 2. Пропорційна ланка */
    float p_term = pid->kp * error;

    /* 3. Диференціальна ланка (Derivative on Measurement) з ФНЧ */
    float d_raw = -measured_rate_dps;
    pid->d_lpf_state += pid->d_lpf_alpha * (d_raw - pid->d_lpf_state);
    float d_term = pid->kd * pid->d_lpf_state;

    /* 4. Попереднє керування без нового інтеграла */
    float u_tentative = p_term + pid->integrator + d_term;

    /* 5. Захист від насичення інтегратора: Clamping Anti-Windup */
    bool is_saturated = false;
    if (u_tentative > pid->out_max || u_tentative < pid->out_min) {
        is_saturated = true;
    }

    /* Інтегруємо лише якщо привід не в насиченні АБО знак помилки протилежний знаку насичення */
    bool same_sign = (u_tentative * error > 0.0f);
    if (!is_saturated || !same_sign) {
        pid->integrator += pid->ki * error * dt;
    }

    /* 6. Повний вихід регулятора із жорстким обмеженням */
    float u_out = p_term + pid->integrator + d_term;
    if (u_out > pid->out_max) u_out = pid->out_max;
    if (u_out < pid->out_min) u_out = pid->out_min;

    return u_out;
}

/* Перерахунок кута відхилення сервоприводу в мікросекунди ШІМ */
uint16_t servo_output_map(float correction_deg)
{
    /* Мапування діапазону [-45°, +45°] на [1000 мкс, 2000 мкс], де 0° = 1500 мкс */
    float us_per_deg = (GIMBAL_SERVO_MAX_US - GIMBAL_SERVO_MIN_US) / (2.0f * GIMBAL_MAX_ANGLE_DEG);
    float pulse_us = GIMBAL_SERVO_MID_US + correction_deg * us_per_deg;

    if (pulse_us < GIMBAL_SERVO_MIN_US) pulse_us = GIMBAL_SERVO_MIN_US;
    if (pulse_us > GIMBAL_SERVO_MAX_US) pulse_us = GIMBAL_SERVO_MAX_US;

    return (uint16_t)(pulse_us + 0.5f);
}

/* Головний крок обробки (викликається кожні 5 мс за перериванням таймера) */
uint16_t gimbal_step(SingleAxisGimbal *gimbal, float raw_gyro_dps, float ay, float az)
{
    /* 1. Оновлення оцінки кута */
    float current_angle = comp_filter_update(&gimbal->filter, raw_gyro_dps,
                                            gimbal->gyro_bias_dps, ay, az, GIMBAL_DT_SEC);

    /* 2. Кутова швидкість за вирахуванням зміщення */
    float rate_dps = raw_gyro_dps - gimbal->gyro_bias_dps;

    /* 3. Уставка стабілізації горизонту (0.0 градусів) */
    float target_angle = 0.0f;

    /* 4. Розрахунок кутової корекції ПІД */
    float correction_deg = pid_update(&gimbal->pid, target_angle, current_angle,
                                      rate_dps, GIMBAL_DT_SEC);

    /* 5. Формування сигналу ШІМ для сервоприводу */
    return servo_output_map(correction_deg);
}
```
```cpp
/* ============================================================================
 * GimbalController.hpp
 * Модуль одноосьового гіропідвісу на ідіоматичному C++20
 * ============================================================================ */

#include <cstdint>
#include <cmath>
#include <span>
#include <algorithm>
#include <numbers>

namespace gimbal {

inline constexpr float DT_SEC        = 0.005f;   // 200 Гц такт
inline constexpr float SERVO_MIN_US  = 1000.0f;
inline constexpr float SERVO_MID_US  = 1500.0f;
inline constexpr float SERVO_MAX_US  = 2000.0f;
inline constexpr float MAX_ANGLE_DEG = 45.0f;
inline constexpr float MAX_BIAS_VAR  = 0.25f;    // (°/с)² поріг спокою

class ComplementaryFilter {
public:
    explicit constexpr ComplementaryFilter(float alpha = 0.98f) noexcept
        : alpha_{alpha}, angle_deg_{0.0f} {}

    [[nodiscard]] float update(float raw_gyro_dps, float gyro_bias_dps,
                               float ay, float az, float dt) noexcept {
        const float rate_dps = raw_gyro_dps - gyro_bias_dps;
        const float pred_angle = angle_deg_ + rate_dps * dt;

        // Кут за акселерометром
        const float acc_angle_deg = std::atan2(ay, az) *
                                   (180.0f / std::numbers::pi_v<float>);

        angle_deg_ = alpha_ * pred_angle + (1.0f - alpha_) * acc_angle_deg;
        return angle_deg_;
    }

    [[nodiscard]] constexpr float angle() const noexcept { return angle_deg_; }
    void reset(float initial_angle = 0.0f) noexcept { angle_deg_ = initial_angle; }

private:
    float alpha_;
    float angle_deg_;
};

class PidController {
public:
    struct Config {
        float kp{1.8f};
        float ki{0.6f};
        float kd{0.08f};
        float out_min{-MAX_ANGLE_DEG};
        float out_max{MAX_ANGLE_DEG};
        float d_cutoff_hz{25.0f};
    };

    explicit PidController(const Config& cfg) noexcept
        : cfg_{cfg} {
        if (cfg_.d_cutoff_hz > 0.0f) {
            const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cfg_.d_cutoff_hz);
            d_lpf_alpha_ = DT_SEC / (DT_SEC + rc);
        } else {
            d_lpf_alpha_ = 1.0f;
        }
    }

    [[nodiscard]] float update(float setpoint_deg, float current_angle_deg,
                               float measured_rate_dps, float dt) noexcept {
        const float error = setpoint_deg - current_angle_deg;
        const float p_term = cfg_.kp * error;

        // Derivative on Measurement + ФНЧ
        const float d_raw = -measured_rate_dps;
        d_lpf_state_ += d_lpf_alpha_ * (d_raw - d_lpf_state_);
        const float d_term = cfg_.kd * d_lpf_state_;

        // Попередній вихід для перевірки насичення
        const float u_tentative = p_term + integrator_ + d_term;
        const bool is_saturated = (u_tentative > cfg_.out_max || u_tentative < cfg_.out_min);
        const bool same_direction = (u_tentative * error > 0.0f);

        // Clamping Anti-Windup
        if (!is_saturated || !same_direction) {
            integrator_ += cfg_.ki * error * dt;
        }

        const float u_out = p_term + integrator_ + d_term;
        return std::clamp(u_out, cfg_.out_min, cfg_.out_max);
    }

    void reset() noexcept {
        integrator_ = 0.0f;
        d_lpf_state_ = 0.0f;
    }

private:
    Config cfg_;
    float  integrator_{0.0f};
    float  d_lpf_state_{0.0f};
    float  d_lpf_alpha_{1.0f};
};

class Stabilizer {
public:
    Stabilizer(float filter_alpha, const PidController::Config& pid_cfg) noexcept
        : filter_{filter_alpha}, pid_{pid_cfg} {}

    [[nodiscard]] bool calibrate_gyro(std::span<const float> static_samples) noexcept {
        if (static_samples.size() < 10) return false;

        float sum = 0.0f;
        for (float val : static_samples) {
            sum += val;
        }
        const float mean = sum / static_cast<float>(static_samples.size());

        float var_sum = 0.0f;
        for (float val : static_samples) {
            const float diff = val - mean;
            var_sum += diff * diff;
        }
        const float variance = var_sum / static_cast<float>(static_samples.size() - 1);

        if (variance > MAX_BIAS_VAR) {
            is_calibrated_ = false;
            return false;
        }

        gyro_bias_dps_ = mean;
        is_calibrated_ = true;
        return true;
    }

    [[nodiscard]] uint16_t process_step(float raw_gyro_dps, float ay, float az) noexcept {
        const float current_angle = filter_.update(raw_gyro_dps, gyro_bias_dps_,
                                                  ay, az, DT_SEC);
        const float rate_dps = raw_gyro_dps - gyro_bias_dps_;

        // Бажаний кут — горизонталь (0°)
        const float correction_deg = pid_.update(0.0f, current_angle, rate_dps, DT_SEC);

        return map_servo_pulse(correction_deg);
    }

    [[nodiscard]] static constexpr uint16_t map_servo_pulse(float angle_deg) noexcept {
        constexpr float us_per_deg = (SERVO_MAX_US - SERVO_MIN_US) / (2.0f * MAX_ANGLE_DEG);
        const float pulse = SERVO_MID_US + angle_deg * us_per_deg;
        const float clamped = std::clamp(pulse, SERVO_MIN_US, SERVO_MAX_US);
        return static_cast<uint16_t>(clamped + 0.5f);
    }

    [[nodiscard]] float estimated_angle() const noexcept { return filter_.angle(); }
    [[nodiscard]] bool is_calibrated() const noexcept { return is_calibrated_; }

private:
    ComplementaryFilter filter_;
    PidController       pid_;
    float               gyro_bias_dps_{0.0f};
    bool                is_calibrated_{false};
};

} // namespace gimbal
```
:::

## Методика стендового тестування та валідації

Для підтвердження якості стабілізації проводять три стандартні лабораторні тести:

1. **Тест перехідної характеристики на сходинку (Step Response Test):**
   При стабільній базі платформу різко відхиляють рукою на кут 15° і відпускають. Через послідовний порт знімають графік кута `θ_filt(t)` з кроком 5 мс. Якісно налаштований контур демонструє аперіодичний або слабоколивальний перехідний процес: перерегулювання не перевищує 5%, а час встановлення (Settling Time до коридору ±0.5°) становить менше 100–120 мс. Якщо графік демонструє понад три повні періоди згасаючих коливань — демпфування `K_d` недостатнє або `K_p` завищений.
2. **Тест придушення кутового збурення бази (Disturbance Rejection Test):**
   Базову платформу підвісу вручну або за допомогою стендового вібростенда розгойдують із частотою 1–3 Гц та амплітудою ±20°. Одночасно записують кут нахилу бази `θ_base(t)` та вихідний кут платформи `θ_load(t)`. Коефіцієнт придушення збурення розраховується як відношення амплітуд `A_load / A_base`. Для правильно скомпенсованої системи залишкове відхилення вантажу не перевищує 0.5°–1.0° (придушення понад 26 дБ).
3. **Тест утримання нульового балансу (Static Zero-Hold):**
   Підвіс залишають у спокої на 10 хвилин. Контролюють дрейф інтегратора та нагрів корпусу сервоприводу. За відсутності зовнішніх збурень середнє значення похибки має строго дорівнювати нулю, а струм споживання не повинен перевищувати струм холостого ходу сервопідсилювача (20–40 мА).

## Інженерні пастки реального стенда та їх подолання

1. **Люфт редуктора та зона нечутливості сервоприводу (Gear Backlash & Deadband):**
   Бюджетні пластикові сервоприводи (SG90, MG90S) мають внутрішню зону нечутливості потенціометра близько 3…5 мкс (0.5°…1.0°). Спроба підняти `K_p` або `K_i` призводить до дрібного високочастотного тремтіння (дребезгу вала) навколо точки балансу. Для усунення тремтіння знижують інтегральну складову та встановлюють програмну мертву зону похибки (Deadzone: якщо `|e| < 0.3°`, вважати `e = 0`).
2. **Просадки напруги живлення сервоприводу (Brownout Reset):**
   Пусковий струм сервоприводу під час різкої зміни напрямку сягає 0.8…1.5 А. Живлення сервоприводу безпосередньо від 5V шини мікроконтролера викликає імпульсне просідання напруги, скидання MCU за сигналом Brownout та циклічне перезавантаження стенда. Сервопривід обов'язково живиться від виділеного стабілізатора (Step-Down BEC) зі спільним заземленням (GND) та згладжувальним електролітичним конденсатором 470…1000 мкФ поруч із роз'ємом.
3. **Механічний резонанс кріплення IMU:**
   Якщо плата давача закріплена на пружній стійці без вібророзв'язки, вібрації мотора потрапляють у смугу пропускання гіроскопа, генеруючи фантомну кутову швидкість. D-ланка підсилює ці високочастотні коливання, перевантажуючи сервопривід. Зріз вбудованого ФНЧ похідної (`d_cutoff_hz`) на рівні 20…30 Гц ефективно гасить резонансні сплески без втрати фази контуру стабілізації.
4. **Зависання шини I2C через електромагнітні завади колектора (Bus Lockup):**
   Іскріння щіток колекторного мотора наводить імпульсні перешкоди на довгі дроти шини I2C. Якщо лінія SDA залипає у низькому рівні (Slave Clock Stretching / Lockup), процесор зависає у нескінченному циклі очікування. У драйвері IMU обов'язково налаштовують апаратний сторожовий таймер (I2C Timeout): при відсутності відповіді протягом 2 мс шина скидається генерацією 9 імпульсів на лінії SCL (I2C Bus Recovery Routine).

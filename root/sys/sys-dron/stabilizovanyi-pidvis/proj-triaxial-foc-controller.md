# Реалізація контролера триосьового стабілізованого підвісу на C та C++

Стабілізація камери на безпілотному літальному апараті вимагає безперервної та узгодженої роботи трьох механічних осей підвісу (Yaw, Roll, Pitch). Кожна вісь приводиться в рух безколекторним двигуном прямого приводу (Direct Drive) з векторним керуванням (FOC) і керується власним каскадним контуром зворотного зв'язку.

У цьому проекті наведено архітектуру мікропрограми контролера підвісу для вбудованих 32-розрядних мікроконтролерів (ARM Cortex-M4/M7, ESP32-S3 або STM32G4). Система містить швидкісний генератор просторово-векторної ШІМ (SVPWM), векторні перетворення Park/Clarke, модуль зчитування абсолютних магнітних енкодерів AS5048A по шині SPI, біквадратний режекторний фільтр (Notch Filter) для пригнічення структурних резонансів, каскадний PID-регулятор із захистом від насичення інтегратора (anti-windup), а також модуль кінематичної розв'язки осей і перемикання режимів стеження (Lock / Follow Mode).

## Структури даних та математичне ядро FOC

Основою швидкісного контуру є точне обчислення електричного кута ротора `θ_e = p · θ_m − θ_zero` (де `p` — кількість пар полюсів, `θ_m` — механічний кут з енкодера, `θ_zero` — калібрувальний нульовий зсув) та перетворення вектора напруги в коефіцієнти заповнення ШІМ трьох напівмостів.

Коливання напруги живлення під навантаженням (наприклад, просідання бортової батареї при різких маневрах дрона) компенсуються нормалізацією модулюючого вектора до миттєвої виміряної напруги шини `v_bus`. Завдяки цьому крутний момент підвісу залишається незмінним протягом усього часу розряду акумулятора.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PI_CONST 3.14159265358979323846f
#define TWO_PI   6.28318530717958647692f
#define ONE_BY_SQRT3 0.57735026919f
#define SQRT3        1.73205080757f

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

typedef struct {
    float duty_a;
    float duty_b;
    float duty_c;
    uint8_t sector;
} SvpwmDuty;

typedef struct {
    float b0, b1, b2;
    float a1, a2;
    float x1, x2;
    float y1, y2;
} BiquadNotchFilter;

typedef struct {
    float kp;
    float ki;
    float kd;
    float integral;
    float prev_error;
    float out_max;
    float i_max;
    float d_filter_alpha; /* Коефіцієнт ФНЧ для похідної */
    float prev_d_filtered;
} PidController;

typedef struct {
    uint8_t pole_pairs;      /* Кількість пар полюсів (11 для 22P або 14 для 28P) */
    float zero_offset_rad;   /* Електричний нульовий зсув енкодера */
    float v_bus;             /* Напруга шини живлення (В) */
    float u_limit;           /* Максимальна амплітуда вихідної напруги */
    
    /* Стан осі */
    float mech_angle_rad;    /* Механічний кут з енкодера */
    float elec_angle_rad;    /* Електричний кут для перетворення Парка */
    float gyro_rate_rad_s;   /* Кутова швидкість з гіроскопа камери */
    
    /* Фільтрація резонансів */
    BiquadNotchFilter notch;
    
    /* Каскадні регулятори */
    PidController pos_pid;   /* Зовнішній контур: кут -> бажана швидкість */
    PidController rate_pid;  /* Внутрішній контур: швидкість -> напруга U_q */
    
    /* Виходи FOC */
    float u_d;
    float u_q;
    SvpwmDuty svpwm;
} GimbalAxis;

/* Нормалізація кута в межі [0, 2π) */
static inline float normalize_angle(float angle) {
    float a = fmodf(angle, TWO_PI);
    return (a >= 0.0f) ? a : (a + TWO_PI);
}

/* Ініціалізація біквадратного режекторного фільтра (Notch Filter) */
void notch_filter_init(BiquadNotchFilter *f, float center_freq_hz, float q_factor, float sample_rate_hz) {
    float omega = 2.0f * PI_CONST * center_freq_hz / sample_rate_hz;
    float sn = sinf(omega);
    float cs = cosf(omega);
    float alpha = sn / (2.0f * q_factor);
    
    float a0 = 1.0f + alpha;
    f->b0 = 1.0f / a0;
    f->b1 = (-2.0f * cs) / a0;
    f->b2 = 1.0f / a0;
    f->a1 = (-2.0f * cs) / a0;
    f->a2 = (1.0f - alpha) / a0;
    
    f->x1 = f->x2 = f->y1 = f->y2 = 0.0f;
}

/* Обробка вибірки через Notch-фільтр */
float notch_filter_update(BiquadNotchFilter *f, float in) {
    float out = f->b0 * in + f->b1 * f->x1 + f->b2 * f->x2 - f->a1 * f->y1 - f->a2 * f->y2;
    f->x2 = f->x1;
    f->x1 = in;
    f->y2 = f->y1;
    f->y1 = out;
    return out;
}

/* Обчислення електричного кута ротора */
void gimbal_axis_update_electrical_angle(GimbalAxis *axis, float raw_mech_angle) {
    axis->mech_angle_rad = raw_mech_angle;
    float elec = ((float)axis->pole_pairs * raw_mech_angle) - axis->zero_offset_rad;
    axis->elec_angle_rad = normalize_angle(elec);
}

/* Генератор просторово-векторної модуляції (SVPWM) */
SvpwmDuty svpwm_generate(float u_alpha, float u_beta, float v_bus) {
    SvpwmDuty out;
    if (v_bus <= 0.01f) {
        out.duty_a = out.duty_b = out.duty_c = 0.5f;
        out.sector = 0;
        return out;
    }
    
    float u_a_norm = u_alpha / v_bus;
    float u_b_norm = u_beta / v_bus;
    
    float v1 = u_b_norm;
    float v2 = (SQRT3 * u_a_norm - u_b_norm) * 0.5f;
    float v3 = (-SQRT3 * u_a_norm - u_b_norm) * 0.5f;
    
    uint8_t sector = 0;
    if (v1 > 0.0f) sector |= 1;
    if (v2 > 0.0f) sector |= 2;
    if (v3 > 0.0f) sector |= 4;
    
    float t1 = 0.0f, t2 = 0.0f;
    float ta = 0.5f, tb = 0.5f, tc = 0.5f;
    
    switch (sector) {
        case 3: /* Сектор 1 (0° .. 60°) */
            t1 = SQRT3 * u_a_norm - u_b_norm;
            t2 = 2.0f * u_b_norm;
            out.sector = 1;
            break;
        case 1: /* Сектор 2 (60° .. 120°) */
            t1 = SQRT3 * u_a_norm + u_b_norm;
            t2 = -SQRT3 * u_a_norm + u_b_norm;
            out.sector = 2;
            break;
        case 5: /* Сектор 3 (120° .. 180°) */
            t1 = 2.0f * u_b_norm;
            t2 = -SQRT3 * u_a_norm - u_b_norm;
            out.sector = 3;
            break;
        case 4: /* Сектор 4 (180° .. 240°) */
            t1 = -SQRT3 * u_a_norm + u_b_norm;
            t2 = -2.0f * u_b_norm;
            out.sector = 4;
            break;
        case 6: /* Сектор 5 (240° .. 300°) */
            t1 = -SQRT3 * u_a_norm - u_b_norm;
            t2 = SQRT3 * u_a_norm - u_b_norm;
            out.sector = 5;
            break;
        case 2: /* Сектор 6 (300° .. 360°) */
            t1 = -2.0f * u_b_norm;
            t2 = SQRT3 * u_a_norm + u_b_norm;
            out.sector = 6;
            break;
        default:
            t1 = 0.0f;
            t2 = 0.0f;
            out.sector = 0;
            break;
    }
    
    float t_sum = t1 + t2;
    if (t_sum > 1.0f) {
        t1 /= t_sum;
        t2 /= t_sum;
    }
    
    float t0 = 1.0f - t1 - t2;
    float t_half0 = t0 * 0.5f;
    
    switch (out.sector) {
        case 1:
            ta = t1 + t2 + t_half0;
            tb = t2 + t_half0;
            tc = t_half0;
            break;
        case 2:
            ta = t1 + t_half0;
            tb = t1 + t2 + t_half0;
            tc = t_half0;
            break;
        case 3:
            ta = t_half0;
            tb = t1 + t2 + t_half0;
            tc = t2 + t_half0;
            break;
        case 4:
            ta = t_half0;
            tb = t1 + t_half0;
            tc = t1 + t2 + t_half0;
            break;
        case 5:
            ta = t2 + t_half0;
            tb = t_half0;
            tc = t1 + t2 + t_half0;
            break;
        case 6:
            ta = t1 + t2 + t_half0;
            tb = t_half0;
            tc = t1 + t_half0;
            break;
        default:
            ta = tb = tc = 0.5f;
            break;
    }
    
    out.duty_a = ta;
    out.duty_b = tb;
    out.duty_c = tc;
    return out;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <numbers>
#include <array>
#include <algorithm>

namespace gimbal {

constexpr float PI = std::numbers::pi_v<float>;
constexpr float TWO_PI = 2.0f * PI;
constexpr float SQRT3 = 1.73205080757f;

struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct SvpwmDuty {
    float duty_a{0.5f};
    float duty_b{0.5f};
    float duty_c{0.5f};
    uint8_t sector{0};
};

class BiquadNotchFilter {
public:
    void init(float center_freq_hz, float q_factor, float sample_rate_hz) noexcept {
        const float omega = 2.0f * PI * center_freq_hz / sample_rate_hz;
        const float sn = std::sin(omega);
        const float cs = std::cos(omega);
        const float alpha = sn / (2.0f * q_factor);

        const float a0 = 1.0f + alpha;
        b0_ = 1.0f / a0;
        b1_ = (-2.0f * cs) / a0;
        b2_ = 1.0f / a0;
        a1_ = (-2.0f * cs) / a0;
        a2_ = (1.0f - alpha) / a0;

        reset();
    }

    float update(float in) noexcept {
        const float out = b0_ * in + b1_ * x1_ + b2_ * x2_ - a1_ * y1_ - a2_ * y2_;
        x2_ = x1_;
        x1_ = in;
        y2_ = y1_;
        y1_ = out;
        return out;
    }

    void reset() noexcept {
        x1_ = x2_ = y1_ = y2_ = 0.0f;
    }

private:
    float b0_{1.0f}, b1_{0.0f}, b2_{0.0f};
    float a1_{0.0f}, a2_{0.0f};
    float x1_{0.0f}, x2_{0.0f};
    float y1_{0.0f}, y2_{0.0f};
};

class PidController {
public:
    PidController(float kp, float ki, float kd, float out_max, float i_max, float d_alpha = 0.8f)
        : kp_(kp), ki_(ki), kd_(kd), out_max_(out_max), i_max_(i_max), d_alpha_(d_alpha) {}

    float update(float target, float current, float dt) noexcept {
        float error = target - current;
        
        float p_term = kp_ * error;
        
        // Anti-windup clamping
        integral_ += error * dt;
        integral_ = std::clamp(integral_, -i_max_, i_max_);
        float i_term = ki_ * integral_;
        
        // Диференціювання з ФНЧ
        float safe_dt = (dt > 1e-6f) ? dt : 1e-6f;
        float raw_d = (error - prev_error_) / safe_dt;
        prev_error_ = error;
        prev_d_filtered_ = d_alpha_ * prev_d_filtered_ + (1.0f - d_alpha_) * raw_d;
        float d_term = kd_ * prev_d_filtered_;
        
        float output = p_term + i_term + d_term;
        return std::clamp(output, -out_max_, out_max_);
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_error_ = 0.0f;
        prev_d_filtered_ = 0.0f;
    }

private:
    float kp_;
    float ki_;
    float kd_;
    float integral_{0.0f};
    float prev_error_{0.0f};
    float out_max_;
    float i_max_;
    float d_alpha_;
    float prev_d_filtered_{0.0f};
};

class FocDriver {
public:
    static SvpwmDuty generate_svpwm(float u_alpha, float u_beta, float v_bus) noexcept {
        SvpwmDuty out;
        if (v_bus <= 0.01f) return out;

        const float u_a_norm = u_alpha / v_bus;
        const float u_b_norm = u_beta / v_bus;

        const float v1 = u_b_norm;
        const float v2 = (SQRT3 * u_a_norm - u_b_norm) * 0.5f;
        const float v3 = (-SQRT3 * u_a_norm - u_b_norm) * 0.5f;

        uint8_t sector_mask = 0;
        if (v1 > 0.0f) sector_mask |= 1;
        if (v2 > 0.0f) sector_mask |= 2;
        if (v3 > 0.0f) sector_mask |= 4;

        float t1 = 0.0f, t2 = 0.0f;

        switch (sector_mask) {
            case 3:
                t1 = SQRT3 * u_a_norm - u_b_norm;
                t2 = 2.0f * u_b_norm;
                out.sector = 1;
                break;
            case 1:
                t1 = SQRT3 * u_a_norm + u_b_norm;
                t2 = -SQRT3 * u_a_norm + u_b_norm;
                out.sector = 2;
                break;
            case 5:
                t1 = 2.0f * u_b_norm;
                t2 = -SQRT3 * u_a_norm - u_b_norm;
                out.sector = 3;
                break;
            case 4:
                t1 = -SQRT3 * u_a_norm + u_b_norm;
                t2 = -2.0f * u_b_norm;
                out.sector = 4;
                break;
            case 6:
                t1 = -SQRT3 * u_a_norm - u_b_norm;
                t2 = SQRT3 * u_a_norm - u_b_norm;
                out.sector = 5;
                break;
            case 2:
                t1 = -2.0f * u_b_norm;
                t2 = SQRT3 * u_a_norm + u_b_norm;
                out.sector = 6;
                break;
            default:
                out.sector = 0;
                return out;
        }

        const float t_sum = t1 + t2;
        if (t_sum > 1.0f) {
            t1 /= t_sum;
            t2 /= t_sum;
        }

        const float t0 = 1.0f - t1 - t2;
        const float t_half0 = t0 * 0.5f;

        switch (out.sector) {
            case 1:
                out.duty_a = t1 + t2 + t_half0;
                out.duty_b = t2 + t_half0;
                out.duty_c = t_half0;
                break;
            case 2:
                out.duty_a = t1 + t_half0;
                out.duty_b = t1 + t2 + t_half0;
                out.duty_c = t_half0;
                break;
            case 3:
                out.duty_a = t_half0;
                out.duty_b = t1 + t2 + t_half0;
                out.duty_c = t2 + t_half0;
                break;
            case 4:
                out.duty_a = t_half0;
                out.duty_b = t1 + t_half0;
                out.duty_c = t1 + t2 + t_half0;
                break;
            case 5:
                out.duty_a = t2 + t_half0;
                out.duty_b = t_half0;
                out.duty_c = t1 + t2 + t_half0;
                break;
            case 6:
                out.duty_a = t1 + t2 + t_half0;
                out.duty_b = t_half0;
                out.duty_c = t1 + t_half0;
                break;
            default:
                break;
        }
        return out;
    }
};

} // namespace gimbal
```
:::

## Модуль магнітного енкодера AS5048A по шині SPI

Для точного розрахунку електричного кута ротора потрібен абсолютний кутовий енкодер високої роздільної здатності. Сенсор AS5048A передає 14-бітні кутові відліки (16384 дискрети на оберт, крок ~0.022°) через інтерфейс SPI на тактовій частоті до 10 МГц. 

Кожен 16-бітний кадр відповіді містить старший біт парності (Even Parity) та прапорець апаратної діагностики (Error Flag). Помилка виникає, якщо відстань між чіпом та діаметрально намагніченим неодимовим магнітом виходить за межі 0.5–2.5 мм, або напруженість магнітного поля падає нижче 30 мТл.

:::tabs
```c
#define AS5048A_CMD_READ_ANGLE 0x3FFF
#define AS5048A_PARITY_BIT     0x8000
#define AS5048A_ERROR_FLAG     0x4000
#define AS5048A_DATA_MASK      0x3FFF

/* Розрахунок біта парності (Even Parity) */
static uint16_t as5048a_calc_even_parity(uint16_t value) {
    uint16_t count = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        if (value & (1 << i)) count++;
    }
    return (count & 1) ? AS5048A_PARITY_BIT : 0;
}

/* Декодування пакета кута з енкодера AS5048A */
bool as5048a_parse_response(uint16_t raw_response, float *angle_rad_out) {
    uint16_t parity = as5048a_calc_even_parity(raw_response & ~AS5048A_PARITY_BIT);
    if ((raw_response & AS5048A_PARITY_BIT) != parity) {
        return false; /* Помилка парності кадру SPI */
    }
    
    if (raw_response & AS5048A_ERROR_FLAG) {
        return false; /* Помилка сенсора: втрата магніту або вихід за межі поля */
    }
    
    uint16_t raw_data = raw_response & AS5048A_DATA_MASK;
    *angle_rad_out = ((float)raw_data / 16384.0f) * TWO_PI;
    return true;
}
```
```cpp
#include <cstdint>
#include <bit>
#include <expected>
#include <numbers>

namespace gimbal {

enum class EncoderError {
    ParityMismatch,
    SensorFault,
    SpiTimeout
};

class As5048aParser {
public:
    static constexpr uint16_t CMD_READ_ANGLE = 0x3FFF;
    static constexpr uint16_t PARITY_BIT     = 0x8000;
    static constexpr uint16_t ERROR_FLAG     = 0x4000;
    static constexpr uint16_t DATA_MASK      = 0x3FFF;

    static std::expected<float, EncoderError> parse_response(uint16_t raw_response) noexcept {
        const uint16_t payload = raw_response & ~PARITY_BIT;
        const bool is_odd = (std::popcount(payload) % 2) != 0;
        const bool frame_parity_bit = (raw_response & PARITY_BIT) != 0;

        if (is_odd != frame_parity_bit) {
            return std::unexpected(EncoderError::ParityMismatch);
        }

        if ((raw_response & ERROR_FLAG) != 0) {
            return std::unexpected(EncoderError::SensorFault);
        }

        const uint16_t raw_ticks = raw_response & DATA_MASK;
        const float angle_rad = (static_cast<float>(raw_ticks) / 16384.0f) * (2.0f * std::numbers::pi_v<float>);
        return angle_rad;
    }
};

} // namespace gimbal
```
:::

## Каскадний контур керування та триосьова координація

Повний контролер реалізує трирівневу ієрархію розрахунків:
1. **Зовнішній контур положення (500 Гц):** відстежує цільові кути орієнтації камери та обчислює помилку орієнтації за найкоротшою дугою кола;
2. **Середній контур кутової швидкості (1000–2000 Гц):** порівнює швидкість з високочастотного гіроскопа камери, фільтрує вібрації режекторним фільтром і формує цільовий момент / напругу `u_q`;
3. **Внутрішній векторний контур FOC (20–30 кГц):** виконує зворотне перетворення Парка та синтезує комутацію ключів інвертора.

У контурі осі Pitch обов'язково застосовується пряма компенсація гравітаційного моменту (Feedforward). Якщо центр ваги камери зміщений відносно осі обертання на плече `r_cg`, виникає постійний перекидний момент `τ_g = m · g · r_cg · cos(θ_pitch)`. Без прямої компенсації інтегратор PID-регулятора мусив би постійно накопичувати статичну помилку, що знижувало б швидкодію підвісу під час різких поворотів.

:::tabs
```c
typedef struct {
    GimbalAxis yaw_axis;
    GimbalAxis roll_axis;
    GimbalAxis pitch_axis;
    
    float target_yaw_rad;
    float target_roll_rad;
    float target_pitch_rad;
    
    float est_yaw_rad;
    float est_roll_rad;
    float est_pitch_rad;
    
    /* Пряма гравітаційна компенсація (Feedforward) */
    float pitch_gravity_ff_v;
} TriaxialGimbalController;

/* Крок швидкісного контуру FOC */
void gimbal_controller_foc_step(GimbalAxis *axis) {
    float s_e = sinf(axis->elec_angle_rad);
    float c_e = cosf(axis->elec_angle_rad);
    
    float u_alpha = -axis->u_q * s_e + axis->u_d * c_e;
    float u_beta  =  axis->u_q * c_e + axis->u_d * s_e;
    
    axis->svpwm = svpwm_generate(u_alpha, u_beta, axis->v_bus);
}

/* Крок каскадного регулятора осі */
void gimbal_axis_cascade_update(GimbalAxis *axis, float target_angle, float current_angle, 
                                float gyro_rate, float feedforward_voltage, float dt) {
    float error_angle = target_angle - current_angle;
    
    while (error_angle > PI_CONST)  error_angle -= TWO_PI;
    while (error_angle < -PI_CONST) error_angle += TWO_PI;
    
    float des_rate = axis->pos_pid.kp * error_angle;
    if (des_rate > axis->pos_pid.out_max) des_rate = axis->pos_pid.out_max;
    if (des_rate < -axis->pos_pid.out_max) des_rate = -axis->pos_pid.out_max;
    
    /* Фільтрація сигналу швидкості від структурного резонансу */
    float filtered_gyro = notch_filter_update(&axis->notch, gyro_rate);
    float rate_error = des_rate - filtered_gyro;
    
    float p_term = axis->rate_pid.kp * rate_error;
    
    axis->rate_pid.integral += rate_error * dt;
    if (axis->rate_pid.integral > axis->rate_pid.i_max) axis->rate_pid.integral = axis->rate_pid.i_max;
    if (axis->rate_pid.integral < -axis->rate_pid.i_max) axis->rate_pid.integral = -axis->rate_pid.i_max;
    float i_term = axis->rate_pid.ki * axis->rate_pid.integral;
    
    float raw_d = (rate_error - axis->rate_pid.prev_error) / dt;
    axis->rate_pid.prev_error = rate_error;
    axis->rate_pid.prev_d_filtered = axis->rate_pid.d_filter_alpha * axis->rate_pid.prev_d_filtered + 
                                     (1.0f - axis->rate_pid.d_filter_alpha) * raw_d;
    float d_term = axis->rate_pid.kd * axis->rate_pid.prev_d_filtered;
    
    float u_q_cmd = p_term + i_term + d_term + feedforward_voltage;
    
    if (u_q_cmd > axis->u_limit) u_q_cmd = axis->u_limit;
    if (u_q_cmd < -axis->u_limit) u_q_cmd = -axis->u_limit;
    
    axis->u_d = 0.0f;
    axis->u_q = u_q_cmd;
}

/* Оновлення всіх трьох осей */
void triaxial_gimbal_update(TriaxialGimbalController *gimbal, Vec3 gyro_rad_s, float dt) {
    /* Гравітаційна компенсація зміщення центру мас камери для осі Pitch */
    float pitch_ff = gimbal->pitch_gravity_ff_v * cosf(gimbal->est_pitch_rad);
    
    gimbal_axis_cascade_update(&gimbal->yaw_axis, gimbal->target_yaw_rad, gimbal->est_yaw_rad, gyro_rad_s.z, 0.0f, dt);
    gimbal_controller_foc_step(&gimbal->yaw_axis);
    
    gimbal_axis_cascade_update(&gimbal->roll_axis, gimbal->target_roll_rad, gimbal->est_roll_rad, gyro_rad_s.x, 0.0f, dt);
    gimbal_controller_foc_step(&gimbal->roll_axis);
    
    gimbal_axis_cascade_update(&gimbal->pitch_axis, gimbal->target_pitch_rad, gimbal->est_pitch_rad, gyro_rad_s.y, pitch_ff, dt);
    gimbal_controller_foc_step(&gimbal->pitch_axis);
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <numbers>
#include <algorithm>

namespace gimbal {

struct GimbalConfig {
    uint8_t pole_pairs{11};
    float zero_offset_rad{0.0f};
    float v_bus{12.0f};
    float u_limit{6.0f};
    float notch_freq_hz{220.0f};
    float notch_q{2.5f};
};

class AxisController {
public:
    AxisController(const GimbalConfig& cfg, 
                   const PidController& pos_pid, 
                   const PidController& rate_pid,
                   float sample_rate_hz = 1000.0f)
        : config_(cfg), pos_pid_(pos_pid), rate_pid_(rate_pid) {
        notch_.init(config_.notch_freq_hz, config_.notch_q, sample_rate_hz);
    }

    void update_feedback(float raw_mech_angle, float gyro_rate_rad_s) noexcept {
        mech_angle_rad_ = raw_mech_angle;
        gyro_rate_rad_s_ = gyro_rate_rad_s;
        
        float elec = (static_cast<float>(config_.pole_pairs) * raw_mech_angle) - config_.zero_offset_rad;
        float a = std::fmod(elec, 2.0f * std::numbers::pi_v<float>);
        elec_angle_rad_ = (a >= 0.0f) ? a : (a + 2.0f * std::numbers::pi_v<float>);
    }

    void update_cascade(float target_angle, float current_estimated_angle, float feedforward_v, float dt) noexcept {
        float error_angle = target_angle - current_estimated_angle;
        constexpr float PI = std::numbers::pi_v<float>;
        constexpr float TWO_PI = 2.0f * PI;
        while (error_angle > PI)  error_angle -= TWO_PI;
        while (error_angle < -PI) error_angle += TWO_PI;

        float des_rate = pos_pid_.update(target_angle, current_estimated_angle, dt);

        float filtered_gyro = notch_.update(gyro_rate_rad_s_);
        float u_q_cmd = rate_pid_.update(des_rate, filtered_gyro, dt) + feedforward_v;
        
        u_q_ = std::clamp(u_q_cmd, -config_.u_limit, config_.u_limit);
        u_d_ = 0.0f;

        const float s_e = std::sin(elec_angle_rad_);
        const float c_e = std::cos(elec_angle_rad_);

        const float u_alpha = -u_q_ * s_e + u_d_ * c_e;
        const float u_beta  =  u_q_ * c_e + u_d_ * s_e;

        svpwm_ = FocDriver::generate_svpwm(u_alpha, u_beta, config_.v_bus);
    }

    [[nodiscard]] const SvpwmDuty& get_duty() const noexcept { return svpwm_; }
    [[nodiscard]] float get_mech_angle() const noexcept { return mech_angle_rad_; }

private:
    GimbalConfig config_;
    PidController pos_pid_;
    PidController rate_pid_;
    BiquadNotchFilter notch_;
    
    float mech_angle_rad_{0.0f};
    float elec_angle_rad_{0.0f};
    float gyro_rate_rad_s_{0.0f};
    
    float u_d_{0.0f};
    float u_q_{0.0f};
    SvpwmDuty svpwm_{};
};

class TriaxialGimbalSystem {
public:
    TriaxialGimbalSystem(AxisController yaw, AxisController roll, AxisController pitch, float pitch_gravity_ff = 0.8f)
        : yaw_(yaw), roll_(roll), pitch_(pitch), pitch_gravity_ff_(pitch_gravity_ff) {}

    void process(const Vec3& targets, const Vec3& estimated_attitude, const Vec3& gyro_rates, float dt) {
        float pitch_ff = pitch_gravity_ff_ * std::cos(estimated_attitude.y);
        
        yaw_.update_cascade(targets.z, estimated_attitude.z, 0.0f, dt);
        roll_.update_cascade(targets.x, estimated_attitude.x, 0.0f, dt);
        pitch_.update_cascade(targets.y, estimated_attitude.y, pitch_ff, dt);
    }

    [[nodiscard]] const AxisController& yaw() const noexcept { return yaw_; }
    [[nodiscard]] const AxisController& roll() const noexcept { return roll_; }
    [[nodiscard]] const AxisController& pitch() const noexcept { return pitch_; }

    AxisController& yaw() noexcept { return yaw_; }
    AxisController& roll() noexcept { return roll_; }
    AxisController& pitch() noexcept { return pitch_; }

private:
    AxisController yaw_;
    AxisController roll_;
    AxisController pitch_;
    float pitch_gravity_ff_{0.8f};
};

} // namespace gimbal
```
:::

## Калібрування електричного нуля та захист від збоїв

Під час першого запуску двигуна підвісу зв'язок між механічним нулем енкодера та початком відліку магнітного поля ротора є довільним. Якщо подати струм без калібрувального зсуву `zero_offset_rad`, вектор струму `u_q` виявиться спрямованим не під кутом 90° до магнітів ротора, а під випадковим кутом. Це спричиняє або повну відсутність корисного моменту, або шалений паразитний нагрів через надлишковий потік осі `d`, або самовільний зрив осі в автоколивання.

### Процедура автоматичного вирівнювання нуля (Zero Offset Calibration)
1. **Примусове позиціонування:** на обмотки мотора подається фіксований вектор напруги `u_d = U_align` (приблизно 20–30% від напруги шини живлення), `u_q = 0` при фіксованому куті `θ_e = 0`.
2. **Заспокоєння ротора:** під дією магнітного поля ротор автоматично притягується до положення найменшого магнітного опору. Контролер вичікує 800–1200 мс для повного згасання механічних коливань.
3. **Фіксація зсуву:** з енкодера зчитується стабільний механічний кут `θ_m_locked`. Калібрувальний зсув обчислюється як: `zero_offset_rad = p · θ_m_locked`.
4. **Перевірка напрямку фаз:** контролер плавно повертає вектор напруги вперед на +90° електричних. Якщо енкодер фіксує рух у зворотний бік, прапорець інверсії напрямку обертання перемикається, або дві фази інвертора міняються програмно місцями.

### Придушення структурного резонансу підвісу
При високих коефіцієнтах підсилення `K_p` контуру кутової швидкості механічна піддатливість тонкостінних карбонових трубок і консольних кронштейнів підвісу утворює замкнений коливальний контур на частотах 180–350 Гц. Простий низькочастотний фільтр (ФНЧ) першого порядку вносить фазове запізнення в робочій смузі, що знижує запас стійкості системи.

Застосування режекторного фільтра другого порядку (Biquad Notch Filter), налаштованого точно на виявлену резонансну пікову частоту, дає змогу ослабити амплітуду на 20–35 дБ у вузькій смузі завширшки 20–40 Гц, зберігаючи фазову чистоту в низькочастотному діапазоні стабілізації (0–50 Гц).

### Синхронізація таймерів ШІМ та переривань FOC
Оновлення коефіцієнтів шпаруватості в регістрах таймера ШІМ повинно відбуватися строго синхронно з моментами перегину лічильника (Overflow/Underflow у режимі Center-Aligned Up-Down). Оновлення регістрів посеред напівперіоду ШІМ спричиняє асиметрію відкриття транзисторів верхнього та нижнього плеча, створюючи різкі імпульсні сплески струму, акустичний свист і високочастотні наведення на шини I2C/SPI сенсорної підсистеми.

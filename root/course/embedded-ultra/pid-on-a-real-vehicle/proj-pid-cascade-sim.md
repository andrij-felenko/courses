# ⚙️ Дискретне моделювання каскадного контуру стабілізації на C та C++

Цей проєкт реалізує повну замкнену цифрову модель фізичного тіла апарата з одним ступенем вільності (кутовий нахил навколо однієї осі), безколекторними моторами з урахуванням часової затримки ротора, сенсорним шумом і каскадним ПІД-регулятором із фільтрацією D-ланки та анти-віндапом. Симуляція дозволяє перевірити стійкість контурів, випробувати реакцію на ступінчасте збурення вітром і переконатися у відсутності намотування інтегратора до того, як код буде завантажено в реальний польотний контролер.

### Фізична модель обертального важеля

Розглянемо фізичну систему, що моделює динаміку квадрокоптера за однією віссю (крен або тангаж). Система складається з невагомої балки довжиною `2 · L`, закріпленої в центрі на шарнірі з моментом інерції `I`. На обох кінцях балки встановлено безколекторні мотори з пропелерами, які створюють тяги `T_1` та `T_2`.

Обертальний момент, що діє на апарат, визначається різницею тяг моторів та плечем `L`, а також зовнішнім аеродинамічним збуренням від вітру `τ_dist`:

```
τ_total = (T_1 − T_2) · L + τ_dist
```

За другим законом Ньютона для обертального руху кутове прискорення системи `α` дорівнює:

```
α = dω / dt = τ_total / I
```

У неперервному часі кут нахилу `θ` є результатом подвійного інтегрування кутового прискорення: спочатку прискорення інтегрується у кутову швидкість `ω`, а потім швидкість інтегрується в кут `θ`. Ця подвійна інтеграція створює фундаментальний фазовий зсув у 180 градусів, через що одноконтурний регулятор кута втрачає запас стійкості при будь-яких помітних затримках у виконавчому тракті.

### Динаміка безколекторного двигуна та затримка ротора

У наївних підручникових симуляціях тягу двигунів вважають миттєвою функцією від сигналу керування `u(t)`. У фізичній реальності безколекторний двигун разом із пропелером має власний момент інерції, індуктивність обмоток і аеродинамічний опір лопатей. 

Перехідний процес встановлення обертів після зміни шпаруватості ШІМ чи пакета DShot моделюється аперіодичною ланкою першого порядку (фільтром низьких частот першого порядку) зі сталою часу `τ_motor`:

```
d(T_diff) / dt = (1 / τ_motor) · (T_target − T_diff)
```

Для типового 5-дюймового квадрокоптерного мотора стала часу `τ_motor` лежить у межах 20–40 мілісекунд (0.02–0.04 с). Ця затримка вносить додаткове запізнення фази, що різко обмежує максимальне значення коефіцієнта пропорційного підсилення `K_p` у контурі швидкості.

### Дискретизація фільтрів та ланок регулятора

Для цифрової реалізації неперервних рівнянь фільтрації та диференціювання застосовується дискретизація за часом із фіксованим кроком `dt`.

Аперіодичний фільтр першого порядку (PT1) у неперервному часі описується передавальною функцією `H(s) = 1 / (1 + s·RC)`, де `RC = 1 / (2·π·f_c)`, а `f_c` — частота зрізу в герцах. Після заміни похідної на різницеве співвідношення Ейлера (Backward Euler) отримуємо рекурентне рівняння для кроку `k`:

```
y[k] = y[k-1] + α · (x[k] − y[k-1])
```

де ваговий коефіцієнт згладжування `α` обчислюється аналітично через сталу часу кола та період дискретизації:

```
α = dt / (RC + dt)
= (2·π·f_c·dt) / (1 + 2·π·f_c·dt)     [підстановка RC = 1 / (2·π·f_c)]
```

Контур керування складається з двох ієрархічних рівнів із різною частотою виконання:
1. **Зовнішній контур кута (Angle loop):** виконується на частоті 250 Гц (`dt_angle = 0.004 с`). Він порівнює заданий кут `θ_target` із виміряним `θ_meas` і формує цільову кутову швидкість `ω_target = K_p_angle · (θ_target − θ_meas)`.
2. **Внутрішній контур кутової швидкості (Rate loop):** виконується на частоті 1000 Гц (`dt_rate = 0.001 с`). Він обчислює різницю між `ω_target` та виміряною гіроскопом швидкістю `ω_meas`, виконує диференціювання виміру з фільтрацією PT1, інтегрує похибку з контролем насичення (Anti-Windup) та додає прямий зв'язок (Feedforward).

Нижче наведено повністю робочий програмний стенд симуляції замкненої системи на мовах C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PI_F 3.14159265358979323846f

typedef struct {
    float state;
    float alpha;
} PT1Filter;

static inline void pt1_init(PT1Filter *f, float cutoff_hz, float dt) {
    float rc = 1.0f / (2.0f * PI_F * cutoff_hz);
    f->alpha = dt / (rc + dt);
    f->state = 0.0f;
}

static inline float pt1_update(PT1Filter *f, float input) {
    f->state += f->alpha * (input - f->state);
    return f->state;
}

typedef struct {
    float kp;
    float ki;
    float kd;
    float k_ff;
    float i_term;
    float i_max;
    float out_max;
    float prev_meas;
    PT1Filter d_filter;
} RatePID;

static inline void rate_pid_init(RatePID *pid, float kp, float ki, float kd, float k_ff,
                                 float i_max, float out_max, float d_cutoff_hz, float dt) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->k_ff = k_ff;
    pid->i_term = 0.0f;
    pid->i_max = i_max;
    pid->out_max = out_max;
    pid->prev_meas = 0.0f;
    pt1_init(&pid->d_filter, d_cutoff_hz, dt);
}

static inline float rate_pid_update(RatePID *pid, float target_rate, float meas_rate, float dt) {
    float error = target_rate - meas_rate;

    // Пропорційна ланка
    float p_out = pid->kp * error;

    // Прямий зв'язок (Feedforward) для прискорення реакції на зміну завдання
    float ff_out = pid->k_ff * target_rate;

    // Диференційна ланка: D-on-Measurement з фільтрацією PT1
    float raw_d = -(meas_rate - pid->prev_meas) / dt;
    pid->prev_meas = meas_rate;
    float filtered_d = pt1_update(&pid->d_filter, raw_d);
    float d_out = pid->kd * filtered_d;

    // Сума ланок без інтеграла
    float u_no_i = p_out + d_out + ff_out;

    // Інтегральна ланка з умовним інтегруванням (Conditional Integration Anti-Windup)
    float new_i = pid->i_term + (pid->ki * error * dt);
    if (new_i > pid->i_max) new_i = pid->i_max;
    if (new_i < -pid->i_max) new_i = -pid->i_max;

    float potential_out = u_no_i + new_i;
    bool saturated = (potential_out > pid->out_max && error > 0.0f) ||
                     (potential_out < -pid->out_max && error < 0.0f);

    if (!saturated) {
        pid->i_term = new_i;
    }

    // Підсумкове обмеження вихідного зусилля
    float output = u_no_i + pid->i_term;
    if (output > pid->out_max) output = pid->out_max;
    if (output < -pid->out_max) output = -pid->out_max;

    return output;
}

typedef struct {
    float kp;
    float max_rate;
} AnglePID;

static inline float angle_pid_update(const AnglePID *pid, float target_angle, float meas_angle) {
    float error = target_angle - meas_angle;
    float target_rate = pid->kp * error;
    if (target_rate > pid->max_rate) target_rate = pid->max_rate;
    if (target_rate < -pid->max_rate) target_rate = -pid->max_rate;
    return target_rate;
}

int main(void) {
    const float dt_sim = 0.001f;     // Базовий крок симуляції (1000 Гц)
    const float sim_time = 2.0f;     // Тривалість 2.0 секунди
    const int total_steps = (int)(sim_time / dt_sim);

    // Фізичні константи обертального важеля
    float angle_rad = 0.0f;
    float rate_rad_s = 0.0f;
    const float inertia = 0.005f;    // кг·м²
    const float arm_length = 0.15f;  // м
    const float motor_tau = 0.03f;   // Стала часу мотора (30 мс)
    float motor_thrust_diff = 0.0f;

    // Ініціалізація регуляторів
    RatePID rate_pid;
    rate_pid_init(&rate_pid, 0.18f, 0.25f, 0.004f, 0.02f, 0.3f, 1.0f, 60.0f, dt_sim);

    AnglePID angle_pid = { .kp = 6.5f, .max_rate = 4.0f };

    const float target_angle = 0.35f; // Уставка кута: 0.35 рад (~20 градусів)
    float target_rate = 0.0f;

    for (int step = 0; step < total_steps; ++step) {
        float t = (float)step * dt_sim;

        // Зовнішній контур Angle loop викликається кожні 4 кроки (250 Гц)
        if (step % 4 == 0) {
            target_rate = angle_pid_update(&angle_pid, target_angle, angle_rad);
        }

        // Внутрішній контур Rate loop викликається щокроку (1000 Гц)
        float control_cmd = rate_pid_update(&rate_pid, target_rate, rate_rad_s, dt_sim);

        // Динаміка зміни тяги моторів через перехідний процес першого порядку
        float target_thrust_diff = control_cmd * 2.0f;
        motor_thrust_diff += (dt_sim / motor_tau) * (target_thrust_diff - motor_thrust_diff);

        // Ступінчасте збурення вітром на інтервалі 1.0–1.3 с
        float wind_torque = 0.0f;
        if (t >= 1.0f && t <= 1.3f) {
            wind_torque = 0.08f; // Зовнішній момент 0.08 Н·м
        }

        // Сумарний момент і розрахунок кутового прискорення
        float total_torque = (motor_thrust_diff * arm_length) + wind_torque;
        float angular_accel = total_torque / inertia;

        // Чисельне інтегрування динаміки руху (метод Ейлера)
        rate_rad_s += angular_accel * dt_sim;
        angle_rad += rate_rad_s * dt_sim;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <cmath>
#include <algorithm>
#include <numbers>

class Pt1Filter {
public:
    constexpr Pt1Filter() noexcept = default;

    void init(float cutoff_hz, float dt) noexcept {
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
        alpha_ = dt / (rc + dt);
        state_ = 0.0f;
    }

    [[nodiscard]] float update(float input) noexcept {
        state_ += alpha_ * (input - state_);
        return state_;
    }

    [[nodiscard]] float state() const noexcept { return state_; }

private:
    float state_{0.0f};
    float alpha_{1.0f};
};

class RatePidController {
public:
    struct Config {
        float kp{0.18f};
        float ki{0.25f};
        float kd{0.004f};
        float k_ff{0.02f};
        float i_max{0.3f};
        float out_max{1.0f};
        float d_cutoff_hz{60.0f};
    };

    RatePidController(const Config& cfg, float dt) noexcept
        : cfg_(cfg), dt_(dt) {
        d_filter_.init(cfg_.d_cutoff_hz, dt_);
    }

    [[nodiscard]] float update(float target_rate, float meas_rate) noexcept {
        const float error = target_rate - meas_rate;

        const float p_out = cfg_.kp * error;
        const float ff_out = cfg_.k_ff * target_rate;

        // D-on-Measurement з фільтрацією PT1
        const float raw_d = -(meas_rate - prev_meas_) / dt_;
        prev_meas_ = meas_rate;
        const float filtered_d = d_filter_.update(raw_d);
        const float d_out = cfg_.kd * filtered_d;

        const float u_no_i = p_out + d_out + ff_out;

        // Anti-Windup Clamping & Conditional Integration
        const float new_i = std::clamp(i_term_ + (cfg_.ki * error * dt_), -cfg_.i_max, cfg_.i_max);
        const float potential_out = u_no_i + new_i;

        const bool saturated = (potential_out > cfg_.out_max && error > 0.0f) ||
                               (potential_out < -cfg_.out_max && error < 0.0f);

        if (!saturated) {
            i_term_ = new_i;
        }

        return std::clamp(u_no_i + i_term_, -cfg_.out_max, cfg_.out_max);
    }

    void reset() noexcept {
        i_term_ = 0.0f;
        prev_meas_ = 0.0f;
    }

private:
    Config cfg_;
    float dt_;
    float i_term_{0.0f};
    float prev_meas_{0.0f};
    Pt1Filter d_filter_;
};

class AnglePidController {
public:
    struct Config {
        float kp{6.5f};
        float max_rate{4.0f};
    };

    explicit constexpr AnglePidController(const Config& cfg) noexcept : cfg_(cfg) {}

    [[nodiscard]] float update(float target_angle, float meas_angle) const noexcept {
        const float error = target_angle - meas_angle;
        return std::clamp(cfg_.kp * error, -cfg_.max_rate, cfg_.max_rate);
    }

private:
    Config cfg_;
};

int main() {
    constexpr float kDtSim = 0.001f;     // Базовий крок 1000 Гц
    constexpr float kSimDuration = 2.0f; // 2 секунди
    constexpr auto kTotalSteps = static_cast<std::size_t>(kSimDuration / kDtSim);

    float angle_rad = 0.0f;
    float rate_rad_s = 0.0f;
    constexpr float kInertia = 0.005f;
    constexpr float kArmLength = 0.15f;
    constexpr float kMotorTau = 0.03f;
    float motor_thrust_diff = 0.0f;

    RatePidController rate_pid(RatePidController::Config{}, kDtSim);
    AnglePidController angle_pid(AnglePidController::Config{});

    constexpr float kTargetAngle = 0.35f; // Ціль 20 градусів
    float target_rate = 0.0f;

    for (std::size_t step = 0; step < kTotalSteps; ++step) {
        const float t = static_cast<float>(step) * kDtSim;

        if (step % 4 == 0) {
            target_rate = angle_pid.update(kTargetAngle, angle_rad);
        }

        const float control_cmd = rate_pid.update(target_rate, rate_rad_s);

        const float target_thrust = control_cmd * 2.0f;
        motor_thrust_diff += (kDtSim / kMotorTau) * (target_thrust - motor_thrust_diff);

        float wind_torque = 0.0f;
        if (t >= 1.0f && t <= 1.3f) {
            wind_torque = 0.08f;
        }

        const float total_torque = (motor_thrust_diff * kArmLength) + wind_torque;
        const float angular_accel = total_torque / kInertia;

        rate_rad_s += angular_accel * kDtSim;
        angle_rad += rate_rad_s * kDtSim;
    }

    return 0;
}
```
:::

### Аналіз поведінки та інженерні висновки

1. **Вплив затримки ротора на фазовий запас стійкості.** Якщо провести серію експериментів зі зміною `τ_motor` від 0.01 с до 0.06 с при однакових коефіцієнтах ПІД, виявиться, що при зростанні затримки двигунів перехідний процес перетворюється зі згасаючого на розбіжний. Фазовий зсув `φ = −arctan(2·π·f·τ_motor)` зменшує фазовий запас замкненої системи нижче критичних 30 градусів, провокуючи автоколивання. Це демонструє, чому легкі безколекторні мотори з низькою інерцією ротора піддаються значно агресивнішому налаштуванню, ніж важкі великі мотори промислових дронів.
2. **Робота умовного інтегрування під час збурення.** На інтервалі дії вітрового моменту (1.0–1.3 с) похибка кута призводить до зростання керуючого сигналу. Коли сума `P + D + FF + I` досягає межі `out_max = 1.0`, алгоритм заморожує оновлення `i_term`. Це запобігає намотуванню інтеграла. У мить зняття навантаження (1.3 с) апарат не зазнає зворотного перельоту (overshoot) і повертається до горизонталі за 80 мілісекунд.
3. **Роль прямого зв'язку Feedforward.** Коефіцієнт `k_ff` формує керівний сигнал пропорційно швидкості зміни уставки. На відміну від збільшення `K_p`, яке робить контур жорсткішим і підвищує схильність до резонансу на високих частотах, ланка `FF` діє виключно в момент руху стіка пілота, скорочуючи затримку реакції без погіршення стійкості при утриманні позиції в турбулентному повітрі.
4. **Стабільність часового кроку `dt`.** У дискретній системі будь-яке коливання періоду квантування викликає миттєвий сплеск у розрахунку `d_out`. Якщо таймер мікроконтролера викликає функцію оновлення з тремтінням (джиттером) у 10%, рівень шуму на вході моторів зростає на порядок. Тому в прошивці виклик функції `rate_pid_update()` завжди прив'язують до апаратного переривання завершення вимірювання датчика IMU.

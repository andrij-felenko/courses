# ⚙️ Каркас замкненого контуру стабілізації на C та C++

Управління безпілотним літальним апаратом вимагає безперервного узгодження між даними інерційних сенсорів та обертами чотирьох безколекторних моторів. Головний цикл прошивки польотного контролера повинен виконуватися з фіксованим інтервалом (наприклад, рівно 1000 мікросекунд при частоті 1 кГц), зчитувати кутові швидкості, оцінювати кути нахилу, обчислювати виправлення за ПІД-алгоритмом і оновлювати шпаруватість сигналів широтно-імпульсної модуляції (ШІМ).

Будь-яка непередбачувана затримка в цьому циклі призводить до відставання керуючого впливу за фазою. Якщо система реагує на нахил із запізненням навіть на кілька мілісекунд, додатний зворотний зв'язок розгойдує апарат, і дрон втрачає стійкість.

## Архітектура неблокуючого контуру

Для забезпечення детермінізму вся робота розбивається на послідовні фази без викликів блокуючих затримок (`delay_ms`):

```
1. Синхронізація: очікування прапорця апаратного таймера (1 кГц)
2. Зчитування: отримання сирих даних гіроскопа й акселерометра через SPI/DMA
3. Злиття: комплементарний фільтр обчислює кути крену (roll) та тангажу (pitch)
4. Регулювання: три дискретні ПІД-регулятори розраховують моменти стабілізації
5. Мікшування: розподіл тяги та моментів по чотирьох моторах
6. Видача: запис нових значень у регістри таймерів ШІМ
7. Безпека: скидання сторожового таймера (watchdog)
```

Нижче наведено повну реалізацію архітектури двома основними мовами вбудованої розробки: на процедурному мовному стандарті C та в ідіоматичному об'єктно-орієнтованому стилі C++ без динамічного виділення пам'яті.

:::tabs
```c
/* ========================================================================== */
/* flight_controller.c — C-реалізація замкненого контуру керування 1 кГц      */
/* ========================================================================== */
#include <stdint.h>
#include <stdbool.h>

/* Фізичні та алгоритмічні константи */
#define LOOP_PERIOD_SEC    0.001f    /* Період квантування: 1 мс (1 кГц) */
#define FILTER_ALPHA       0.98f     /* Ваговий коефіцієнт гіроскопа */
#define MOTOR_MIN_PWM      1000      /* Мінімальна тривалість імпульсу ШІМ (мкс) */
#define MOTOR_MAX_PWM      2000      /* Максимальна тривалість імпульсу ШІМ (мкс) */
#define MOTOR_IDLE_PWM     1100      /* Шпаруватість холостого ходу */

/* Вектор 3D-величин (кутові швидкості, прискорення, кути) */
typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

/* Стан та коефіцієнти дискретного ПІД-регулятора */
typedef struct {
    float kp;             /* Пропорційний коефіцієнт */
    float ki;             /* Інтегральний коефіцієнт */
    float kd;             /* Диференціальний коефіцієнт */
    float integral;       /* Накопичена сума похибки */
    float prev_error;     /* Похибка на попередньому такті */
    float out_limit;      /* Межа насичення виходу */
    float int_limit;      /* Межа запобігання накопиченню (anti-windup) */
} PidController;

/* Структура стану безпілотного апарата */
typedef struct {
    Vector3f gyro_dps;        /* Кутові швидкості (°/с) */
    Vector3f accel_g;         /* Лінійні прискорення (g) */
    Vector3f attitude_deg;    /* Оцінка кутів орієнтації (крен, тангаж, курс) */
    Vector3f target_angle;    /* Задані пілотом кути */
    float target_throttle;    /* Задана базова тяга (0.0 .. 1.0) */
    uint16_t motor_pwm[4];    /* Значення ШІМ для моторів M1..M4 */
    bool armed;               /* Прапорець дозволу роботи моторів */
} FlightState;

/* Ініціалізація ПІД-регулятора */
void pid_init(PidController* pid, float kp, float ki, float kd, float out_limit, float int_limit) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->out_limit = out_limit;
    pid->int_limit = int_limit;
}

/* Обчислення керуючого впливу за один такт */
float pid_update(PidController* pid, float target, float current, float dt) {
    float error = target - current;

    /* Пропорційна складова */
    float p_term = pid->kp * error;

    /* Інтегральна складова із захистом від перенасичення (anti-windup) */
    pid->integral += error * dt;
    if (pid->integral > pid->int_limit) {
        pid->integral = pid->int_limit;
    } else if (pid->integral < -pid->int_limit) {
        pid->integral = -pid->int_limit;
    }
    float i_term = pid->ki * pid->integral;

    /* Диференціальна складова за зміною похибки */
    float d_term = 0.0f;
    if (dt > 0.0f) {
        d_term = pid->kd * ((error - pid->prev_error) / dt);
    }
    pid->prev_error = error;

    float output = p_term + i_term + d_term;

    /* Обмеження вихідного сигналу */
    if (output > pid->out_limit) {
        output = pid->out_limit;
    } else if (output < -pid->out_limit) {
        output = -pid->out_limit;
    }
    return output;
}

/* Комплементарний фільтр оцінки орієнтації */
void attitude_filter_update(Vector3f* att, const Vector3f* gyro, const Vector3f* accel, float dt) {
    /* 1. Наближена оцінка кутів крену та тангажу за акселерометром */
    /* За нульових кутів accel_g.z = 1.0g; спрощене лінійне наближення для малих кутів */
    float accel_roll = accel->y * 57.29578f;   /* Радіани в градуси: 180 / π */
    float accel_pitch = -accel->x * 57.29578f;

    /* 2. Інтегрування гіроскопа та злиття з даними акселерометра */
    att->x = FILTER_ALPHA * (att->x + gyro->x * dt) + (1.0f - FILTER_ALPHA) * accel_roll;
    att->y = FILTER_ALPHA * (att->y + gyro->y * dt) + (1.0f - FILTER_ALPHA) * accel_pitch;
    att->z += gyro->z * dt; /* Курс (yaw) розраховується прямим інтегруванням */
}

/* Матриця мікшування для квадрокоптера схеми Quad-X */
void motor_mixer(FlightState* state, float roll_corr, float pitch_corr, float yaw_corr) {
    if (!state->armed) {
        for (int i = 0; i < 4; ++i) {
            state->motor_pwm[i] = MOTOR_MIN_PWM;
        }
        return;
    }

    float base_throttle = (float)MOTOR_MIN_PWM + state->target_throttle * (float)(MOTOR_MAX_PWM - MOTOR_MIN_PWM);
    if (base_throttle < (float)MOTOR_IDLE_PWM) {
        base_throttle = (float)MOTOR_IDLE_PWM;
    }

    /* Мотори Quad-X:
       M1: передній правий (CCW)  = Base - Roll + Pitch + Yaw
       M2: задній правий   (CW)   = Base - Roll - Pitch - Yaw
       M3: задній лівий    (CCW)  = Base + Roll - Pitch + Yaw
       M4: передній лівий  (CW)   = Base + Roll + Pitch - Yaw */
    float m[4];
    m[0] = base_throttle - roll_corr + pitch_corr + yaw_corr;
    m[1] = base_throttle - roll_corr - pitch_corr - yaw_corr;
    m[2] = base_throttle + roll_corr - pitch_corr + yaw_corr;
    m[3] = base_throttle + roll_corr + pitch_corr - yaw_corr;

    for (int i = 0; i < 4; ++i) {
        if (m[i] < (float)MOTOR_IDLE_PWM) m[i] = (float)MOTOR_IDLE_PWM;
        if (m[i] > (float)MOTOR_MAX_PWM)  m[i] = (float)MOTOR_MAX_PWM;
        state->motor_pwm[i] = (uint16_t)m[i];
    }
}

/* Зовнішні прототипи драйверів низького рівня (HAL/Регістри) */
extern bool hardware_timer_wait_next_tick(void);
extern void sensor_read_imu(Vector3f* gyro, Vector3f* accel);
extern void radio_read_commands(Vector3f* target_angle, float* throttle, bool* armed);
extern void pwm_write_channels(const uint16_t pwm[4]);
extern void watchdog_feed(void);

/* Головна точка входу керуючого циклу */
void flight_controller_main_loop(void) {
    PidController pid_roll;
    PidController pid_pitch;
    PidController pid_yaw;

    pid_init(&pid_roll,  2.5f, 0.4f, 0.08f, 300.0f, 100.0f);
    pid_init(&pid_pitch, 2.5f, 0.4f, 0.08f, 300.0f, 100.0f);
    pid_init(&pid_yaw,   4.0f, 0.8f, 0.00f, 400.0f, 150.0f);

    FlightState state = {0};

    while (1) {
        /* 1. Блокування до настання періодичного переривання (1 кГц) */
        if (!hardware_timer_wait_next_tick()) {
            continue;
        }

        /* 2. Зчитування сенсорів */
        sensor_read_imu(&state.gyro_dps, &state.accel_g);

        /* 3. Оцінка орієнтації */
        attitude_filter_update(&state.attitude_deg, &state.gyro_dps, &state.accel_g, LOOP_PERIOD_SEC);

        /* 4. Отримання цілей від радіоприймача */
        radio_read_commands(&state.target_angle, &state.target_throttle, &state.armed);

        /* 5. Розрахунок впливів ПІД */
        float roll_u  = pid_update(&pid_roll,  state.target_angle.x, state.attitude_deg.x, LOOP_PERIOD_SEC);
        float pitch_u = pid_update(&pid_pitch, state.target_angle.y, state.attitude_deg.y, LOOP_PERIOD_SEC);
        float yaw_u   = pid_update(&pid_yaw,   state.target_angle.z, state.gyro_dps.z,     LOOP_PERIOD_SEC);

        /* 6. Мікшування та видача на ШІМ */
        motor_mixer(&state, roll_u, pitch_u, yaw_u);
        pwm_write_channels(state.motor_pwm);

        /* 7. Скидання сторожового таймера */
        watchdog_feed();
    }
}
```
```cpp
// =============================================================================
// flight_controller.cpp — Ідіоматична C++ реалізація без динамічної пам'яті
// =============================================================================
#include <array>
#include <algorithm>
#include <cstdint>
#include <span>

namespace flight {

// Фізичні та алгоритмічні константи часу компіляції
struct Config {
    static constexpr float loop_period_sec = 0.001f; // 1 кГц
    static constexpr float filter_alpha    = 0.98f;
    static constexpr uint16_t motor_min_pwm  = 1000;
    static constexpr uint16_t motor_max_pwm  = 2000;
    static constexpr uint16_t motor_idle_pwm = 1100;
    static constexpr float rad_to_deg      = 57.29578f;
};

// 3D-вектор з базовими операціями
struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3f operator+(const Vector3f& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3f operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};

// Клас дискретного ПІД-регулятора із захистом від насичення
class PidController {
public:
    constexpr PidController(float kp, float ki, float kd, float out_limit, float int_limit) noexcept
        : kp_{kp}, ki_{ki}, kd_{kd}, out_limit_{out_limit}, int_limit_{int_limit} {}

    float update(float target, float current, float dt) noexcept {
        const float error = target - current;

        // Пропорційна ланка
        const float p_term = kp_ * error;

        // Інтегральна ланка з anti-windup обмеженням
        integral_ += error * dt;
        integral_ = std::clamp(integral_, -int_limit_, int_limit_);
        const float i_term = ki_ * integral_;

        // Диференціальна ланка
        float d_term = 0.0f;
        if (dt > 0.0f) {
            d_term = kd_ * ((error - prev_error_) / dt);
        }
        prev_error_ = error;

        // Насичення виходу
        return std::clamp(p_term + i_term + d_term, -out_limit_, out_limit_);
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_error_ = 0.0f;
    }

private:
    float kp_;
    float ki_;
    float kd_;
    float integral_{0.0f};
    float prev_error_{0.0f};
    float out_limit_;
    float int_limit_;
};

// Клас комплементарної оцінки орієнтації
class AttitudeEstimator {
public:
    void update(const Vector3f& gyro_dps, const Vector3f& accel_g, float dt) noexcept {
        const float accel_roll  = accel_g.y * Config::rad_to_deg;
        const float accel_pitch = -accel_g.x * Config::rad_to_deg;

        attitude_.x = Config::filter_alpha * (attitude_.x + gyro_dps.x * dt)
                    + (1.0f - Config::filter_alpha) * accel_roll;
        attitude_.y = Config::filter_alpha * (attitude_.y + gyro_dps.y * dt)
                    + (1.0f - Config::filter_alpha) * accel_pitch;
        attitude_.z += gyro_dps.z * dt;
    }

    [[nodiscard]] const Vector3f& attitude() const noexcept { return attitude_; }

private:
    Vector3f attitude_{};
};

// Мікшер моторів Quad-X
class MotorMixer {
public:
    using PwmOutputs = std::array<uint16_t, 4>;

    static PwmOutputs compute(float throttle, float roll, float pitch, float yaw, bool armed) noexcept {
        PwmOutputs outputs{};
        if (!armed) {
            outputs.fill(Config::motor_min_pwm);
            return outputs;
        }

        const float base = Config::motor_min_pwm
                         + throttle * (Config::motor_max_pwm - Config::motor_min_pwm);
        const float clamped_base = std::max(base, static_cast<float>(Config::motor_idle_pwm));

        const std::array<float, 4> raw = {
            clamped_base - roll + pitch + yaw, // M1
            clamped_base - roll - pitch - yaw, // M2
            clamped_base + roll - pitch + yaw, // M3
            clamped_base + roll + pitch - yaw  // M4
        };

        for (size_t i = 0; i < 4; ++i) {
            const float val = std::clamp(raw[i],
                                         static_cast<float>(Config::motor_idle_pwm),
                                         static_cast<float>(Config::motor_max_pwm));
            outputs[i] = static_cast<uint16_t>(val);
        }
        return outputs;
    }
};

// Інтерфейс драйверів апаратного рівня
class HardwareBridge {
public:
    virtual ~HardwareBridge() = default;
    virtual bool wait_tick() noexcept = 0;
    virtual void read_imu(Vector3f& gyro, Vector3f& accel) noexcept = 0;
    virtual void read_radio(Vector3f& target, float& throttle, bool& armed) noexcept = 0;
    virtual void write_motors(std::span<const uint16_t, 4> pwm) noexcept = 0;
    virtual void feed_watchdog() noexcept = 0;
};

// Головний контролер польоту (композиція компонентів)
class FlightController {
public:
    explicit FlightController(HardwareBridge& hw) noexcept
        : hw_{hw},
          pid_roll_{2.5f, 0.4f, 0.08f, 300.0f, 100.0f},
          pid_pitch_{2.5f, 0.4f, 0.08f, 300.0f, 100.0f},
          pid_yaw_{4.0f, 0.8f, 0.00f, 400.0f, 150.0f} {}

    void run() noexcept {
        Vector3f gyro{};
        Vector3f accel{};
        Vector3f target_angle{};
        float throttle{0.0f};
        bool armed{false};

        while (true) {
            if (!hw_.wait_tick()) {
                continue;
            }

            hw_.read_imu(gyro, accel);
            estimator_.update(gyro, accel, Config::loop_period_sec);
            hw_.read_radio(target_angle, throttle, armed);

            const auto& att = estimator_.attitude();
            const float roll_u  = pid_roll_.update(target_angle.x, att.x, Config::loop_period_sec);
            const float pitch_u = pid_pitch_.update(target_angle.y, att.y, Config::loop_period_sec);
            const float yaw_u   = pid_yaw_.update(target_angle.z, gyro.z, Config::loop_period_sec);

            const auto motors = MotorMixer::compute(throttle, roll_u, pitch_u, yaw_u, armed);
            hw_.write_motors(motors);

            hw_.feed_watchdog();
        }
    }

private:
    HardwareBridge& hw_;
    AttitudeEstimator estimator_{};
    PidController pid_roll_;
    PidController pid_pitch_;
    PidController pid_yaw_;
};

} // namespace flight
```
:::

## Порівняння підходів C та C++ у мікроконтролерах

Подані вище дві реалізації вирішують абсолютно однакову фізичну задачу, але демонструють два різних світогляди системного програмування:

1. **Інкапсуляція та захист стану:** У версії на C структура `PidController` передається як вказівник у відкриті функції. Будь-який сторонній модуль може випадково змінити поле `pid->integral` напряму, що призведе до несподіваного зриву стабілізації. У версії на C++ внутрішні змінні інтегратора та похибки сховані в секції `private`, а публічний інтерфейс гарантує виконання правил обмеження `std::clamp` при кожному оновленні.
2. **Константи та безпека типів:** Константи C (`#define`) діють як неконтрольована текстова заміна препроцесора без перевірки типів. C++ використовує `constexpr` усередині простору імен `Config`, що гарантує строгий контроль типів на етапі компіляції та повну оптимізацію без витрат пам'яті у виконуваному коді (*zero-cost abstraction*).
3. **Безпечна передача масивів:** Замість передачі сирого вказівника `const uint16_t pwm[4]` (який у C автоматично деградує до звичайного вказівника `uint16_t*` без перевірки меж), C++ використовує `std::span<const uint16_t, 4>`. Це дозволяє компілятору виявляти спроби виходу за межі масиву ще до прошивки чипа.

## Детальний розбір вузлів алгоритму

Наведений каркас демонструє ключові принципи надійної вбудованої розробки реального часу:

### 1. Синхронізація часу та усунення джитера

Функція `hardware_timer_wait_next_tick()` не викликає звичайний цикл затримки. Вона переводить процесор у стан очікування події (наприклад, інструкція `WFE` / `WFI` в архітектурі ARM). Апаратний таймер мікроконтролера щоразу відраховує рівно `1000.0 мкс`, після чого генерує сигнал пробудження ядра.

Це повністю усуває накопичення похибки періоду: навіть якщо тіло обчислень в одному такті зайняло 220 мкс, а в іншому — 310 мкс через математичні гілки, наступний такт завжди стартує у строго фіксований момент часу.

### 2. Комплементарна фільтрація проти інтегрування дрейфу

Гіроскоп дає чисту кутову швидкість без запізнення, але пряме чисельне інтегрування `θ = θ + ω·Δt` неминуче накопичує похибку зміщення нуля (дрейф). Акселерометр вимірює вектор сили тяжіння, що дозволяє визначити кути нахилу через тригонометричні співвідношення, але під час вібрацій пропелерів його сигнал містить високочастотний шум амплітудою в кілька одиниць g.

Комплементарний фільтр розділяє спектр сигналу на дві смуги за допомогою коефіцієнта `FILTER_ALPHA = 0.98`:
- На швидких рухах (високі частоти) 98% оцінки формується швидким інтегруванням гіроскопа.
- На повільних змінах (низькі частоти) 2% внеску акселерометра безупинно підтягують оцінку до справжньої вертикалі, ліквідуючи накопичений дрейф.

### 3. Математика матриці мікшування моторів (Quad-X)

Розподіл зусиль на чотири мотори спирається на фізику балансу тяги та реактивних моментів:
- **Крен (Roll):** для нахилу праворуч тяга лівих моторів (M3, M4) збільшується, а правих (M1, M2) — зменшується.
- **Тангаж (Pitch):** для нахилу вперед тяга задніх моторів (M2, M3) збільшується, а передніх (M1, M4) — зменшується.
- **Курс (Yaw):** мотори M1 та M3 обертаються проти годинникової стрілки (CCW), створюючи за третім законом Ньютона реактивний момент обертання корпусу за годинниковою стрілкою. Мотори M2 та M4 обертаються за годинниковою стрілкою (CW). Для повороту за курсом збільшують оберти однієї діагональної пари та зменшують оберти протилежної, зберігаючи сумарну підйомну силу незмінною.

## Інженерні підводні камені та захист

При перенесенні цього каркаса на реальну друковану плату виникають чотири критичні загрози:

1. **Плаваюча кома на чипах без FPU:** якщо мікроконтролер не має апаратного співпроцесора обчислень із рухомою комою (FPU), програмна емуляція операцій `float` вимагає сотень машинних тактів на кожне множення. У такому разі весь розрахунок переписують на цілочисельну арифметику з фіксованою комою (*fixed-point arithmetic*), де числа масштабуються множником `1000` або зсувом бітів `<< 16`.
2. **Переповнення інтегратора (Integral Windup):** коли дрон затиснуто руками або коли один із моторів уперся в максимальну межу ШІМ (2000 мкс), похибка не зникає. Інтегральна складова без обмеження продовжує зростати до величезних чисел. Коли апарат відпускають, накопичений інтеграл ще кілька секунд продовжує крутити мотори з максимальною силою, викликаючи різке перекидання. Жорстке затискання інтегральної суми межами `int_limit` повністю усуває цей дефект.
3. **Шум диференціювання:** операція знаходження похідної `(error - prev_error) / dt` ділить малу різницю на малий крок часу (`0.001 с`), що еквівалентно множенню шуму на `1000`. Будь-яка вібрація рами створює колосальні сплески в диференціальній ланці, мотори починають нагріватися й деренчати. На практиці сигнал помилки або кутову швидкість перед диференціюванням обов'язково пропускають через цифровий фільтр низьких частот 2-го порядку (фільтр Баттерворта).
4. **Втрата радіосигналу (Failsafe):** якщо радіоприймач перестав надсилати пакети керування протягом 500 мс, функція `radio_read_commands` зобов'язана зняти прапорець `armed = false` або перевести дрон у режим плавного автозниження, інакше апарат полетить у неконтрольованому напрямку на останніх збережених значеннях газу.

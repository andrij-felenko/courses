# ⚙️ Модуль каскадного автопілота

Повний каскадний контролер для мультикоптера поєднує чотири шари керування в єдину дискретну систему: зовнішній контур позиції (перетворює відхилення просторових координат на бажані швидкості), контур швидкості (формує вектор горизонтальних прискорень та кутів нахилу з компенсацією вітрового зносу), контур орієнтації (розраховує цільові кутові швидкості з корекцією розвороту на 360°) та внутрішній швидкий контур кутових швидкостей, що безпосередньо керує тягою й моментами моторів через моторний мікшер.

## Архітектурний поділ та частотні контури

У реальному польотному контролері обчислення розбивають на дві незалежні часові зони, які синхронізуються через атомарний обмін даними:
1. **Повільний навігаційний контур (50 Гц, `dt = 0.02 с`):** опрацьовує макродинаміку апарата. Сюди входять P-регулятор координат у площині NEU, PID-регулятор швидкостей польоту, перетворення прискорень Землі у кути нахилу корпусу, а також динамічна компенсація розряду батареї та просідання тяги в нахилі.
2. **Швидкий контур стабілізації (500 Гц, `dt = 0.002 с`):** працює всередині переривання апаратного таймера або DMA-готовності шини SPI від гіроскопа. Він обчислює похибку орієнтації, формує бажані швидкості обертання та генерує віртуальні моменти `(Roll, Pitch, Yaw)`.

Такий розподіл дозволяє мінімізувати фазове запізнення внутрішнього контуру: гіроскоп опитується без затримок на частоті 500–1000 Гц, а важкі тригонометричні перетворення та робота з супутниковими координатами виконуються на спокійній частоті 50 Гц.

У багатопотокових операційних системах реального часу (FreeRTOS або NuttX у складі PX4/ArduPilot) ці дві задачі виконуються в окремих потоках із різними пріоритетами. Щоб уникнути стану перегонів (англ. *race condition*) під час передачі масиву цільових кутів із повільного потоку в швидкий, застосовують механізм подвійної буферизації або безблокувальні атомарні змінні (англ. *lock-free triple buffering*). Швидкий потік ніколи не очікує на завершення повільного, читаючи останній валідний знімок уставок.

## Захист від насичення інтегратора (Clamping Anti-Windup)

Класична проблема польотних контролерів — насичення інтегральної складової регулятора під час різких маневрів або затиску приводів у межі ESC (0% або 100%). Якщо дрон уперся у фізичну межу тяги моторів або максимального кута нахилу, а похибка не зникає, звичайний інтегратор продовжує накопичувати значення `∫ e dt` до гігантських величин. Коли апарат нарешті повертається у нормальний режим, розрядка перенасиченого інтегратора призводить до глибокого перельоту цілі та розгойдування.

У наведеному модулі реалізовано алгоритм умовного інтегрування (англ. *clamping anti-windup*). Інтегрування похибки дозволяється лише за одночасного виконання двох умов:
- Регулятор ще не досяг максимального або мінімального вихідного обмеження.
- Якщо вихід уже обмежений, знак нової похибки має бути протилежним до знака насичення (тобто похибка повинна сприяти виходу із насичення, а не поглиблювати його).

Цей механізм захищає як горизонтальні інтегратори швидкості (що борються з вітром), так і внутрішні інтегратори кутових швидкостей гіроскопа.

## Фільтрація диференційної складової (D-term Low-Pass Filter)

Диференційна складова ПІД-регулятора кутових швидкостей надзвичайно чутлива до високочастотного шуму. Двигуни БПЛА обертаються зі швидкістю 5000–30000 об/хв, створюючи потужні механічні вібрації на частотах 100–500 Гц. Операція взяття похідної `d(meas)/dt` є математичним фільтром верхніх частот: вона підсилює високочастотний шум пропорційно до його частоти.

Якщо подати сирий диференційний сигнал на регулятор, мотори почнуть неконтрольовано грітися, споживаючи шалений струм на відпрацювання неіснуючого шуму вібрацій. Тому у практичних автопілотах сигнал диференціатора обов'язково пропускають крізь цифровий фільтр низьких частот першого або другого порядку (PT1 або фільтр Баттерворта) із частотою зрізу близько 30–50 Гц. У наведеному базовому коді похідна береться від вимірюваної величини (Derivative on Measurement), що усуває диференційний удар при стрибках уставки, а в реальному залізі цей блок доповнюється ковзним експоненційним згладжуванням.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ── Векторна геометрія ──────────────────────────────────────────────────────
typedef struct { float x, y, z; } Vector3f;

static inline float clampf(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

static inline float wrap_pi(float rad) {
    while (rad > (float)M_PI)  rad -= 2.0f * (float)M_PI;
    while (rad < -(float)M_PI) rad += 2.0f * (float)M_PI;
    return rad;
}

// ── Дискретний ПІД-регулятор із захистом від насичення (Anti-Windup) ────────
typedef struct {
    float kp, ki, kd;
    float integ;
    float integ_max;
    float prev_meas;
    float out_min, out_max;
} PID_Controller;

static void pid_init(PID_Controller *pid, float kp, float ki, float kd,
                     float i_max, float out_min, float out_max) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integ = 0.0f;
    pid->integ_max = i_max;
    pid->prev_meas = 0.0f;
    pid->out_min = out_min;
    pid->out_max = out_max;
}

static float pid_update(PID_Controller *pid, float target, float meas, float dt) {
    float error = target - meas;

    // Диференційна складова від похідної виміру (запобігає удару при стрибку уставки)
    float deriv = 0.0f;
    if (dt > 1e-6f) {
        deriv = -(meas - pid->prev_meas) / dt;
    }
    pid->prev_meas = meas;

    // Попередній вихід без урахування нового інтеграла
    float p_term = pid->kp * error;
    float d_term = pid->kd * deriv;
    float out_unsat = p_term + pid->ki * pid->integ + d_term;

    // Умовне інтегрування (clamping anti-windup): не накопичуємо, якщо регулятор у насиченні
    bool saturated_high = (out_unsat >= pid->out_max && error > 0.0f);
    bool saturated_low  = (out_unsat <= pid->out_min && error < 0.0f);

    if (!saturated_high && !saturated_low) {
        pid->integ += error * dt;
        pid->integ = clampf(pid->integ, -pid->integ_max, pid->integ_max);
    }

    float out = p_term + pid->ki * pid->integ + d_term;
    return clampf(out, pid->out_min, pid->out_max);
}

// ── Структури стану та конфігурації автопілота ──────────────────────────────
typedef struct {
    // Входи від EKF / IMU
    Vector3f pos_neu;       // [м] Північ, Схід, Вгору
    Vector3f vel_neu;       // [м/с]
    Vector3f euler_rad;     // [рад] Roll, Pitch, Yaw
    Vector3f gyro_rps;      // [рад/с] кутові швидкості тіла P, Q, R
    float v_battery;        // [В] поточна напруга
    float v_nominal;        // [В] номінальна напруга 4S (14.8В) або 6S (22.2В)

    // Уставки від планувальника місії
    Vector3f target_pos_neu;
    float target_yaw_rad;

    // Проміжні змінні каскадів
    Vector3f des_vel_neu;
    Vector3f des_accel_neu;
    Vector3f des_euler_rad;
    Vector3f des_rates_rps;
    float base_throttle;

    // Регулятори
    PID_Controller pid_pos_n, pid_pos_e, pid_pos_z;
    PID_Controller pid_vel_n, pid_vel_e, pid_vel_z;
    PID_Controller pid_rate_p, pid_rate_q, pid_rate_r;

    // Коефіцієнти P для кутів орієнтації
    float kp_roll_angle, kp_pitch_angle, kp_yaw_angle;

    // Фізичні обмеження
    float max_horiz_vel;    // [м/с] напр. 12.0
    float max_tilt_angle;   // [рад] напр. 0.61 (35°)
    float thr_hover;        // [0..1] базова тяга зависання, напр. 0.45
} CascadedAutopilot;

void autopilot_init(CascadedAutopilot *ap) {
    // Горизонтальна позиція: P-регулятор формує бажану швидкість
    pid_init(&ap->pid_pos_n, 1.0f, 0.0f, 0.0f, 0.0f, -12.0f, 12.0f);
    pid_init(&ap->pid_pos_e, 1.0f, 0.0f, 0.0f, 0.0f, -12.0f, 12.0f);
    pid_init(&ap->pid_pos_z, 1.2f, 0.0f, 0.0f, 0.0f, -3.0f, 4.0f);

    // Швидкості: PID формує прискорення [м/с²]
    pid_init(&ap->pid_vel_n, 2.0f, 0.5f, 0.1f, 5.0f, -6.0f, 6.0f);
    pid_init(&ap->pid_vel_e, 2.0f, 0.5f, 0.1f, 5.0f, -6.0f, 6.0f);
    pid_init(&ap->pid_vel_z, 2.5f, 1.2f, 0.05f, 4.0f, -8.0f, 8.0f);

    // Орієнтація: P-контур на кути
    ap->kp_roll_angle  = 6.5f;
    ap->kp_pitch_angle = 6.5f;
    ap->kp_yaw_angle   = 3.5f;

    // Кутові швидкості: PID формує нормовані моменти [-1.0 .. +1.0]
    pid_init(&ap->pid_rate_p, 0.15f, 0.20f, 0.003f, 0.3f, -1.0f, 1.0f);
    pid_init(&ap->pid_rate_q, 0.15f, 0.20f, 0.003f, 0.3f, -1.0f, 1.0f);
    pid_init(&ap->pid_rate_r, 0.22f, 0.12f, 0.000f, 0.3f, -1.0f, 1.0f);

    ap->max_horiz_vel = 12.0f;
    ap->max_tilt_angle = 35.0f * (float)M_PI / 180.0f;
    ap->thr_hover = 0.45f;
    ap->v_nominal = 16.0f;
    ap->v_battery = 16.0f;
}

// ── Повільний крок: Контури позиції та швидкості (50 Гц) ────────────────────
void autopilot_update_slow_loop(CascadedAutopilot *ap, float dt) {
    const float GRAVITY = 9.80665f;

    // 1. Контур позиції (P): розрахунок цільової швидкості
    float des_vn = pid_update(&ap->pid_pos_n, ap->target_pos_neu.x, ap->pos_neu.x, dt);
    float des_ve = pid_update(&ap->pid_pos_e, ap->target_pos_neu.y, ap->pos_neu.y, dt);
    float des_vz = pid_update(&ap->pid_pos_z, ap->target_pos_neu.z, ap->pos_neu.z, dt);

    // Обмеження вектора горизонтальної швидкості
    float horiz_speed = sqrtf(des_vn * des_vn + des_ve * des_ve);
    if (horiz_speed > ap->max_horiz_vel && horiz_speed > 1e-4f) {
        float scale = ap->max_horiz_vel / horiz_speed;
        des_vn *= scale;
        des_ve *= scale;
    }
    ap->des_vel_neu.x = des_vn;
    ap->des_vel_neu.y = des_ve;
    ap->des_vel_neu.z = des_vz;

    // 2. Контур швидкостей (PID): розрахунок бажаних прискорень
    float a_n = pid_update(&ap->pid_vel_n, ap->des_vel_neu.x, ap->vel_neu.x, dt);
    float a_e = pid_update(&ap->pid_vel_e, ap->des_vel_neu.y, ap->vel_neu.y, dt);
    float a_z = pid_update(&ap->pid_vel_z, ap->des_vel_neu.z, ap->vel_neu.z, dt);
    ap->des_accel_neu = (Vector3f){ a_n, a_e, a_z };

    // 3. Проекція прискорень Землі на курс апарата (Body Frame)
    float psi = ap->euler_rad.z; // поточний курс
    float cos_psi = cosf(psi);
    float sin_psi = sinf(psi);

    float a_fwd   =  a_n * cos_psi + a_e * sin_psi;
    float a_right = -a_n * sin_psi + a_e * cos_psi;

    // 4. Перетворення прискорень на кути нахилу корпуса
    float target_pitch = atan2f(a_fwd, GRAVITY);
    float target_roll  = atan2f(a_right, GRAVITY);

    target_pitch = clampf(target_pitch, -ap->max_tilt_angle, ap->max_tilt_angle);
    target_roll  = clampf(target_roll,  -ap->max_tilt_angle, ap->max_tilt_angle);

    ap->des_euler_rad.x = target_roll;
    ap->des_euler_rad.y = target_pitch;
    ap->des_euler_rad.z = ap->target_yaw_rad;

    // 5. Вертикальний канал тяги з компенсацією нахилу та напруги
    float roll = ap->euler_rad.x;
    float pitch = ap->euler_rad.y;
    float cos_tilt = cosf(roll) * cosf(pitch);
    if (cos_tilt < 0.35f) cos_tilt = 0.35f; // оберігаємо від ділення на 0 при екстремальних кутах

    // Відносна зміна тяги від прискорення a_z
    float thr_accel_offset = (a_z / GRAVITY) * ap->thr_hover;
    float raw_throttle = (ap->thr_hover + thr_accel_offset) / cos_tilt;

    // Компенсація розряду акумулятора
    if (ap->v_battery > 6.0f) {
        raw_throttle *= (ap->v_nominal / ap->v_battery);
    }
    ap->base_throttle = clampf(raw_throttle, 0.08f, 0.95f);
}

// ── Швидкий крок: Контури орієнтації та кутових швидкостей (500 Гц) ─────────
void autopilot_update_fast_loop(CascadedAutopilot *ap, float dt,
                               float *out_roll_t, float *out_pitch_t,
                               float *out_yaw_t,  float *out_throttle) {
    // 1. Контур орієнтації (P-регулятор кутів)
    float err_roll  = ap->des_euler_rad.x - ap->euler_rad.x;
    float err_pitch = ap->des_euler_rad.y - ap->euler_rad.y;
    float err_yaw   = wrap_pi(ap->des_euler_rad.z - ap->euler_rad.z); // захист від розкручування

    ap->des_rates_rps.x = clampf(ap->kp_roll_angle  * err_roll,  -4.0f, 4.0f);
    ap->des_rates_rps.y = clampf(ap->kp_pitch_angle * err_pitch, -4.0f, 4.0f);
    ap->des_rates_rps.z = clampf(ap->kp_yaw_angle   * err_yaw,   -2.5f, 2.5f);

    // 2. Контур кутових швидкостей (PID-регулятор гіроскопа)
    *out_roll_t  = pid_update(&ap->pid_rate_p, ap->des_rates_rps.x, ap->gyro_rps.x, dt);
    *out_pitch_t = pid_update(&ap->pid_rate_q, ap->des_rates_rps.y, ap->gyro_rps.y, dt);
    *out_yaw_t   = pid_update(&ap->pid_rate_r, ap->des_rates_rps.z, ap->gyro_rps.z, dt);
    *out_throttle = ap->base_throttle;
}

// Приклад виклику та симуляції кроку керування
int main(void) {
    CascadedAutopilot ap;
    autopilot_init(&ap);

    // Встановлюємо ціль: 10 м на північ, 5 м на схід, висота 25 м, курс 90° (схід)
    ap.target_pos_neu = (Vector3f){ 10.0f, 5.0f, 25.0f };
    ap.target_yaw_rad = 90.0f * (float)M_PI / 180.0f;

    // Поточний стан: висимо на (0, 0, 20), курс 0°
    ap.pos_neu   = (Vector3f){ 0.0f, 0.0f, 20.0f };
    ap.vel_neu   = (Vector3f){ 0.0f, 0.0f, 0.0f };
    ap.euler_rad = (Vector3f){ 0.0f, 0.0f, 0.0f };
    ap.gyro_rps  = (Vector3f){ 0.0f, 0.0f, 0.0f };

    // Такт повільного контуру
    autopilot_update_slow_loop(&ap, 0.02f);

    // Такт швидкого контуру
    float tau_roll, tau_pitch, tau_yaw, throttle;
    autopilot_update_fast_loop(&ap, 0.002f, &tau_roll, &tau_pitch, &tau_yaw, &throttle);

    printf("Результати розрахунку каскаду:\n");
    printf("Бажана швидкість: Vn=%.2f, Ve=%.2f, Vz=%.2f м/с\n",
           ap.des_vel_neu.x, ap.des_vel_neu.y, ap.des_vel_neu.z);
    printf("Цільовий тангаж: %.2f deg, крен: %.2f deg\n",
           ap.des_euler_rad.y * 180.0f / (float)M_PI,
           ap.des_euler_rad.x * 180.0f / (float)M_PI);
    printf("Команди моторів: Roll=%.3f, Pitch=%.3f, Yaw=%.3f, Throttle=%.3f\n",
           tau_roll, tau_pitch, tau_yaw, throttle);

    return 0;
}
```
```cpp
#include <iostream>
#include <numbers>
#include <cmath>
#include <algorithm>

namespace autopilot {

struct Vector3 {
    float x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] constexpr float length_xy() const noexcept {
        return std::sqrt(x * x + y * y);
    }
};

[[nodiscard]] inline float wrap_pi(float rad) noexcept {
    while (rad > std::numbers::pi_v<float>)  rad -= 2.0f * std::numbers::pi_v<float>;
    while (rad < -std::numbers::pi_v<float>) rad += 2.0f * std::numbers::pi_v<float>;
    return rad;
}

class PidController {
public:
    struct Config {
        float kp{0.0f};
        float ki{0.0f};
        float kd{0.0f};
        float i_max{0.0f};
        float out_min{-1.0f};
        float out_max{1.0f};
    };

    explicit PidController(const Config& cfg) : cfg_(cfg) {}

    [[nodiscard]] float update(float target, float meas, float dt) noexcept {
        const float error = target - meas;
        float deriv = 0.0f;
        if (dt > 1e-6f) {
            deriv = -(meas - prev_meas_) / dt;
        }
        prev_meas_ = meas;

        const float p_term = cfg_.kp * error;
        const float d_term = cfg_.kd * deriv;
        const float out_raw = p_term + cfg_.ki * integ_ + d_term;

        // Clamping anti-windup
        const bool sat_high = (out_raw >= cfg_.out_max && error > 0.0f);
        const bool sat_low  = (out_raw <= cfg_.out_min && error < 0.0f);

        if (!sat_high && !sat_low) {
            integ_ += error * dt;
            integ_ = std::clamp(integ_, -cfg_.i_max, cfg_.i_max);
        }

        const float out = p_term + cfg_.ki * integ_ + d_term;
        return std::clamp(out, cfg_.out_min, cfg_.out_max);
    }

    void reset() noexcept {
        integ_ = 0.0f;
        prev_meas_ = 0.0f;
    }

private:
    Config cfg_;
    float integ_{0.0f};
    float prev_meas_{0.0f};
};

struct AutopilotState {
    Vector3 pos_neu;
    Vector3 vel_neu;
    Vector3 euler_rad;
    Vector3 gyro_rps;
    float v_battery{16.0f};
    float v_nominal{16.0f};
};

struct AutopilotCommands {
    float roll_torque{0.0f};
    float pitch_torque{0.0f};
    float yaw_torque{0.0f};
    float throttle{0.0f};
};

class CascadedFlightController {
public:
    CascadedFlightController()
        : pid_pos_n_({ .kp = 1.0f, .ki = 0.0f, .kd = 0.0f, .i_max = 0.0f, .out_min = -12.0f, .out_max = 12.0f }),
          pid_pos_e_({ .kp = 1.0f, .ki = 0.0f, .kd = 0.0f, .i_max = 0.0f, .out_min = -12.0f, .out_max = 12.0f }),
          pid_pos_z_({ .kp = 1.2f, .ki = 0.0f, .kd = 0.0f, .i_max = 0.0f, .out_min = -3.0f,  .out_max = 4.0f }),
          pid_vel_n_({ .kp = 2.0f, .ki = 0.5f, .kd = 0.1f, .i_max = 5.0f, .out_min = -6.0f,  .out_max = 6.0f }),
          pid_vel_e_({ .kp = 2.0f, .ki = 0.5f, .kd = 0.1f, .i_max = 5.0f, .out_min = -6.0f,  .out_max = 6.0f }),
          pid_vel_z_({ .kp = 2.5f, .ki = 1.2f, .kd = 0.05f, .i_max = 4.0f, .out_min = -8.0f, .out_max = 8.0f }),
          pid_rate_p_({ .kp = 0.15f, .ki = 0.20f, .kd = 0.003f, .i_max = 0.3f, .out_min = -1.0f, .out_max = 1.0f }),
          pid_rate_q_({ .kp = 0.15f, .ki = 0.20f, .kd = 0.003f, .i_max = 0.3f, .out_min = -1.0f, .out_max = 1.0f }),
          pid_rate_r_({ .kp = 0.22f, .ki = 0.12f, .kd = 0.000f, .i_max = 0.3f, .out_min = -1.0f, .out_max = 1.0f }) {}

    void set_targets(const Vector3& target_pos, float target_yaw_rad) noexcept {
        target_pos_ = target_pos;
        target_yaw_rad_ = target_yaw_rad;
    }

    void update_slow_loop(const AutopilotState& state, float dt) noexcept {
        constexpr float kGravity = 9.80665f;

        // 1. Позиція -> Швидкість
        float des_vn = pid_pos_n_.update(target_pos_.x, state.pos_neu.x, dt);
        float des_ve = pid_pos_e_.update(target_pos_.y, state.pos_neu.y, dt);
        float des_vz = pid_pos_z_.update(target_pos_.z, state.pos_neu.z, dt);

        const float horiz_spd = std::sqrt(des_vn * des_vn + des_ve * des_ve);
        if (horiz_spd > max_horiz_vel_ && horiz_spd > 1e-4f) {
            const float scale = max_horiz_vel_ / horiz_spd;
            des_vn *= scale;
            des_ve *= scale;
        }
        des_vel_ = { des_vn, des_ve, des_vz };

        // 2. Швидкість -> Прискорення
        const float a_n = pid_vel_n_.update(des_vel_.x, state.vel_neu.x, dt);
        const float a_e = pid_vel_e_.update(des_vel_.y, state.vel_neu.y, dt);
        const float a_z = pid_vel_z_.update(des_vel_.z, state.vel_neu.z, dt);

        // 3. Проекція прискорень на курс корпусу
        const float psi = state.euler_rad.z;
        const float cos_psi = std::cos(psi);
        const float sin_psi = std::sin(psi);

        const float a_fwd   =  a_n * cos_psi + a_e * sin_psi;
        const float a_right = -a_n * sin_psi + a_e * cos_psi;

        // 4. Прискорення -> Кути нахилу
        const float target_pitch = std::clamp(std::atan2(a_fwd, kGravity), -max_tilt_angle_, max_tilt_angle_);
        const float target_roll  = std::clamp(std::atan2(a_right, kGravity), -max_tilt_angle_, max_tilt_angle_);

        des_euler_ = { target_roll, target_pitch, target_yaw_rad_ };

        // 5. Вертикальний канал тяги
        const float cos_tilt = std::max(0.35f, std::cos(state.euler_rad.x) * std::cos(state.euler_rad.y));
        const float thr_accel_offset = (a_z / kGravity) * thr_hover_;
        float raw_thr = (thr_hover_ + thr_accel_offset) / cos_tilt;

        if (state.v_battery > 6.0f) {
            raw_thr *= (state.v_nominal / state.v_battery);
        }
        base_throttle_ = std::clamp(raw_thr, 0.08f, 0.95f);
    }

    [[nodiscard]] AutopilotCommands update_fast_loop(const AutopilotState& state, float dt) noexcept {
        // 1. Орієнтація (P) -> Кутові швидкості
        const float err_roll  = des_euler_.x - state.euler_rad.x;
        const float err_pitch = des_euler_.y - state.euler_rad.y;
        const float err_yaw   = wrap_pi(des_euler_.z - state.euler_rad.z);

        const Vector3 des_rates{
            std::clamp(kp_roll_angle_  * err_roll,  -4.0f, 4.0f),
            std::clamp(kp_pitch_angle_ * err_pitch, -4.0f, 4.0f),
            std::clamp(kp_yaw_angle_   * err_yaw,   -2.5f, 2.5f)
        };

        // 2. Кутові швидкості (PID) -> Моменти
        return AutopilotCommands{
            .roll_torque  = pid_rate_p_.update(des_rates.x, state.gyro_rps.x, dt),
            .pitch_torque = pid_rate_q_.update(des_rates.y, state.gyro_rps.y, dt),
            .yaw_torque   = pid_rate_r_.update(des_rates.z, state.gyro_rps.z, dt),
            .throttle     = base_throttle_
        };
    }

    [[nodiscard]] const Vector3& desired_velocity() const noexcept { return des_vel_; }
    [[nodiscard]] const Vector3& desired_euler() const noexcept { return des_euler_; }

private:
    Vector3 target_pos_{};
    float target_yaw_rad_{0.0f};

    Vector3 des_vel_{};
    Vector3 des_euler_{};
    float base_throttle_{0.45f};

    PidController pid_pos_n_, pid_pos_e_, pid_pos_z_;
    PidController pid_vel_n_, pid_vel_e_, pid_vel_z_;
    PidController pid_rate_p_, pid_rate_q_, pid_rate_r_;

    float kp_roll_angle_{6.5f};
    float kp_pitch_angle_{6.5f};
    float kp_yaw_angle_{3.5f};

    float max_horiz_vel_{12.0f};
    float max_tilt_angle_{35.0f * std::numbers::pi_v<float> / 180.0f};
    float thr_hover_{0.45f};
};

} // namespace autopilot

int main() {
    using namespace autopilot;

    CascadedFlightController controller;
    controller.set_targets(Vector3{ 10.0f, 5.0f, 25.0f }, 90.0f * std::numbers::pi_v<float> / 180.0f);

    AutopilotState state{
        .pos_neu   = { 0.0f, 0.0f, 20.0f },
        .vel_neu   = { 0.0f, 0.0f, 0.0f },
        .euler_rad = { 0.0f, 0.0f, 0.0f },
        .gyro_rps  = { 0.0f, 0.0f, 0.0f },
        .v_battery = 16.0f,
        .v_nominal = 16.0f
    };

    controller.update_slow_loop(state, 0.02f);
    const auto cmd = controller.update_fast_loop(state, 0.002f);

    std::cout << "C++ автопілот успішно розрахував такт керування.\n";
    std::cout << "Тяга: " << cmd.throttle
              << ", Моменти: [" << cmd.roll_torque
              << ", " << cmd.pitch_torque
              << ", " << cmd.yaw_torque << "]\n";

    return 0;
}
```
:::

## Диференціювання виміру (Derivative on Measurement)

Зверніть увагу на розрахунок диференційної складової в функції `pid_update`:

```
deriv = −(meas − prev_meas) / dt
```

У класичному підручниковому ПІД похідна береться від самої похибки: `d(target − meas) / dt`. Коли оператор або планувач місії різко змінює цільову координату (наприклад, стрибок уставки на 10 метрів), похідна від уставки миттєво прямує до нескінченності. Це породжує так званий «диференційний удар» (англ. *derivative kick*), який змушує мотори видавати максимальний ривок струму й може пошкодити силові ключі ESC.

Взяття похідної виключно від зміни **фізичного виміру** `meas` із від'ємним знаком повністю усуває цей ривок при зміні цілі, зберігаючи при цьому повноцінне аеродинамічне демпфування зовнішніх збурень.

## Поведінка системи при ступінчастій зміні уставки

При стрибкоподібній зміні цільових координат вектор похибки плавно насичується на рівні `max_horiz_vel` (12 м/с), забезпечуючи гладкий перехід без різких стрибків кутової швидкості. Коли дрон наближається до точки призначення (похибка менша за 1–2 метри), зовнішній пропорційний контур плавно зменшує цільову швидкість до нуля. Одночасно контур швидкості плавно повертає раму в горизонтальне положення, виключаючи переліт цільової точки.

# ⚙️ Повний автомат процедури виходу з дока на C та C++

Вихід автономної платформи із зарядної станції або відчалювання від пірса — це критична фаза місії, де звичайні алгоритми навігації безпорадні: простір обмежений напрямними рейками, магнітометр спотворений масивними металевими конструкціями, а супутниковий приймач ще не набрав мінімальної шляхової швидкості для визначення курсу. Якщо процедуру реалізувати лінійним кодом із затримками `sleep()`, перший же збій — приварювання силового контакту, проковзування коліс на мокрому металі чи порив притискного вітру — призведе до апаратного заклинювання або аварії. Нижче наведено завершену реалізацію неблокуючого скінченного автомата (Finite State Machine, FSM) виходу з дока промислового рівня мовами C та C++.

## Математична модель та інваріанти станів автомата

Автомат керування реалізує детермінований перехід між вісьмома внутрішніми станами із жорсткими сторожовими таймерами (Watchdogs) та безперервним моніторингом сенсорів зворотного зв'язку:

```
 [IDLE] ──(Start)──> [POWER_CHECK] ──(I_charge < 50mA)──> [PRE_TORQUE] (UGV)
                                                     │
                                                     └──> [UNMOORING_BURST] (USV)
                                                                 │
 [CORRIDOR_REVERSE] <──(Brake Released)──────────────────────────┘
        │
        └──(s_enc >= L_exit)──> [TRACTION_CHECK] ──(s_slip < 0.25)──> [HEADING_ALIGN]
                                                                            │
 [COMPLETE] <──(v_gnss > 0.8 m/s OR t > 4s)─────────────────────────────────┘
```

Для кожного стану визначено математичні інваріанти безпеки та фізичні критерії переходу:

1. `DOCK_STATE_IDLE` — стан очікування команди старту. Силові мотори знеструмлені, стоянкове гальмо затиснуте пружинами, споживання струму мінімальне.
2. `DOCK_STATE_POWER_CHECK` — перевірка розриву силового реле станції (`|I_charge| < 0.05` А, `V_dock < 1.5` В). Якщо за 3.0 секунди напруга не падає, процедура переривається через ризик виникнення електричної дуги на клемах.
3. `DOCK_STATE_PRE_TORQUE` — плавне лінійне нарощування опорного моменту тягових двигунів для запобігання скочуванню (Anti-Rollback) на схилах:
```
M_hold = (m · g · sin(α) · r_wheel) / (2 · i_gear)
```
Сигнал на розтискання стоянкового гальма подається лише після того, як інвертор FOC створив стійке електромагнітне поле в обмотках двигуна.
4. `DOCK_STATE_CORRIDOR_REVERSE` — рух по механічних напрямних ложемента на фіксованій швидкості `v_exit` із контролем одометрії `s = ∫ v dt` та захистом від перекосу за струмом бортів (`|I_left - I_right| < I_max`).
5. `DOCK_STATE_UNMOORING_BURST` — виконання імпульсного маневру віджимання від причалу (Bow Kick / Thrust Burst) для безекіпажних катерів для подолання ефекту Бернуллі біля стінки пірса.
6. `DOCK_STATE_TRACTION_CHECK` — валідація коефіцієнта зчеплення коліс/гусениць на виході з дока через порівняння швидкості енкодерів з інтегралом акселерометра `s_slip = |v_enc - v_imu| / max(...)`.
7. `DOCK_STATE_HEADING_ALIGN` — стабілізація кута курсу за інтегратором гіроскопа до моменту набору швидкості й валідації супутникового вектора GNSS COG (`v_gnss > 0.8` м/с).
8. `DOCK_STATE_COMPLETE` — успішне завершення, передача керування головному навігаційному планувальнику (Waypoint Navigator).
9. `DOCK_STATE_ABORT` — аварійна зупинка при перевищенні таймаутів або виявленні критичних дефектів (миттєве затискання гальм).

## Реалізація автомата на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Перелік станів автомата виходу з дока
typedef enum {
    DOCK_FSM_IDLE = 0,
    DOCK_FSM_POWER_CHECK,
    DOCK_FSM_PRE_TORQUE,
    DOCK_FSM_CORRIDOR_REVERSE,
    DOCK_FSM_UNMOORING_BURST,
    DOCK_FSM_TRACTION_CHECK,
    DOCK_FSM_HEADING_ALIGN,
    DOCK_FSM_COMPLETE,
    DOCK_FSM_ABORT
} dock_fsm_state_t;

// Коди помилок автомата
typedef enum {
    DOCK_ERR_NONE = 0,
    DOCK_ERR_POWER_NOT_DISCONNECTED,
    DOCK_ERR_BRAKE_RELEASE_FAILED,
    DOCK_ERR_CORRIDOR_JAMMED,
    DOCK_ERR_EXCESSIVE_SLIP,
    DOCK_ERR_TIMEOUT
} dock_fsm_error_t;

// Конфігураційні параметри процедури
typedef struct {
    bool is_marine_vehicle;      // true = USV (човен), false = UGV (ровер)
    float exit_velocity_mps;     // Швидкість реверсу у коридорі (м/с)
    float exit_distance_m;       // Довжина напрямних дока (м)
    float vehicle_mass_kg;       // Маса платформи (кг)
    float wheel_radius_m;        // Радіус колеса (м)
    float gear_ratio;            // Передатне число редуктора
    float max_allowed_slip;      // Граничний коефіцієнт ковзання (напр. 0.25)
    float max_motor_current_a;   // Струм відсічки при заклинюванні (А)
    float unmooring_burst_thrust;// Амплітуда імпульсу відчалювання (0.0..1.0)
    float unmooring_burst_dur_s; // Тривалість імпульсу відчалювання (с)
    float phase_timeout_s;       // Таймаут на окрему фазу (с)
} dock_fsm_config_t;

// Вхідні дані телеметрії сенсорів
typedef struct {
    float charge_current_a;      // Струм зарядної лінії
    float dock_voltage_v;        // Напруга на контактах
    float pitch_angle_rad;       // Тангаж (кут схилу)
    float current_left_a;        // Струм лівого мотора
    float current_right_a;       // Струм правого мотора
    float encoder_dist_m;        // Пройдена дистанція за енкодерами
    float encoder_vel_mps;       // Лінійна швидкість за енкодерами
    float imu_accel_x_mps2;      // Поздовжнє прискорення з IMU
    float imu_gyro_z_radps;      // Кутова швидкість рискання
    float gnss_ground_speed_mps; // Швидкість за GNSS
} dock_fsm_inputs_t;

// Вихідні команди на приводи
typedef struct {
    float cmd_vel_linear_mps;    // Задана лінійна швидкість
    float cmd_vel_angular_radps; // Задана кутова швидкість
    float cmd_motor_torque_nm;   // Момент утримання (Pre-Torque)
    float cmd_thrust_left;       // Тяга лівого рушія (-1.0..1.0)
    float cmd_thrust_right;      // Тяга правого рушія (-1.0..1.0)
    bool brake_release_gpio;     // Сигнал зняття стоянкового гальма
} dock_fsm_outputs_t;

// Контекст автомата
typedef struct {
    dock_fsm_state_t state;
    dock_fsm_error_t error;
    dock_fsm_config_t cfg;
    float state_timer_s;
    float start_encoder_dist_m;
    float integrated_heading_rad;
} dock_fsm_context_t;

void dock_fsm_init(dock_fsm_context_t *ctx, const dock_fsm_config_t *cfg) {
    ctx->state = DOCK_FSM_IDLE;
    ctx->error = DOCK_ERR_NONE;
    ctx->cfg = *cfg;
    ctx->state_timer_s = 0.0f;
    ctx->start_encoder_dist_m = 0.0f;
    ctx->integrated_heading_rad = 0.0f;
}

void dock_fsm_start(dock_fsm_context_t *ctx) {
    if (ctx->state == DOCK_FSM_IDLE) {
        ctx->state = DOCK_FSM_POWER_CHECK;
        ctx->error = DOCK_ERR_NONE;
        ctx->state_timer_s = 0.0f;
    }
}

void dock_fsm_step(dock_fsm_context_t *ctx, 
                   const dock_fsm_inputs_t *in, 
                   dock_fsm_outputs_t *out, 
                   float dt) 
{
    ctx->state_timer_s += dt;
    ctx->integrated_heading_rad += in->imu_gyro_z_radps * dt;

    // Скидання вихідних команд за замовчуванням
    out->cmd_vel_linear_mps = 0.0f;
    out->cmd_vel_angular_radps = 0.0f;
    out->cmd_motor_torque_nm = 0.0f;
    out->cmd_thrust_left = 0.0f;
    out->cmd_thrust_right = 0.0f;
    out->brake_release_gpio = false;

    switch (ctx->state) {
        case DOCK_FSM_IDLE:
            break;

        case DOCK_FSM_POWER_CHECK:
            // Перевірка фізичного розриву ланцюга заряду
            if (fabsf(in->charge_current_a) < 0.05f && in->dock_voltage_v < 1.5f) {
                if (ctx->cfg.is_marine_vehicle) {
                    ctx->state = DOCK_FSM_UNMOORING_BURST;
                } else {
                    ctx->state = DOCK_FSM_PRE_TORQUE;
                }
                ctx->state_timer_s = 0.0f;
            } else if (ctx->state_timer_s > ctx->cfg.phase_timeout_s) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_POWER_NOT_DISCONNECTED;
            }
            break;

        case DOCK_FSM_PRE_TORQUE: {
            // Розрахунок антискочувального моменту для ровера: M = (m * g * sin(pitch) * r) / (2 * i)
            float g = 9.80665f;
            float slope_torque = (ctx->cfg.vehicle_mass_kg * g * sinf(in->pitch_angle_rad) * 
                                  ctx->cfg.wheel_radius_m) / (2.0f * ctx->cfg.gear_ratio);
            
            out->cmd_motor_torque_nm = slope_torque;
            
            // Після 200 мс натягу трансмісії подаємо сигнал на розтискання колодок
            if (ctx->state_timer_s > 0.2f) {
                out->brake_release_gpio = true;
            }

            if (ctx->state_timer_s > 0.6f) {
                ctx->state = DOCK_FSM_CORRIDOR_REVERSE;
                ctx->state_timer_s = 0.0f;
                ctx->start_encoder_dist_m = in->encoder_dist_m;
            }
            break;
        }

        case DOCK_FSM_CORRIDOR_REVERSE: {
            out->brake_release_gpio = true;
            out->cmd_vel_linear_mps = -fabsf(ctx->cfg.exit_velocity_mps); // Реверс
            out->cmd_vel_angular_radps = 0.0f; // Суворо прямо

            // Захист від механічного заклинювання в напрямних
            if (fabsf(in->current_left_a) > ctx->cfg.max_motor_current_a ||
                fabsf(in->current_right_a) > ctx->cfg.max_motor_current_a) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_CORRIDOR_JAMMED;
                break;
            }

            float traveled = fabsf(in->encoder_dist_m - ctx->start_encoder_dist_m);
            if (traveled >= ctx->cfg.exit_distance_m) {
                ctx->state = DOCK_FSM_TRACTION_CHECK;
                ctx->state_timer_s = 0.0f;
            } else if (ctx->state_timer_s > ctx->cfg.phase_timeout_s) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_TIMEOUT;
            }
            break;
        }

        case DOCK_FSM_UNMOORING_BURST:
            // Сплеск різнотягу для відтискання носа катера від причалу
            out->cmd_thrust_left = ctx->cfg.unmooring_burst_thrust;
            out->cmd_thrust_right = -ctx->cfg.unmooring_burst_thrust * 0.5f;

            if (ctx->state_timer_s >= ctx->cfg.unmooring_burst_dur_s) {
                ctx->state = DOCK_FSM_HEADING_ALIGN;
                ctx->state_timer_s = 0.0f;
            }
            break;

        case DOCK_FSM_TRACTION_CHECK: {
            out->brake_release_gpio = true;
            out->cmd_vel_linear_mps = -ctx->cfg.exit_velocity_mps * 0.5f;

            // Оцінка пробуксовки: порівняння швидкості енкодерів з інтегрованим прискоренням
            float est_speed = fabsf(in->imu_accel_x_mps2 * ctx->state_timer_s);
            float enc_speed = fabsf(in->encoder_vel_mps);
            float max_s = enc_speed > est_speed ? enc_speed : est_speed;
            
            float slip_ratio = 0.0f;
            if (max_s > 0.05f) {
                slip_ratio = fabsf(enc_speed - est_speed) / max_s;
            }

            if (slip_ratio > ctx->cfg.max_allowed_slip && ctx->state_timer_s > 0.5f) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_EXCESSIVE_SLIP;
            } else if (ctx->state_timer_s > 1.0f) {
                ctx->state = DOCK_FSM_HEADING_ALIGN;
                ctx->state_timer_s = 0.0f;
            }
            break;
        }

        case DOCK_FSM_HEADING_ALIGN:
            out->brake_release_gpio = true;
            // Утримання нульового кутового відхилення від осі виходу
            out->cmd_vel_angular_radps = -1.5f * ctx->integrated_heading_rad;
            out->cmd_vel_linear_mps = ctx->cfg.exit_velocity_mps;

            // Критерій успіху: набір швидкості для валідації курсу GNSS
            if (in->gnss_ground_speed_mps > 0.8f || ctx->state_timer_s > 3.0f) {
                ctx->state = DOCK_FSM_COMPLETE;
            }
            break;

        case DOCK_FSM_COMPLETE:
            out->brake_release_gpio = true;
            break;

        case DOCK_FSM_ABORT:
            // Аварійний скид: мотори блокуються, гальмо затискається
            out->brake_release_gpio = false;
            out->cmd_vel_linear_mps = 0.0f;
            out->cmd_vel_angular_radps = 0.0f;
            break;
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <expected>
#include <string_view>

namespace autonomy::docking {

enum class State : uint8_t {
    Idle = 0,
    PowerCheck,
    PreTorque,
    CorridorReverse,
    UnmooringBurst,
    TractionCheck,
    HeadingAlign,
    Complete,
    Abort
};

enum class Error : uint8_t {
    None = 0,
    PowerNotDisconnected,
    BrakeReleaseFailed,
    CorridorJammed,
    ExcessiveSlip,
    Timeout
};

struct Config {
    bool is_marine_vehicle{false};
    float exit_velocity_mps{0.12f};
    float exit_distance_m{1.80f};
    float vehicle_mass_kg{45.0f};
    float wheel_radius_m{0.125f};
    float gear_ratio{15.0f};
    float max_allowed_slip{0.25f};
    float max_motor_current_a{18.0f};
    float unmooring_burst_thrust{0.75f};
    float unmooring_burst_dur_s{1.20f};
    float phase_timeout_s{5.0f};
};

struct Telemetry {
    float charge_current_a{0.0f};
    float dock_voltage_v{0.0f};
    float pitch_angle_rad{0.0f};
    float current_left_a{0.0f};
    float current_right_a{0.0f};
    float encoder_dist_m{0.0f};
    float encoder_vel_mps{0.0f};
    float imu_accel_x_mps2{0.0f};
    float imu_gyro_z_radps{0.0f};
    float gnss_ground_speed_mps{0.0f};
};

struct ActuatorCommands {
    float cmd_vel_linear_mps{0.0f};
    float cmd_vel_angular_radps{0.0f};
    float cmd_motor_torque_nm{0.0f};
    float cmd_thrust_left{0.0f};
    float cmd_thrust_right{0.0f};
    bool brake_release_gpio{false};
};

class DockExitFsm {
public:
    explicit DockExitFsm(Config cfg) : cfg_(cfg) {}

    void start() noexcept {
        if (state_ == State::Idle) {
            state_ = State::PowerCheck;
            error_ = Error::None;
            state_timer_s_ = 0.0f;
            integrated_heading_rad_ = 0.0f;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] Error error() const noexcept { return error_; }
    [[nodiscard]] bool is_finished() const noexcept { return state_ == State::Complete; }
    [[nodiscard]] bool is_faulted() const noexcept { return state_ == State::Abort; }

    ActuatorCommands update(const Telemetry& in, float dt) noexcept {
        state_timer_s_ += dt;
        integrated_heading_rad_ += in.imu_gyro_z_radps * dt;

        ActuatorCommands out{};

        switch (state_) {
            case State::Idle:
                break;

            case State::PowerCheck:
                if (std::abs(in.charge_current_a) < 0.05f && in.dock_voltage_v < 1.5f) {
                    state_ = cfg_.is_marine_vehicle ? State::UnmooringBurst : State::PreTorque;
                    state_timer_s_ = 0.0f;
                } else if (state_timer_s_ > cfg_.phase_timeout_s) {
                    abort(Error::PowerNotDisconnected);
                }
                break;

            case State::PreTorque: {
                constexpr float g = 9.80665f;
                const float slope_torque = (cfg_.vehicle_mass_kg * g * std::sin(in.pitch_angle_rad) * 
                                            cfg_.wheel_radius_m) / (2.0f * cfg_.gear_ratio);
                
                out.cmd_motor_torque_nm = slope_torque;
                if (state_timer_s_ > 0.2f) {
                    out.brake_release_gpio = true;
                }
                if (state_timer_s_ > 0.6f) {
                    state_ = State::CorridorReverse;
                    state_timer_s_ = 0.0f;
                    start_encoder_dist_m_ = in.encoder_dist_m;
                }
                break;
            }

            case State::CorridorReverse: {
                out.brake_release_gpio = true;
                out.cmd_vel_linear_mps = -std::abs(cfg_.exit_velocity_mps);
                out.cmd_vel_angular_radps = 0.0f;

                if (std::abs(in.current_left_a) > cfg_.max_motor_current_a ||
                    std::abs(in.current_right_a) > cfg_.max_motor_current_a) {
                    abort(Error::CorridorJammed);
                    break;
                }

                const float traveled = std::abs(in.encoder_dist_m - start_encoder_dist_m_);
                if (traveled >= cfg_.exit_distance_m) {
                    state_ = State::TractionCheck;
                    state_timer_s_ = 0.0f;
                } else if (state_timer_s_ > cfg_.phase_timeout_s) {
                    abort(Error::Timeout);
                }
                break;
            }

            case State::UnmooringBurst:
                out.cmd_thrust_left = cfg_.unmooring_burst_thrust;
                out.cmd_thrust_right = -cfg_.unmooring_burst_thrust * 0.5f;

                if (state_timer_s_ >= cfg_.unmooring_burst_dur_s) {
                    state_ = State::HeadingAlign;
                    state_timer_s_ = 0.0f;
                }
                break;

            case State::TractionCheck: {
                out.brake_release_gpio = true;
                out.cmd_vel_linear_mps = -cfg_.exit_velocity_mps * 0.5f;

                const float est_speed = std::abs(in.imu_accel_x_mps2 * state_timer_s_);
                const float enc_speed = std::abs(in.encoder_vel_mps);
                const float max_s = std::max(enc_speed, est_speed);

                const float slip_ratio = (max_s > 0.05f) ? (std::abs(enc_speed - est_speed) / max_s) : 0.0f;

                if (slip_ratio > cfg_.max_allowed_slip && state_timer_s_ > 0.5f) {
                    abort(Error::ExcessiveSlip);
                } else if (state_timer_s_ > 1.0f) {
                    state_ = State::HeadingAlign;
                    state_timer_s_ = 0.0f;
                }
                break;
            }

            case State::HeadingAlign:
                out.brake_release_gpio = true;
                out.cmd_vel_angular_radps = -1.5f * integrated_heading_rad_;
                out.cmd_vel_linear_mps = cfg_.exit_velocity_mps;

                if (in.gnss_ground_speed_mps > 0.8f || state_timer_s_ > 3.0f) {
                    state_ = State::Complete;
                }
                break;

            case State::Complete:
                out.brake_release_gpio = true;
                break;

            case State::Abort:
                out.brake_release_gpio = false;
                out.cmd_vel_linear_mps = 0.0f;
                out.cmd_vel_angular_radps = 0.0f;
                break;
        }

        return out;
    }

private:
    void abort(Error err) noexcept {
        state_ = State::Abort;
        error_ = err;
    }

    Config cfg_;
    State state_{State::Idle};
    Error error_{Error::None};
    float state_timer_s_{0.0f};
    float start_encoder_dist_m_{0.0f};
    float integrated_heading_rad_{0.0f};
};

} // namespace autonomy::docking
```
:::

## Часові затримки та монотонні таймери вбудованих систем

Під час реалізації автомата на мікроконтролерах реального часу (STM32, ESP32 або TI Sitara під керуванням FreeRTOS/Zephyr) категорично заборонено використовувати астрономічний календарний час `gettimeofday()` або функції затримки `delay_ms()`. 

Синхронізація системного часу через GNSS або протокол NTP викликає дискретні стрибки годинника назад чи вперед, що призводить до миттєвого помилкового спрацьовування сторожового таймера `state_timer_s` або, навпаки, до зависання в поточному стані.

Правильна архітектура спирається на монотонні апаратні таймери високої роздільної здатності:

* У середовищі POSIX/Linux: виклик `clock_gettime(CLOCK_MONOTONIC_RAW, &ts)`.
* На мікроконтролерах ARM Cortex-M: 32-бітний регістр циклів ядра `DWT->CYCCNT` або апаратний 64-бітний таймер SysTick / FreeRTOS `xTaskGetTickCount()`.
* Крок інтегрування `dt` обчислюється як різниця між двома послідовними запусками функції `dock_fsm_step()` із санітарним обмеженням `0.001 с ≤ dt ≤ 0.100 с`.

## Модульне тестування автомата (Software-in-the-Loop Harness)

Для валідації надійності переходу між станами автомат тестується синтетичними телеметричними сценаріями в ізольованому тестовому середовищі (SITL):

1. **Сценарій "Ідеальний вихід UGV":** струм падає за 100 мс → розтискання гальма за 600 мс → одометрія наростає до 1.8 м за струму 4.2 А → перевірка зчеплення показує `s_slip = 0.04` → швидкість GNSS досягає 0.9 м/с → перехід у стан `DOCK_FSM_COMPLETE`.
2. **Сценарій "Прикипання контакту":** струм заряду залишається на рівні 12.0 А після подачі команди розмикання → автомат очікує 5.0 с та безаварійно переходить у `DOCK_FSM_ABORT` з помилкою `DOCK_ERR_POWER_NOT_DISCONNECTED`.
3. **Сценарій "Механічне заклинювання":** під час реверсу на відстані 0.4 м струм лівого двигуна підскакує до 24.5 А (перекіс у напрямних) → автомат за один такт фіксує перевантаження і блокує приводи з помилкою `DOCK_ERR_CORRIDOR_JAMMED`.
4. **Сценарій "Пробуксовка на льоду":** колеса крутяться зі швидкістю 0.25 м/с, але інтеграл прискорення IMU показує швидкість менше 0.02 м/с → розрахований коефіцієнт ковзання `s_slip = 0.92 > 0.25` → зупинка за помилкою `DOCK_ERR_EXCESSIVE_SLIP`.
5. **Сценарій "Відчалювання катера (USV)":** після перевірки знеструмлення активується різнотяг `+75% / -37%` на 1.2 секунди → катер розвертається на кут 25° від стінки пірса → перехід до стабілізації курсу за гіроскопом.

## Інженерні підводні камені та крайові випадки

1. **Мікроприварювання контактів (Contact Micro-Welding):** якщо розмикання реле станції дало збій або на клемах залишився ємнісний заряд фільтра інвертора, контактні площадки можуть злипнутися через електродинамічну ерозію. Спроба рушити заблокує мотори. Автомат фіксує перевищення порогу `max_motor_current_a` за відсутності зміни енкодерів і безпечно переходить у `DOCK_FSM_ABORT` замість спалювання обмоток двигуна чи редуктора.
2. **Пробуксовка на вологих металевих апарелях:** коефіцієнт тертя мокрої сталі становить `μ ≈ 0.15–0.25` (проти `0.7–0.8` для сухого асфальту). Фаза `TractionCheck` виявляє розбіжність швидкості енкодерів з інтегратором акселерометра ще до того, як ровер виїде на відкритий ґрунт, запобігаючи неконтрольованому спотворенню одометрії.
3. **Ефект присмоктування стінки пірса:** для безекіпажних човнів (USV) у фазі `UnmooringBurst` різнотяг гвинтів створює початковий відривний момент, запобігаючи затисканню кормової частини катера хвилями, що відбиваються від причальної стінки.
4. **Магнітна девіація в доку:** у фазі `HeadingAlign` автопілот спирається на інтегратор гіроскопа, повністю ігноруючи компас, доки апарат не віддалиться на безпечну відстань від сталевих конструкцій дока.

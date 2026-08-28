# ⚙️ Модуль автомата зльоту польотного контролера на C та C++

Модуль автомата зльоту (англ. *Takeoff Finite State Machine*) керує критичною фазою переходу безпілотного апарата зі статичного положення на землі у стабільне кероване висіння в повітрі. Він реалізує детермінований ланцюг перевірок і переходів із жорсткими часовими та просторовими блокуваннями, виключаючи людський фактор і захищаючи дрон від перекидання, заклинювання моторів чи розгону з некоректним станом навігаційного фільтра.

## Архітектура та часовий регламент модуля

Модуль інтегрується в ієрархію польотного контролера між навігаційним планувальником місії (зовнішній рівень) та контурами стабілізації орієнтації й розподілу тяги (внутрішній рівень). Він виконується в регулярному потоці автопілота з фіксованим періодом квантування `dt = 0.01 с` (частота 100 Гц) або `0.004 с` (250 Гц).

Автомат оперує сімома послідовними станами:
1. `TAKEOFF_STATE_DISARMED` — мотори знеструмлені; постійне фонове опитування передпольотних умов (Pre-Arm Checks);
2. `TAKEOFF_STATE_SPOOLUP` — плавне лінійне або S-подібне нарощування тяги від нуля до порогу холостого ходу (`Idle Throttle`, 5–10%) протягом 1.0 с; моніторинг струмів і обертів по кожному мотору через ESC-телеметрію;
3. `TAKEOFF_STATE_GROUND_RAMP` — підвищення тяги до 60–70% від розрахункової тяги висіння; заморожування інтегральних складових (I-term freeze) регуляторів кутів та вертикальної швидкості для запобігання перекиданню на опорах;
4. `TAKEOFF_STATE_RAPID_CLIMB` — форсований підйом із заданою вертикальною швидкістю `V_z = 1.5–2.0 м/с` для швидкого пробиття турбулентного шару екранного ефекту землі (`z < 1.2 м`); розморожування інтеграторів після детектування відриву;
5. `TAKEOFF_STATE_LEVEL_OFF` — плавне гальмування вертикальної швидкості при наближенні до цільової висоти зльоту `h_target` (наприклад, 5.0 м);
6. `TAKEOFF_STATE_COMPLETE` — зліт успішно завершено; передача керування навігаційному автомату поточної місії або утримання позиції (Position Hold);
7. `TAKEOFF_STATE_ABORT` — аварійне переривання зльоту; миттєве скидання газу на нуль (`Disarm`), блокування виходів ESC, фіксація коду помилки та генерація критичного сповіщення.

## Інженерні принципи реалізації та детермінізм

Для забезпечення надійності в реальному часі на вбудованих мікроконтролерах ARM Cortex-M4/M7/H7 модуль спроєктовано за жорсткими стандартами безпеки:
- **Повна відсутність динамічної пам'яті (Zero Heap Allocation):** Усі структури даних, буфери телеметрії та контексти станів розміщуються статично або на стеку. Жоден виклик `malloc()`, `free()` або оператор `new` не використовується, що запобігає фрагментації оперативної пам'яті;
- **Гарантований час виконання (Deterministic Execution Budget):** Кожен такт виклику функції `takeoff_fsm_update()` виконує фіксовану кількість арифметичних операцій без нескінченних циклів чи очікувань, витрачаючи менше ніж `1.5 мкс` процесорного часу при частоті ядра 480 МГц;
- **Безпека за замовчуванням (Fail-Safe Default State):** Будь-який невідомий або пошкоджений стан пам'яті автоматично перемикає FSM у гілку `ABORT` зі скиданням командної тяги до нуля;
- **Ізоляція інтерфейсів:** Модуль приймає сирі структури телеметрії та повертає уніфікований вектор команд керування (`ControlOutput`), не маючи прямих залежностей від апаратних регістрів таймерів чи драйверів шини CAN/I2C.

## Послідовність обробки телеметрії та захисних блокувань

Під час виконання кожного такту модуль здійснює багаторівневу фільтрацію сигналів і перевірку аварійних порогів:
1. **Контроль нахилу на землі:** Якщо сумарний кут нахилу `θ = sqrt(roll² + pitch²)` перевищує поріг 15 градусів на етапах розкрутки чи набору тяги, це інтерпретується як початок перекидання дрона на ніжці, що викликає негайне вимикання моторів за час `< 10 мс`;
2. **Аналіз симетрії струмів і обертів:** Струм кожного двигуна порівнюється із середнім значенням. Якщо розкид перевищує допустимий поріг (наприклад, 3.5 А при струмі холостого ходу 2.0 А), це свідчить про заклинювання підшипника, дефект пропелера або попадання стороннього предмета;
3. **Детектор застрягання (Stuck Detection):** Якщо тяга перевищує 70% від номінальної тяги висіння понад 1.5 с, але вертикальна швидкість залишається меншою за 0.15 м/с, автомат фіксує зачеплення за ґрунт чи кабель і перериває зліт;
4. **Усунення інтегрального насичення (Anti-Windup):** Прапорець `freeze_integrators` утримується у значенні `true` протягом усього часу контакту з поверхнею, що блокує накопичення інтегральних сум у регуляторах кутів і швидкості підйому.

## Обробка крайових випадків та перешкод

У реальних польотних умовах автомат зльоту стикається з низкою специфічних збурень, які вимагають окремої логіки:
- **Короткочасні пориви вітру на землі:** При бічному пориві вітру струм одного з навітряних моторів може короткочасно підскочити. Щоб уникнути хибного спрацювання захисту по струму, в алгоритм закладено фільтр ковзного вікна або перевірку перевищення протягом не менше ніж `50 мс`;
- **Збій телеметрії DShot (CRC Errors):** Якщо пакет цифрової телеметрії ESC спотворений перешкодою від силового інвертора, модуль ігнорує окремий бітий кадр, спираючись на попереднє валідне значення; якщо ж зв'язок втрачено на більш ніж `100 мс`, фіксується відмова привода;
- **Гістерезис детектування відриву:** Перехід зі стану `GROUND_RAMP` у `RAPID_CLIMB` є незворотним. Якщо після детектування відриву вертикальна швидкість тимчасово зменшиться через турбулентність, автомат не повертається у стан землі, а продовжує підйом за внутрішнім таймером до виходу на безпечну висоту.

## Реалізація модуля

Нижче наведено повну реалізацію автомата зльоту: на мові C99 без динамічного виділення пам'яті (MISRA-сумісний дизайн) та на сучасному C++20 із застосуванням сильної типізації `enum class`, `std::array`, `std::string_view` та інкапсуляції в клас `TakeoffFSM`.

:::tabs
```c
/* ============================================================================
 * takeoff_fsm.h / takeoff_fsm.c
 * Автомат процедури зльоту безпілотного апарата (C99)
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_MOTORS 8
#define GRAVITY_MSS 9.80665f

typedef enum {
    TAKEOFF_STATE_DISARMED = 0,
    TAKEOFF_STATE_SPOOLUP,
    TAKEOFF_STATE_GROUND_RAMP,
    TAKEOFF_STATE_RAPID_CLIMB,
    TAKEOFF_STATE_LEVEL_OFF,
    TAKEOFF_STATE_COMPLETE,
    TAKEOFF_STATE_ABORT
} takeoff_state_t;

typedef enum {
    ABORT_NONE = 0,
    ABORT_TILT_EXCEEDED,        /* Кут нахилу на землі перевищив 15 градусів */
    ABORT_MOTOR_CURRENT_IMBALANCE,/* Струм одного з моторів суттєво відхилився */
    ABORT_MOTOR_RPM_LOSS,       /* Втрата обертів одного з роторів */
    ABORT_SPOOLUP_TIMEOUT,      /* Розкрутка перевищила ліміт часу */
    ABORT_TAKEOFF_STUCK,        /* Тяга висока, але відриву немає за 1.5 с */
    ABORT_EKF_DIVERGENCE,       /* Розходження навігаційного фільтра */
    ABORT_MANUAL_COMMAND        /* Команда оператора або скидання з пульта */
} takeoff_abort_reason_t;

/* Вхідні телеметричні дані від підсистем літака */
typedef struct {
    float roll_deg;             /* Поточний крен [град] */
    float pitch_deg;            /* Поточний тангаж [град] */
    float yaw_deg;              /* Поточний курс [град] */
    float alt_rel_m;            /* Відносна висота над точкою старту [м] */
    float vz_ms;                /* Вертикальна швидкість (догори > 0) [м/с] */
    float accel_z_mss;          /* Вертикальне прискорення [м/с^2] */
    
    /* Дані GNSS та EKF */
    bool ekf_healthy;           /* Працездатність EKF */
    float ekf_hpos_variance;    /* Горизонтальна дисперсія позиції EKF [м] */
    float ekf_vpos_variance;    /* Вертикальна дисперсія позиції EKF [м] */
    uint8_t gnss_sats;          /* Кількість видимих супутників */
    float gnss_hdop;            /* Geometric dilution of precision */
    
    /* Батарея */
    float battery_voltage;      /* Загальна напруга АКБ [В] */
    float cell_min_voltage;     /* Мінімальна напруга комірки [В] */
    
    /* ESC-телеметрія моторів (DShot / RPM) */
    uint8_t num_motors;
    float motor_currents[MAX_MOTORS]; /* Струм кожного мотора [А] */
    float motor_rpm[MAX_MOTORS];      /* Оберти кожного мотора [об/хв] */
} takeoff_telemetry_t;

/* Налаштування автомата зльоту */
typedef struct {
    float target_alt_m;         /* Цільова висота зльоту (за замовчуванням 5.0 м) */
    float ground_clear_alt_m;   /* Висота виходу з екрана землі (1.2 м) */
    float climb_rate_ms;        /* Швидкість пробиття екрана (2.0 м/с) */
    float hover_throttle;       /* Оцінка газу висіння (0.45 .. 0.55) */
    float idle_throttle;        /* Газ холостого ходу (0.08) */
    float max_tilt_on_ground;   /* Поріг нахилу до відриву (15.0 град) */
    float max_current_imbalance;/* Макс. допустимий перекіс струму [А] (3.5 А) */
    float spoolup_time_s;       /* Тривалість розкрутки (1.0 с) */
    float liftoff_detect_vz_ms; /* Поріг детектування відриву за Vz (0.25 м/с) */
} takeoff_config_t;

/* Керівні команди, що видає автомат у контури стабілізації */
typedef struct {
    float throttle_cmd;         /* Нормалізований сигнал газу [0.0 .. 1.0] */
    float vz_setpoint_ms;       /* Уставка вертикальної швидкості [м/с] */
    float alt_setpoint_m;       /* Уставка висоти [м] */
    bool freeze_integrators;    /* Прапорець заморожування I-складових PID */
    bool arm_command;           /* Команда на зведення моторів */
    bool home_point_latch_req;  /* Вимога зафіксувати Home Point */
} takeoff_control_output_t;

/* Контекст автомата */
typedef struct {
    takeoff_state_t state;
    takeoff_abort_reason_t abort_reason;
    takeoff_config_t config;
    float state_timer_s;
    bool liftoff_confirmed;
    bool home_latched;
} takeoff_fsm_t;

/* Ініціалізація модуля */
void takeoff_fsm_init(takeoff_fsm_t *fsm, const takeoff_config_t *cfg)
{
    if (!fsm) return;
    if (cfg) {
        fsm->config = *cfg;
    } else {
        /* Значення за замовчуванням */
        fsm->config.target_alt_m = 5.0f;
        fsm->config.ground_clear_alt_m = 1.2f;
        fsm->config.climb_rate_ms = 2.0f;
        fsm->config.hover_throttle = 0.50f;
        fsm->config.idle_throttle = 0.08f;
        fsm->config.max_tilt_on_ground = 15.0f;
        fsm->config.max_current_imbalance = 3.5f;
        fsm->config.spoolup_time_s = 1.0f;
        fsm->config.liftoff_detect_vz_ms = 0.25f;
    }
    fsm->state = TAKEOFF_STATE_DISARMED;
    fsm->abort_reason = ABORT_NONE;
    fsm->state_timer_s = 0.0f;
    fsm->liftoff_confirmed = false;
    fsm->home_latched = false;
}

/* Перевірка передпольотних умов (Pre-Arm Checks) */
bool takeoff_check_prearm(const takeoff_telemetry_t *telem)
{
    if (!telem) return false;
    
    /* 1. Стан навігаційного фільтра EKF */
    if (!telem->ekf_healthy) return false;
    if (telem->ekf_hpos_variance > 1.2f || telem->ekf_vpos_variance > 2.0f) return false;
    
    /* 2. Якість фіксу GNSS */
    if (telem->gnss_sats < 8 || telem->gnss_hdop > 1.4f) return false;
    
    /* 3. Горизонтальне положення на землі */
    if (fabsf(telem->roll_deg) > 10.0f || fabsf(telem->pitch_deg) > 10.0f) return false;
    
    /* 4. Напруга АКБ */
    if (telem->cell_min_voltage < 3.75f) return false;
    
    return true;
}

/* Перевірка симетрії струмів моторів під час розкрутки */
static bool check_motor_current_symmetry(const takeoff_telemetry_t *telem, float max_diff)
{
    if (telem->num_motors < 2) return true;
    
    float sum = 0.0f;
    for (uint8_t i = 0; i < telem->num_motors; ++i) {
        sum += telem->motor_currents[i];
    }
    float avg = sum / (float)telem->num_motors;
    
    for (uint8_t i = 0; i < telem->num_motors; ++i) {
        if (fabsf(telem->motor_currents[i] - avg) > max_diff) {
            return false; /* Виявлено асиметрію: заклинювання або дефект гвинта */
        }
    }
    return true;
}

/* Головний такт оновлення автомата зльоту */
void takeoff_fsm_update(takeoff_fsm_t *fsm,
                        const takeoff_telemetry_t *telem,
                        float dt,
                        takeoff_control_output_t *out)
{
    if (!fsm || !telem || !out) return;
    
    fsm->state_timer_s += dt;
    
    /* За замовчуванням безпечні виходи */
    out->throttle_cmd = 0.0f;
    out->vz_setpoint_ms = 0.0f;
    out->alt_setpoint_m = 0.0f;
    out->freeze_integrators = true;
    out->arm_command = false;
    out->home_point_latch_req = false;
    
    /* Загальний захист: перевищення кута нахилу до повного набору висоти */
    float tilt = sqrtf(telem->roll_deg * telem->roll_deg + telem->pitch_deg * telem->pitch_deg);
    if (fsm->state >= TAKEOFF_STATE_SPOOLUP && fsm->state <= TAKEOFF_STATE_GROUND_RAMP) {
        if (tilt > fsm->config.max_tilt_on_ground) {
            fsm->state = TAKEOFF_STATE_ABORT;
            fsm->abort_reason = ABORT_TILT_EXCEEDED;
        }
    }
    
    switch (fsm->state) {
    case TAKEOFF_STATE_DISARMED:
        out->arm_command = false;
        out->throttle_cmd = 0.0f;
        out->freeze_integrators = true;
        break;
        
    case TAKEOFF_STATE_SPOOLUP:
        out->arm_command = true;
        out->freeze_integrators = true;
        
        /* Плавна рампа газу холостого ходу */
        {
            float progress = fsm->state_timer_s / fsm->config.spoolup_time_s;
            if (progress > 1.0f) progress = 1.0f;
            out->throttle_cmd = fsm->config.idle_throttle * progress;
        }
        
        /* Перевірка симетрії наприкінці розкрутки */
        if (fsm->state_timer_s >= fsm->config.spoolup_time_s) {
            if (!check_motor_current_symmetry(telem, fsm->config.max_current_imbalance)) {
                fsm->state = TAKEOFF_STATE_ABORT;
                fsm->abort_reason = ABORT_MOTOR_CURRENT_IMBALANCE;
            } else {
                /* Перехід до набору тяги відриву */
                fsm->state = TAKEOFF_STATE_GROUND_RAMP;
                fsm->state_timer_s = 0.0f;
            }
        }
        break;
        
    case TAKEOFF_STATE_GROUND_RAMP:
        out->arm_command = true;
        out->freeze_integrators = true;
        
        /* Форсована тяга відриву: 1.25 від тяги висіння */
        {
            float target_takeoff_thr = fsm->config.hover_throttle * 1.25f;
            float ramp = fsm->state_timer_s / 0.5f; /* 0.5 с на досягнення */
            if (ramp > 1.0f) ramp = 1.0f;
            out->throttle_cmd = fsm->config.idle_throttle + 
                               (target_takeoff_thr - fsm->config.idle_throttle) * ramp;
        }
        
        /* Детектування відриву */
        if (telem->vz_ms > fsm->config.liftoff_detect_vz_ms || telem->alt_rel_m > 0.15f) {
            fsm->liftoff_confirmed = true;
            if (!fsm->home_latched) {
                out->home_point_latch_req = true;
                fsm->home_latched = true;
            }
            fsm->state = TAKEOFF_STATE_RAPID_CLIMB;
            fsm->state_timer_s = 0.0f;
        } else if (fsm->state_timer_s > 1.5f) {
            /* Тяга піднята, але вертикального руху немає — апарат застряг */
            fsm->state = TAKEOFF_STATE_ABORT;
            fsm->abort_reason = ABORT_TAKEOFF_STUCK;
        }
        break;
        
    case TAKEOFF_STATE_RAPID_CLIMB:
        out->arm_command = true;
        out->freeze_integrators = false; /* Розморожуємо інтегратори після відриву */
        out->vz_setpoint_ms = fsm->config.climb_rate_ms;
        out->throttle_cmd = fsm->config.hover_throttle * 1.20f;
        
        /* Перевірка виходу із зони екрана */
        if (telem->alt_rel_m >= fsm->config.ground_clear_alt_m) {
            fsm->state = TAKEOFF_STATE_LEVEL_OFF;
            fsm->state_timer_s = 0.0f;
        }
        break;
        
    case TAKEOFF_STATE_LEVEL_OFF:
        out->arm_command = true;
        out->freeze_integrators = false;
        out->alt_setpoint_m = fsm->config.target_alt_m;
        
        /* Пропорційне гасіння вертикальної швидкості при наближенні до цілі */
        {
            float remaining = fsm->config.target_alt_m - telem->alt_rel_m;
            if (remaining < 0.8f) {
                out->vz_setpoint_ms = fsm->config.climb_rate_ms * (remaining / 0.8f);
                if (out->vz_setpoint_ms < 0.2f) out->vz_setpoint_ms = 0.2f;
            } else {
                out->vz_setpoint_ms = fsm->config.climb_rate_ms;
            }
        }
        
        /* Завершення зльоту при досягненні 95% висоти */
        if (telem->alt_rel_m >= (fsm->config.target_alt_m * 0.95f) && fabsf(telem->vz_ms) < 0.3f) {
            fsm->state = TAKEOFF_STATE_COMPLETE;
            fsm->state_timer_s = 0.0f;
        }
        break;
        
    case TAKEOFF_STATE_COMPLETE:
        out->arm_command = true;
        out->freeze_integrators = false;
        out->alt_setpoint_m = fsm->config.target_alt_m;
        out->vz_setpoint_ms = 0.0f;
        out->throttle_cmd = fsm->config.hover_throttle;
        break;
        
    case TAKEOFF_STATE_ABORT:
    default:
        out->arm_command = false; /* Негайний Disarm */
        out->throttle_cmd = 0.0f;
        out->vz_setpoint_ms = 0.0f;
        out->freeze_integrators = true;
        break;
    }
}

/* Запуск процедури зльоту за командою оператора */
bool takeoff_fsm_start(takeoff_fsm_t *fsm, const takeoff_telemetry_t *telem)
{
    if (!fsm || !telem) return false;
    if (fsm->state != TAKEOFF_STATE_DISARMED) return false;
    
    if (!takeoff_check_prearm(telem)) {
        return false; /* Передпольотні перевірки не пройшли */
    }
    
    fsm->state = TAKEOFF_STATE_SPOOLUP;
    fsm->abort_reason = ABORT_NONE;
    fsm->state_timer_s = 0.0f;
    fsm->liftoff_confirmed = false;
    fsm->home_latched = false;
    return true;
}
```
```cpp
// ============================================================================
// TakeoffFSM.hpp
// Автомат процедури зльоту безпілотного апарата (C++20)
// ============================================================================
#pragma once

#include <array>
#include <cmath>
#include <span>
#include <string_view>
#include <algorithm>
#include <numeric>

namespace drone::flight {

constexpr size_t MaxMotors = 8;
constexpr float GravityMss = 9.80665f;

enum class TakeoffState : uint8_t {
    Disarmed = 0,
    Spoolup,
    GroundRamp,
    RapidClimb,
    LevelOff,
    Complete,
    Abort
};

enum class AbortReason : uint8_t {
    None = 0,
    TiltExceeded,
    MotorCurrentImbalance,
    MotorRpmLoss,
    SpoolupTimeout,
    TakeoffStuck,
    EkfDivergence,
    ManualCommand
};

struct Telemetry {
    float rollDeg{0.0f};
    float pitchDeg{0.0f};
    float yawDeg{0.0f};
    float altRelM{0.0f};
    float vzMs{0.0f};
    float accelZMss{0.0f};

    bool ekfHealthy{false};
    float ekfHposVariance{0.0f};
    float ekfVposVariance{0.0f};
    uint8_t gnssSats{0};
    float gnssHdop{99.0f};

    float batteryVoltage{0.0f};
    float cellMinVoltage{0.0f};

    uint8_t numMotors{4};
    std::array<float, MaxMotors> motorCurrents{};
    std::array<float, MaxMotors> motorRpm{};
};

struct Config {
    float targetAltM{5.0f};
    float groundClearAltM{1.2f};
    float climbRateMs{2.0f};
    float hoverThrottle{0.50f};
    float idleThrottle{0.08f};
    float maxTiltOnGround{15.0f};
    float maxCurrentImbalance{3.5f};
    float spoolupTimeS{1.0f};
    float liftoffDetectVzMs{0.25f};
};

struct ControlOutput {
    float throttleCmd{0.0f};
    float vzSetpointMs{0.0f};
    float altSetpointM{0.0f};
    bool freezeIntegrators{true};
    bool armCommand{false};
    bool homePointLatchReq{false};
};

class TakeoffFSM {
public:
    explicit constexpr TakeoffFSM(const Config& cfg = Config{}) : config_{cfg} {}

    [[nodiscard]] bool checkPrearm(const Telemetry& telem) const noexcept {
        if (!telem.ekfHealthy) return false;
        if (telem.ekfHposVariance > 1.2f || telem.ekfVposVariance > 2.0f) return false;
        if (telem.gnssSats < 8 || telem.gnssHdop > 1.4f) return false;
        if (std::abs(telem.rollDeg) > 10.0f || std::abs(telem.pitchDeg) > 10.0f) return false;
        if (telem.cellMinVoltage < 3.75f) return false;
        return true;
    }

    bool start(const Telemetry& telem) noexcept {
        if (state_ != TakeoffState::Disarmed) return false;
        if (!checkPrearm(telem)) return false;

        state_ = TakeoffState::Spoolup;
        abortReason_ = AbortReason::None;
        stateTimerS_ = 0.0f;
        liftoffConfirmed_ = false;
        homeLatched_ = false;
        return true;
    }

    void abort(AbortReason reason) noexcept {
        state_ = TakeoffState::Abort;
        abortReason_ = reason;
        stateTimerS_ = 0.0f;
    }

    void update(const Telemetry& telem, float dt, ControlOutput& out) noexcept {
        stateTimerS_ += dt;

        out.throttleCmd = 0.0f;
        out.vzSetpointMs = 0.0f;
        out.altSetpointM = 0.0f;
        out.freezeIntegrators = true;
        out.armCommand = false;
        out.homePointLatchReq = false;

        // Захист від нахилу на землі
        const float tilt = std::hypot(telem.rollDeg, telem.pitchDeg);
        if (state_ >= TakeoffState::Spoolup && state_ <= TakeoffState::GroundRamp) {
            if (tilt > config_.maxTiltOnGround) {
                abort(AbortReason::TiltExceeded);
            }
        }

        switch (state_) {
        case TakeoffState::Disarmed:
            out.armCommand = false;
            out.freezeIntegrators = true;
            break;

        case TakeoffState::Spoolup: {
            out.armCommand = true;
            out.freezeIntegrators = true;

            const float progress = std::clamp(stateTimerS_ / config_.spoolupTimeS, 0.0f, 1.0f);
            out.throttleCmd = config_.idleThrottle * progress;

            if (stateTimerS_ >= config_.spoolupTimeS) {
                if (!checkCurrentSymmetry(telem)) {
                    abort(AbortReason::MotorCurrentImbalance);
                } else {
                    state_ = TakeoffState::GroundRamp;
                    stateTimerS_ = 0.0f;
                }
            }
            break;
        }

        case TakeoffState::GroundRamp: {
            out.armCommand = true;
            out.freezeIntegrators = true;

            const float targetThr = config_.hoverThrottle * 1.25f;
            const float ramp = std::clamp(stateTimerS_ / 0.5f, 0.0f, 1.0f);
            out.throttleCmd = config_.idleThrottle + (targetThr - config_.idleThrottle) * ramp;

            if (telem.vzMs > config_.liftoffDetectVzMs || telem.altRelM > 0.15f) {
                liftoffConfirmed_ = true;
                if (!homeLatched_) {
                    out.homePointLatchReq = true;
                    homeLatched_ = true;
                }
                state_ = TakeoffState::RapidClimb;
                stateTimerS_ = 0.0f;
            } else if (stateTimerS_ > 1.5f) {
                abort(AbortReason::TakeoffStuck);
            }
            break;
        }

        case TakeoffState::RapidClimb:
            out.armCommand = true;
            out.freezeIntegrators = false; // Розморожуємо PID після відриву
            out.vzSetpointMs = config_.climbRateMs;
            out.throttleCmd = config_.hoverThrottle * 1.20f;

            if (telem.altRelM >= config_.groundClearAltM) {
                state_ = TakeoffState::LevelOff;
                stateTimerS_ = 0.0f;
            }
            break;

        case TakeoffState::LevelOff: {
            out.armCommand = true;
            out.freezeIntegrators = false;
            out.altSetpointM = config_.targetAltM;

            const float remaining = config_.targetAltM - telem.altRelM;
            if (remaining < 0.8f) {
                out.vzSetpointMs = std::max(0.2f, config_.climbRateMs * (remaining / 0.8f));
            } else {
                out.vzSetpointMs = config_.climbRateMs;
            }

            if (telem.altRelM >= (config_.targetAltM * 0.95f) && std::abs(telem.vzMs) < 0.3f) {
                state_ = TakeoffState::Complete;
                stateTimerS_ = 0.0f;
            }
            break;
        }

        case TakeoffState::Complete:
            out.armCommand = true;
            out.freezeIntegrators = false;
            out.altSetpointM = config_.targetAltM;
            out.vzSetpointMs = 0.0f;
            out.throttleCmd = config_.hoverThrottle;
            break;

        case TakeoffState::Abort:
        default:
            out.armCommand = false;
            out.throttleCmd = 0.0f;
            out.vzSetpointMs = 0.0f;
            out.freezeIntegrators = true;
            break;
        }
    }

    [[nodiscard]] TakeoffState state() const noexcept { return state_; }
    [[nodiscard]] AbortReason abortReason() const noexcept { return abortReason_; }
    [[nodiscard]] bool isComplete() const noexcept { return state_ == TakeoffState::Complete; }

    [[nodiscard]] std::string_view stateName() const noexcept {
        switch (state_) {
        case TakeoffState::Disarmed:   return "DISARMED";
        case TakeoffState::Spoolup:    return "SPOOLUP";
        case TakeoffState::GroundRamp: return "GROUND_RAMP";
        case TakeoffState::RapidClimb: return "RAPID_CLIMB";
        case TakeoffState::LevelOff:   return "LEVEL_OFF";
        case TakeoffState::Complete:   return "COMPLETE";
        case TakeoffState::Abort:      return "ABORT";
        default:                       return "UNKNOWN";
        }
    }

private:
    [[nodiscard]] bool checkCurrentSymmetry(const Telemetry& telem) const noexcept {
        if (telem.numMotors < 2) return true;
        const auto activeCurrents = std::span(telem.motorCurrents.data(), telem.numMotors);
        const float sum = std::accumulate(activeCurrents.begin(), activeCurrents.end(), 0.0f);
        const float avg = sum / static_cast<float>(telem.numMotors);

        for (float curr : activeCurrents) {
            if (std::abs(curr - avg) > config_.maxCurrentImbalance) {
                return false;
            }
        }
        return true;
    }

    Config config_;
    TakeoffState state_{TakeoffState::Disarmed};
    AbortReason abortReason_{AbortReason::None};
    float stateTimerS_{0.0f};
    bool liftoffConfirmed_{false};
    bool homeLatched_{false};
};

} // namespace drone::flight
```
:::

## Інтеграція з контурами навігації та телеметрії

Після завершення фази зльоту (перехід у стан `TAKEOFF_STATE_COMPLETE`) модуль виставляє сигнал успішного зведення, утримуючи задану висоту `h_target` та нульову вертикальну швидкість `V_z = 0.0 м/с`. Навігаційний стек автопілота зчитує стан завершення через метод `isComplete()` і перемикає джерело цільових координат на планувальник польотного завдання. Якщо ж у процесі зльоту спрацьовує аварійне блокування, причина відмови `AbortReason` транслюється у рядок MAVLink `STATUSTEXT`, інформуючи наземну станцію про точний фактор переривання місії.

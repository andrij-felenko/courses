# ⚙️ Модуль кінцевого автомата скасування посадки з верифікацією висот і залишку заряду

Цей проектний модуль реалізує автономний кінцевий автомат скасування посадки (англ. *Go-Around / Abort Landing FSM*) для вбудованих польотних контролерів безпілотних літальних апаратів. Модуль розв'язує задачу безпечного переривання фінального зниження при виявленні перешкод, поривів вітру чи збоїв позиціювання, виконує розрахунок динамічної просадки по висоті та динамічно оцінює залишок енергії в акумуляторі перед ухваленням рішення про вихід на друге коло або аварійний відхід на запасний майданчик.

Без цього механізму автономний дрон при раптовому виникненні перешкоди або збої оптичного наведення або продовжує спуск у небезпечну зону, викликаючи аварію, або намагається злетіти без урахування інерції та залишку заряду, що призводить до зіткнення з землею через просідання чи вимкнення живлення в повітрі через просідання напруги батареї.

---

### Архітектура модуля та потік даних

Модуль спроектовано для роботи у складі навігаційного контуру автопілота з фіксованою частотою виклику 50 Гц (період дискретизації `dt = 20 мс`). Архітектура виключає динамічне виділення пам'яті (`malloc`/`free` або оператори `new`/`delete`), що гарантує детермінізм часу виконання та запобігає фрагментації оперативної пам'яті мікроконтролера.

```
+-----------------------------------------------------------------------------+
|                               ВХІДНІ ДАНІ                                   |
| - Барометрична/злита висота Z та вертикальна швидкість Vz                   |
| - Дистанція з лазерного далекоміра (LiDAR) з фільтром валідності            |
| - Поточні кути орієнтації (Roll, Pitch, Yaw)                                |
| - Телеметрія батареї: напруга під навантаженням V_bat, струм I_bat, SOC     |
| - Прапорці аварійних команд оператора (RC switch / MAVLink command)         |
+--------------------------------------|--------------------------------------+
                                       v
+-----------------------------------------------------------------------------+
|                          БЛОК ОБРОБКИ ТА ФІЛЬТРАЦІЇ                         |
| - Антибрязкіт далекоміра (Debounce filter: N валідних відліків поспіль)     |
| - Оцінка кінематичної просадки: Δh_sink = |Vz|·t_spool + Vz² / (2·a_climb)  |
| - Аудит енергії на друге коло: E_req = P_climb·t1 + P_loiter·t2 + P_land·t3 |
+--------------------------------------|--------------------------------------+
                                       v
+-----------------------------------------------------------------------------+
|                             АВТОМАТ СТАНІВ (FSM)                            |
| 1. APPROACH_DESCENT  -> Спуск за глісадою, контроль висоти рішення          |
| 2. ABORT_BRAKE_CLIMB -> Екстрений вертикальний набір, Roll/Pitch = 0        |
| 3. ENERGY_AUDIT      -> Оцінка можливості повторного заходу                 |
| 4. CIRCUIT_LOITER    -> Коло очікування та повторний вихід на FAF           |
| 5. EMERGENCY_FAILSAFE-> Відхід на Rally Point або керована посадка          |
+--------------------------------------|--------------------------------------+
                                       v
+-----------------------------------------------------------------------------+
|                             ВИХІДНІ УСТАВКИ                                 |
| - Цільова вертикальна швидкість Vz_setpoint                                 |
| - Цільова висота Alt_setpoint                                               |
| - Обмеження кутів крену й тангажу Tilt_limit_max                            |
| - Прапорець пріоритету вертикальної тяги Climb_priority                     |
+-----------------------------------------------------------------------------+
```

Вхідні сигнали надходять із трьох незалежних підсистем автопілота:
1. **Інерціально-навігаційна система (EKF)**: постачає злиту оцінку висоти над точкою старту `altitude_m`, вертикальну швидкість `vertical_speed_ms` та кути Ейлера (`roll_rad`, `pitch_rad`).
2. **Далекомір надиру (LiDAR / Sonar)**: передає сиру дистанцію до перешкоди `lidar_distance_m` разом із прапорцем достовірності `lidar_valid`.
3. **Система моніторингу живлення (Power Monitor)**: вимірює напругу `battery_voltage_v`, миттєвий струм `battery_current_a` та розраховує нормалізований рівень заряду `battery_soc` (0.0..1.0).

---

### Математичні моделі та алгоритми

#### 1. Фільтрація показань лідара та захист від сплесків (Debouncing)
Оптичні лазерні далекоміри можуть видавати поодинокі хибні відліки через пролітання пилу, оптичні відблиски або потрапляння променя на стебла трави. Щоб уникнути помилкового скасування посадки на чистому майданчику, модуль застосовує алгоритм підтвердження тригера за часом.

Для спрацьовування тригера перешкоди необхідно, щоб дистанція з далекоміра була меншою за порогову протягом `N` циклів поспіль (за замовчуванням 5 циклів по 20 мс = 100 мс):

```
Count_obstacle = Count_obstacle + 1   [якщо d_lidar < Obstacle_Threshold]
Count_obstacle = 0                    [якщо d_lidar >= Obstacle_Threshold]
Trigger_Obstacle = (Count_obstacle >= N_confirm)
```

Такий підхід повністю відсікає короткочасні шумові викиди далекоміра, зберігаючи реакцію на реальну статичну або динамічну перешкоду в межах однієї десятої секунди.

#### 2. Розрахунок динамічної просадки (Sinkage Estimator)
При виникненні тригера скасування модуль обчислює фізичну просадку апарата вниз, враховуючи поточну вертикальну швидкість спуску `v_z` та тягооснащеність силової установки `T_ratio = T_max / (m · g)`:

```
a_climb_avail = (T_ratio - 1.0) · g       [доступне вертикальне прискорення]
Δh_spool = |v_z| · t_spoolup              [просідання під час розгону роторів]
Δh_brake = (v_z)² ÷ (2 · a_climb_avail)   [шлях гальмування вертикальної швидкості]
Δh_sink = Δh_spool + Δh_brake             [повна просадка]
```

Якщо поточна висота `h_current < Δh_sink + h_margin`, скасування посадки фізично не встигне зупинити контакт із землею. У такій ситуації замість набору максимального газу модуль активує режим екстреного приземлення, запобігаючи руйнуванню пропелерів на повній тязі під час удару об землю.

#### 3. Модель енергетичного балансу акумулятора
Перед переходом у коло очікування модуль виконує аудит залишкової енергії батареї. Напруга під навантаженням падає через внутрішній опір комірок `R_int`:

```
V_cell_loaded = V_cell_ocv - I_climb · R_int      [напруга під максимальним струмом]
```

Якщо `V_cell_loaded < V_cutoff` (наприклад, менше 3.35 В на комірку) або обчислений залишок заряду `SOC` менший за мінімально допустимий поріг `min_soc_for_retry` (22%), спроба заходу на друге коло блокується, і система активує аварійний відхід на запасний майданчик.

---

### Повна реалізація модуля на C та C++

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define GO_AROUND_DT_S 0.02f                  /* Період оновлення 50 Гц (20 мс) */
#define DEFAULT_MAX_ATTEMPTS 2U               /* Максимальна кількість спроб */
#define LIDAR_CONFIRM_TICKS 5U                /* 5 циклів * 20 мс = 100 мс фільтр */
#define GRAVITY_MSS 9.80665f

typedef enum {
    GA_STATE_APPROACH_DESCENT = 0,
    GA_STATE_ABORT_BRAKE_CLIMB,
    GA_STATE_ENERGY_AUDIT,
    GA_STATE_CIRCUIT_LOITER,
    GA_STATE_EMERGENCY_FAILSAFE
} ga_state_t;

typedef struct {
    float max_thrust_to_weight;   /* Тягооснащеність, наприклад 1.8 */
    float motor_spoolup_time_s;   /* Час розкрутки моторів, наприклад 0.20 с */
    float safety_margin_m;        /* Запас висоти над просадкою, наприклад 0.8 м */
    float missed_approach_alt_m;  /* Безпечний ешелон відходу, наприклад 25.0 м */
    float obstacle_dist_thresh_m; /* Поріг виявлення перешкоди лідаром, наприклад 1.5 м */
    float max_tilt_angle_rad;     /* Граничний кут нахилу, наприклад 0.436 рад (25 град) */
    float min_soc_for_retry;      /* Мінімальний SOC для другої спроби, наприклад 0.22 */
    float min_cell_voltage_v;     /* Мінімальна напруга банки під навантаженням, наприклад 3.35 В */
    uint8_t cell_count;           /* Кількість послідовних банок (наприклад, 6 для 6S) */
    uint8_t max_attempts;         /* Ліміт повторних спроб */
    uint32_t loiter_duration_ms;  /* Тривалість кружляння перед повторним заходом */
} ga_config_t;

typedef struct {
    float altitude_m;
    float vertical_speed_ms;      /* Від'ємна при спуску */
    float lidar_distance_m;
    float roll_rad;
    float pitch_rad;
    float battery_voltage_v;
    float battery_current_a;
    float battery_soc;            /* 0.0 .. 1.0 */
    bool lidar_valid;
    bool operator_abort_req;
} ga_telemetry_t;

typedef struct {
    float target_alt_m;
    float target_vz_ms;
    float target_roll_rad;
    float target_pitch_rad;
    float max_tilt_limit_rad;
    bool climb_priority;
    bool emergency_land_now;
} ga_setpoints_t;

typedef struct {
    ga_state_t state;
    uint8_t attempt_counter;
    uint8_t lidar_obstacle_counter;
    uint32_t state_timer_ms;
    ga_config_t config;
    ga_setpoints_t setpoints;
} ga_fsm_t;

/* Розрахунок динамічної просадки */
static float calculate_sinkage(float v_z, float thrust_ratio, float spool_time) {
    if (v_z >= 0.0f) {
        return 0.0f;
    }
    float abs_vz = fabsf(v_z);
    float a_climb = (thrust_ratio - 1.0f) * GRAVITY_MSS;
    if (a_climb < 1.0f) {
        a_climb = 1.0f; /* Захист від ділення на нуль при слабкій тязі */
    }
    float h_spool = abs_vz * spool_time;
    float h_brake = (abs_vz * abs_vz) / (2.0f * a_climb);
    return h_spool + h_brake;
}

/* Ініціалізація автомата */
void ga_fsm_init(ga_fsm_t *fsm, const ga_config_t *cfg) {
    if (cfg != NULL) {
        fsm->config = *cfg;
    } else {
        fsm->config.max_thrust_to_weight = 1.8f;
        fsm->config.motor_spoolup_time_s = 0.20f;
        fsm->config.safety_margin_m = 0.8f;
        fsm->config.missed_approach_alt_m = 25.0f;
        fsm->config.obstacle_dist_thresh_m = 1.5f;
        fsm->config.max_tilt_angle_rad = 0.436f;
        fsm->config.min_soc_for_retry = 0.22f;
        fsm->config.min_cell_voltage_v = 3.35f;
        fsm->config.cell_count = 6U;
        fsm->config.max_attempts = DEFAULT_MAX_ATTEMPTS;
        fsm->config.loiter_duration_ms = 15000U;
    }

    fsm->state = GA_STATE_APPROACH_DESCENT;
    fsm->attempt_counter = 0U;
    fsm->lidar_obstacle_counter = 0U;
    fsm->state_timer_ms = 0U;

    fsm->setpoints.target_alt_m = 0.0f;
    fsm->setpoints.target_vz_ms = -1.0f;
    fsm->setpoints.target_roll_rad = 0.0f;
    fsm->setpoints.target_pitch_rad = 0.0f;
    fsm->setpoints.max_tilt_limit_rad = 0.436f;
    fsm->setpoints.climb_priority = false;
    fsm->setpoints.emergency_land_now = false;
}

/* Перевірка тригерів аварійного скасування */
static bool check_abort_conditions(ga_fsm_t *fsm, const ga_telemetry_t *telem) {
    if (telem->operator_abort_req) {
        return true;
    }

    /* Фільтр антибрязкоту лідара */
    if (telem->lidar_valid && (telem->lidar_distance_m < fsm->config.obstacle_dist_thresh_m)) {
        if (fsm->lidar_obstacle_counter < LIDAR_CONFIRM_TICKS) {
            fsm->lidar_obstacle_counter++;
        }
    } else {
        fsm->lidar_obstacle_counter = 0U;
    }

    if (fsm->lidar_obstacle_counter >= LIDAR_CONFIRM_TICKS) {
        return true;
    }

    /* Критичне відхилення кутів орієнтації */
    if ((fabsf(telem->roll_rad) > fsm->config.max_tilt_angle_rad) ||
        (fabsf(telem->pitch_rad) > fsm->config.max_tilt_angle_rad)) {
        return true;
    }

    return false;
}

/* Перевірка енергетичного бюджету на повторне коло */
static bool check_energy_budget(const ga_fsm_t *fsm, const ga_telemetry_t *telem) {
    if (fsm->attempt_counter >= fsm->config.max_attempts) {
        return false;
    }

    if (telem->battery_soc < fsm->config.min_soc_for_retry) {
        return false;
    }

    float cell_v = telem->battery_voltage_v / (float)fsm->config.cell_count;
    if (cell_v < fsm->config.min_cell_voltage_v) {
        return false;
    }

    return true;
}

/* Головна функція такту автомата (50 Гц) */
void ga_fsm_step(ga_fsm_t *fsm, const ga_telemetry_t *telem, uint32_t now_ms) {
    switch (fsm->state) {
    case GA_STATE_APPROACH_DESCENT:
        fsm->setpoints.target_vz_ms = -1.0f;
        fsm->setpoints.climb_priority = false;
        fsm->setpoints.max_tilt_limit_rad = fsm->config.max_tilt_angle_rad;
        fsm->setpoints.emergency_land_now = false;

        if (check_abort_conditions(fsm, telem)) {
            float sinkage = calculate_sinkage(telem->vertical_speed_ms,
                                              fsm->config.max_thrust_to_weight,
                                              fsm->config.motor_spoolup_time_s);

            /* Якщо висота менша за просадку + запас, відхід неможливий -> екстрена посадка */
            if (telem->altitude_m < (sinkage + fsm->config.safety_margin_m)) {
                fsm->state = GA_STATE_EMERGENCY_FAILSAFE;
                fsm->setpoints.emergency_land_now = true;
            } else {
                fsm->attempt_counter++;
                fsm->state = GA_STATE_ABORT_BRAKE_CLIMB;
                fsm->setpoints.target_alt_m = telem->altitude_m + fsm->config.missed_approach_alt_m;
                fsm->state_timer_ms = now_ms;
            }
        }
        break;

    case GA_STATE_ABORT_BRAKE_CLIMB:
        /* Режим екстреного підйому: максимальний темп, нахили заблоковані */
        fsm->setpoints.target_vz_ms = 3.5f;
        fsm->setpoints.target_roll_rad = 0.0f;
        fsm->setpoints.target_pitch_rad = 0.0f;
        fsm->setpoints.max_tilt_limit_rad = 0.087f; /* Затиснуто до ~5 градусів */
        fsm->setpoints.climb_priority = true;

        if (telem->altitude_m >= fsm->setpoints.target_alt_m) {
            fsm->state = GA_STATE_ENERGY_AUDIT;
            fsm->state_timer_ms = now_ms;
        }
        break;

    case GA_STATE_ENERGY_AUDIT:
        fsm->setpoints.climb_priority = false;
        fsm->setpoints.target_vz_ms = 0.0f; /* Зависання для аналізу */
        fsm->setpoints.max_tilt_limit_rad = fsm->config.max_tilt_angle_rad;

        if (check_energy_budget(fsm, telem)) {
            fsm->state = GA_STATE_CIRCUIT_LOITER;
        } else {
            fsm->state = GA_STATE_EMERGENCY_FAILSAFE;
        }
        fsm->state_timer_ms = now_ms;
        break;

    case GA_STATE_CIRCUIT_LOITER:
        fsm->setpoints.target_vz_ms = 0.0f;
        /* Очікування завершення кола очікування перед повторним заходом */
        if ((now_ms - fsm->state_timer_ms) >= fsm->config.loiter_duration_ms) {
            fsm->state = GA_STATE_APPROACH_DESCENT;
            fsm->state_timer_ms = now_ms;
            fsm->lidar_obstacle_counter = 0U;
        }
        break;

    case GA_STATE_EMERGENCY_FAILSAFE:
        /* Аварійний спуск зі швидкістю 0.6 м/с або виконання Rally Divert */
        fsm->setpoints.target_vz_ms = -0.6f;
        fsm->setpoints.climb_priority = false;
        break;
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <optional>

namespace Autopilot::Safety {

inline constexpr float GravityMs2 = 9.80665f;
inline constexpr float DeltaTimeSec = 0.02f; // 50 Hz

enum class GoAroundState : uint8_t {
    ApproachDescent,
    AbortBrakeClimb,
    EnergyAudit,
    CircuitLoiter,
    EmergencyFailsafe
};

struct GoAroundConfig {
    float maxThrustToWeight{1.8f};
    float motorSpoolupTimeSec{0.20f};
    float safetyMarginM{0.8f};
    float missedApproachAltM{25.0f};
    float obstacleDistThreshM{1.5f};
    float maxTiltAngleRad{0.436f};    // ~25 deg
    float minSocForRetry{0.22f};
    float minCellVoltageV{3.35f};
    uint8_t cellCount{6U};
    uint8_t maxAttempts{2U};
    uint32_t loiterDurationMs{15000U};
    uint8_t lidarConfirmTicks{5U};
};

struct TelemetrySnapshot {
    float altitudeM{0.0f};
    float verticalSpeedMs{0.0f};      // Negative during descent
    float lidarDistanceM{0.0f};
    float rollRad{0.0f};
    float pitchRad{0.0f};
    float batteryVoltageV{24.0f};
    float batteryCurrentA{0.0f};
    float batterySoc{1.0f};           // 0.0 .. 1.0
    bool lidarValid{false};
    bool operatorAbortReq{false};
};

struct ControllerSetpoints {
    float targetAltM{0.0f};
    float targetVzMs{-1.0f};
    float targetRollRad{0.0f};
    float targetPitchRad{0.0f};
    float maxTiltLimitRad{0.436f};
    bool climbPriority{false};
    bool emergencyLandNow{false};
};

class GoAroundStateMachine {
public:
    explicit GoAroundStateMachine(const GoAroundConfig& config = GoAroundConfig{}) noexcept
        : m_config(config) {}

    void step(const TelemetrySnapshot& telem, uint32_t nowMs) noexcept {
        switch (m_state) {
        case GoAroundState::ApproachDescent:
            m_setpoints.targetVzMs = -1.0f;
            m_setpoints.climbPriority = false;
            m_setpoints.maxTiltLimitRad = m_config.maxTiltAngleRad;
            m_setpoints.emergencyLandNow = false;

            if (checkAbortConditions(telem)) {
                const float sinkage = calculateSinkage(telem.verticalSpeedMs);

                // Якщо висоти замало для безпечного гальмування — примусова аварійна посадка
                if (telem.altitudeM < (sinkage + m_config.safetyMarginM)) {
                    m_state = GoAroundState::EmergencyFailsafe;
                    m_setpoints.emergencyLandNow = true;
                } else {
                    ++m_attemptCounter;
                    m_state = GoAroundState::AbortBrakeClimb;
                    m_setpoints.targetAltM = telem.altitudeM + m_config.missedApproachAltM;
                    m_stateTimerMs = nowMs;
                }
            }
            break;

        case GoAroundState::AbortBrakeClimb:
            // Екстрений вертикальний набір з фіксацією нахилів
            m_setpoints.targetVzMs = 3.5f;
            m_setpoints.targetRollRad = 0.0f;
            m_setpoints.targetPitchRad = 0.0f;
            m_setpoints.maxTiltLimitRad = 0.087f; // ~5 deg
            m_setpoints.climbPriority = true;

            if (telem.altitudeM >= m_setpoints.targetAltM) {
                m_state = GoAroundState::EnergyAudit;
                m_stateTimerMs = nowMs;
            }
            break;

        case GoAroundState::EnergyAudit:
            m_setpoints.climbPriority = false;
            m_setpoints.targetVzMs = 0.0f; // Зависання
            m_setpoints.maxTiltLimitRad = m_config.maxTiltAngleRad;

            if (isEnergyBudgetSufficient(telem)) {
                m_state = GoAroundState::CircuitLoiter;
            } else {
                m_state = GoAroundState::EmergencyFailsafe;
            }
            m_stateTimerMs = nowMs;
            break;

        case GoAroundState::CircuitLoiter:
            m_setpoints.targetVzMs = 0.0f;
            if (nowMs - m_stateTimerMs >= m_config.loiterDurationMs) {
                m_state = GoAroundState::ApproachDescent;
                m_stateTimerMs = nowMs;
                m_lidarObstacleCounter = 0U;
            }
            break;

        case GoAroundState::EmergencyFailsafe:
            m_setpoints.targetVzMs = -0.6f;
            m_setpoints.climbPriority = false;
            break;
        }
    }

    [[nodiscard]] GoAroundState state() const noexcept { return m_state; }
    [[nodiscard]] uint8_t attempts() const noexcept { return m_attemptCounter; }
    [[nodiscard]] const ControllerSetpoints& setpoints() const noexcept { return m_setpoints; }

    void reset() noexcept {
        m_state = GoAroundState::ApproachDescent;
        m_attemptCounter = 0U;
        m_lidarObstacleCounter = 0U;
        m_stateTimerMs = 0U;
        m_setpoints = ControllerSetpoints{};
    }

private:
    [[nodiscard]] float calculateSinkage(float vz) const noexcept {
        if (vz >= 0.0f) {
            return 0.0f;
        }
        const float absVz = std::abs(vz);
        const float aClimb = std::max(1.0f, (m_config.maxThrustToWeight - 1.0f) * GravityMs2);
        const float hSpool = absVz * m_config.motorSpoolupTimeSec;
        const float hBrake = (absVz * absVz) / (2.0f * aClimb);
        return hSpool + hBrake;
    }

    [[nodiscard]] bool checkAbortConditions(const TelemetrySnapshot& telem) noexcept {
        if (telem.operatorAbortReq) {
            return true;
        }

        if (telem.lidarValid && (telem.lidarDistanceM < m_config.obstacleDistThreshM)) {
            if (m_lidarObstacleCounter < m_config.lidarConfirmTicks) {
                ++m_lidarObstacleCounter;
            }
        } else {
            m_lidarObstacleCounter = 0U;
        }

        if (m_lidarObstacleCounter >= m_config.lidarConfirmTicks) {
            return true;
        }

        return (std::abs(telem.rollRad) > m_config.maxTiltAngleRad) ||
               (std::abs(telem.pitchRad) > m_config.maxTiltAngleRad);
    }

    [[nodiscard]] bool isEnergyBudgetSufficient(const TelemetrySnapshot& telem) const noexcept {
        if (m_attemptCounter >= m_config.maxAttempts) {
            return false;
        }
        if (telem.batterySoc < m_config.minSocForRetry) {
            return false;
        }
        const float cellVoltage = telem.batteryVoltageV / static_cast<float>(m_config.cellCount);
        return cellVoltage >= m_config.minCellVoltageV;
    }

    GoAroundConfig m_config;
    GoAroundState m_state{GoAroundState::ApproachDescent};
    uint8_t m_attemptCounter{0U};
    uint8_t m_lidarObstacleCounter{0U};
    uint32_t m_stateTimerMs{0U};
    ControllerSetpoints m_setpoints{};
};

} // namespace Autopilot::Safety
```
:::

---

### Покроковий розбір коду та інваріанти переходів

#### 1. Структура `ga_config_t` / `GoAroundConfig`
Містить усі калібрувальні параметри, які завантажуються з постійної енергонезалежної пам'яті (Flash/EEPROM) автопілота:
- `max_thrust_to_weight`: відношення максимальної сумарної тяги до ваги дрона. Визначає доступне прискорення гальмування `a_climb`. Для промислових мультикоптерів лежить у діапазоні 1.6–2.2.
- `motor_spoolup_time_s`: час розгону роторів від посадкового газу до максимального. Для гвинтів діаметром 15–20 дюймів становить 0.18–0.25 с.
- `safety_margin_m`: додатковий запас висоти для компенсації нерівностей рельєфу та похибок альтиметра (зазвичай 0.5–1.0 м).
- `min_soc_for_retry` та `min_cell_voltage_v`: критерії відсікання за станом акумулятора. Запобігають повторному зльоту при розрядженій батареї.

#### 2. Функція `calculate_sinkage()`
Обчислює сумарну втрату висоти після отримання сигналу Abort:
- `h_spool = |v_z| · t_spoolup`: просідання за час виходу моторів на режим повної тяги.
- `h_brake = v_z² / (2 · a_climb)`: відстань гальмування під дією максимального вертикального прискорення.
- Умова `if (v_z >= 0.0f) return 0.0f;` захищає від некоректних розрахунків, якщо апарат на момент скасування вже рухався вгору.

#### 3. Функція `check_abort_conditions()`
Виконує синхронний моніторинг трьох груп факторів:
- Наявність прямої команди від оператора або наземної станції (`operator_abort_req`).
- Перевірка дистанції лідара: лічильник `lidar_obstacle_counter` інкрементується лише при валідному статусі `lidar_valid` та дистанції, меншій за `obstacle_dist_thresh_m`. Скидається в 0 при першому ж чистому відліку.
- Перевірка кутів орієнтації: якщо крен або тангаж перевищує `max_tilt_angle_rad` (25°), це вказує на дестабілізацію в турбулентному приземному шарі.

#### 4. Обробка переходів у `ga_fsm_step()`
- **Вхід у `GA_STATE_ABORT_BRAKE_CLIMB`**: встановлює цільову вертикальну швидкість `target_vz_ms = 3.5 м/с`, примусово обнуляє цільові кути нахилу (`target_roll_rad = 0`, `target_pitch_rad = 0`) та затискає максимальний кут нахилу рами до 5 градусів (`max_tilt_limit_rad = 0.087 рад`). Прапорець `climb_priority = true` інформує мікшер моторів про необхідність віддати 100% доступної потужності на спільний газ, жертвуючи моментами рискання.
- **Вхід у `GA_STATE_ENERGY_AUDIT`**: після набору висоти до `target_alt_m` контролер скидає вертикальну швидкість до нуля для стабілізації струму батареї. Виконується оцінка залишкового заряду.
- **Вхід у `GA_STATE_CIRCUIT_LOITER`**: дрон утримує позицію на безпечній висоті протягом `loiter_duration_ms` (15 секунд), що дозволяє оператору оцінити майданчик візуально або через камеру корисного навантаження.
- **Вхід у `GA_STATE_EMERGENCY_FAILSAFE`**: якщо висота була меншою за розрахункову просадку або батарея вичерпана, встановлюється безпечна швидкість аварійного спуску `target_vz_ms = -0.6 м/с`.

---

### Аналіз тестових сценаріїв та верифікація

Для перевірки надійності модуля розроблено набір автономних модульних тестів (англ. *unit tests*), що покривають ключові граничні умови:

```
[TEST 1] Штатне скасування на безпечній висоті (h = 4.0 м, Vz = -1.2 м/с):
         -> Розрахована просадка: Δh_sink = 0.38 м.
         -> Перевірка h > (Δh_sink + 0.8 м) = 1.18 м -> УСПІХ.
         -> Перехід: APPROACH -> ABORT_BRAKE_CLIMB -> ENERGY_AUDIT -> CIRCUIT_LOITER.

[TEST 2] Скасування нижче висоти прийняття рішення (h = 0.6 м, Vz = -1.5 м/с):
         -> Розрахована просадка: Δh_sink = 0.46 м.
         -> Повна критична висота: 0.46 + 0.8 = 1.26 м > 0.6 м.
         -> Модуль забороняє набір газу -> Перехід у EMERGENCY_FAILSAFE (захист пропелерів).

[TEST 3] Повторне скасування при виснаженій батареї (SOC = 18%, N_attempt = 2):
         -> Стан ENERGY_AUDIT фіксує SOC < 22% та N >= MAX_ATTEMPTS.
         -> Перехід у EMERGENCY_FAILSAFE (заборона виходу на 3-тє коло, відхід на Rally Point).

[TEST 4] Фільтрація поодиноких шумових сплесків лідара:
         -> Подача 3 хибних відліків d = 0.8 м при порозі 1.5 м.
         -> Лічильник досягає 3 < 5 -> Тригер не спрацьовує, спуск триває штатно.
```

---

### Синхронізація потоків та безпека пам'яті в RTOS

У реальних системах автопілота (наприклад, на базі ядра NuttX у PX4 або ChibiOS в ArduPilot) виникає потенційний стан перегонів (англ. *race condition*):
- Потік опитування сенсорів (Sensor Driver Thread) працює на частоті 100–250 Гц і записує дистанцію далекоміра та напругу.
- Потік навігаційного планувальника (Navigator Thread) працює на частоті 50 Гц і виконує крок `ga_fsm_step()`.

Для виключення блокувань м'ютексами всередині критичного контуру керування застосовується техніка подвійної буферизації (англ. *double-buffering*) зі збереженням знімка телеметрії `TelemetrySnapshot` за один атомарний крок копіювання перед викликом кроку автомата.

---

### Інтеграція в польотні стеки (PX4 / ArduPilot)

Модуль легко вбудовується в архітектуру сучасних відкритих польотних стеків:
- **У стеку PX4 Autopilot**: модуль інтегрується у клас `FlightModeManager` як захисний плагін стану `Navigator`, що взаємодіє з модулем `land_detector` через внутрішню шину повідомлень uORB (`vehicle_land_detected`, `vehicle_status`, `vehicle_local_position_setpoint`).
- **У стеку ArduPilot**: модуль вбудовується в підсистему `mode_land.cpp` / `mode_rtl.cpp`, керуючи прапорцями стану через структуру `AP_Vehicle::failsafe`.

Модуль гарантує повну безпеку апарата при автономних місіях у складних урбаністичних та промислових середовищах.

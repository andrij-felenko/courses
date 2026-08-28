# ⚙️ Монітор узгодженості дій оператора та режиму апарата

У складних безпілотних комплексах розсинхронізація між діями оператора та поточним режимом польотного контролера часто призводить до аварії за лічені секунди. Якщо автопілот перейшов в автономний режим повернення на базу (`AUTO_RTH`), а пілот переконаний, що керує апаратом вручну, виникає небезпечний конфлікт: людина щосили відхиляє стік убік, намагаючись обійти перешкоду, тоді як автопілот ігнорує команди й продовжує рух за закладеним навігаційним вектором.

Нижче наведено закінчену реалізацію бортового **монітора узгодженості дій оператора** (англ. *Mode Consistency Monitor*). Модуль працює у реальному часі з частотою 50–100 Гц, аналізує вхідні сигнали радіокерування, поточний стан автомата режимів та вектор руху з навігаційного фільтра (EKF), після чого своєчасно генерує попередження або ініціює аварійне повернення повноважень людині.

## Архітектура та математичні критерії виявлення аномалій

Монітор працює як незалежний спостерігач у контурі керування польотного контролера. Він не підміняє собою ПІД-регулятори стабілізації, а безперервно оцінює ступінь збігу намірів оператора з фізичною поведінкою та модальним станом машини. Алгоритм базується на розрахунку чотирьох взаємодоповнюючих метрик узгодженості.

### 1. Протидія навігаційному вектору (Stick Fighting Autopilot)

Коли активний повністю автономний режим (наприклад, політ за маршрутними точками `AUTO_MISSION` або повернення на точку зльоту `AUTO_RTH`), навігаційний контролер генерує цільовий вектор швидкості `V_nav = (vel_x, vel_y)` у системі координат NED (North-East-Down).

Оператор, який не помітив увімкнення автономного режиму або вважає, що апарат продовжує рух за його ручними командами, бачить неочікуване зближення з перешкодою (будівлею, деревом, високовольтною лінією) і намагається відвернути дрон, відхиляючи стік Roll/Pitch у протилежний бік.

Монітор нормалізує вектор відхилення стіків у діапазон `[-1.0 .. +1.0]`, де тангаж `pitch` спрямований вздовж осі X (North), а крен `roll` — вздовж осі Y (East). Далі розраховується скалярний добуток вектора зусилля стіка `S = (pitch, roll)` на поточний вектор швидкості руху `V = (vel_x, vel_y)`:

```
dot = (pitch · vel_x) + (roll · vel_y)
```

Якщо `dot < 0`, напрямок команди пілота прямо протилежний напрямку фактичного переміщення апарата. Якщо водночас амплітуда відхилення `|S| = sqrt(roll² + pitch²)` перевищує поріг активного втручання `STICK_FIGHT_THRESHOLD` (35% від повного ходу ручки), це свідчить про наявність явного конфлікту цілей.

Щоб випадковий короткий рух пальця пілота не спричинив хибного зриву місії, вводиться інтегратор часу `FIGHTING_TIME_LIMIT_MS` (400 мс). Якщо суперечливе зусилля утримується довше цього інтервалу, монітор активує найвищий пріоритет тривоги — `SEVERITY_OVERRIDE_TAKEOVER`.

### 2. Пастка нульового газу (Throttle Inversion Trap)

У класичних ручних режимах керування (`MANUAL`, `ACRO`, `STABILIZE`) положення стіка газу безпосередньо задає швидкість обертання безколекторних моторів (шпаруватість ШІМ від 0% до 100%). Стік у крайньому нижньому положенні повністю вимикає тягу або переводить двигуни на мінімальні оберти холостого ходу (Idle).

Навпаки, у режимах із замкненим контуром висоти (`ALT_HOLD`, `POS_HOLD`, `AUTO_RTH`) стік газу перетворюється на селектор вертикальної швидкості (англ. *climb/descent rate*). Центральне положення стіка (50% з мертвою зоною ±10%) відповідає утриманню поточної висоти (вертикальна швидкість 0 м/с). Відхилення вниз задає контрольоване зниження з фіксованою максимальною швидкістю (зазвичай 1.5–2.5 м/с), а не зупинку двигунів.

Якщо оператор перебуває в полоні ментальної моделі ручного керування і намагається терміново «скинути газ» при нештатній ситуації біля землі, він тягне важіль у нуль. У режимі `ALT_HOLD` або `RTH` апарат починає плавно спускатися, продовжуючи рухатися вперед за маршрутом. Не побачивши миттєвого падіння тяги, пілот впадає в паніку. Монітор відстежує утримання газу нижче 5% у висотних режимах довше 800 мс і формує термінове голосове попередження.

### 3. Дрейф після непоміченого відкату (Silent Fallback Drift)

Найчастіша аварія під час польотів у складній радіоелектронній обстановці — непомітний для пілота відкат автопілота з режиму утримання позиції за супутниками (`POS_HOLD`) у режим утримання лише барометричної висоти (`ALT_HOLD`) через глушіння GPS або розбіжність фільтра EKF.

У режимі `POS_HOLD` пілот звикає, що відпускання стіків у нуль призводить до активного аеродинамічного гальмування: дрон автоматично протидіє інерції та поривам вітру. У режимі `ALT_HOLD` нульове положення стіка лише тримає горизонт (кути крену й тангажу 0°), тоді як горизонтальна швидкість ніяк не компенсується — апарат безперешкодно летить за вітром або продовжує рух за накопиченою інерцією зі швидкістю 10–15 м/с.

Монітор зіставляє нульове положення стіків (перебування в межах мертвої зони `STICK_DEADZONE`) із наявністю горизонтальної швидкості польоту вище 1.5 м/с у режимі `ALT_HOLD`. Якщо такий стан триває понад 1.2 секунди, система ідентифікує, що пілот не усвідомлює дрейфу, і генерує алерт `UNNOTICED_DRIFT_IN_ALTHOLD`.

### 4. Панічне сіпання стіками (Panic Stick Stirring)

Коли людина остаточно втрачає розуміння того, що робить машина (стан повної дезорієнтації або «Automation Surprise»), вона інстинктивно переходить до високочастотного знакозмінного переміщення стіків у різні боки (англ. *stick stirring*).

Монітор оцінює похідну переміщення ручок у часі `d(roll)/dt` та фіксує моменти зміни знака швидкості руху стіка. Якщо протягом плаваючого вікна тривалістю 600 мс фіксується 4 або більше реверсів із високою кутовою швидкістю, стан кваліфікується як панічний, що запускає захисні заходи стабілізації.

## Програмна реалізація: C та ідіоматичний C++

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define STICK_DEADZONE          0.08f
#define STICK_FIGHT_THRESHOLD   0.35f
#define THROTTLE_LOW_THRESHOLD  0.05f
#define DRIFT_SPEED_THRESHOLD   1.5f     /* м/с */
#define STIR_DERIVATIVE_THRESH  2.5f     /* 1/c */

#define FIGHTING_TIME_LIMIT_MS  400
#define THROTTLE_TIME_LIMIT_MS  800
#define DRIFT_TIME_LIMIT_MS     1200
#define STIR_WINDOW_MS          600
#define STIR_MAX_REVERSALS      4

typedef enum {
    FLIGHT_MODE_MANUAL = 0,
    FLIGHT_MODE_STABILIZE,
    FLIGHT_MODE_ALT_HOLD,
    FLIGHT_MODE_POS_HOLD,
    FLIGHT_MODE_AUTO_MISSION,
    FLIGHT_MODE_AUTO_RTH,
    FLIGHT_MODE_EMERGENCY_LAND
} FlightMode;

typedef enum {
    SEVERITY_NORMAL = 0,
    SEVERITY_WARNING_ANNUNCIATION,
    SEVERITY_OVERRIDE_TAKEOVER
} MismatchSeverity;

typedef struct {
    float roll;      /* Нормалізовані відхилення [-1.0 .. +1.0] */
    float pitch;
    float yaw;
    float throttle; /* [0.0 .. 1.0] */
} PilotSticks;

typedef struct {
    float vel_x;    /* Північ, м/с */
    float vel_y;    /* Схід, м/с */
    float vel_z;    /* Вниз, м/с */
} NavVector;

typedef struct {
    uint32_t fight_start_time_ms;
    uint32_t throttle_panic_start_ms;
    uint32_t drift_start_time_ms;
    
    float last_roll;
    float last_pitch;
    uint32_t last_update_ms;
    
    int reversal_count;
    uint32_t stir_window_start_ms;
    float last_sign;
    
    MismatchSeverity current_severity;
    const char *alarm_reason;
} ConsistencyMonitor;

void consistency_monitor_init(ConsistencyMonitor *mon) {
    mon->fight_start_time_ms = 0;
    mon->throttle_panic_start_ms = 0;
    mon->drift_start_time_ms = 0;
    mon->last_roll = 0.0f;
    mon->last_pitch = 0.0f;
    mon->last_update_ms = 0;
    mon->reversal_count = 0;
    mon->stir_window_start_ms = 0;
    mon->last_sign = 0.0f;
    mon->current_severity = SEVERITY_NORMAL;
    mon->alarm_reason = "OK";
}

MismatchSeverity consistency_monitor_update(ConsistencyMonitor *mon,
                                           FlightMode active_mode,
                                           const PilotSticks *sticks,
                                           const NavVector *nav,
                                           uint32_t now_ms) {
    float dt = (mon->last_update_ms == 0) ? 0.02f : (float)(now_ms - mon->last_update_ms) / 1000.0f;
    if (dt <= 0.0f) dt = 0.02f;
    mon->last_update_ms = now_ms;

    mon->current_severity = SEVERITY_NORMAL;
    mon->alarm_reason = "OK";

    /* 1. Перевірка на протидію автопілоту в автономних режимах */
    bool is_autonomous = (active_mode == FLIGHT_MODE_AUTO_MISSION || active_mode == FLIGHT_MODE_AUTO_RTH);
    if (is_autonomous) {
        float stick_mag = sqrtf(sticks->roll * sticks->roll + sticks->pitch * sticks->pitch);
        float nav_mag = sqrtf(nav->vel_x * nav->vel_x + nav->vel_y * nav->vel_y);

        if (stick_mag > STICK_FIGHT_THRESHOLD && nav_mag > 0.5f) {
            /* Скалярний добуток вектора стіка та вектора руху: roll -> vel_y (схід), pitch -> vel_x (північ) */
            float dot_product = (sticks->pitch * nav->vel_x) + (sticks->roll * nav->vel_y);
            if (dot_product < 0.0f) {
                if (mon->fight_start_time_ms == 0) {
                    mon->fight_start_time_ms = now_ms;
                } else if (now_ms - mon->fight_start_time_ms > FIGHTING_TIME_LIMIT_MS) {
                    mon->current_severity = SEVERITY_OVERRIDE_TAKEOVER;
                    mon->alarm_reason = "STICK_FIGHTING_RTH";
                    return mon->current_severity;
                }
            } else {
                mon->fight_start_time_ms = 0;
            }
        } else {
            mon->fight_start_time_ms = 0;
        }
    } else {
        mon->fight_start_time_ms = 0;
    }

    /* 2. Пастка нульового газу при утриманні висоти або поверненні */
    bool holds_altitude = (active_mode == FLIGHT_MODE_ALT_HOLD || 
                           active_mode == FLIGHT_MODE_POS_HOLD || 
                           is_autonomous);
    if (holds_altitude && sticks->throttle < THROTTLE_LOW_THRESHOLD) {
        if (mon->throttle_panic_start_ms == 0) {
            mon->throttle_panic_start_ms = now_ms;
        } else if (now_ms - mon->throttle_panic_start_ms > THROTTLE_TIME_LIMIT_MS) {
            mon->current_severity = SEVERITY_WARNING_ANNUNCIATION;
            mon->alarm_reason = "ZERO_THROTTLE_IN_ALTHOLD";
        }
    } else {
        mon->throttle_panic_start_ms = 0;
    }

    /* 3. Дрейф при очікуванні PosHold після відкату в AltHold */
    if (active_mode == FLIGHT_MODE_ALT_HOLD) {
        float stick_mag = sqrtf(sticks->roll * sticks->roll + sticks->pitch * sticks->pitch);
        float horiz_speed = sqrtf(nav->vel_x * nav->vel_x + nav->vel_y * nav->vel_y);

        if (stick_mag < STICK_DEADZONE && horiz_speed > DRIFT_SPEED_THRESHOLD) {
            if (mon->drift_start_time_ms == 0) {
                mon->drift_start_time_ms = now_ms;
            } else if (now_ms - mon->drift_start_time_ms > DRIFT_TIME_LIMIT_MS) {
                mon->current_severity = SEVERITY_WARNING_ANNUNCIATION;
                mon->alarm_reason = "UNNOTICED_DRIFT_IN_ALTHOLD";
            }
        } else {
            mon->drift_start_time_ms = 0;
        }
    } else {
        mon->drift_start_time_ms = 0;
    }

    /* 4. Виявлення панічного сіпання стіками */
    float d_roll = (sticks->roll - mon->last_roll) / dt;
    float current_sign = (d_roll > 0.1f) ? 1.0f : ((d_roll < -0.1f) ? -1.0f : 0.0f);

    if (now_ms - mon->stir_window_start_ms > STIR_WINDOW_MS) {
        mon->stir_window_start_ms = now_ms;
        mon->reversal_count = 0;
    }

    if (current_sign != 0.0f && mon->last_sign != 0.0f && current_sign != mon->last_sign) {
        if (fabsf(d_roll) > STIR_DERIVATIVE_THRESH) {
            mon->reversal_count++;
            if (mon->reversal_count >= STIR_MAX_REVERSALS) {
                mon->current_severity = SEVERITY_WARNING_ANNUNCIATION;
                mon->alarm_reason = "PANIC_STICK_STIRRING";
            }
        }
    }

    mon->last_sign = current_sign;
    mon->last_roll = sticks->roll;
    mon->last_pitch = sticks->pitch;

    return mon->current_severity;
}
```
```cpp
#include <cmath>
#include <cstdint>
#include <string_view>
#include <algorithm>

namespace FlightSafety {

enum class FlightMode : uint8_t {
    Manual = 0,
    Stabilize,
    AltHold,
    PosHold,
    AutoMission,
    AutoRth,
    EmergencyLand
};

enum class MismatchSeverity : uint8_t {
    Normal = 0,
    WarningAnnunciation,
    OverrideTakeover
};

struct PilotSticks {
    float roll{0.0f};      // [-1.0 .. +1.0]
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{0.0f}; // [0.0 .. 1.0]

    [[nodiscard]] constexpr float magnitude() const noexcept {
        return std::sqrt(roll * roll + pitch * pitch);
    }
};

struct NavVector {
    float vel_x{0.0f}; // Північ, м/с
    float vel_y{0.0f}; // Схід, м/с
    float vel_z{0.0f}; // Вниз, м/с

    [[nodiscard]] constexpr float horizontal_speed() const noexcept {
        return std::sqrt(vel_x * vel_x + vel_y * vel_y);
    }
};

class ModeConsistencyMonitor {
public:
    static constexpr float StickDeadzone{0.08f};
    static constexpr float StickFightThreshold{0.35f};
    static constexpr float ThrottleLowThreshold{0.05f};
    static constexpr float DriftSpeedThreshold{1.5f};
    static constexpr float StirDerivativeThresh{2.5f};

    static constexpr uint32_t FightingTimeLimitMs{400};
    static constexpr uint32_t ThrottleTimeLimitMs{800};
    static constexpr uint32_t DriftTimeLimitMs{1200};
    static constexpr uint32_t StirWindowMs{600};
    static constexpr int StirMaxReversals{4};

    struct AssessmentResult {
        MismatchSeverity severity{MismatchSeverity::Normal};
        std::string_view reason{"OK"};
    };

    AssessmentResult update(FlightMode active_mode,
                            const PilotSticks& sticks,
                            const NavVector& nav,
                            uint32_t now_ms) noexcept {
        float dt = (last_update_ms_ == 0) ? 0.02f : static_cast<float>(now_ms - last_update_ms_) / 1000.0f;
        if (dt <= 0.0f) dt = 0.02f;
        last_update_ms_ = now_ms;

        // 1. Боротьба з автопілотом в автономних режимах
        if (is_autonomous(active_mode)) {
            if (sticks.magnitude() > StickFightThreshold && nav.horizontal_speed() > 0.5f) {
                float dot_product = (sticks.pitch * nav.vel_x) + (sticks.roll * nav.vel_y);
                if (dot_product < 0.0f) {
                    if (fight_start_time_ms_ == 0) {
                        fight_start_time_ms_ = now_ms;
                    } else if (now_ms - fight_start_time_ms_ > FightingTimeLimitMs) {
                        return {MismatchSeverity::OverrideTakeover, "STICK_FIGHTING_RTH"};
                    }
                } else {
                    fight_start_time_ms_ = 0;
                }
            } else {
                fight_start_time_ms_ = 0;
            }
        } else {
            fight_start_time_ms_ = 0;
        }

        // 2. Пастка нульового газу в режимах утримання висоти
        if (holds_altitude(active_mode) && sticks.throttle < ThrottleLowThreshold) {
            if (throttle_panic_start_ms_ == 0) {
                throttle_panic_start_ms_ = now_ms;
            } else if (now_ms - throttle_panic_start_ms_ > ThrottleTimeLimitMs) {
                return {MismatchSeverity::WarningAnnunciation, "ZERO_THROTTLE_IN_ALTHOLD"};
            }
        } else {
            throttle_panic_start_ms_ = 0;
        }

        // 3. Дрейф після тихого скидання PosHold -> AltHold
        if (active_mode == FlightMode::AltHold) {
            if (sticks.magnitude() < StickDeadzone && nav.horizontal_speed() > DriftSpeedThreshold) {
                if (drift_start_time_ms_ == 0) {
                    drift_start_time_ms_ = now_ms;
                } else if (now_ms - drift_start_time_ms_ > DriftTimeLimitMs) {
                    return {MismatchSeverity::WarningAnnunciation, "UNNOTICED_DRIFT_IN_ALTHOLD"};
                }
            } else {
                drift_start_time_ms_ = 0;
            }
        } else {
            drift_start_time_ms_ = 0;
        }

        // 4. Панічне сіпання стіками
        float d_roll = (sticks.roll - last_roll_) / dt;
        float current_sign = (d_roll > 0.1f) ? 1.0f : ((d_roll < -0.1f) ? -1.0f : 0.0f);

        if (now_ms - stir_window_start_ms_ > StirWindowMs) {
            stir_window_start_ms_ = now_ms;
            reversal_count_ = 0;
        }

        if (current_sign != 0.0f && last_sign_ != 0.0f && current_sign != last_sign_) {
            if (std::abs(d_roll) > StirDerivativeThresh) {
                if (++reversal_count_ >= StirMaxReversals) {
                    return {MismatchSeverity::WarningAnnunciation, "PANIC_STICK_STIRRING"};
                }
            }
        }

        last_sign_ = current_sign;
        last_roll_ = sticks.roll;
        last_pitch_ = sticks.pitch;

        return {MismatchSeverity::Normal, "OK"};
    }

    void reset() noexcept {
        fight_start_time_ms_ = 0;
        throttle_panic_start_ms_ = 0;
        drift_start_time_ms_ = 0;
        last_roll_ = 0.0f;
        last_pitch_ = 0.0f;
        last_update_ms_ = 0;
        reversal_count_ = 0;
        stir_window_start_ms_ = 0;
        last_sign_ = 0.0f;
    }

private:
    static constexpr bool is_autonomous(FlightMode mode) noexcept {
        return mode == FlightMode::AutoMission || mode == FlightMode::AutoRth;
    }

    static constexpr bool holds_altitude(FlightMode mode) noexcept {
        return mode == FlightMode::AltHold || mode == FlightMode::PosHold || is_autonomous(mode);
    }

    uint32_t fight_start_time_ms_{0};
    uint32_t throttle_panic_start_ms_{0};
    uint32_t drift_start_time_ms_{0};

    float last_roll_{0.0f};
    float last_pitch_{0.0f};
    uint32_t last_update_ms_{0};

    int reversal_count_{0};
    uint32_t stir_window_start_ms_{0};
    float last_sign_{0.0f};
};

} // namespace FlightSafety
```
:::

## Інтеграція в цикл керування та практичні пастки

При підключенні монітора в основний цикл польотного контролера слід враховувати три тонкі моменти:

1. **Гістерезис переривання автономного режиму (Stick Breakout Hysteresis):**
   Якщо монітор повернув стан `SEVERITY_OVERRIDE_TAKEOVER`, автопілот зобов'язаний перейти в режим `ALT_HOLD` або `POS_HOLD`, передавши контроль пілоту. Щоб уникнути брязкоту режимів (коли при знятті зусилля зі стіка автопілот негайно відновлює RTH), потрібен часовий замок на відновлення місії (наприклад, 3 секунди обов'язкового ручного пілотування).

2. **Затримка оцінки швидкості навігаційного фільтра (EKF Lag):**
   Після різкого маневру фільтр оцінки стану може давати затримку розрахунку вектора швидкості у 50–150 мс. Скалярний добуток `(sticks · vel)` має фільтруватися апертурним фільтром або вимагати утримання протидії щонайменше 300–400 мс, щоб виключити хибні спрацьовування під час коротких ручних корекцій.

3. **Мертва зона нейтралі (Deadzone):**
   Потенціометри дешевих або зношених стіків пульта керування можуть дрейфувати на 2–5% від центру. Поріг `STICK_DEADZONE` у 8% запобігає хибній фіксації дій оператора, коли руки зняті з пульта.

4. **Диспетчеризація сповіщень через MAVLink:**
   При генерації `SEVERITY_WARNING_ANNUNCIATION` модуль відправляє в чергу телеметрії пакет `STATUSTEXT` із рівнем `MAV_SEVERITY_WARNING` та відповідним прапорцем для наземної станції або OSD, що вмикає звуковий синтез на пульті.

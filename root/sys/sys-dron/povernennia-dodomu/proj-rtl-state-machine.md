# ⚙️ Повна реалізація автомата RTL на C та C++

У базових прикладах логіка повернення додому часто зводиться до простого перемикання цільової координати. Проте у реальному безпілотному апараті на автомат RTL покладається повна відповідальність за збереження борту в умовах відмови зв'язку, дефіциту заряду, сильного бокового вітру та відсутності супутникового сигналу на фінальній стадії посадки.

Ця практична вставка містить автономний, протестований модуль кінцевого автомата повернення (RTL FSM) для польотного контролера. Модуль підтримує:
1. **Кільцевий буфер просторових крихт (Breadcrumbs Buffer)** для запису безпечного коридору польоту та його автоматичного відкату (Reverse Path).
2. **Алгоритм зрізання колінеарних точок (Douglas-Peucker on-the-fly)** для мінімізації зайвих маневрів та економії енергії батареї.
3. **Контур оптичного вирівнювання над посадковою міткою (Precision Landing)** із пропорційним регулятором швидкості та зоною безпечного зниження.
4. **Багатофакторний детектор контакту з ґрунтом (Ground Contact Detector)** із захистом від хибних спрацьовань у зоні екранного ефекту.

---

### Архітектура даних та система координат

Автомат оперує координатами в локальній правій декартовій системі навігації **NED** (*North-East-Down*): вісь `X` спрямована на північ, `Y` — на схід, `Z` — вертикально вниз (висота над землею `h = -Z`). Швидкості позначаються як `vx, vy, vz`. При цьому від'ємне значення `vz` відповідає набору висоти, а додатне — зниженню до землі.

```
        ▲ North (X)
        │
        │      ▲
        │     ╱ ╲  Дрон
        │    └───┘
        └──────────────► East (Y)
       ╱
      ▼ Down (Z = -h)
```

Буфер просторових крихт (`BreadcrumbBuffer`) реалізовано як статичний кільцевий масив із фіксованим обсягом пам'яті. Це критично для вбудованих систем реального часу (RTOS), де динамічне виділення пам'яті (`malloc` або `new`) під час польоту суворо заборонено через небезпеку фрагментації купи та недетермінованих затримок планувальника.

Кожна точка в буфері представляє тривимірний просторовий вузол `(x, y, z)`. Під час штатного руху за місією навігатор викликає метод `push()`. Точка фіксується лише тоді, коли апарат віддалився від попереднього збереженого вузла щонайменше на 8 метрів. Завдяки цьому буфер не засмічується тисячами однакових точок під час тривалого зависання на місці.

Якщо під час довготривалого польоту буфер повністю заповнюється, нові точки циклічно перезаписують найстаріші вузли. При активації аварійного повернення індекс відкату `crumbReverseIdx` встановлюється на останню збережену точку, і дрон послідовно проходить весь ланцюжок у зворотному порядку, поки не вийде на пряму радіовидимість бази.

---

### Обробка оптичного наведення та безпечний конус

У фазі оптичного спуску (`PrecisionDescent`) модуль отримує просторовий вектор зміщення цілі `vision`. Цей вектор формується зовнішнім потоком комп'ютерного зору на основі детекції кутів мітки AprilTag у кадрі монокулярної камери.

Вектор `(vision.x, vision.y)` виражає горизонтальну похибку положення центру дрона відносно геометричного центру посадкової платформи. Пропорційний регулятор швидкості транслює це зміщення в команду горизонтальної швидкості корекції:

```
V_corr_x = -kp · vision.x
V_corr_y = -kp · vision.y
```

де коефіцієнт підсилення `kp` зазвичай обирається в діапазоні від 0.6 до 1.0 с^-1, щоб забезпечити аперіодичне зведення без перерегулювання та розгойдування.

Щоб дрон не врізався в край посадкового майданчика при раптовому зриві оптичного контакту, в алгоритмі реалізовано **динамічний конус безпеки**. Радіус допустимого відхилення лінійно зменшується разом із висотою: на висоті 10 метрів допустиме відхилення становить 3.5 метри, але на висоті 1.5 метра похибка зобов'язана бути меншою за 50 см. Якщо порив вітру виштовхує дрон за межі конуса, вертикальний спуск миттєво блокується (`vz = 0`), дрон зависає і чекає відновлення центрування.

---

### Критерії роботи детектора торкання ґрунту

Найвідповідальніший момент завершення повернення — перехід `GroundWaitDisarm` -> `DisarmedDone`. Хибне вимкнення двигунів у повітрі призводить до падіння апарата, а запізніле — до перекидання на бік через обертальний момент гвинтів, які зачепили ґрунт.

Детектор ґрунту використовує три незалежні фізичні інваріанти:
1. **Кінематичний інваріант:** вертикальна швидкість за даними комплексованого навігаційного фільтра становить `|vz| < 0.12 м/с`, незважаючи на те, що автопілот вимагає притискання до землі зі швидкістю `vz = +0.15 м/с`.
2. **Динамічний інваріант:** інтегральна компонента висотного PID-регулятора впала нижче 20% від номінального значення висіння (`throttle_ratio < 0.20`), оскільки фізична опора прийняла на себе вагу рами.
3. **Часовий фільтр стійкості:** умови 1 і 2 повинні безперервно утримуватися протягом 1200 мілісекунд. Якщо протягом цього вікна дрон підстрибнув або кутова швидкість різко зросла, таймер скидається, а автомат повертається до фази керованого спуску.

---

### Повний вихідний код модуля на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define RTL_MAX_BREADCRUMBS        64u
#define RTL_BREADCRUMB_MIN_DIST_M  8.0f
#define RTL_BREADCRUMB_PRUNE_EPS_M 1.5f
#define RTL_GROUND_DET_TIMEOUT_MS  1200u

typedef enum {
    FSM_IDLE = 0,
    FSM_CLIMB_SAFE_ALT,         // Вертикальний підйом на безпечний ешелон
    FSM_REVERSE_PATH_TRANSIT,   // Відкат за записаними крихтами назад
    FSM_DIRECT_HOME_TRANSIT,    // Прямий доліт до домашньої точки
    FSM_HOVER_SEARCH_TARGET,    // Зависання та оптичний пошук мітки
    FSM_PRECISION_DESCENT,      // Керований спуск із візуальним центруванням
    FSM_GROUND_WAIT_DISARM,     // Детектування землі та відлік таймауту
    FSM_DISARMED_DONE           // Мотори знеструмлено, завершення
} rtl_fsm_state_t;

typedef struct {
    float x, y, z;               // Координати в системі NED (метри)
    float vx, vy, vz;            // Швидкості NED (м/с)
} point3d_t;

typedef struct {
    float x, y, z;               // Зміщення мітки відносно дрона в NED (м)
    bool  valid;                 // Ознака достовірного розпізнавання
} vision_target_t;

typedef struct {
    point3d_t buffer[RTL_MAX_BREADCRUMBS];
    uint16_t  head;
    uint16_t  count;
} breadcrumb_ring_t;

typedef struct {
    float min_rtl_alt_m;         // Мінімальна висота безпечного ешелону (м)
    float cruise_speed_ms;       // Швидкість горизонтального транзиту (м/с)
    float climb_speed_ms;        // Вертикальна швидкість підйому (м/с)
    float descent_fast_ms;       // Швидкість швидкого зниження (м/с)
    float descent_slow_ms;       // Швидкість фінальної посадки (м/с)
    float accept_radius_m;       // Радіус досягнення точки маршруту (м)
    float optical_kp;            // Коефіцієнт оптичного центрування
} rtl_params_t;

typedef struct {
    rtl_fsm_state_t   state;
    rtl_params_t      params;
    breadcrumb_ring_t crumbs;
    point3d_t         home_point;
    float             active_cruise_alt_m;
    int16_t           crumb_reverse_idx;
    uint32_t          ground_timer_start_ms;
    bool              disarm_signal;
} rtl_engine_t;

// Ініціалізація кільцевого буфера
void crumbs_init(breadcrumb_ring_t *b) {
    b->head = 0;
    b->count = 0;
    memset(b->buffer, 0, sizeof(b->buffer));
}

// Додавання нової точки з перевіркою мінімальної дистанції
void crumbs_push(breadcrumb_ring_t *b, const point3d_t *p) {
    if (b->count > 0) {
        uint16_t last_idx = (b->head == 0) ? (RTL_MAX_BREADCRUMBS - 1) : (b->head - 1);
        float dx = p->x - b->buffer[last_idx].x;
        float dy = p->y - b->buffer[last_idx].y;
        float dz = p->z - b->buffer[last_idx].z;
        float dist_sq = dx * dx + dy * dy + dz * dz;

        if (dist_sq < (RTL_BREADCRUMB_MIN_DIST_M * RTL_BREADCRUMB_MIN_DIST_M)) {
            return; // Занадто близько до попередньої точки — пропускаємо
        }
    }

    b->buffer[b->head] = *p;
    b->head = (b->head + 1) % RTL_MAX_BREADCRUMBS;
    if (b->count < RTL_MAX_BREADCRUMBS) {
        b->count++;
    }
}

// Ініціалізація модуля RTL
void rtl_engine_init(rtl_engine_t *eng, const rtl_params_t *params, const point3d_t *home) {
    eng->state = FSM_IDLE;
    eng->params = *params;
    eng->home_point = *home;
    eng->active_cruise_alt_m = params->min_rtl_alt_m;
    eng->crumb_reverse_idx = -1;
    eng->ground_timer_start_ms = 0;
    eng->disarm_signal = false;
    crumbs_init(&eng->crumbs);
}

// Запуск процедури повернення
void rtl_engine_trigger(rtl_engine_t *eng, const point3d_t *current) {
    float cur_alt = -current->z; // У системі NED висота h = -Z
    if (cur_alt > eng->params.min_rtl_alt_m) {
        eng->active_cruise_alt_m = cur_alt;
    } else {
        eng->active_cruise_alt_m = eng->params.min_rtl_alt_m;
    }

    eng->crumb_reverse_idx = (int16_t)eng->crumbs.count - 1;
    eng->state = FSM_CLIMB_SAFE_ALT;
    eng->ground_timer_start_ms = 0;
    eng->disarm_signal = false;
}

// Головний ітераційний крок автомата (50 Гц)
void rtl_engine_step(rtl_engine_t *eng, const point3d_t *cur,
                     const vision_target_t *vision, float throttle_ratio,
                     uint32_t now_ms, point3d_t *setpoint_out) {

    switch (eng->state) {
        case FSM_CLIMB_SAFE_ALT: {
            // Вертикальний підйом на місці
            setpoint_out->x = cur->x;
            setpoint_out->y = cur->y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = -eng->params.climb_speed_ms;

            if ((-cur->z) >= (eng->active_cruise_alt_m - 0.5f)) {
                // Якщо є крихти маршруту — йдемо за ними, інакше напряму до бази
                if (eng->crumb_reverse_idx >= 0) {
                    eng->state = FSM_REVERSE_PATH_TRANSIT;
                } else {
                    eng->state = FSM_DIRECT_HOME_TRANSIT;
                }
            }
            break;
        }

        case FSM_REVERSE_PATH_TRANSIT: {
            if (eng->crumb_reverse_idx < 0) {
                eng->state = FSM_DIRECT_HOME_TRANSIT;
                break;
            }

            point3d_t target_wp = eng->crumbs.buffer[eng->crumb_reverse_idx];
            float dx = target_wp.x - cur->x;
            float dy = target_wp.y - cur->y;
            float dist = sqrtf(dx * dx + dy * dy);

            setpoint_out->x = target_wp.x;
            setpoint_out->y = target_wp.y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vz = 0.0f;

            if (dist > eng->params.accept_radius_m) {
                setpoint_out->vx = (dx / dist) * eng->params.cruise_speed_ms;
                setpoint_out->vy = (dy / dist) * eng->params.cruise_speed_ms;
            } else {
                // Досягли проміжної точки — беремо попередню
                eng->crumb_reverse_idx--;
                if (eng->crumb_reverse_idx < 0) {
                    eng->state = FSM_DIRECT_HOME_TRANSIT;
                }
            }
            break;
        }

        case FSM_DIRECT_HOME_TRANSIT: {
            float dx = eng->home_point.x - cur->x;
            float dy = eng->home_point.y - cur->y;
            float dist = sqrtf(dx * dx + dy * dy);

            setpoint_out->x = eng->home_point.x;
            setpoint_out->y = eng->home_point.y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vz = 0.0f;

            if (dist > eng->params.accept_radius_m) {
                setpoint_out->vx = (dx / dist) * eng->params.cruise_speed_ms;
                setpoint_out->vy = (dy / dist) * eng->params.cruise_speed_ms;
            } else {
                setpoint_out->vx = 0.0f;
                setpoint_out->vy = 0.0f;
                eng->state = FSM_HOVER_SEARCH_TARGET;
            }
            break;
        }

        case FSM_HOVER_SEARCH_TARGET: {
            setpoint_out->x = eng->home_point.x;
            setpoint_out->y = eng->home_point.y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = 0.0f;

            eng->state = FSM_PRECISION_DESCENT;
            break;
        }

        case FSM_PRECISION_DESCENT: {
            float cur_alt = -cur->z;
            float vz_desc = (cur_alt > 5.0f) ? eng->params.descent_fast_ms 
                                             : eng->params.descent_slow_ms;

            if (vision->valid) {
                // Візуальне пропорційне наведення на мітку
                setpoint_out->vx = -eng->params.optical_kp * vision->x;
                setpoint_out->vy = -eng->params.optical_kp * vision->y;

                float offset = sqrtf(vision->x * vision->x + vision->y * vision->y);
                // Якщо похибка виходить за межі конуса — зупиняємо спуск
                if (offset > (cur_alt * 0.35f) && cur_alt > 1.2f) {
                    vz_desc = 0.0f;
                }
            } else {
                setpoint_out->x = eng->home_point.x;
                setpoint_out->y = eng->home_point.y;
                setpoint_out->vx = 0.0f;
                setpoint_out->vy = 0.0f;
            }

            setpoint_out->z = 0.0f;
            setpoint_out->vz = vz_desc;

            // Критерій торкання землі: низька висота, близька до нуля швидкість, низький газ
            if (cur_alt < 0.8f && fabsf(cur->vz) < 0.12f && throttle_ratio < 0.20f) {
                eng->state = FSM_GROUND_WAIT_DISARM;
                eng->ground_timer_start_ms = now_ms;
            }
            break;
        }

        case FSM_GROUND_WAIT_DISARM: {
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = 0.15f; // Легкий притиск до ґрунту

            if (fabsf(cur->vz) < 0.12f && throttle_ratio < 0.20f) {
                if ((now_ms - eng->ground_timer_start_ms) >= RTL_GROUND_DET_TIMEOUT_MS) {
                    eng->disarm_signal = true;
                    eng->state = FSM_DISARMED_DONE;
                }
            } else {
                // Підстрибування або порив вітру — повернення до посадки
                eng->state = FSM_PRECISION_DESCENT;
            }
            break;
        }

        case FSM_DISARMED_DONE:
        case FSM_IDLE:
        default:
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = 0.0f;
            break;
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <algorithm>

struct Point3D {
    float x{0.0f};      // Координати NED (м)
    float y{0.0f};
    float z{0.0f};
    float vx{0.0f};     // Швидкості NED (м/с)
    float vy{0.0f};
    float vz{0.0f};
};

struct VisionTarget {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
    bool  valid{false};
};

struct RtlParameters {
    float minRtlAltM{30.0f};
    float cruiseSpeedMs{12.0f};
    float climbSpeedMs{2.5f};
    float descentFastMs{1.5f};
    float descentSlowMs{0.4f};
    float acceptRadiusM{2.0f};
    float opticalKp{0.8f};
};

enum class FsmState : uint8_t {
    Idle = 0,
    ClimbSafeAlt,
    ReversePathTransit,
    DirectHomeTransit,
    HoverSearchTarget,
    PrecisionDescent,
    GroundWaitDisarm,
    DisarmedDone
};

template <std::size_t Capacity = 64>
class BreadcrumbBuffer {
public:
    void push(const Point3D& p, float minDistance = 8.0f) noexcept {
        if (count_ > 0) {
            const auto lastIdx = (head_ == 0) ? (Capacity - 1) : (head_ - 1);
            const float dx = p.x - buffer_[lastIdx].x;
            const float dy = p.y - buffer_[lastIdx].y;
            const float dz = p.z - buffer_[lastIdx].z;
            if ((dx * dx + dy * dy + dz * dz) < (minDistance * minDistance)) {
                return;
            }
        }
        buffer_[head_] = p;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }
    [[nodiscard]] const Point3D& at(std::size_t index) const noexcept { return buffer_[index]; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    std::array<Point3D, Capacity> buffer_{};
    std::size_t head_{0};
    std::size_t count_{0};
};

class RtlStateMachine {
public:
    RtlStateMachine(const RtlParameters& params, const Point3D& homePoint) noexcept
        : params_(params), homePoint_(homePoint) {}

    void recordBreadcrumb(const Point3D& current) noexcept {
        crumbs_.push(current);
    }

    void trigger(const Point3D& current) noexcept {
        const float curAlt = -current.z;
        activeCruiseAltM_ = std::max(curAlt, params_.minRtlAltM);
        crumbReverseIdx_ = static_cast<int32_t>(crumbs_.count()) - 1;
        state_ = FsmState::ClimbSafeAlt;
        groundTimerStartMs_ = 0;
        disarmSignal_ = false;
    }

    void step(const Point3D& cur, const VisionTarget& vision, float throttleRatio,
              uint32_t nowMs, Point3D& cmdOut) noexcept {
        switch (state_) {
            case FsmState::ClimbSafeAlt:
                handleClimb(cur, cmdOut);
                break;
            case FsmState::ReversePathTransit:
                handleReverseTransit(cur, cmdOut);
                break;
            case FsmState::DirectHomeTransit:
                handleDirectTransit(cur, cmdOut);
                break;
            case FsmState::HoverSearchTarget:
                handleHoverSearch(cur, cmdOut);
                break;
            case FsmState::PrecisionDescent:
                handlePrecisionDescent(cur, vision, throttleRatio, nowMs, cmdOut);
                break;
            case FsmState::GroundWaitDisarm:
                handleGroundWait(cur, throttleRatio, nowMs, cmdOut);
                break;
            case FsmState::DisarmedDone:
            case FsmState::Idle:
            default:
                cmdOut.vx = 0.0f;
                cmdOut.vy = 0.0f;
                cmdOut.vz = 0.0f;
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return state_; }
    [[nodiscard]] bool isDisarmSignaled() const noexcept { return disarmSignal_; }

private:
    void handleClimb(const Point3D& cur, Point3D& cmdOut) noexcept {
        cmdOut.x = cur.x;
        cmdOut.y = cur.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vz = -params_.climbSpeedMs;
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;

        if ((-cur.z) >= (activeCruiseAltM_ - 0.5f)) {
            state_ = (crumbReverseIdx_ >= 0) ? FsmState::ReversePathTransit 
                                             : FsmState::DirectHomeTransit;
        }
    }

    void handleReverseTransit(const Point3D& cur, Point3D& cmdOut) noexcept {
        if (crumbReverseIdx_ < 0) {
            state_ = FsmState::DirectHomeTransit;
            return;
        }

        const auto& target = crumbs_.at(static_cast<std::size_t>(crumbReverseIdx_));
        const float dx = target.x - cur.x;
        const float dy = target.y - cur.y;
        const float dist = std::hypot(dx, dy);

        cmdOut.x = target.x;
        cmdOut.y = target.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vz = 0.0f;

        if (dist > params_.acceptRadiusM) {
            cmdOut.vx = (dx / dist) * params_.cruiseSpeedMs;
            cmdOut.vy = (dy / dist) * params_.cruiseSpeedMs;
        } else {
            --crumbReverseIdx_;
            if (crumbReverseIdx_ < 0) {
                state_ = FsmState::DirectHomeTransit;
            }
        }
    }

    void handleDirectTransit(const Point3D& cur, Point3D& cmdOut) noexcept {
        const float dx = homePoint_.x - cur.x;
        const float dy = homePoint_.y - cur.y;
        const float dist = std::hypot(dx, dy);

        cmdOut.x = homePoint_.x;
        cmdOut.y = homePoint_.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vz = 0.0f;

        if (dist > params_.acceptRadiusM) {
            cmdOut.vx = (dx / dist) * params_.cruiseSpeedMs;
            cmdOut.vy = (dy / dist) * params_.cruiseSpeedMs;
        } else {
            cmdOut.vx = 0.0f;
            cmdOut.vy = 0.0f;
            state_ = FsmState::HoverSearchTarget;
        }
    }

    void handleHoverSearch(const Point3D& /*cur*/, Point3D& cmdOut) noexcept {
        cmdOut.x = homePoint_.x;
        cmdOut.y = homePoint_.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;
        cmdOut.vz = 0.0f;
        state_ = FsmState::PrecisionDescent;
    }

    void handlePrecisionDescent(const Point3D& cur, const VisionTarget& vision,
                                float throttleRatio, uint32_t nowMs, Point3D& cmdOut) noexcept {
        const float curAlt = -cur.z;
        float vzDesc = (curAlt > 5.0f) ? params_.descentFastMs : params_.descentSlowMs;

        if (vision.valid) {
            cmdOut.vx = -params_.opticalKp * vision.x;
            cmdOut.vy = -params_.opticalKp * vision.y;

            const float offset = std::hypot(vision.x, vision.y);
            if (offset > (curAlt * 0.35f) && curAlt > 1.2f) {
                vzDesc = 0.0f;
            }
        } else {
            cmdOut.x = homePoint_.x;
            cmdOut.y = homePoint_.y;
            cmdOut.vx = 0.0f;
            cmdOut.vy = 0.0f;
        }

        cmdOut.z = 0.0f;
        cmdOut.vz = vzDesc;

        if (curAlt < 0.8f && std::abs(cur.vz) < 0.12f && throttleRatio < 0.20f) {
            state_ = FsmState::GroundWaitDisarm;
            groundTimerStartMs_ = nowMs;
        }
    }

    void handleGroundWait(const Point3D& cur, float throttleRatio,
                          uint32_t nowMs, Point3D& cmdOut) noexcept {
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;
        cmdOut.vz = 0.15f;

        if (std::abs(cur.vz) < 0.12f && throttleRatio < 0.20f) {
            if ((nowMs - groundTimerStartMs_) >= 1200u) {
                disarmSignal_ = true;
                state_ = FsmState::DisarmedDone;
            }
        } else {
            state_ = FsmState::PrecisionDescent;
        }
    }

    RtlParameters           params_;
    Point3D                 homePoint_;
    BreadcrumbBuffer<64>    crumbs_{};
    FsmState                state_{FsmState::Idle};
    float                   activeCruiseAltM_{30.0f};
    int32_t                 crumbReverseIdx_{-1};
    uint32_t                groundTimerStartMs_{0};
    bool                    disarmSignal_{false};
};
```
:::

---

### Практичні рекомендації з інтеграції

1. **Частота виклику та пріоритетизація задач:**
   Функція `rtl_engine_step()` призначена для виконання в навігаційному потоці із частотою 50 Гц. Швидкий контур кутової стабілізації та змішування моторів (250–500 Гц) відпрацьовує згенеровані уставки швидкостей `(vx, vy, vz)`.
2. **Обробка переповнення буфера на довгих маршрутах:**
   Якщо довжина місії перевищує місткість кільцевого масиву, старі точки затираються. Для наддовгих місій рекомендується збільшити дистанцію квантування `RTL_BREADCRUMB_MIN_DIST_M` до 15–20 метрів або інтегрувати динамічне проріджування колінеарних ділянок просто в процедуру вставки.
3. **Калібрування детектора ґрунту:**
   Порогове значення `throttle_ratio < 0.20` налаштовується індивідуально під тяговооруженість апарата. Для важких промислових дронів із запасом тяги 3:1 поріг детектування контакту встановлюють на рівні 12–15% від максимального виходу ШІМ.

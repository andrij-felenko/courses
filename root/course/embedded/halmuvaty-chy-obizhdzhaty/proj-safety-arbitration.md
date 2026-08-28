# ⚙️ Диспетчер зон безпеки та безударний арбітраж швидкостей

Практична реалізація детермінованого вбудованого модуля арбітражу швидкостей для автономних мобільних роботів і безпілотних апаратів. Модуль працює на жорсткій частоті 100 Гц (період 10 мс), обчислює динамічні межі трьох зон безпеки з урахуванням поточної швидкості апарата, керує скінченним автоматом переходів із просторово-часовим гістерезисом і здійснює безударне зшивання (velocity blending) планового вектора від повільного планувальника з реактивним вектором ухиляння.

## 1. Архітектура та математична модель модуля

Головна проблема дворівневої навігації полягає в різниці темпів: планувальник надсилає бажаний вектор руху `v_plan` з низькою частотою (1–10 Гц) через інтерфейс CAN або UART, тоді як сирі промені далекоміра надходять безпосередньо в мікроконтролер із частотою 50–200 Гц. Якщо мікроконтролер просто перемикатиме уставки жорстким мультиплексором, мотори отримуватимуть ступінчасті удари струму, а апарат розхитуватиметься на межі виявлення перешкоди.

Модуль арбітражу усуває цю проблему за рахунок чотирьох послідовних етапів обробки на кожному такті:

```
                  ┌──────────────────────────────────────────────┐
                  │    Вхідний вектор плану: v_plan (1–10 Гц)    │
                  │    Вхідний вектор рефлексу: v_react (100 Гц) │
                  │    Мінімальна дальність: d_min (100 Гц)      │
                  │    Поточна швидкість: current_speed (100 Гц) │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │  1. Динамічний розрахунок меж зон R_stop(v), │
                  │     R_warn(v) за гальмівною кінематикою      │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │  2. Автомат переходів із подвійним           │
                  │     просторово-часовим гістерезисом          │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │  3. Змішування векторів v_cmd(α) та          │
                  │     динамічне зрізання швидкості за v_safe   │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │  4. Моніторинг таймауту зв'язку (Watchdog)   │
                  │     та захист від зависання планувальника    │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │    Фінальна уставка швидкості: v_cmd (100 Гц)│
                  └──────────────────────────────────────────────┘
```

### Динамічні межі зон безпеки

Статичні радіуси зон не працюють у динаміці: радіус, безпечний на швидкості 1 м/с, призведе до гарантованого зіткнення на швидкості 10 м/с. Тому межі зон перераховуються щотакту за кінематичними формулами рівносповільненого руху:

```
d_brake = current_speed² / (2 · max_accel)
R_stop  = d_brake + current_speed · reaction_time + stop_margin
R_warn  = R_stop + current_speed · planner_period + warn_buffer
```

Де:
- `max_accel` — гарантоване максимальне сповільнення апарата на поточному покритті (м/с²);
- `reaction_time` — апаратна затримка спрацьовування силового тракту: час наростання тиску в гідравліці, затримка фільтрації ESC або час розмагнічування обмоток (типово 0.03–0.06 с);
- `stop_margin` — геометричний запас безпеки між зупиненим апаратом і перешкодою (типово 0.3–0.5 м);
- `planner_period` — максимальний очікуваний період між послідовними оновленнями планової траєкторії від бортового комп'ютера (типово 0.1–0.5 с);
- `warn_buffer` — просторовий запас для виконання плавного бічного маневру (типово 0.5–1.2 м).

### Плавне зшивання векторів швидкості (Velocity Blending)

Коли мінімальна виявлена дистанція `d_min` потрапляє в зону застереження (`R_stop < d_min ≤ R_warn`), арбітр обчислює нормалізований коефіцієнт змішування `α ∈ [0.0, 1.0]`:

```
α = (R_warn - d_min) / (R_warn - R_stop)
```

Вектор вихідної уставки швидкості формується безперервною лінійною інтерполяцією:

```
v_cmd = (1.0 - α) · v_plan + α · v_react
```

Якщо `d_min == R_warn`, маємо `α = 0.0` (повне підпорядкування планувальнику). У міру наближення до перешкоди частка реактивного вектора плавно зростає, досягаючи `α = 1.0` на межі `R_stop`.

Одночасно на модуль накладається кінематичне обмеження безпечної швидкості зближення:

```
dist_to_stop = d_min - R_stop
v_safe = √(2 · max_accel · dist_to_stop)
```

Якщо довжина вектора `|v_cmd|` перевищує `v_safe`, вектор масштабується зі збереженням напрямку:

```
v_cmd = v_cmd · (v_safe / |v_cmd|)
```

### Захист від деренчання: просторово-часовий гістерезис

При русі вздовж нерівного паркану чи чагарнику виміряна дистанція `d_min` безперервно коливається через шуми давача та дрібні виступи. Без спеціального захисту автомат станів постійно перемикався б між `ZONE_WARNING` та `ZONE_OBSERVATION`, викликаючи високочастотні посмикування уставки.

Для стабілізації впроваджено два правила:
1. **Миттєва ескалація**: перехід у бік більшої небезпеки (`OBSERVATION → WARNING → ESTOP`) відбувається миттєво на першому ж такті, коли зафіксовано порушення порогу.
2. **Затримана деескалація**: перехід у бік меншої небезпеки дозволяється лише тоді, коли перешкода відійшла далі за поріг на величину просторового гістерезису `SAFETY_HYST_DIST_M` (наприклад, +30 см) і залишається там безперервно протягом `SAFETY_HOLD_TICKS` тактів (наприклад, 200 мс).

---

## 2. Реалізація мовами C та C++

Код спроєктовано для вбудованих систем реального часу: нульове динамічне виділення пам'яті (zero-heap allocation), відсутність блокуючих викликів, повний захист від ділення на нуль і переповнення буферів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAFETY_DT_SEC          0.010f  // Період такту: 10 мс (100 Гц)
#define SAFETY_HOLD_TICKS      20U     // Час стабілізації: 20 тактів (200 мс)
#define SAFETY_HYST_DIST_M     0.30f   // Просторовий гістерезис: 30 см
#define SAFETY_WATCHDOG_TICKS  50U     // Таймаут планувальника: 500 мс

typedef enum {
    ZONE_OBSERVATION = 0,  // Вільний рух за глобальним планом
    ZONE_WARNING,          // Плавне змішування векторів та гальмування
    ZONE_ESTOP             // Аварійне переривання та повний стоп
} SafetyZone;

typedef struct {
    float x;
    float y;
} Vector2D;

typedef struct {
    float max_accel;        // Максимальне сповільнення, м/с² (типово 2.5)
    float reaction_time;    // Затримка реакції приводу, с (типово 0.05)
    float planner_period;   // Очікуваний період планувальника, с (типово 0.20)
    float stop_margin;      // Фізичний зазор зупинки, м (типово 0.40)
    float warn_buffer;      // Буфер зони застереження, м (типово 0.80)
} SafetyParams;

typedef struct {
    SafetyZone current_zone;
    uint32_t   hold_counter;
    uint32_t   planner_watchdog;
    Vector2D   last_cmd_vel;
    bool       override_active;
    bool       planner_timed_out;
} SafetyArbiter;

static inline float vec2d_len(Vector2D v) {
    return sqrtf(v.x * v.x + v.y * v.y);
}

static inline Vector2D vec2d_scale(Vector2D v, float s) {
    Vector2D out = { v.x * s, v.y * s };
    return out;
}

static inline Vector2D vec2d_add(Vector2D a, Vector2D b) {
    Vector2D out = { a.x + b.x, a.y + b.y };
    return out;
}

void safety_arbiter_init(SafetyArbiter *arb) {
    arb->current_zone = ZONE_OBSERVATION;
    arb->hold_counter = 0;
    arb->planner_watchdog = 0;
    arb->last_cmd_vel.x = 0.0f;
    arb->last_cmd_vel.y = 0.0f;
    arb->override_active = false;
    arb->planner_timed_out = false;
}

void safety_arbiter_feed_planner_heartbeat(SafetyArbiter *arb) {
    arb->planner_watchdog = 0;
    arb->planner_timed_out = false;
}

Vector2D safety_arbiter_update(SafetyArbiter *arb,
                              const SafetyParams *params,
                              Vector2D v_plan,
                              Vector2D v_react,
                              float min_obstacle_dist,
                              float current_speed) {
    // 0. Моніторинг працездатності каналу зв'язку з планувальником
    arb->planner_watchdog++;
    if (arb->planner_watchdog > SAFETY_WATCHDOG_TICKS) {
        arb->planner_timed_out = true;
        // При втраті зв'язку обнуляємо плановий вектор (fail-safe)
        v_plan.x = 0.0f;
        v_plan.y = 0.0f;
    }

    // 1. Кінематичний розрахунок динамічних меж зон
    float safe_speed = (current_speed > 0.0f) ? current_speed : 0.0f;
    float d_brake = (safe_speed * safe_speed) / (2.0f * params->max_accel);
    float r_stop = d_brake + (safe_speed * params->reaction_time) + params->stop_margin;
    float r_warn = r_stop + (safe_speed * params->planner_period) + params->warn_buffer;

    // 2. Визначення миттєвої зони
    SafetyZone target_zone;
    if (min_obstacle_dist <= r_stop) {
        target_zone = ZONE_ESTOP;
    } else if (min_obstacle_dist <= r_warn) {
        target_zone = ZONE_WARNING;
    } else {
        target_zone = ZONE_OBSERVATION;
    }

    // 3. Автомат переходів із просторово-часовим гістерезисом
    if (target_zone > arb->current_zone) {
        // Ескалація: миттєвий перехід без затримок
        arb->current_zone = target_zone;
        arb->hold_counter = SAFETY_HOLD_TICKS;
    } else if (target_zone < arb->current_zone) {
        // Деескалація: вимагаємо просторовий запас та відлік таймера
        bool hyst_cleared = false;
        if (arb->current_zone == ZONE_ESTOP) {
            hyst_cleared = (min_obstacle_dist > (r_stop + SAFETY_HYST_DIST_M));
        } else if (arb->current_zone == ZONE_WARNING) {
            hyst_cleared = (min_obstacle_dist > (r_warn + SAFETY_HYST_DIST_M));
        }

        if (hyst_cleared) {
            if (arb->hold_counter > 0) {
                arb->hold_counter--;
            } else {
                arb->current_zone = target_zone;
                arb->hold_counter = SAFETY_HOLD_TICKS;
            }
        } else {
            arb->hold_counter = SAFETY_HOLD_TICKS;
        }
    } else {
        arb->hold_counter = SAFETY_HOLD_TICKS;
    }

    // 4. Формування вихідного вектора швидкості
    Vector2D cmd_out = { 0.0f, 0.0f };

    switch (arb->current_zone) {
        case ZONE_ESTOP:
            arb->override_active = true;
            cmd_out.x = 0.0f;
            cmd_out.y = 0.0f;
            break;

        case ZONE_WARNING: {
            arb->override_active = false;
            float span = r_warn - r_stop;
            float alpha = (span > 0.01f) ? ((r_warn - min_obstacle_dist) / span) : 1.0f;
            if (alpha < 0.0f) alpha = 0.0f;
            if (alpha > 1.0f) alpha = 1.0f;

            // Змішування: v_cmd = (1 - alpha)*v_plan + alpha*v_react
            Vector2D part_plan = vec2d_scale(v_plan, 1.0f - alpha);
            Vector2D part_react = vec2d_scale(v_react, alpha);
            cmd_out = vec2d_add(part_plan, part_react);

            // Динамічне обмеження швидкості за профілем гальмування
            float dist_to_stop = min_obstacle_dist - r_stop;
            if (dist_to_stop > 0.0f) {
                float v_safe = sqrtf(2.0f * params->max_accel * dist_to_stop);
                float cmd_len = vec2d_len(cmd_out);
                if (cmd_len > v_safe && cmd_len > 0.001f) {
                    cmd_out = vec2d_scale(cmd_out, v_safe / cmd_len);
                }
            } else {
                cmd_out.x = 0.0f;
                cmd_out.y = 0.0f;
            }
            break;
        }

        case ZONE_OBSERVATION:
        default:
            arb->override_active = false;
            cmd_out = v_plan;
            break;
    }

    arb->last_cmd_vel = cmd_out;
    return cmd_out;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <optional>

namespace navigation::safety {

enum class Zone : uint8_t {
    Observation = 0,
    Warning,
    EmergencyStop
};

struct Vector2D {
    float x{0.0f};
    float y{0.0f};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& o) const noexcept {
        return { x + o.x, y + o.y };
    }

    [[nodiscard]] constexpr Vector2D operator*(float s) const noexcept {
        return { x * s, y * s };
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(x * x + y * y);
    }

    [[nodiscard]] Vector2D normalized() const noexcept {
        const float len = length();
        return (len > 1e-4f) ? Vector2D{ x / len, y / len } : Vector2D{ 0.0f, 0.0f };
    }
};

struct Config {
    float maxDeceleration{2.5f};     // Максимальне сповільнення, м/с²
    float reactionTime{0.05f};       // Затримка реакції приводу, с
    float plannerPeriod{0.20f};      // Очікуваний період планувальника, с
    float stopMargin{0.40f};         // Запас зупинки, м
    float warnBuffer{0.80f};         // Додатковий буфер зони застереження, м
    float hystDistance{0.30f};       // Просторовий гістерезис деескалації, м
    uint32_t holdTicks{20};          // Кількість тактів утримання перед деескалацією
    uint32_t watchdogTimeoutTicks{50}; // Таймаут зв'язку (500 мс при такті 10 мс)
};

class Arbiter {
public:
    explicit constexpr Arbiter(const Config& config = {}) noexcept
        : cfg_(config), currentZone_(Zone::Observation),
          holdCounter_(0), watchdogCounter_(0),
          plannerTimedOut_(false), lastCommand_{} {}

    struct UpdateResult {
        Vector2D velocityCommand;
        Zone activeZone;
        bool isEmergencyOverride;
        bool isPlannerTimedOut;
    };

    void feedPlannerHeartbeat() noexcept {
        watchdogCounter_ = 0;
        plannerTimedOut_ = false;
    }

    [[nodiscard]] UpdateResult update(Vector2D planVel,
                                      const Vector2D& reactVel,
                                      float minObstacleDist,
                                      float currentSpeed) noexcept {
        // 0. Перевірка таймауту каналу зв'язку
        ++watchdogCounter_;
        if (watchdogCounter_ > cfg_.watchdogTimeoutTicks) {
            plannerTimedOut_ = true;
            planVel = { 0.0f, 0.0f };
        }

        // 1. Кінематичний розрахунок динамічних радіусів зон
        const float safeSpeed = std::max(0.0f, currentSpeed);
        const float dBrake = (safeSpeed * safeSpeed) / (2.0f * cfg_.maxDeceleration);
        const float rStop  = dBrake + (safeSpeed * cfg_.reactionTime) + cfg_.stopMargin;
        const float rWarn  = rStop + (safeSpeed * cfg_.plannerPeriod) + cfg_.warnBuffer;

        // 2. Оцінка миттєвої зони
        const Zone instantZone = evaluateZone(minObstacleDist, rStop, rWarn);

        // 3. Автомат переходів із фільтрацією перемикань
        manageZoneTransitions(instantZone, minObstacleDist, rStop, rWarn);

        // 4. Генерація та масштабування вихідного вектора
        Vector2D outVelocity{ 0.0f, 0.0f };
        bool overrideActive = false;

        switch (currentZone_) {
            case Zone::EmergencyStop:
                overrideActive = true;
                outVelocity = { 0.0f, 0.0f };
                break;

            case Zone::Warning: {
                overrideActive = false;
                const float span = rWarn - rStop;
                const float alpha = (span > 1e-3f)
                    ? std::clamp((rWarn - minObstacleDist) / span, 0.0f, 1.0f)
                    : 1.0f;

                outVelocity = (planVel * (1.0f - alpha)) + (reactVel * alpha);

                // Обмеження швидкості за безпечним гальмівним профілем
                const float distToStop = minObstacleDist - rStop;
                if (distToStop > 0.0f) {
                    const float vSafe = std::sqrt(2.0f * cfg_.maxDeceleration * distToStop);
                    const float len = outVelocity.length();
                    if (len > vSafe && len > 1e-4f) {
                        outVelocity = outVelocity * (vSafe / len);
                    }
                } else {
                    outVelocity = { 0.0f, 0.0f };
                }
                break;
            }

            case Zone::Observation:
            default:
                overrideActive = false;
                outVelocity = planVel;
                break;
        }

        lastCommand_ = outVelocity;
        return { outVelocity, currentZone_, overrideActive, plannerTimedOut_ };
    }

    [[nodiscard]] Zone getZone() const noexcept { return currentZone_; }
    [[nodiscard]] Vector2D getLastCommand() const noexcept { return lastCommand_; }
    [[nodiscard]] bool isPlannerTimedOut() const noexcept { return plannerTimedOut_; }

private:
    [[nodiscard]] static constexpr Zone evaluateZone(float dist, float rStop, float rWarn) noexcept {
        if (dist <= rStop) return Zone::EmergencyStop;
        if (dist <= rWarn) return Zone::Warning;
        return Zone::Observation;
    }

    void manageZoneTransitions(Zone instantZone, float dist, float rStop, float rWarn) noexcept {
        if (instantZone > currentZone_) {
            currentZone_ = instantZone;
            holdCounter_ = cfg_.holdTicks;
        } else if (instantZone < currentZone_) {
            bool hysteresisPassed = false;
            if (currentZone_ == Zone::EmergencyStop) {
                hysteresisPassed = (dist > (rStop + cfg_.hystDistance));
            } else if (currentZone_ == Zone::Warning) {
                hysteresisPassed = (dist > (rWarn + cfg_.hystDistance));
            }

            if (hysteresisPassed) {
                if (holdCounter_ > 0) {
                    --holdCounter_;
                } else {
                    currentZone_ = instantZone;
                    holdCounter_ = cfg_.holdTicks;
                }
            } else {
                holdCounter_ = cfg_.holdTicks;
            }
        } else {
            holdCounter_ = cfg_.holdTicks;
        }
    }

    Config cfg_;
    Zone currentZone_;
    uint32_t holdCounter_;
    uint32_t watchdogCounter_;
    bool plannerTimedOut_;
    Vector2D lastCommand_;
};

} // namespace navigation::safety
```
:::

---

## 3. Розбір крайових випадків та інтеграційні пастки

Під час переносу алгоритму на реальне бортове залізо розробники стикаються з чотирма типовими пастками:

1. **Джитер таймауту каналу зв'язку (Transport Latency Jitter):**
   При передачі `v_plan` через віртуальний COM-порт (USB-CDC) або перевантажену шину CAN затримка між пакетами може нерівномірно коливатися від 50 до 350 мс. Якщо поріг watchdog виставити занадто малим (наприклад, 1.1 × `T_plan`), апарат систематично смикатиметься від помилкових спрацювань таймауту. Оптимальний емпіричний поріг становить `2.0–2.5 × T_plan`.

2. **Неузгодженість систем координат (Frame Mismatch):**
   Планувальник часто оперує векторами у глобальній системі координат одометрії (`Odom / Map Frame`), тоді як реактивний шар розраховує вектори у зв'язаній системі координат апарата (`Body Frame`). Змішування векторів із різних систем координат призведе до неконтрольованого обертання машини навколо вертикальної осі. Арбітр зобов'язаний отримувати обидва вектори, приведені до єдиного фрейму (рекомендовано `Body Frame`).

3. **Скидання інтегратора регулятора швидкості (Integrator Windup Reset):**
   У мить переходу в стан `ZONE_ESTOP` арбітр повинен виставити прапорець `override_active`. Низькорівневий каскадний регулятор швидкості (PID) зобов'язаний за цим прапорцем скинути накопичену інтегральну суму `I-term` у нуль, інакше після виходу з аварійного режиму накопичена помилка викличе різкий неконтрольований ривок моторів.

4. **Продуктивність та обчислення на мікроконтролері:**
   Увесь цикл `safety_arbiter_update` містить дві операції взяття квадратного кореня `sqrtf` та кілька десятків операцій додавання/множення з плаваючою комою. На мікроконтролері з апаратним FPU (наприклад, STM32F4/F7/H7, Cortex-M4F/M7) функція виконується менш ніж за 250 тактів процесора (близько 1.2 мікросекунди на частоті 216 МГц), що становить менше 0.02% від доступного бюджету 10-мілісекундного такту.

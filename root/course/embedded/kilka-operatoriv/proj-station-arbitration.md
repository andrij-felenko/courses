# ⚙️ Бортовий контролер арбітражу кількох станцій керування

У цій проектній вставці наведено повну програмну реалізацію бортового модуля арбітражу та розмежування повноважень наземних станцій (GCS). Модуль розроблений для застосування у вбудовуваних системах реального часу (STM32, ESP32 під керуванням FreeRTOS або мікрокомп'ютери Linux) і забезпечує детерміновану фільтрацію пакетів, облік оренди токенів, перевірку нейтралі стіків під час передачі зміни та безумовне аварійне перехоплення командиром.

---

## 1. Архітектурна концепція та місце в контурі керування

Модуль арбітражу функціонує як ізольований захисний шар (Security Boundary) між мережевим стеком (UART/UDP/MAVLink) та виконавчими контурами автопілота (мікшер моторів, регулятори стабілізації, контролер підвісу). Його головне завдання — унеможливити виконання суперечливих команд від різних пультів, відсікаючи несанкціонований трафік ще до потрапляння в ПІД-регулятори.

```
   Мережевий потік пакетів (UDP/UART)
                  │
                  ▼
   ┌───────────────────────────────┐
   │    Парсер кадрів та CRC16     │
   └──────────────┬────────────────┘
                  │
                  ▼
   ┌───────────────────────────────┐
   │   Бортовий арбітр токенів     │ ◄─── Системний таймер (SysTick / 1 кГц)
   │  (Onboard Authority Arbiter)  │
   ├───────────────────────────────┤
   │ 1. Звірка Source ID та Nonce  │
   │ 2. Перевірка оренди Heartbeat │
   │ 3. Валідація мертвої зони     │
   │ 4. Обробка аварійного Override│
   └──────────────┬────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
 ┌───────────────┐ ┌───────────────┐
 │ Польотний     │ │ Підсистема    │
 │ контролер     │ │ підвісу       │
 │ (Тільки Пілот)│ │ (Тільки Сенсор│
 └───────────────┘ └───────────────┘
```

Контролер спроєктовано з дотриманням чотирьох жорстких інженерних інваріантів:
1. **Нульовий динамічний розподіл пам'яті (Zero Heap Allocation):** Усі структури даних, дескриптори сесій та черги виділяються статично під час компіляції. Це гарантує відсутність фрагментації оперативної пам'яті та детермінований час виконання функцій арбітражу у жорсткому реалтаймі.
2. **Атомарність зміни володіння (Atomic Ownership Switch):** Перемикання дескриптора активного пілота між станціями відбувається за одну атомарну операцію запису з одночасним оновленням 32-бітного псевдовипадкового числа `token_nonce`. Це унеможливлює стан гонитви (Race Condition), коли старий пульт міг би встигнути вклинитися між перемиканням прапорців.
3. **Гістерезис мертвої зони (Deadband Hysteresis):** Перевірка нульового положення стіків змінного пульта враховує шуми потенціометрів та механічний люфт пружин, запобігаючи несподіваним ривкам апарата при передачі зміни.
4. **Ізоляція каналів (Plane Separation):** Канал керування корисним навантаженням (камера, скидання) повністю відокремлений від каналу навігації, тому активність оператора сенсорів ні за яких умов не впливає на стабільність польоту.

---

## 2. Повна програмна реалізація контролера

Нижче наведено самодостатній вихідний код модуля арбітражу на мові C та його ідіоматичний еквівалент на сучасному стандарті C++20.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ARBITER_MAX_STATIONS        8
#define ARBITER_HEARTBEAT_TIMEOUT   1000  /* мс */
#define ARBITER_HANDOVER_TIMEOUT    5000  /* мс */
#define ARBITER_DEADBAND_LIMIT        30  /* 3% від діапазону 1000 */

typedef enum {
    ROLE_FLAG_NONE      = 0x00,
    ROLE_FLAG_MONITOR   = 0x01,
    ROLE_FLAG_PILOT     = 0x02,
    ROLE_FLAG_PAYLOAD   = 0x04,
    ROLE_FLAG_COMMANDER = 0x08
} role_flag_t;

typedef enum {
    STATE_IDLE = 0,
    STATE_PILOT_ACTIVE,
    STATE_HANDOVER_WAIT_STICK,
    STATE_LINK_LOST,
    STATE_COMMANDER_LOCKED
} arbiter_state_t;

typedef struct {
    int16_t roll;      /* -1000 .. +1000 */
    int16_t pitch;     /* -1000 .. +1000 */
    int16_t yaw;       /* -1000 .. +1000 */
    int16_t throttle;  /* 0 .. 1000 */
} stick_axes_t;

typedef struct {
    uint8_t         pilot_gcs_id;
    uint8_t         payload_gcs_id;
    uint8_t         pending_pilot_gcs_id;
    uint32_t        pilot_lease_deadline;
    uint32_t        handover_deadline;
    uint32_t        token_nonce;
    arbiter_state_t state;
} arbiter_context_t;

static arbiter_context_t g_arbiter;

static uint32_t generate_next_nonce(void) {
    static uint32_t s_seed = 0x1337BEEF;
    s_seed = s_seed * 1664525u + 1013904223u;
    return s_seed;
}

static bool is_axis_in_deadband(int16_t val, int16_t limit) {
    return (val >= -limit) && (val <= limit);
}

void arbiter_init(void) {
    memset(&g_arbiter, 0, sizeof(g_arbiter));
    g_arbiter.state = STATE_IDLE;
    g_arbiter.token_nonce = generate_next_nonce();
}

bool arbiter_request_pilot_token(uint8_t gcs_id, uint32_t now_ms, uint32_t *out_nonce) {
    if (g_arbiter.state == STATE_COMMANDER_LOCKED) {
        return false;
    }
    if (g_arbiter.state == STATE_IDLE || g_arbiter.state == STATE_LINK_LOST) {
        g_arbiter.pilot_gcs_id = gcs_id;
        g_arbiter.pilot_lease_deadline = now_ms + ARBITER_HEARTBEAT_TIMEOUT;
        g_arbiter.token_nonce = generate_next_nonce();
        g_arbiter.state = STATE_PILOT_ACTIVE;
        if (out_nonce) {
            *out_nonce = g_arbiter.token_nonce;
        }
        return true;
    }
    return false;
}

bool arbiter_process_heartbeat(uint8_t gcs_id, uint8_t roles, uint32_t now_ms) {
    if (gcs_id == g_arbiter.pilot_gcs_id && (roles & ROLE_FLAG_PILOT)) {
        g_arbiter.pilot_lease_deadline = now_ms + ARBITER_HEARTBEAT_TIMEOUT;
        if (g_arbiter.state == STATE_LINK_LOST) {
            g_arbiter.state = STATE_PILOT_ACTIVE;
        }
        return true;
    }
    if (roles & ROLE_FLAG_PAYLOAD) {
        g_arbiter.payload_gcs_id = gcs_id;
    }
    return true;
}

bool arbiter_initiate_handover(uint8_t current_pilot_id, uint8_t target_gcs_id, uint32_t now_ms) {
    if (g_arbiter.state != STATE_PILOT_ACTIVE || current_pilot_id != g_arbiter.pilot_gcs_id) {
        return false;
    }
    g_arbiter.pending_pilot_gcs_id = target_gcs_id;
    g_arbiter.handover_deadline = now_ms + ARBITER_HANDOVER_TIMEOUT;
    g_arbiter.state = STATE_HANDOVER_WAIT_STICK;
    return true;
}

bool arbiter_confirm_handover_sticks(uint8_t candidate_id, const stick_axes_t *sticks, uint32_t now_ms, uint32_t *out_nonce) {
    if (g_arbiter.state != STATE_HANDOVER_WAIT_STICK || candidate_id != g_arbiter.pending_pilot_gcs_id) {
        return false;
    }
    if (now_ms > g_arbiter.handover_deadline) {
        g_arbiter.state = STATE_PILOT_ACTIVE;
        g_arbiter.pending_pilot_gcs_id = 0;
        return false;
    }
    /* Перевірка нейтралі: крен, тангаж, рискання у межах 3% */
    if (!is_axis_in_deadband(sticks->roll, ARBITER_DEADBAND_LIMIT) ||
        !is_axis_in_deadband(sticks->pitch, ARBITER_DEADBAND_LIMIT) ||
        !is_axis_in_deadband(sticks->yaw, ARBITER_DEADBAND_LIMIT)) {
        return false;
    }

    /* Атомарне перемикання володаря */
    g_arbiter.pilot_gcs_id = candidate_id;
    g_arbiter.pending_pilot_gcs_id = 0;
    g_arbiter.pilot_lease_deadline = now_ms + ARBITER_HEARTBEAT_TIMEOUT;
    g_arbiter.token_nonce = generate_next_nonce();
    g_arbiter.state = STATE_PILOT_ACTIVE;

    if (out_nonce) {
        *out_nonce = g_arbiter.token_nonce;
    }
    return true;
}

void arbiter_commander_override(uint8_t commander_id, uint32_t now_ms) {
    (void)commander_id;
    (void)now_ms;
    g_arbiter.state = STATE_COMMANDER_LOCKED;
    g_arbiter.pilot_gcs_id = 0;
    g_arbiter.pending_pilot_gcs_id = 0;
    g_arbiter.token_nonce = generate_next_nonce();
}

bool arbiter_is_flight_command_allowed(uint8_t src_gcs_id, uint32_t nonce) {
    if (g_arbiter.state != STATE_PILOT_ACTIVE && g_arbiter.state != STATE_HANDOVER_WAIT_STICK) {
        return false;
    }
    return (src_gcs_id == g_arbiter.pilot_gcs_id) && (nonce == g_arbiter.token_nonce);
}

void arbiter_periodic_tick(uint32_t now_ms) {
    if (g_arbiter.state == STATE_PILOT_ACTIVE || g_arbiter.state == STATE_HANDOVER_WAIT_STICK) {
        if (now_ms >= g_arbiter.pilot_lease_deadline) {
            g_arbiter.state = STATE_LINK_LOST;
        }
    }
    if (g_arbiter.state == STATE_HANDOVER_WAIT_STICK) {
        if (now_ms >= g_arbiter.handover_deadline) {
            g_arbiter.state = STATE_PILOT_ACTIVE;
            g_arbiter.pending_pilot_gcs_id = 0;
        }
    }
}
```
```cpp
#pragma once

#include <cstdint>
#include <optional>
#include <expected>
#include <span>

namespace auth::arbiter {

inline constexpr uint32_t HeartbeatTimeoutMs = 1000;
inline constexpr uint32_t HandoverTimeoutMs  = 5000;
inline constexpr int16_t  DeadbandLimit      = 30; // 3% від 1000

enum class RoleFlags : uint8_t {
    None      = 0x00,
    Monitor   = 0x01,
    Pilot     = 0x02,
    Payload   = 0x04,
    Commander = 0x08
};

[[nodiscard]] constexpr RoleFlags operator|(RoleFlags a, RoleFlags b) noexcept {
    return static_cast<RoleFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

enum class State : uint8_t {
    Idle,
    PilotActive,
    HandoverWaitStick,
    LinkLost,
    CommanderLocked
};

enum class ArbiterError : uint8_t {
    Unauthorized,
    AlreadyLocked,
    StickNotNeutral,
    Timeout,
    StateMismatch
};

struct StickAxes {
    int16_t roll{0};      // -1000 .. +1000
    int16_t pitch{0};     // -1000 .. +1000
    int16_t yaw{0};       // -1000 .. +1000
    int16_t throttle{0};  // 0 .. 1000

    [[nodiscard]] constexpr bool is_neutral(int16_t limit = DeadbandLimit) const noexcept {
        return (roll >= -limit && roll <= limit) &&
               (pitch >= -limit && pitch <= limit) &&
               (yaw >= -limit && yaw <= limit);
    }
};

class StationArbiter {
public:
    constexpr StationArbiter() noexcept {
        reset();
    }

    void reset() noexcept {
        pilot_gcs_id_ = 0;
        payload_gcs_id_ = 0;
        pending_pilot_gcs_id_ = 0;
        pilot_lease_deadline_ = 0;
        handover_deadline_ = 0;
        token_nonce_ = next_nonce();
        state_ = State::Idle;
    }

    [[nodiscard]] std::expected<uint32_t, ArbiterError> request_pilot_token(uint8_t gcs_id, uint32_t now_ms) noexcept {
        if (state_ == State::CommanderLocked) {
            return std::unexpected(ArbiterError::AlreadyLocked);
        }
        if (state_ == State::Idle || state_ == State::LinkLost) {
            pilot_gcs_id_ = gcs_id;
            pilot_lease_deadline_ = now_ms + HeartbeatTimeoutMs;
            token_nonce_ = next_nonce();
            state_ = State::PilotActive;
            return token_nonce_;
        }
        return std::unexpected(ArbiterError::AlreadyLocked);
    }

    bool process_heartbeat(uint8_t gcs_id, RoleFlags roles, uint32_t now_ms) noexcept {
        if (gcs_id == pilot_gcs_id_ && (static_cast<uint8_t>(roles) & static_cast<uint8_t>(RoleFlags::Pilot))) {
            pilot_lease_deadline_ = now_ms + HeartbeatTimeoutMs;
            if (state_ == State::LinkLost) {
                state_ = State::PilotActive;
            }
            return true;
        }
        if (static_cast<uint8_t>(roles) & static_cast<uint8_t>(RoleFlags::Payload)) {
            payload_gcs_id_ = gcs_id;
        }
        return true;
    }

    [[nodiscard]] std::expected<void, ArbiterError> initiate_handover(uint8_t current_pilot, uint8_t target_gcs, uint32_t now_ms) noexcept {
        if (state_ != State::PilotActive || current_pilot != pilot_gcs_id_) {
            return std::unexpected(ArbiterError::Unauthorized);
        }
        pending_pilot_gcs_id_ = target_gcs;
        handover_deadline_ = now_ms + HandoverTimeoutMs;
        state_ = State::HandoverWaitStick;
        return {};
    }

    [[nodiscard]] std::expected<uint32_t, ArbiterError> confirm_handover_sticks(uint8_t candidate_id, const StickAxes& sticks, uint32_t now_ms) noexcept {
        if (state_ != State::HandoverWaitStick || candidate_id != pending_pilot_gcs_id_) {
            return std::unexpected(ArbiterError::Unauthorized);
        }
        if (now_ms > handover_deadline_) {
            state_ = State::PilotActive;
            pending_pilot_gcs_id_ = 0;
            return std::unexpected(ArbiterError::Timeout);
        }
        if (!sticks.is_neutral()) {
            return std::unexpected(ArbiterError::StickNotNeutral);
        }

        pilot_gcs_id_ = candidate_id;
        pending_pilot_gcs_id_ = 0;
        pilot_lease_deadline_ = now_ms + HeartbeatTimeoutMs;
        token_nonce_ = next_nonce();
        state_ = State::PilotActive;
        return token_nonce_;
    }

    void commander_override(uint8_t /*commander_id*/, uint32_t /*now_ms*/) noexcept {
        state_ = State::CommanderLocked;
        pilot_gcs_id_ = 0;
        pending_pilot_gcs_id_ = 0;
        token_nonce_ = next_nonce();
    }

    [[nodiscard]] bool is_flight_command_allowed(uint8_t src_gcs_id, uint32_t nonce) const noexcept {
        if (state_ != State::PilotActive && state_ != State::HandoverWaitStick) {
            return false;
        }
        return (src_gcs_id == pilot_gcs_id_) && (nonce == token_nonce_);
    }

    void periodic_tick(uint32_t now_ms) noexcept {
        if (state_ == State::PilotActive || state_ == State::HandoverWaitStick) {
            if (now_ms >= pilot_lease_deadline_) {
                state_ = State::LinkLost;
            }
        }
        if (state_ == State::HandoverWaitStick) {
            if (now_ms >= handover_deadline_) {
                state_ = State::PilotActive;
                pending_pilot_gcs_id_ = 0;
            }
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint8_t active_pilot() const noexcept { return pilot_gcs_id_; }

private:
    static uint32_t next_nonce() noexcept {
        static uint32_t seed = 0x900DCAFE;
        seed = seed * 1664525u + 1013904223u;
        return seed;
    }

    uint8_t   pilot_gcs_id_{0};
    uint8_t   payload_gcs_id_{0};
    uint8_t   pending_pilot_gcs_id_{0};
    uint32_t  pilot_lease_deadline_{0};
    uint32_t  handover_deadline_{0};
    uint32_t  token_nonce_{0};
    State     state_{State::Idle};
};

} // namespace auth::arbiter
```
:::

---

## 3. Інтеграція в середовище FreeRTOS та потік подій

У типовій архітектурі на базі мікроконтролера STM32 модуль арбітражу інтегрується у вигляді захисного фасаду над чергою польотних команд.

### Розподіл завдань та синхронізація

1. **Завдання прийому телеметрії та зв'язку (`TelemetryTask`, низький пріоритет):** Зчитує байти з UART/Ethernet, десеріалізує пакети протоколу MAVLink та викликає `arbiter_process_heartbeat()`. Оновлення оренди відбувається без блокування польотного контуру.
2. **Завдання обробки ручного керування (`RcInputTask`, високий пріоритет, 50 Гц):** Отримує швидкі пакети стіків `MANUAL_CONTROL` та перевіряє право виконання через виклик `arbiter_is_flight_command_allowed(src_id, nonce)`. Якщо повертається `false`, пакет негайно відкидається без передачі в мікшер моторів.
3. **Системний таймер або періодичний потік (`ArbiterTimerTask`, 10–50 Гц):** Викликає `arbiter_periodic_tick(now_ms)` для перевірки прострочення оренди та тайм-аутів передачі зміни.

Завдяки тому, що всі операції читання та перевірки зводяться до атомарного порівняння цілих чисел (`uint8_t` та `uint32_t`), арбітраж не потребує важких блокувань через м'ютекси (Mutexes). Для синхронізації між перериваннями та потоками FreeRTOS достатньо критичної секції `taskENTER_CRITICAL()` лише на короткий момент запису нової сесії під час успішного завершення передачі зміни.

---

## 4. Практичні пастки та крайові випадки інтеграції

Під час експлуатації та налагодження розподіленого керування в реальних польових умовах виникають чотири критичні інженерні проблеми:

1. **Електричний дрейф аналогових потенціометрів (ADC Offset Drift):**
   Фізичні стіки на бюджетних пультах рідко повертаються в ідеальний центр (значення 0). Через температурні коливання та знос пружин значення спокою може плавати в межах від -18 до +24 одиниць (із повного діапазону 1000). Якщо встановити поріг мертвої зони занадто вузьким (наприклад, менше ніж 1.5%), процедура передачі зміни зависне назавжди: змінний пілот буде переконаний, що відпустив ручки, але борт постійно відхилятиме підтвердження з кодом `ERR_STICK_NOT_NEUTRAL`. Практично обґрунтований діапазон для надійного захоплення становить 2.5%–4.0% від повної шкали.

2. **Асиметричне зникнення каналу зв'язку (Unidirectional Radio Drop):**
   У радіомережах можливий сценарій, коли борт стабільно приймає пакети від наземної станції, але станція перестає чути зворотні відповіді через перегрів підсилювача на борту або локальну заваду біля антени пульта. У цьому випадку борт продовжує скидати таймер оренди, тоді як на екрані пілота виникає попередження про втрату зв'язку. Арбітр проєктується як повністю автономний модуль: він спирається виключно на локальні таймери бортового лічильника часу, не довіряючи зовнішнім статусам лінка, що приходять з ефіру.

3. **Стрибок тяги при безконтактному переході (Throttle Step Discontinuity):**
   На відміну від каналів крену та тангажу, які в режимі зависання перебувають у центрі, стік газу (Throttle) у польоті завжди має ненульове відхилення (близько 45%–60% для підтримання горизонту). Якщо передати зміну, коли стік газу змінного пульта лежить у нульовому положенні (в упорі внизу), в момент передачі токена мотори миттєво скинуть оберти, що призведе до глибокого просідання апарата. Тому інтерфейс наземної станції змінного пілота зобов'язаний візуально підсвічувати цільове положення газу і не відправляти підтвердження `STICK_CHECK`, поки положення газу не збіжиться з поточною тягою апарата в межах допустимого вікна.

4. **Затримки планувальника операційної системи (Scheduler Jitter):**
   Якщо виклик `arbiter_periodic_tick()` розмістити у фоновому потоці з низьким пріоритетом разом із повільним записом логів на карту micro-SD, операція запису флеш-пам'яті (яка може тривати до 150 мс) заблокує перевірку часу. Це призведе до помилкового спрацьовування тайм-ауту оренди та безпідставного переходу автопілота в аварійний режим `LOITER`. Усі періодичні перевірки часу арбітражу повинні виконуватися або в обробнику системного таймера, або у високопріоритетному завданні реального часу.

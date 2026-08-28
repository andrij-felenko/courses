# ⚙️ Безпечний арбітр ручного керування та обробник MAVLink MANUAL_CONTROL

У системах телекерування безпілотними літальними апаратами, наземними роботизованими комплексами (UGV) та безекіпажними катерами часто виникає потреба підтримувати одночасно два джерела ручних команд. Перше — це прямий апаратний пульт пілота (зв'язок через протоколи CRSF, ExpressLRS або S.BUS). Друге — це маніпулятор або віртуальний джойстик, підключений до робочого місця оператора на наземній станції керування (GCS, англ. *Ground Control Station*), який передає керівні дії через радіомодем у вигляді повідомлень MAVLink `MANUAL_CONTROL` (ідентифікатор #69).

Якщо реалізувати прийом команд від станції спрощено — звичайним копіюванням значень осей у контур стабілізації при надходженні кожного нового кадру, — система стає вразливою до фатальних аварій. Будь-яке зависання програми на ноутбуці, затримка в чергах операційної системи або обрив USB-кабелю призводить до того, що апарат продовжує політ із останнім зафіксованим положенням стіків (наприклад, із максимальним нахилом убік або вперед). 

Нижче наведено архітектуру та повний вихідний код модуля безпечного арбітражу, що забезпечує надійне перемикання джерел, захист від застигання осей, незалежний нагляд за таймінгами та лімітування швидкості наростання сигналу (англ. *slew-rate limiting*).

---

## Архітектурні вимоги та аналіз протоколів

Перед проєктуванням коду необхідно вирішити ключову протокольну дилему: яке саме повідомлення MAVLink використовувати для передачі дій оператора.

В екосистемі MAVLink існують два основні повідомлення для передачі ручних дій:
1. `RC_CHANNELS_OVERRIDE` (ID #70) — історичне повідомлення, яке передає сирі значення мікросекунд сервоприводів (1000–2000 мкс) для кожного каналу окремо, імітуючи класичний PWM/PPM приймач.
2. `MANUAL_CONTROL` (ID #69) — стандартизоване нормалізоване повідомлення, що передає нормовані осі тангажу `x`, крену `y`, тяги `z`, курсу `r` у діапазоні `[-1000 .. 1000]` та бітову маску натиснутих кнопок.

Використання `RC_CHANNELS_OVERRIDE` у сучасних автопілотах (PX4, ArduPilot) вважається застарілим і небезпечним підходом (англ. *anti-pattern*). Воно підміняє апаратні канали на низькому рівні, обходячи внутрішню логіку калібрування експонент і мертвих зон автопілота, а також ускладнює перехоплення керування фізичним пультом. На противагу цьому, `MANUAL_CONTROL` працює на рівні польотних режимів: автопілот сам інтерпретує осі залежно від активного режиму (наприклад, як кут нахилу в режимі `Stabilize` або як вектор швидкості в метрах на секунду в режимі `Position Hold`).

### Чотири правила безпечного арбітражу

Модуль арбітражу на бортовому мікроконтролері реалізує чотири обов'язкові бар'єри захисту:

1. **Безумовний пріоритет фізичного пульта (RC Preemption / Override).** Фізичний пульт у руках пілота безпеки завжди має вищий пріоритет над станцією. Якщо пілот відхиляє будь-який стік за межі мертвої зони (5% від нейтралі), модуль миттєво відключає потік команд від станції та передає керування пульту без затримок і згладжувань.
2. **Дворівнева шкала таймаутів (Watchdog FSM).** Оскільки потік `MANUAL_CONTROL` може затримуватися через завади в ефірі, вводиться два часові пороги:
   - **М'яка деградація (Soft Degrade, 250 мс)**: якщо свіжий пакет не надійшов за 250 мс, кутові команди плавно зводяться до нуля (горизонтальне положення), а тяга фіксується на рівні зависання, запобігаючи неконтрольованому зміщенню.
   - **Аварійний Failsafe (1000 мс)**: якщо зв'язок відсутній понад 1 секунду, система ініціює процедуру аварійного повернення додому (RTL) або автоматичну посадку.
3. **Лімітування швидкості наростання (Slew-Rate Limiting).** Якщо пакети затримуються в операційній системі станції, а потім вистрілюють пачкою, різкий стрибок значень згладжується цифровим інтегратором, щоб захистити мотоустановку та механіку від ударних перевантажень.
4. **Ізоляція від загального серцебиття (Heartbeat Isolation).** Наземна станція відправляє повідомлення `HEARTBEAT` із частотою 1 Гц, а потік керування — 20–50 Гц. Станція може продовжувати слати `HEARTBEAT` при повністю завислому вікні введення джойстика. Тому таймаут арбітра розраховується виключно за мітками часу `MANUAL_CONTROL`.

---

## Виробнича реалізація модуля на C та C++

Нижче наведено повну реалізацію автомата арбітражу. Реалізація мовою C (C99) орієнтована на вбудовані RTOS із статичним виділенням пам'яті, а версія на C++20 використовує строгу типізацію, простори імен, роботу з часом та методи без динамічної алокації (`noexcept`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RC_DEADBAND_NORM            50      // 5% від діапазону [-1000..1000]
#define GCS_TIMEOUT_DEGRADE_MS      250     // Поріг м'якої нейтралізації (мс)
#define GCS_TIMEOUT_FAILSAFE_MS     1000    // Поріг повного аварійного режиму (мс)
#define MAX_AXIS_SLEW_PER_SEC       4000.0f // Максимальна швидкість зміни (одиниць/с)

typedef enum {
    SOURCE_NONE = 0,
    SOURCE_DIRECT_RC,
    SOURCE_GCS_MANUAL
} ControlSource;

typedef enum {
    STATE_DISARMED = 0,
    STATE_RC_ACTIVE,
    STATE_GCS_ACTIVE,
    STATE_GCS_DEGRADED,
    STATE_FAILSAFE
} ArbiterState;

typedef struct {
    int16_t roll;      // [-1000 .. 1000] (крен: позитивний — вправо)
    int16_t pitch;     // [-1000 .. 1000] (тангаж: позитивний — вперед)
    int16_t throttle;  // [0 .. 1000]      (тяга)
    int16_t yaw;       // [-1000 .. 1000] (рискання: позитивний — за годинниковою)
    uint16_t buttons;  // Бітова маска кнопок
} ControlAxes;

typedef struct {
    ArbiterState state;
    ControlAxes current_output;
    ControlAxes raw_rc;
    ControlAxes raw_gcs;
    uint32_t last_rc_time_ms;
    uint32_t last_gcs_time_ms;
    bool rc_link_lost;
} SafeControlArbiter;

static int16_t clamp_int16(int16_t val, int16_t min_v, int16_t max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

static bool is_rc_stick_deflected(const ControlAxes *rc) {
    if (rc->roll < -RC_DEADBAND_NORM || rc->roll > RC_DEADBAND_NORM) return true;
    if (rc->pitch < -RC_DEADBAND_NORM || rc->pitch > RC_DEADBAND_NORM) return true;
    if (rc->yaw < -RC_DEADBAND_NORM || rc->yaw > RC_DEADBAND_NORM) return true;
    // Відхилення газу вище 10% від базового нульового положення
    if (rc->throttle > 100) return true;
    return false;
}

static int16_t apply_slew_rate(int16_t current, int16_t target, float dt_sec) {
    float max_delta = MAX_AXIS_SLEW_PER_SEC * dt_sec;
    float diff = (float)(target - current);
    if (diff > max_delta) return current + (int16_t)max_delta;
    if (diff < -max_delta) return current - (int16_t)max_delta;
    return target;
}

void arbiter_init(SafeControlArbiter *arb) {
    memset(arb, 0, sizeof(SafeControlArbiter));
    arb->state = STATE_DISARMED;
    arb->rc_link_lost = true;
}

void arbiter_feed_direct_rc(SafeControlArbiter *arb, const ControlAxes *rc, uint32_t now_ms) {
    arb->raw_rc = *rc;
    arb->last_rc_time_ms = now_ms;
    arb->rc_link_lost = false;
}

void arbiter_feed_mavlink_manual_control(SafeControlArbiter *arb, 
                                        int16_t x, int16_t y, int16_t z, int16_t r, 
                                        uint16_t buttons, uint32_t now_ms) {
    // MAVLink MANUAL_CONTROL #69: x=pitch, y=roll, z=throttle, r=yaw
    arb->raw_gcs.pitch = clamp_int16(x, -1000, 1000);
    arb->raw_gcs.roll = clamp_int16(y, -1000, 1000);
    arb->raw_gcs.throttle = clamp_int16(z, 0, 1000);
    arb->raw_gcs.yaw = clamp_int16(r, -1000, 1000);
    arb->raw_gcs.buttons = buttons;
    arb->last_gcs_time_ms = now_ms;
}

void arbiter_update(SafeControlArbiter *arb, uint32_t now_ms, float dt_sec) {
    uint32_t gcs_age = now_ms - arb->last_gcs_time_ms;
    uint32_t rc_age = now_ms - arb->last_rc_time_ms;

    if (rc_age > 100) {
        arb->rc_link_lost = true;
    }

    // 1. Апаратний пріоритет прямого пульта
    bool rc_has_control = !arb->rc_link_lost && is_rc_stick_deflected(&arb->raw_rc);

    if (rc_has_control) {
        arb->state = STATE_RC_ACTIVE;
        // Прямий пульт не підлягає штучному slew-rate, щоб зберегти миттєву реакцію
        arb->current_output = arb->raw_rc;
        return;
    }

    // 2. Обробка команд від наземної станції
    if (gcs_age < GCS_TIMEOUT_DEGRADE_MS) {
        arb->state = STATE_GCS_ACTIVE;
        arb->current_output.roll = apply_slew_rate(arb->current_output.roll, arb->raw_gcs.roll, dt_sec);
        arb->current_output.pitch = apply_slew_rate(arb->current_output.pitch, arb->raw_gcs.pitch, dt_sec);
        arb->current_output.yaw = apply_slew_rate(arb->current_output.yaw, arb->raw_gcs.yaw, dt_sec);
        arb->current_output.throttle = apply_slew_rate(arb->current_output.throttle, arb->raw_gcs.throttle, dt_sec);
        arb->current_output.buttons = arb->raw_gcs.buttons;
    } else if (gcs_age < GCS_TIMEOUT_FAILSAFE_MS) {
        // М'яка деградація: нейтралізація кутів, фіксація тяги на рівні зависання (500)
        arb->state = STATE_GCS_DEGRADED;
        arb->current_output.roll = apply_slew_rate(arb->current_output.roll, 0, dt_sec);
        arb->current_output.pitch = apply_slew_rate(arb->current_output.pitch, 0, dt_sec);
        arb->current_output.yaw = apply_slew_rate(arb->current_output.yaw, 0, dt_sec);
        arb->current_output.throttle = apply_slew_rate(arb->current_output.throttle, 500, dt_sec);
    } else {
        // Повний аварійний таймаут
        arb->state = STATE_FAILSAFE;
        arb->current_output.roll = 0;
        arb->current_output.pitch = 0;
        arb->current_output.yaw = 0;
        arb->current_output.throttle = 0;
    }
}
```
```cpp
#include <cstdint>
#include <algorithm>
#include <chrono>
#include <span>

namespace flight_safety {

constexpr int16_t kRcDeadbandNorm = 50;          // 5% deadband
constexpr uint32_t kGcsTimeoutDegradeMs = 250;  // Поріг м'якої деградації
constexpr uint32_t kGcsTimeoutFailsafeMs = 1000;// Поріг аварійного таймауту
constexpr float kMaxAxisSlewPerSec = 4000.0f;   // Одиниць на секунду

enum class ArbiterState : uint8_t {
    Disarmed = 0,
    RcActive,
    GcsActive,
    GcsDegraded,
    Failsafe
};

struct ControlAxes {
    int16_t roll{0};      // [-1000 .. 1000]
    int16_t pitch{0};     // [-1000 .. 1000]
    int16_t throttle{0};  // [0 .. 1000]
    int16_t yaw{0};       // [-1000 .. 1000]
    uint16_t buttons{0};

    [[nodiscard]] constexpr bool isDeflected() const noexcept {
        return (std::abs(roll) > kRcDeadbandNorm) ||
               (std::abs(pitch) > kRcDeadbandNorm) ||
               (std::abs(yaw) > kRcDeadbandNorm) ||
               (throttle > 100);
    }
};

class SafeControlArbiter {
public:
    constexpr SafeControlArbiter() noexcept = default;

    void feedDirectRc(const ControlAxes& rc, uint32_t now_ms) noexcept {
        raw_rc_ = rc;
        last_rc_time_ms_ = now_ms;
        rc_link_lost_ = false;
    }

    void feedMavlinkManualControl(int16_t x, int16_t y, int16_t z, int16_t r, 
                                 uint16_t buttons, uint32_t now_ms) noexcept {
        raw_gcs_.pitch = std::clamp<int16_t>(x, -1000, 1000);
        raw_gcs_.roll = std::clamp<int16_t>(y, -1000, 1000);
        raw_gcs_.throttle = std::clamp<int16_t>(z, 0, 1000);
        raw_gcs_.yaw = std::clamp<int16_t>(r, -1000, 1000);
        raw_gcs_.buttons = buttons;
        last_gcs_time_ms_ = now_ms;
    }

    void update(uint32_t now_ms, float dt_sec) noexcept {
        const uint32_t gcs_age = now_ms - last_gcs_time_ms_;
        const uint32_t rc_age = now_ms - last_rc_time_ms_;

        if (rc_age > 100) {
            rc_link_lost_ = true;
        }

        // 1. Апаратне перехоплення фізичним пультом пілота
        if (!rc_link_lost_ && raw_rc_.isDeflected()) {
            state_ = ArbiterState::RcActive;
            current_output_ = raw_rc_;
            return;
        }

        // 2. Лінійка станів таймауту від станції
        if (gcs_age < kGcsTimeoutDegradeMs) {
            state_ = ArbiterState::GcsActive;
            current_output_.roll = applySlew(current_output_.roll, raw_gcs_.roll, dt_sec);
            current_output_.pitch = applySlew(current_output_.pitch, raw_gcs_.pitch, dt_sec);
            current_output_.yaw = applySlew(current_output_.yaw, raw_gcs_.yaw, dt_sec);
            current_output_.throttle = applySlew(current_output_.throttle, raw_gcs_.throttle, dt_sec);
            current_output_.buttons = raw_gcs_.buttons;
        } else if (gcs_age < kGcsTimeoutFailsafeMs) {
            state_ = ArbiterState::GcsDegraded;
            current_output_.roll = applySlew(current_output_.roll, 0, dt_sec);
            current_output_.pitch = applySlew(current_output_.pitch, 0, dt_sec);
            current_output_.yaw = applySlew(current_output_.yaw, 0, dt_sec);
            current_output_.throttle = applySlew(current_output_.throttle, 500, dt_sec);
        } else {
            state_ = ArbiterState::Failsafe;
            current_output_ = ControlAxes{};
        }
    }

    [[nodiscard]] constexpr ArbiterState state() const noexcept { return state_; }
    [[nodiscard]] constexpr const ControlAxes& output() const noexcept { return current_output_; }

private:
    [[nodiscard]] static int16_t applySlew(int16_t current, int16_t target, float dt_sec) noexcept {
        const float max_delta = kMaxAxisSlewPerSec * dt_sec;
        const float diff = static_cast<float>(target - current);
        if (diff > max_delta) return current + static_cast<int16_t>(max_delta);
        if (diff < -max_delta) return current - static_cast<int16_t>(max_delta);
        return target;
    }

    ArbiterState state_{ArbiterState::Disarmed};
    ControlAxes current_output_{};
    ControlAxes raw_rc_{};
    ControlAxes raw_gcs_{};
    uint32_t last_rc_time_ms_{0};
    uint32_t last_gcs_time_ms_{0};
    bool rc_link_lost_{true};
};

} // namespace flight_safety
```
:::

---

## Розбір крайових випадків та підводних каменів

1. **Одночасне підключення кількох станцій (Multiple GCS Collision).** Якщо на бортовий радіомодем налаштовано маршрутизацію від двох ноутбуків одночасно (наприклад, станція пілота і станція оператора корисного навантаження), обидві станції можуть надсилати `MANUAL_CONTROL`. Автопілот зобов'язаний фільтрувати пакети за полем `target_system` та фіксувати `sender_system_id` першої авторизованої станції, ігноруючи сторонні пакети.
2. **Армінг через GCS проти апаратного тумблера.** При використанні джойстика станції армінг (англ. *Arming* — запуск моторів) через комбінацію стіків (наприклад, лівий стік у правий нижній кут) є небезпечним через можливі затримки пакетів. Надійніше вимагати окрему команду `MAV_CMD_COMPONENT_ARM_DISARM` із підтвердженням від користувача.
3. **Асиметрія частоти виклику `update()` та прийому UART.** Функція `arbiter_update()` повинна викликатися з постійною частотою основного контуру стабілізації (наприклад, 400 Гц у PX4/ArduPilot), незалежно від того, коли саме прийшов черговий пакет по радіолінії. Це гарантує плавний розрахунок швидкості зміни (Slew-Rate) та точний відлік мілісекундних таймаутів.

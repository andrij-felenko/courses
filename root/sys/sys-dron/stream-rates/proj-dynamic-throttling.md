# ⚙️ Практична реалізація динамічного троттлінгу телеметрії

Цей документ містить повнофункціональний алгоритм автоматичного адаптивного регулювання частот потоків MAVLink на базі скінченного автомата станів (State Machine) з часовим гістерезисом та моніторингом вихідного буфера радіомодема.

---

### 1. Постановка інженерної задачі та фізика затору

Під час реальної експлуатації безпілотного авіаційного комплексу параметри радіоканалу безперервно змінюються під впливом зовнішніх факторів:
- **Збільшення дистанції:** Віддалення апарата від наземної антени призводить до затухання напруженості електромагнітного поля за законом обернених квадратів, зменшуючи рівень сигналу RSSI.
- **Просторове затінення антен (Airframe Shadowing):** Під час виконання глибоких віражів, розворотів або маневрів ухилення металеві частини двигунів, карбонові силові елементи крила та масивні акумуляторні батареї перекривають пряму видимість між передавальною та приймальною антенами, спричиняючи раптове падіння сигналу на 15–25 дБ.
- **Багатопроменева інтерференція та локальні радіозавади:** Відбиття хвиль від водної поверхні або міської забудови створює фазові спотворення, що збільшує частоту виникнення бітових помилок (Bit Error Rate, BER).

Коли якість радіолінії погіршується, апаратний трансивер радіомодема (наприклад, SiK Radio або RFD900) змушений витрачати радіослоти на повторні передачі пошкоджених пакетів (*Retransmissions*) або роботу алгоритмів прямого виправлення помилок (*Forward Error Correction, FEC*). У результаті реальна пропускна здатність радіоефіру падає з номінальних 3500 Байт/с до 500–800 Байт/с.

Якщо польотний контролер продовжує генерувати телеметрію з повною номінальною швидкістю (наприклад, 3.5 кБ/с), виникає явище роздування буфера (*Bufferbloat*):
1. **Експоненційне зростання затримки:** Байти телеметрії надходять у серійний порт UART швидше, ніж модем встигає передати їх у радіоефір. Внутрішній циклічний буфер передавача FIFO переповнюється, утворюючи чергу з сотень пакетів. Затримка доставки телеметрії на екран оператора зростає від нормальних 20–40 мілісекунд до катастрофічних 4–8 секунд.
2. **Параліч контуру ручного пілотування:** Оператор бачить положення штучного горизонту із запізненням у кілька секунд. Будь-яка спроба ручного вирівнювання літака за приладами призводить до розгойдування апарата (Pilot-Induced Oscillation, PIO) та аварії.
3. **Хибне спрацьовування аварійних тайм-аутів (Failsafe):** Пакети перевірки зв'язку `HEARTBEAT` застрягають у хвості черги буфера модема. Наземна станція не отримує сигнал «серцебиття» протягом встановленого таймауту (типово 3–5 секунд), оголошує аварійний стан втрати радіозв'язку та ініціює примусове повернення додому.
4. **Блокування критичних команд керування:** Коли оператор бачить нештатну ситуацію і надсилає з землі команду негайного переходу в ручний режим або аварійне вимкнення двигунів, ця команда не може пробитися крізь забитий напівдуплексний радіоефір.

**Інженерне завдання:** Спроєктувати та реалізувати надійний, детермінований контролер частот, який у режимі реального часу аналізує зворотний зв'язок від радіомодема (`RADIO_STATUS` #109) або статистику втрат пакетів і автоматично надсилає автопілоту команди `MAV_CMD_SET_MESSAGE_INTERVAL` (#511), ступінчасто адаптуючи трафік до реальної ємності ефіру.

---

### 2. Архітектура станів та математика фільтрації метрик

Контролер будується за архітектурою скінченного автомата станів (*Finite State Machine, FSM*) із трьома дискретними режимами навантаження:

```
+-------------------------------------------------------------------------------+
|                    Таблиця профілів частот телеметрії                         |
+---------------------+-------------------+-------------------+-----------------+
| Повідомлення        | Режим NORMAL (Гц) | Режим DEGRADED(Гц)|Режим CRITICAL(Гц|
+---------------------+-------------------+-------------------+-----------------+
| ATTITUDE (#30)      | 50 Гц (20 000 мкс)| 15 Гц (66 666 мкс)| 5 Гц(200 000 мкс|
| GLOBAL_POSITION_INT | 10 Гц(100 000 мкс)| 4 Гц (250 000 мкс)| 1 Гц(1000000 мкс|
| VFR_HUD (#74)       | 10 Гц(100 000 мкс)| 2 Гц (500 000 мкс)| 0 Гц (Вимкнено) |
| SYS_STATUS (#1)     | 2 Гц (500 000 мкс)| 1 Гц (1000000 мкс)| 1 Гц(1000000 мкс|
| GPS_RAW_INT (#24)   | 5 Гц (200 000 мкс)| 2 Гц (500 000 мкс)| 1 Гц(1000000 мкс|
| HEARTBEAT (#0)      | 1 Гц (1000000 мкс)| 1 Гц (1000000 мкс)| 1 Гц(1000000 мкс|
+---------------------+-------------------+-------------------+-----------------+
| Орієнтовний потік   | ~3350 Байт/с      | ~1100 Байт/с      | ~350 Байт/с     |
+---------------------+-------------------+-------------------+-----------------+
```

#### Математична модель фільтрації заповнення буфера (EMA Filter)
Миттєве значення заповненості буфера передавача `txbuf`, що надходить у повідомленні `RADIO_STATUS`, піддається дискретним флуктуаціям. Одиночний сплеск трафіку (наприклад, вичитування точки місії) може короткочасно підняти `txbuf` до 70% на кілька десятків мілісекунд, після чого буфер знову спорожніє.

Щоб контролер не реагував на короткочасні безпечні сплески, сире значення піддається цифровій фільтрації за алгоритмом експоненційного ковзного середнього (*Exponential Moving Average, EMA*):

```
txbuf_smooth[k] = α · txbuf_raw[k] + (1 - α) · txbuf_smooth[k-1]
```

Для цілочисельної арифметики мікроконтролерів без апаратного блоку FPU коефіцієнт згладжування обирається у вигляді раціонального дробу `α = 0.3 = 3/10`:
`txbuf_smooth = (txbuf_smooth * 7 + txbuf_raw * 3) / 10`.

Постійна часу такого фільтра становить приблизно 3–4 цикли оновлення `RADIO_STATUS` (близько 1.5–2.0 секунд), що ідеально згладжує короткочасні шуми, але забезпечує швидку реакцію на системний затор.

#### Логіка несиметричного часового гістерезису
Головна загроза стабільності мережі — явище хитання частот (*Flapping / Chattering*). Якщо безпілотник летить на дистанції, де рівень сигналу коливається навколо порогового значення −75 дБм, автомат без захисту почне перемикати режими щосекунди. Це викличе лавину керуючих команд `MAV_CMD_SET_MESSAGE_INTERVAL`, яка остаточно заб'є радіолінію.

Для запобігання цьому автомат реалізує принцип несиметричного гістерезису:
1. **Миттєве погіршення (Fast Downgrade):** Перехід у стан з нижчою частотою (`NORMAL -> DEGRADED` або `DEGRADED -> CRITICAL`) відбувається **негайно** при першому перевищенні порога заповнення буфера (`txbuf_smooth > 60%` або `> 85%`). Безпека польоту вимагає моментального розвантаження черги.
2. **Затримане відновлення (Slow Upgrade):** Повернення до вищих частот дозволяється виключно тоді, коли буфер залишається вільним (`txbuf_smooth < 30%`), а рівень втрат пакетів — низьким (`packet_loss < 5%`) протягом щонайменше **5000 мілісекунд (5 секунд)** безперервно. Будь-який одиничний стрибок заповнення буфера скидає таймер відновлення в нуль.

---

### 3. Програмна реалізація

Нижче наведено повну реалізацію алгоритму адаптивного троттлінгу мовами C (чистий C99 без динамічного виділення пам'яті для вбудованих систем) та C++ (сучасний стандарт C++20 з використанням типізованих переліків, лямбда-функцій та захищених контейнерів `std::span`).

:::tabs
```c
/* telemetry_throttler.h / .c — Регулятор частот MAVLink на базі автомата станів */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAVLINK_MSG_ID_HEARTBEAT           0
#define MAVLINK_MSG_ID_SYS_STATUS          1
#define MAVLINK_MSG_ID_GPS_RAW_INT         24
#define MAVLINK_MSG_ID_ATTITUDE            30
#define MAVLINK_MSG_ID_GLOBAL_POSITION_INT 33
#define MAVLINK_MSG_ID_VFR_HUD             74
#define MAVLINK_MSG_ID_RADIO_STATUS        109

#define MAV_CMD_SET_MESSAGE_INTERVAL       511

typedef enum {
    THROTTLE_STATE_NORMAL = 0,
    THROTTLE_STATE_DEGRADED,
    THROTTLE_STATE_CRITICAL
} TelemetryState;

typedef struct {
    uint32_t msg_id;
    int32_t  interval_us; /* -1 = вимкнено, >0 = період у мкс */
} StreamConfig;

typedef struct {
    TelemetryState current_state;
    uint32_t       last_state_change_ms;
    uint32_t       recovery_timer_ms;
    uint8_t        txbuf_smooth;
    uint8_t        packet_loss_pct;
    bool           pending_apply;
} TelemetryThrottler;

/* Профілі частот для трьох станів */
static const StreamConfig PROFILE_NORMAL[] = {
    {MAVLINK_MSG_ID_ATTITUDE,            20000},   /* 50 Гц */
    {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 100000},  /* 10 Гц */
    {MAVLINK_MSG_ID_VFR_HUD,             100000},  /* 10 Гц */
    {MAVLINK_MSG_ID_GPS_RAW_INT,         200000},  /* 5 Гц  */
    {MAVLINK_MSG_ID_SYS_STATUS,          500000},  /* 2 Гц  */
    {MAVLINK_MSG_ID_HEARTBEAT,           1000000}  /* 1 Гц  */
};

static const StreamConfig PROFILE_DEGRADED[] = {
    {MAVLINK_MSG_ID_ATTITUDE,            66666},   /* 15 Гц */
    {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 250000},  /* 4 Гц  */
    {MAVLINK_MSG_ID_VFR_HUD,             500000},  /* 2 Гц  */
    {MAVLINK_MSG_ID_GPS_RAW_INT,         500000},  /* 2 Гц  */
    {MAVLINK_MSG_ID_SYS_STATUS,          1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_HEARTBEAT,           1000000}  /* 1 Гц  */
};

static const StreamConfig PROFILE_CRITICAL[] = {
    {MAVLINK_MSG_ID_ATTITUDE,            200000},  /* 5 Гц  */
    {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_VFR_HUD,             -1},      /* Вимкнено */
    {MAVLINK_MSG_ID_GPS_RAW_INT,         1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_SYS_STATUS,          1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_HEARTBEAT,           1000000}  /* 1 Гц  */
};

#define STREAMS_COUNT (sizeof(PROFILE_NORMAL) / sizeof(PROFILE_NORMAL[0]))

void telemetry_throttler_init(TelemetryThrottler *th, uint32_t now_ms) {
    th->current_state = THROTTLE_STATE_NORMAL;
    th->last_state_change_ms = now_ms;
    th->recovery_timer_ms = 0;
    th->txbuf_smooth = 0;
    th->packet_loss_pct = 0;
    th->pending_apply = true;
}

/* Зовнішній виклик: відправка MAVLink-команди SET_MESSAGE_INTERVAL */
extern void mavlink_send_set_interval(uint32_t msg_id, int32_t interval_us);

static void apply_profile(const StreamConfig *profile, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        mavlink_send_set_interval(profile[i].msg_id, profile[i].interval_us);
    }
}

void telemetry_throttler_on_radio_status(TelemetryThrottler *th, uint8_t txbuf_pct,
                                        uint8_t rxerrors, uint32_t now_ms) {
    /* Фільтр експоненційного згладжування (EMA) для заповнення буфера */
    th->txbuf_smooth = (uint8_t)((th->txbuf_smooth * 7 + txbuf_pct * 3) / 10);
    th->packet_loss_pct = rxerrors;
}

void telemetry_throttler_update(TelemetryThrottler *th, uint32_t now_ms) {
    TelemetryState next_state = th->current_state;

    /* 1. Перевірка умов негайної деградації (DOWNGRADE) */
    if (th->txbuf_smooth > 85 || th->packet_loss_pct > 35) {
        next_state = THROTTLE_STATE_CRITICAL;
        th->recovery_timer_ms = 0;
    } else if (th->txbuf_smooth > 60 || th->packet_loss_pct > 15) {
        if (th->current_state == THROTTLE_STATE_NORMAL) {
            next_state = THROTTLE_STATE_DEGRADED;
            th->recovery_timer_ms = 0;
        }
    }

    /* 2. Перевірка умов повільного відновлення з гістерезисом (UPGRADE) */
    if (next_state == th->current_state) {
        if (th->current_state == THROTTLE_STATE_CRITICAL) {
            if (th->txbuf_smooth < 50 && th->packet_loss_pct < 10) {
                if (th->recovery_timer_ms == 0) th->recovery_timer_ms = now_ms;
                if (now_ms - th->recovery_timer_ms >= 5000) {
                    next_state = THROTTLE_STATE_DEGRADED;
                    th->recovery_timer_ms = 0;
                }
            } else {
                th->recovery_timer_ms = 0;
            }
        } else if (th->current_state == THROTTLE_STATE_DEGRADED) {
            if (th->txbuf_smooth < 30 && th->packet_loss_pct < 5) {
                if (th->recovery_timer_ms == 0) th->recovery_timer_ms = now_ms;
                if (now_ms - th->recovery_timer_ms >= 5000) {
                    next_state = THROTTLE_STATE_NORMAL;
                    th->recovery_timer_ms = 0;
                }
            } else {
                th->recovery_timer_ms = 0;
            }
        }
    }

    /* 3. Зміна стану та застосування нових частот */
    if (next_state != th->current_state || th->pending_apply) {
        th->current_state = next_state;
        th->last_state_change_ms = now_ms;
        th->pending_apply = false;

        switch (th->current_state) {
            case THROTTLE_STATE_NORMAL:
                apply_profile(PROFILE_NORMAL, STREAMS_COUNT);
                break;
            case THROTTLE_STATE_DEGRADED:
                apply_profile(PROFILE_DEGRADED, STREAMS_COUNT);
                break;
            case THROTTLE_STATE_CRITICAL:
                apply_profile(PROFILE_CRITICAL, STREAMS_COUNT);
                break;
        }
    }
}
```
```cpp
// TelemetryThrottler.hpp — Ідіоматична C++20 реалізація контролера частот
#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <functional>
#include <optional>
#include <span>

namespace mavlink::telemetry {

enum class State : uint8_t {
    Normal = 0,
    Degraded,
    Critical
};

struct StreamSetting {
    uint32_t msg_id{0};
    int32_t  interval_us{-1}; // -1 = вимкнено, >0 = період у мкс
};

class TelemetryThrottler {
public:
    using Milliseconds = std::chrono::milliseconds;
    using SendCallback = std::function<void(uint32_t msg_id, int32_t interval_us)>;

    explicit TelemetryThrottler(SendCallback sender)
        : send_command_(std::move(sender)) {}

    void on_radio_status(uint8_t txbuf_pct, uint8_t packet_loss_pct) noexcept {
        // Експоненційне згладжування заповнення вихідного FIFO модема
        txbuf_smooth_ = static_cast<uint8_t>((txbuf_smooth_ * 7 + txbuf_pct * 3) / 10);
        packet_loss_pct_ = packet_loss_pct;
    }

    void update(Milliseconds now) {
        auto next_state = evaluate_next_state(now);

        if (next_state != current_state_ || force_reapply_) {
            current_state_ = next_state;
            force_reapply_ = false;
            apply_current_profile();
        }
    }

    [[nodiscard]] State current_state() const noexcept { return current_state_; }
    [[nodiscard]] uint8_t smoothed_txbuf() const noexcept { return txbuf_smooth_; }

private:
    static constexpr std::array<StreamSetting, 6> kProfileNormal{{
        {30,   20'000},  // ATTITUDE (50 Гц)
        {33,  100'000},  // GLOBAL_POSITION_INT (10 Гц)
        {74,  100'000},  // VFR_HUD (10 Гц)
        {24,  200'000},  // GPS_RAW_INT (5 Гц)
        {1,   500'000},  // SYS_STATUS (2 Гц)
        {0,  1'000'000}  // HEARTBEAT (1 Гц)
    }};

    static constexpr std::array<StreamSetting, 6> kProfileDegraded{{
        {30,   66'666},  // ATTITUDE (15 Гц)
        {33,  250'000},  // GLOBAL_POSITION_INT (4 Гц)
        {74,  500'000},  // VFR_HUD (2 Гц)
        {24,  500'000},  // GPS_RAW_INT (2 Гц)
        {1,  1'000'000},  // SYS_STATUS (1 Гц)
        {0,  1'000'000}  // HEARTBEAT (1 Гц)
    }};

    static constexpr std::array<StreamSetting, 6> kProfileCritical{{
        {30,   200'000}, // ATTITUDE (5 Гц)
        {33, 1'000'000}, // GLOBAL_POSITION_INT (1 Гц)
        {74,        -1}, // VFR_HUD (Вимкнено)
        {24, 1'000'000}, // GPS_RAW_INT (1 Гц)
        {1,  1'000'000}, // SYS_STATUS (1 Гц)
        {0,  1'000'000}  // HEARTBEAT (1 Гц)
    }};

    State evaluate_next_state(Milliseconds now) noexcept {
        // 1. Аварійний перехід униз (Downgrade без затримки)
        if (txbuf_smooth_ > 85 || packet_loss_pct_ > 35) {
            recovery_start_time_.reset();
            return State::Critical;
        }
        if (txbuf_smooth_ > 60 || packet_loss_pct_ > 15) {
            if (current_state_ == State::Normal) {
                recovery_start_time_.reset();
                return State::Degraded;
            }
        }

        // 2. Ступінчасте відновлення вгору (Upgrade з 5-секундним гістерезисом)
        if (current_state_ == State::Critical && txbuf_smooth_ < 50 && packet_loss_pct_ < 10) {
            return check_recovery(now, State::Degraded);
        }
        if (current_state_ == State::Degraded && txbuf_smooth_ < 30 && packet_loss_pct_ < 5) {
            return check_recovery(now, State::Normal);
        }

        recovery_start_time_.reset();
        return current_state_;
    }

    State check_recovery(Milliseconds now, State target_state) noexcept {
        if (!recovery_start_time_.has_value()) {
            recovery_start_time_ = now;
            return current_state_;
        }
        if (now - *recovery_start_time_ >= std::chrono::seconds(5)) {
            recovery_start_time_.reset();
            return target_state;
        }
        return current_state_;
    }

    void apply_current_profile() {
        std::span<const StreamSetting> profile{};
        switch (current_state_) {
            case State::Normal:   profile = kProfileNormal; break;
            case State::Degraded: profile = kProfileDegraded; break;
            case State::Critical: profile = kProfileCritical; break;
        }

        for (const auto& item : profile) {
            if (send_command_) {
                send_command_(item.msg_id, item.interval_us);
            }
        }
    }

    SendCallback send_command_;
    State current_state_{State::Normal};
    bool force_reapply_{true};
    uint8_t txbuf_smooth_{0};
    uint8_t packet_loss_pct_{0};
    std::optional<Milliseconds> recovery_start_time_{std::nullopt};
};

} // namespace mavlink::telemetry
```
:::

---

### 4. Аналіз інженерних пасток та крайових випадків

Під час практичного впровадження динамічного троттлінгу в реальні системи безпілотників розробники стикаються з низкою підводних каменів:

#### 1. Де розміщувати логіку: на борту чи на землі?
Існує два підходи до розташування модуля адаптивного троттлінгу:
- **Наземна реалізація (Ground-Side Throttling):** Модуль працює всередині програми QGroundControl або власного GCS-сервісу. Станція аналізує якість прийому та надсилає команди `MAV_CMD_SET_MESSAGE_INTERVAL` на борт. Перевага: простота модифікації інтерфейсу та алгоритму. Недолік: якщо радіолінк уже переповнено, сама керуюча команда від станції може застрягти або загубитися в ефірі, не дійшовши до автопілота.
- **Бортова реалізація (Board-Side Autonomous Throttling):** Модуль інтегровано безпосередньо в прошивку польотного контролера (як драйвер `AP_Radio` в ArduPilot або підсистема `mavlink` у PX4). Контролер читає повідомлення `RADIO_STATUS` безпосередньо з локального порту UART і змінює частоти внутрішнього планувальника миттєво, без участі радіоефіру. Це найнадійніший варіант, що гарантує захист буфера за будь-яких обставин.

#### 2. Запобігання шторму квитувань (Command Storm Prevention)
Під час перемикання стану контролер послідовно надсилає 5–6 команд `MAV_CMD_SET_MESSAGE_INTERVAL`. Автопілот на кожну команду відповідає пакетом `COMMAND_ACK` (#77). Щоб ці квитування не створили короткочасного піка трафіку, відправку команд у профілі рекомендується розносити з мікропаузами в 10–20 мілісекунд або використовувати команду пакетної конфігурації.

#### 3. Недоторканність моніторингу зв'язку (Heartbeat Invariant)
Жоден рівень троттлінгу (навіть режим `CRITICAL`) не має права зменшувати частоту повідомлення `HEARTBEAT` (#0) нижче 1 Гц або вимикати його. Зникнення `HEARTBEAT` на 3 секунди розцінюється як повна аварійна відмова каналу зв'язку. Так само повідомлення `SYS_STATUS` (#1) повинно передаватися щонайменше з частотою 1 Гц, щоб оператор безперервно бачив критичний залишок заряду акумулятора.

#### 4. Коректна взаємодія з апаратним керуванням потоком (RTS/CTS Flow Control)
Якщо лінію UART між польотним контролером і радіомодемом обладнано апаратними лініями RTS/CTS, модем автоматично виставляє високий рівень на лінії CTS, коли його внутрішній буфер заповнюється на 80%. Польотний контролер призупиняє передачу байтів на фізичному рівні. Проте без програмного троттлінгу пакети почнуть накопичуватися вже у вихідному буфері самого польотного контролера. Лише спільна робота апаратного RTS/CTS та програмного адаптивного троттлінгу забезпечує повний захист системи від втрати пакетів.

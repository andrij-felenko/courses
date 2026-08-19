# ⚙️ Реалізація FSM переговорів стіка: від Source Capabilities до замикання ключа

У цій практичній вставці розібрано повну, неблокуючу реалізацію скінченного автомата (англ. *finite state machine*, FSM) для підсистеми керування живленням споживача (Sink Policy Engine). Матеріал призначений для інженерів вбудованих систем, які розробляють прошивки для мікроконтролерів (STM32, ESP32, RP2040, Nordic nRF), що керують зовнішніми трансиверами USB PD (наприклад, ON Semi FUSB302, TI TPS65987, STMicro STUSB4500) або використовують вбудовану апаратну периферію UCPD.

---

## 1. Архітектурні вимоги та виклики реалізації

Протокол USB Power Delivery кардинально відрізняється від традиційних опитувальних інтерфейсів на кшталт I2C чи SPI. У шині Type-C події виникають асинхронно: джерело може в будь-який момент надіслати нове повідомлення, змінити напругу або скинути зв'язок.

При побудові прошивки стіка необхідно розв'язати три взаємопов'язані інженерні задачі:

1. **Суворе дотримання протокольних таймаутів:** якщо мікроконтролер затримає відповідь на `Source_Capabilities` понад 100 мс (`tSinkRequest`), джерело зафіксує протокольну помилку і заблокує доступ до підвищених напруг. Якщо після відправлення запиту `Request` відповідь `Accept` не надійде протягом 30 мс (`tSenderResponse`), стік зобов'язаний ініціювати процедуру аварійного скидання `Hard_Reset`. Будь-яке блокування процесорного ядра (наприклад, тривалий цикл `delay_ms()` або очікування готовності Flash-пам'яті) призводить до зриву контракту.
2. **Асинхронна черга повідомлень та робота переривань:** трансивер фізичного рівня (PHY) приймає пакети BMC по лінії CC і виставляє лінію переривання INT мікроконтролера. Апаратний рівень трансивера самостійно формує пакет `GoodCRC` протягом 195 мкс, але обробка корисного навантаження (PDO) та генерація відповіді `Request` покладаються на програмний стек.
3. **Безпечне керування силовим ключем (VBUS Power Gate):** силова частина вимагає надійного взаємного блокування. Поки на шині VBUS триває перехідний процес зміни напруги (від моменту отримання `Accept` до отримання `PS_RDY`), вхідний силовий MOSFET повинен бути гарантовано розімкнений, а власне споживання плати стіка обмежене струмом не більше 500 мА (або потужністю 2.5 Вт). Порушення цього правила викликає просідання напруги на виході джерела, через що блок живлення аварійно вимикається за захистом від перевантаження (OCP).

---

## 2. Граф станів автомата Sink Policy Engine

Політика стіка моделюється як подієво-орієнтований скінченний автомат із чітким розмежуванням обов'язків між станами.

```
                          [ Фізичне підключення CC (Rd) ]
                                         │
                                         ▼
                            ┌─────────────────────────┐
                            │    PE_SNK_DISCOVERY     │
                            └────────────┬────────────┘
                                         │ VBUS = 5 В стабільно
                                         ▼
                            ┌─────────────────────────┐◄────────────────┐
                 ┌─────────►│  PE_SNK_WAIT_FOR_CAP    │                │
                 │          └────────────┬────────────┘                │
                 │                       │ Отримано Source_Caps        │
                 │                       ▼                             │
                 │          ┌─────────────────────────┐                │
                 │          │  PE_SNK_EVALUATE_CAP    │                │
                 │          └────────────┬────────────┘                │
                 │                       │ Обрано найкращий PDO        │
                 │                       ▼                             │
                 │          ┌─────────────────────────┐                │
                 │ Reject / │   PE_SNK_SELECT_CAP     │                │
                 │ Wait     └────────────┬────────────┘                │
                 │                       │ Отримано Accept             │
                 │                       ▼                             │
                 │          ┌─────────────────────────┐                │
                 └──────────┤ PE_SNK_TRANSITION_SINK  │                │
                            └────────────┬────────────┘                │
                                         │ Отримано PS_RDY             │
                                         ▼                             │
                            ┌─────────────────────────┐                │
                            │      PE_SNK_READY       │                │
                            │   (Ключ VBUS замкнено)  │────────────────┘
                            └────────────┬────────────┘ Нові Source_Caps
                                         │ (переузгодження)
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼ Отримано GotoMin                              ▼ Помилка / CRC / Таймаут
    ┌─────────────────────────┐                     ┌─────────────────────────┐
    │     PE_SNK_GIVEBACK     │                     │    PE_SNK_HARD_RESET    │
    │  (струм <= MinCurrent)  │                     │ (VBUS = 0 В, ключ розімкн)│
    └─────────────────────────┘                     └─────────────────────────┘
```

### Детальний опис станів та переходів

* **`PE_SNK_DISCOVERY` (Виявлення та первинний старт):**
  Початковий стан після подачі живлення на мікроконтролер. Стік перевіряє, чи підтягнуті резистори Rd (5.1 кОм) до ліній CC1/CC2, і очікує появи стабільної базової напруги 5 В (`vSafe5V`) від джерела. Силовий ключ навантаження перебуває у вимкненому стані. Щойно виявлено стабільну напругу, автомат переходить у стан очікування можливостей.
* **`PE_SNK_WAIT_FOR_CAP` (Очікування меню джерела):**
  Стік запускає програмний таймер `tTypeCSinkWaitCap` на 620 мс. У цьому стані пристрій є пасивним слухачем. Якщо джерело підтримує протокол USB PD, воно надсилає пакет `Source_Capabilities`. Якщо таймер вичерпано, а пакет не надійшов, це означає, що підключено звичайний зарядний пристрій без підтримки PD (Legacy Type-C). У цьому разі стік залишається на безпечних 5 В, обмежує споживання струму згідно з аналоговими рівнями напруги на лініях CC (500 мА, 1.5 А або 3.0 А) і переходить у стан `PE_SNK_READY`.
* **`PE_SNK_EVALUATE_CAP` (Аналіз можливостей та вибір профілю):**
  Отримавши масив PDO, стік розбирає параметри кожного профілю (тип, напруга, максимальний струм, пікові можливості). Запускається алгоритм розрахунку цільової функції (Fitness Function), який зіставляє пропозиції джерела з поточними потребами системи. Стік формує 32-бітний об'єкт запиту RDO, де зазначає номер обраного PDO, робочий струм, максимальний ліміт та необхідні прапорці.
* **`PE_SNK_SELECT_CAP` (Відправлення запиту та очікування рішення):**
  Пакет `Request` завантажується у FIFO-буфер трансивера і передається по лінії CC. Автомат зводить таймер очікування відповіді `tSenderResponse` (30 мс). Залежно від реакції джерела відбуваються такі переходи:
  * Отримано `Accept` -> перехід до `PE_SNK_TRANSITION_SINK`;
  * Отримано `Reject` -> джерело відмовило (наприклад, через брак сумарної потужності); стік повертається до попереднього діючого контракту або лишається на 5 В;
  * Отримано `Wait` -> джерело тимчасово зайняте балансуванням портів; стік зводить таймер `tSinkWaitCap` (100 мс) і очікує оновленого меню або дозволу на повторний запит.
* **`PE_SNK_TRANSITION_SINK` (Супроводження зміни напруги):**
  Джерело підтвердило запит і розпочало перебудову вихідного імпульсного перетворювача. Напруга на VBUS плавно зростає або спадає з нормованим темпом наростання (slew rate від 30 до 150 мВ/мкс). Стік запускає таймер `tPSTransition` (550 мс) і суворо блокує вмикання силового навантаження.
* **`PE_SNK_READY` (Штатний робочий режим):**
  Надходить пакет `PS_RDY`. Це підтверджує, що напруга досягла цільового значення і зафіксувалася з точністю не гірше ±5%. Контролер видає сигнал `POWER_OK` на драйвер силового ключа, замикаючи MOSFET навантаження. Пристрій переходить до повнофункціональної роботи.
* **`PE_SNK_GIVEBACK` (Динамічне скидання споживання):**
  Якщо контракт було укладено з прапорцем `GiveBack = 1`, джерело у разі перевантаження мережі може надіслати наказ `GotoMin`. Автомат стіка зобов'язаний за час до 35 мс (`tSinkTransition`) знизити споживання до значення `Min_Operating_Current` (наприклад, призупинити заряд акумулятора або знизити яскравість підсвічування), після чого повернутися в стан готовності.
* **`PE_SNK_HARD_RESET` (Аварійне скидання):**
  У разі виникнення непереборних помилок передачі, повторних спотворень CRC або зависання джерела автомат скидає ключ навантаження, формує на CC-лінії спеціальну сигнальну послідовність `Hard Reset` і очікує повного знеструмлення шини VBUS до рівня менше 0.8 В (`vSafe0V`) з наступним перезапуском.

---

## 3. Математична модель вибору профілю (Fitness Scoring)

Для того щоб стік обрав оптимальний профіль серед розмаїття Fixed, Variable, Battery та PPS PDO, застосовується зважена цільова функція ранжування.

Кожен доступний профіль зі списку оцінюється за формулою:

```
Score[i] = W_POWER · (P_avail / P_req)
         + W_MATCH · IsExactMatch(V_pdo, V_target)
         - W_LOSS  · (I_pdo² · R_cable)
```

де:
* `P_avail` — доступна вихідна потужність профілю (`V · I`);
* `P_req` — потужність, необхідна стіку для виконання поточної задачі;
* `IsExactMatch` — бінарна функція, яка повертає `1`, якщо напруга PDO точно дорівнює напрузі внутрішньої проміжної шини пристрою `V_target` (це дає змогу відкрити прохідний ключ і повністю вимкнути внутрішній імпульсний DC-DC перетворювач, зекономивши до 95% втрат перетворення);
* `I_pdo` — струм, який доведеться відбирати від джерела для отримання потрібної потужності;
* `R_cable` — оціночний повний опір кабелю Type-C та контактних переходів (типово 150–250 мОм);
* `W_POWER`, `W_MATCH`, `W_LOSS` — налаштовувані вагові коефіцієнти алгоритму.

Якщо для жодного профілю потужність не досягає мінімально необхідного рівня `P_min_operating`, алгоритм обирає профіль із найбільшою доступною потужністю, але виставляє в результуючому RDO біт `Capability Mismatch = 1`. Це повідомляє джерелу про дефіцит енергії.

---

## 4. Вихідний код реалізації FSM (C та C++)

Нижче наведено модульний вихідний код реалізації автомата стіка мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PDOS 7
#define V_SAFE_MAX_MV 20000
#define V_TARGET_MV   12000
#define I_REQUIRED_MA 2000
#define R_CABLE_MOHM  200

typedef enum {
    PE_SNK_DISCOVERY,
    PE_SNK_WAIT_FOR_CAP,
    PE_SNK_EVALUATE_CAP,
    PE_SNK_SELECT_CAP,
    PE_SNK_TRANSITION_SINK,
    PE_SNK_READY,
    PE_SNK_GIVEBACK,
    PE_SNK_HARD_RESET
} pe_state_t;

typedef enum {
    EV_NONE,
    EV_VBUS_DETECTED,
    EV_SOURCE_CAPS_RECEIVED,
    EV_ACCEPT_RECEIVED,
    EV_REJECT_RECEIVED,
    EV_WAIT_RECEIVED,
    EV_PS_RDY_RECEIVED,
    EV_GOTOMIN_RECEIVED,
    EV_TIMEOUT,
    EV_ERROR
} pe_event_t;

typedef struct {
    uint8_t  position;     // Позиція PDO (1-based: 1..7)
    uint8_t  type;         // 0: Fixed, 1: Variable, 2: Battery, 3: PPS
    uint32_t voltage_mv;
    uint32_t max_current_ma;
    uint32_t max_power_mw;
} pdo_info_t;

typedef struct {
    pe_state_t state;
    uint32_t   timer_ms;
    uint8_t    active_pdo_pos;
    uint32_t   negotiated_mv;
    uint32_t   negotiated_ma;
    bool       gate_closed;
    pdo_info_t source_pdos[MAX_PDOS];
    uint8_t    pdo_count;
} sink_policy_engine_t;

// Декодування сирого 32-бітного слова PDO від джерела
void parse_source_pdo(uint32_t raw_pdo, uint8_t pos, pdo_info_t *out) {
    out->position = pos;
    out->type = (raw_pdo >> 30) & 0x03;
    if (out->type == 0) { // Fixed Supply
        out->voltage_mv = ((raw_pdo >> 10) & 0x3FF) * 50;
        out->max_current_ma = (raw_pdo & 0x3FF) * 10;
        out->max_power_mw = (out->voltage_mv * out->max_current_ma) / 1000;
    } else {
        out->voltage_mv = 5000;
        out->max_current_ma = 500;
        out->max_power_mw = 2500;
    }
}

// Вибір найкращого профілю за багатокритеріальною цільовою функцією
int evaluate_best_pdo(const pdo_info_t *pdos, uint8_t count, uint32_t *req_ma, bool *cap_mismatch) {
    int best_index = -1;
    int32_t best_score = -1000000;

    for (uint8_t i = 0; i < count; i++) {
        if (pdos[i].voltage_mv > V_SAFE_MAX_MV) continue; // Захист чутливої схеми

        int32_t score = 0;
        // 1. Оцінка корисної потужності
        score += (int32_t)(pdos[i].max_power_mw / 100);

        // 2. Бонус за точний збіг напруги (обхід DC-DC)
        if (pdos[i].voltage_mv == V_TARGET_MV) {
            score += 500;
        }

        // 3. Штраф за втрати нагріву в кабелі: I^2 * R
        int32_t cur_a = pdos[i].max_current_ma / 1000;
        int32_t loss_mw = (cur_a * cur_a * R_CABLE_MOHM);
        score -= (loss_mw / 10);

        if (score > best_score) {
            best_score = score;
            best_index = i;
        }
    }

    if (best_index >= 0) {
        uint32_t avail_ma = pdos[best_index].max_current_ma;
        *req_ma = (avail_ma < I_REQUIRED_MA) ? avail_ma : I_REQUIRED_MA;
        *cap_mismatch = (avail_ma < I_REQUIRED_MA);
    }
    return best_index;
}

// Формування бітового 32-бітного слова RDO
uint32_t build_request_rdo(uint8_t obj_pos, uint32_t oper_ma, uint32_t max_ma, bool mismatch, bool giveback) {
    uint32_t rdo = 0;
    rdo |= ((uint32_t)(obj_pos & 0x0F)) << 28;
    if (giveback) rdo |= (1UL << 27);
    if (mismatch) rdo |= (1UL << 26);
    rdo |= (1UL << 25); // USB Communications Capable
    rdo |= (1UL << 24); // No USB Suspend
    rdo |= (((oper_ma / 10) & 0x3FF) << 10);
    rdo |= (((max_ma / 10) & 0x3FF));
    return rdo;
}

// Апаратні заглушки взаємодії з драйвером PHY
extern void phy_send_request(uint32_t rdo);
extern void phy_send_hard_reset(void);
extern void power_gate_set(bool closed);

// Головний крок машини станів стіка
void sink_fsm_step(sink_policy_engine_t *pe, pe_event_t event, uint32_t elapsed_ms) {
    if (pe->timer_ms > elapsed_ms) pe->timer_ms -= elapsed_ms;
    else pe->timer_ms = 0;

    switch (pe->state) {
    case PE_SNK_DISCOVERY:
        pe->gate_closed = false;
        power_gate_set(false);
        if (event == EV_VBUS_DETECTED) {
            pe->state = PE_SNK_WAIT_FOR_CAP;
            pe->timer_ms = 620; // tTypeCSinkWaitCap
        }
        break;

    case PE_SNK_WAIT_FOR_CAP:
        if (event == EV_SOURCE_CAPS_RECEIVED) {
            pe->state = PE_SNK_EVALUATE_CAP;
        } else if (pe->timer_ms == 0) {
            // Джерело без підтримки PD -> залишаємося на 5 В
            pe->negotiated_mv = 5000;
            pe->negotiated_ma = 500;
            pe->gate_closed = true;
            power_gate_set(true);
            pe->state = PE_SNK_READY;
        }
        break;

    case PE_SNK_EVALUATE_CAP: {
        uint32_t req_ma = 0;
        bool mismatch = false;
        int idx = evaluate_best_pdo(pe->source_pdos, pe->pdo_count, &req_ma, &mismatch);
        if (idx >= 0) {
            pe->active_pdo_pos = pe->source_pdos[idx].position;
            pe->negotiated_mv = pe->source_pdos[idx].voltage_mv;
            pe->negotiated_ma = req_ma;
            uint32_t rdo = build_request_rdo(pe->active_pdo_pos, req_ma, pe->source_pdos[idx].max_current_ma, mismatch, false);
            phy_send_request(rdo);
            pe->state = PE_SNK_SELECT_CAP;
            pe->timer_ms = 30; // tSenderResponse
        } else {
            pe->state = PE_SNK_HARD_RESET;
        }
        break;
    }

    case PE_SNK_SELECT_CAP:
        if (event == EV_ACCEPT_RECEIVED) {
            pe->state = PE_SNK_TRANSITION_SINK;
            pe->timer_ms = 550; // tPSTransition
        } else if (event == EV_REJECT_RECEIVED || event == EV_WAIT_RECEIVED || pe->timer_ms == 0) {
            pe->state = PE_SNK_WAIT_FOR_CAP;
            pe->timer_ms = 100; // tSinkWaitCap
        }
        break;

    case PE_SNK_TRANSITION_SINK:
        if (event == EV_PS_RDY_RECEIVED) {
            pe->gate_closed = true;
            power_gate_set(true); // Замикання ключа лише після стабілізації PS_RDY!
            pe->state = PE_SNK_READY;
        } else if (pe->timer_ms == 0) {
            pe->state = PE_SNK_HARD_RESET;
        }
        break;

    case PE_SNK_READY:
        if (event == EV_SOURCE_CAPS_RECEIVED) {
            pe->state = PE_SNK_EVALUATE_CAP; // Гаряче переузгодження
        } else if (event == EV_GOTOMIN_RECEIVED) {
            pe->state = PE_SNK_GIVEBACK;
        }
        break;

    case PE_SNK_GIVEBACK:
        pe->negotiated_ma = 500; // Оперативне зниження навантаження
        pe->state = PE_SNK_READY;
        break;

    case PE_SNK_HARD_RESET:
        pe->gate_closed = false;
        power_gate_set(false);
        phy_send_hard_reset();
        pe->state = PE_SNK_DISCOVERY;
        break;
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace usb_pd {

enum class PdoType : uint8_t {
    Fixed = 0,
    Variable = 1,
    Battery = 2,
    AugmentedPps = 3
};

enum class State : uint8_t {
    Discovery,
    WaitForCap,
    EvaluateCap,
    SelectCap,
    TransitionSink,
    Ready,
    GiveBack,
    HardReset
};

enum class Event : uint8_t {
    None,
    VbusDetected,
    SourceCapsReceived,
    AcceptReceived,
    RejectReceived,
    WaitReceived,
    PsRdyReceived,
    GotoMinReceived,
    Timeout,
    Error
};

struct Pdo {
    uint8_t  position{0};
    PdoType  type{PdoType::Fixed};
    uint32_t voltage_mv{0};
    uint32_t max_current_ma{0};
    uint32_t max_power_mw{0};

    [[nodiscard]] static constexpr Pdo parse(uint32_t raw, uint8_t pos) noexcept {
        Pdo p;
        p.position = pos;
        p.type = static_cast<PdoType>((raw >> 30) & 0x03);
        if (p.type == PdoType::Fixed) {
            p.voltage_mv = ((raw >> 10) & 0x3FF) * 50;
            p.max_current_ma = (raw & 0x3FF) * 10;
            p.max_power_mw = (p.voltage_mv * p.max_current_ma) / 1000;
        } else {
            p.voltage_mv = 5000;
            p.max_current_ma = 500;
            p.max_power_mw = 2500;
        }
        return p;
    }
};

struct RequestData {
    uint8_t  position{1};
    uint32_t operating_current_ma{500};
    uint32_t max_current_ma{500};
    bool     capability_mismatch{false};
    bool     giveback{false};

    [[nodiscard]] constexpr uint32_t to_raw() const noexcept {
        uint32_t rdo = 0;
        rdo |= (static_cast<uint32_t>(position & 0x0F)) << 28;
        if (giveback)            rdo |= (1UL << 27);
        if (capability_mismatch) rdo |= (1UL << 26);
        rdo |= (1UL << 25); // USB Communications Capable
        rdo |= (1UL << 24); // No USB Suspend
        rdo |= (((operating_current_ma / 10) & 0x3FF) << 10);
        rdo |= (((max_current_ma / 10) & 0x3FF));
        return rdo;
    }
};

class PowerGateGuard {
public:
    static void set(bool enabled) noexcept;
};

class SinkPolicyEngine {
public:
    static constexpr uint32_t V_SAFE_MAX_MV = 20000;
    static constexpr uint32_t V_TARGET_MV   = 12000;
    static constexpr uint32_t I_REQUIRED_MA = 2000;
    static constexpr int32_t  R_CABLE_MOHM  = 200;

    SinkPolicyEngine() = default;

    void update(Event event, uint32_t elapsed_ms) noexcept {
        if (timer_ms_ > elapsed_ms) timer_ms_ -= elapsed_ms;
        else timer_ms_ = 0;

        switch (state_) {
        case State::Discovery:
            isolate_load();
            if (event == Event::VbusDetected) {
                state_ = State::WaitForCap;
                timer_ms_ = 620; // tTypeCSinkWaitCap
            }
            break;

        case State::WaitForCap:
            if (event == Event::SourceCapsReceived) {
                state_ = State::EvaluateCap;
            } else if (timer_ms_ == 0) {
                fallback_safe_5v();
            }
            break;

        case State::EvaluateCap: {
            auto req = evaluate_capabilities();
            if (req.has_value()) {
                send_request(*req);
                state_ = State::SelectCap;
                timer_ms_ = 30; // tSenderResponse
            } else {
                state_ = State::HardReset;
            }
            break;
        }

        case State::SelectCap:
            if (event == Event::AcceptReceived) {
                state_ = State::TransitionSink;
                timer_ms_ = 550; // tPSTransition
            } else if (event == Event::RejectReceived || event == Event::WaitReceived || timer_ms_ == 0) {
                state_ = State::WaitForCap;
                timer_ms_ = 100;
            }
            break;

        case State::TransitionSink:
            if (event == Event::PsRdyReceived) {
                engage_load();
                state_ = State::Ready;
            } else if (timer_ms_ == 0) {
                state_ = State::HardReset;
            }
            break;

        case State::Ready:
            if (event == Event::SourceCapsReceived) {
                state_ = State::EvaluateCap; // Реакція на перерозподіл потужності
            } else if (event == Event::GotoMinReceived) {
                negotiated_ma_ = 500;
                state_ = State::GiveBack;
            }
            break;

        case State::GiveBack:
            state_ = State::Ready;
            break;

        case State::HardReset:
            isolate_load();
            execute_hard_reset();
            state_ = State::Discovery;
            break;
        }
    }

    void load_pdos(std::span<const uint32_t> raw_pdos) noexcept {
        pdo_count_ = static_cast<uint8_t>(std::min(raw_pdos.size(), pdos_.size()));
        for (uint8_t i = 0; i < pdo_count_; ++i) {
            pdos_[i] = Pdo::parse(raw_pdos[i], static_cast<uint8_t>(i + 1));
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint32_t active_voltage() const noexcept { return negotiated_mv_; }
    [[nodiscard]] uint32_t active_current() const noexcept { return negotiated_ma_; }

private:
    [[nodiscard]] std::optional<RequestData> evaluate_capabilities() noexcept {
        int best_idx = -1;
        int32_t best_score = -1000000;

        for (uint8_t i = 0; i < pdo_count_; ++i) {
            const auto& p = pdos_[i];
            if (p.voltage_mv > V_SAFE_MAX_MV) continue;

            int32_t score = static_cast<int32_t>(p.max_power_mw / 100);
            if (p.voltage_mv == V_TARGET_MV) score += 500;

            int32_t cur_a = p.max_current_ma / 1000;
            int32_t loss_mw = cur_a * cur_a * R_CABLE_MOHM;
            score -= (loss_mw / 10);

            if (score > best_score) {
                best_score = score;
                best_idx = i;
            }
        }

        if (best_idx < 0) return std::nullopt;

        const auto& chosen = pdos_[best_idx];
        RequestData req;
        req.position = chosen.position;
        req.operating_current_ma = std::min(chosen.max_current_ma, I_REQUIRED_MA);
        req.max_current_ma = chosen.max_current_ma;
        req.capability_mismatch = (chosen.max_current_ma < I_REQUIRED_MA);
        req.giveback = false;

        negotiated_mv_ = chosen.voltage_mv;
        negotiated_ma_ = req.operating_current_ma;
        return req;
    }

    void isolate_load() noexcept {
        gate_closed_ = false;
        PowerGateGuard::set(false);
    }

    void engage_load() noexcept {
        gate_closed_ = true;
        PowerGateGuard::set(true);
    }

    void fallback_safe_5v() noexcept {
        negotiated_mv_ = 5000;
        negotiated_ma_ = 500;
        engage_load();
        state_ = State::Ready;
    }

    void send_request(const RequestData& req) noexcept;
    void execute_hard_reset() noexcept;

    State state_{State::Discovery};
    uint32_t timer_ms_{0};
    uint32_t negotiated_mv_{5000};
    uint32_t negotiated_ma_{500};
    bool gate_closed_{false};
    std::array<Pdo, 7> pdos_{};
    uint8_t pdo_count_{0};
};

} // namespace usb_pd
```
:::

---

## 5. Низькорівнева взаємодія з апаратним трансивером PHY

Для практичного втілення наведеного автомата мікроконтролер зв'язується з трансивером фізичного рівня (наприклад, FUSB302B по шині I2C зі швидкістю 400 кГц або апаратним блоком STM32 UCPD).

Взаємодія будується на таких апаратних кроках:

1. **Ініціалізація та налаштування компараторів:**
   Контролер записує у регістри трансивера конфігурацію ролі Sink: підключає внутрішні підтяжки Rd (5.1 кОм) до обох ліній CC1/CC2, вмикає компаратор автодетекції орієнтації штекера і налаштовує переривання за зміною стану лінії VBUS (регістри `CONTROL0`, `MASK`, `POWER`).
2. **Апаратна обробка GoodCRC:**
   Чип трансивера налаштовується на автоматичну генерацію та передачу пакета `GoodCRC` у відповідь на будь-який коректний вхідний пакет SOP. Це критично, оскільки норматив стандарту вимагає передати `GoodCRC` не пізніше ніж через 195 мкс після закінчення кадру — мікроконтролер через затримки I2C фізично не встиг би зробити це програмно.
3. **Читання FIFO та передача подій в автомат:**
   Коли трансивер приймає повний пакет даних, він виставляє низький рівень на контакті INT. Обробник переривання мікроконтролера вичитує регістр статусу переривань, забирає байти заголовка та корисного навантаження з приймального буфера RX FIFO і формує подію `EV_SOURCE_CAPS_RECEIVED`, передаючи розібраний масив PDO в функцію `sink_fsm_step()`.
4. **Передача сформованого RDO:**
   Функція `phy_send_request()` записує у передавальний буфер TX FIFO трансивера маркери початку пакета (SOP1, SOP2, SOP3), 16-бітний заголовок повідомлення `Request`, 32-бітне слово RDO та маркер кінця пакета EOP. Трансивер автоматично розраховує CRC-32, перетворює байти у послідовність BMC і передає їх у лінію CC, очікуючи від джерела підтвердження `GoodCRC`.

---

## 6. Покроковий розбір реального логу захоплення переговорів

Розглянемо типовий дамп обміну між мережевим зарядним адаптером на 65 Вт та стіком, знятий апаратним декодером ліній CC:

```
[ t = 0.0 мс ]  Фізичне з'єднання: виявлено Rd на CC1, джерело активує Rp.
[ t = 18.4 мс]  VBUS піднято до 5.0 В (vSafe5V). Стік переходить у PE_SNK_WAIT_FOR_CAP.
[ t = 32.1 мс]  Source -> Sink: Data Message [MsgID=0, NumObj=4, Type=Source_Capabilities]
                - PDO 1: Fixed 5.0 В @ 3.0 А (15.0 Вт)  [0x0801912C]
                - PDO 2: Fixed 9.0 В @ 3.0 А (27.0 Вт)  [0x0002D12C]
                - PDO 3: Fixed 15.0 В @ 3.0 А (45.0 Вт) [0x0004B12C]
                - PDO 4: Fixed 20.0 В @ 3.25 А (65.0 Вт)[0x00064145]
[ t = 32.3 мс]  Sink -> Source: Control Message [GoodCRC, MsgID=0]
[ t = 34.0 мс]  Стік (PE_SNK_EVALUATE_CAP): запускає скоринг.
                Цільова напруга системи V_TARGET = 12 В, максимальна безпечна V_SAFE = 20 В.
                Прямого 12 В немає. Обирається PDO 4 (20 В) для мінімізації I^2*R втрат у кабелі.
[ t = 36.2 мс]  Sink -> Source: Data Message [MsgID=0, NumObj=1, Type=Request]
                - RDO: Pos=4, OperI=3.0A, MaxI=3.25A, GiveBack=0 [0x4304B145]
[ t = 36.4 мс]  Source -> Sink: Control Message [GoodCRC, MsgID=0]
[ t = 42.8 мс]  Source -> Sink: Control Message [Accept, MsgID=1]
[ t = 43.0 мс]  Sink -> Source: Control Message [GoodCRC, MsgID=1]
                Стік переходить у PE_SNK_TRANSITION_SINK (силовий ключ OFF).
[ t = 45.0..110.0 мс] Джерело плавно підвищує напругу VBUS: 5.0 В -> 20.0 В (Slew Rate = 0.23 В/мс).
[ t = 118.5 мс] Source -> Sink: Control Message [PS_RDY, MsgID=2]
[ t = 118.7 мс] Sink -> Source: Control Message [GoodCRC, MsgID=2]
[ t = 119.0 мс] Стік (PE_SNK_READY): сигнал POWER_OK активує плавний затвор MOSFET. Навантаження живиться від 20 В.
```

Цей лог наочно демонструє, що від моменту підключення до отримання повного робочого живлення минає менше 120 мс, причому більшу частину цього часу займає фізичне плавне наростання напруги в силовому каскаді джерела.

---

## 7. Програмна калібрація та динамічний моніторинг падіння напруги (Cable Droop)

Опір реальних кабелів Type-C та контактних груп роз'ємів варіюється від 100 мОм для високоякісних сертифікованих кабелів до 400 мОм для дешевих подовжувачів. При струмі 3.0 А на опорі 300 мОм виникає падіння напруги:

```
ΔV = I · R_cable = 3.0 А · 0.300 Ом = 0.90 В
```

Це означає, що при напрузі джерела 5.0 В до входу пристрою дійде лише 4.10 В, що може спричинити спрацьовування захисту від низької напруги (UVLO) внутрішніх регуляторів.

У зрілих прошивках стіка мікроконтролер періодично вимірює напругу на клемах VBUS за допомогою вбудованого АЦП при зміні споживаного струму (ступінчасте навантаження):

1. Контролер фіксує напругу холостого ходу `V_idle` при струмі 100 мА.
2. Контролер фіксує напругу `V_load` при струмі 2.0 А.
3. Розраховується фактичний динамічний опір з'єднання:
   `R_measured = (V_idle - V_load) / (I_load - I_idle)`.

Якщо виявлено надмірний опір `R_measured > 350 мОм`, автомат формує новий запит на перехід до вищої напруги (наприклад, з 5 В @ 3 А на 9 В @ 1.67 А або з 9 В @ 3 А на 20 В @ 1.35 А), що зберігає повну передану потужність 15–27 Вт, але зменшує струм майже вдвічі, знижуючи теплове падіння напруги та розсіювання потужності в дротах у чотири рази.

---

## 8. Апаратна топологія силового комутатора (Power Path) та захист від перенапруг

Керування лінією VBUS вимагає надійного апаратного каскаду. У найпростіших схемах розробники ставлять один P-канальний MOSFET у розрив плюсової шини. Проте такий підхід містить приховану загрозу: внутрішній паразитичний діод MOSFET (Body Diode) орієнтований анодом до навантаження і катодом до роз'єму Type-C. Якщо всередині пристрою є заряджений акумулятор (наприклад, Li-ion батарея з напругою 8.4 В), а кабель підключається до джерела 5 В, струм від батареї почне неконтрольовано витікати назовні через відкритий body-діод у порт USB, що може спалити вихідний каскад джерела.

Для повної гальванічної ізоляції застосовується топологія зустрічно увімкнених транзисторів (Back-to-Back MOSFETs):
* Два N-канальні або P-канальні польові транзистори вмикаються послідовно із зустрічно спрямованими внутрішніми діодами (витоки з'єднані разом, стоки спрямовані до VBUS та навантаження).
* У закритому стані один діод блокує струм від джерела до навантаження, а другий діод блокує зворотний струм від навантаження до роз'єму USB.
* Керування затворами здійснюється від спеціалізованого драйвера ідеального діода або інтегрованого виходу контролера PD, який містить помпу заряду (Charge Pump) для подачі напруги `VBUS + 5 В` на затвори N-MOSFET.

Окрім комутатора, лінії CC та VBUS повинні обов'язково захищатися двоспрямованими TVS-діодами з низькою ємністю (менше 10 пФ для CC, щоб не спотворювати фронти сигналу BMC) та робочою напругою пробою не нижче 24 В. Це захищає тонкі вхідні компаратори мікросхеми від електростатичного розряду (ESD) при гарячому підключенні кабелю.

---

## 9. Розбір крайових випадків та пасток у реальному залізі

### 1. Несподіване переузгодження в режимі READY
Поширена помилка розробників — проектувати автомат так, ніби переговори відбуваються лише один раз під час подачі живлення. У сучасних багатопортових зарядних пристроях на основі GaN потужність динамічно розподіляється між портами. Якщо до зарядки, яка вже живить пристрій потужністю 65 Вт (20 В @ 3.25 А), користувач підключає другий кабель, адаптер негайно надсилає всім активним стікам нове повідомлення `Source_Capabilities` зі зменшеними лімітами струму (наприклад, 45 Вт). Якщо автомат стіка не передбачає переходу зі стану `READY` назад у `EVALUATE_CAP`, контролер проігнорує нове меню, виникне таймаут зв'язку, і джерело аварійно скине напругу VBUS до 0 В.

### 2. Кидок пускового струму (Inrush Current) при замиканні ключа
Коли навантаження містить велику вхідну фільтруючу ємність (понад 100–470 мкФ), миттєве замикання силового MOSFET-ключа після отримання `PS_RDY` еквівалентне короткому замиканню шини. Струм заряду конденсаторів може сягнути 20–40 А протягом перших кількох мікросекунд. Джерело реагує на це спрацьовуванням апаратного компаратора струмового захисту (OCP) і миттєво відсікає VBUS. Щоб уникнути цього, затвор силового MOSFET повинен керуватися драйвером із ланцюгом м'якого пуску (Soft-Start), який плавно нарощує напругу на навантаженні з темпом 1–5 мс.

### 3. Обробка відповіді Wait від зайнятого джерела
Якщо джерело зайняте внутрішніми тепловими перерахунками або плавним розрядом вихідних ємностей, воно відповідає на запит пакетом `Wait`. Стік у жодному разі не повинен спамити повторними пакетами `Request` — це призведе до блокування черги PHY. Необхідно витримати паузу `tSinkWaitCap` (100 мс) і лише після цього повторити запит або дочекатися спонтанного надсилання нового меню від адаптера.

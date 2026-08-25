# ⚙️ Скінченний автомат передзаряду літієвої комірки з таймерами безпеки

Керування зарядом глибоко розрядженої літієвої батареї в мікроконтролерних системах та прошивках BMS (англ. *Battery Management System*) не можна зводити до простого опитування порогів напруги в головному циклі. Стрибки напруги через внутрішній опір комірки, брязкіт навантаження, затримки пробудження схем первинного захисту та ризик замикання вимагають побудови детермінованого скінченного автомата (FSM, англ. *Finite State Machine*) з жорсткими часовими обмеженнями, програмним гістерезисом та фіксацією аварійних станів.

### Архітектура станів та діаграма переходів

Надійний алгоритм попереднього заряду оперує сімома дискретними станами, кожен із яких відповідає фізичному режиму електрохімічного відновлення або аварійної ізоляції комірки:

1. **`STATE_IDLE` (Очікування):** Джерело живлення VBUS відсутнє або напруга нижча за поріг UVLO (англ. *Undervoltage Lockout*). Силові ключі заряду повністю розімкнені, споживання струму схемою мінімальне.
2. **`STATE_TRICKLE` (Краплинне пробудження):** Напруга комірки `U_bat < 1.50 В` (`V_SHORT`). Батарея або перебуває в стані надглибокого розряду, або її плата захисту (Protection IC) розімкнула вихідні MOSFET і тримає клеми під нульовим потенціалом. Зарядник видає надмалий струм пробудження (0.01C–0.02C), щоб живити внутрішній бандгеп чипа захисту та відкрити його зворотні діоди.
3. **`STATE_PRECHARGE` (Передзаряд):** Напруга комірки перебуває в діапазоні `1.50 В ≤ U_bat < 3.00 В` (`V_LOWV`). Струм заряду суворо обмежений безпечним рівнем `0.05C–0.10C`. У момент входу в цей стан запускається апаратний або програмний таймер безпеки `t_PRECHG`.
4. **`STATE_CONSTANT_CURRENT` (Швидкий заряд CC):** Напруга перевищила `3.00 В + V_HYST`. Безпечний діапазон відновлено, таймер передзаряду скидається, силовий перетворювач видає повний струм `0.5C–1.0C`.
5. **`STATE_CONSTANT_VOLTAGE` (Стабілізація напруги CV):** Напруга сягнула цільового порогу 4.20 В. Контролер фіксує напругу, а струм експоненційно спадає.
6. **`STATE_TERMINATION` (Завершення заряду):** Струм у фазі CV впав нижче порогу відсічки `I_TERM` (зазвичай `C/10` або `C/20`). Силові ключі розмикаються, заряд припиняється.
7. **`STATE_FAULT_LATCH` (Аварійне блокування):** Таймер передзаряду вичерпав ліміт часу `t_PRECHG_MAX` (наприклад, 45 хвилин), а напруга так і не перетнула поріг 3.00 В. Контролер фіксує наявність небезпечного внутрішнього короткого замикання або відмови сепаратора, негайно розмикає всі ключі, виставляє прапорець помилки й забороняє повторні спроби заряду до повного зняття живлення VBUS.

### Реалізація скінченного автомата

Нижче наведено робочий модуль контролера передзаряду з повною фільтрацією переходів, захистом від брязкоту напруги та обробкою аварій таймера.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Пороги напруги в мілівольтах (мВ) */
#define VBAT_SHORT_THRESH_MV    1500U  /* Нижче 1.5 В — краплинне пробудження */
#define VBAT_PRECHG_THRESH_MV   3000U  /* Поріг переходу в CC: 3.0 В */
#define VBAT_HYST_MV             100U  /* Гістерезис перемикання: 100 мВ */
#define VBAT_REG_TARGET_MV      4200U  /* Цільова напруга CV: 4.20 В */

/* Ліміти струму в міліамперах (мА) для батареї 2000 мА·год */
#define CURRENT_TRICKLE_MA        30U  /* 0.015C для пробудження */
#define CURRENT_PRECHARGE_MA     150U  /* 0.075C струм передзаряду */
#define CURRENT_FAST_CC_MA      1000U  /* 0.5C струм швидкого заряду */
#define CURRENT_TERM_MA          100U  /* C/20 поріг термінації */

/* Таймери безпеки в мілісекундах */
#define PRECHARGE_TIMEOUT_MS  (45UL * 60UL * 1000UL) /* 45 хвилин максимум */
#define DEBOUNCE_DELAY_MS        200UL               /* Час стабілізації вимірювань */

typedef enum {
    CHARGE_STATE_IDLE = 0,
    CHARGE_STATE_TRICKLE,
    CHARGE_STATE_PRECHARGE,
    CHARGE_STATE_CONSTANT_CURRENT,
    CHARGE_STATE_CONSTANT_VOLTAGE,
    CHARGE_STATE_TERMINATION,
    CHARGE_STATE_FAULT_LATCH
} charge_state_t;

typedef enum {
    FAULT_NONE = 0,
    FAULT_PRECHARGE_TIMEOUT,
    FAULT_OVERVOLTAGE,
    FAULT_OVERTEMPERATURE
} charge_fault_t;

typedef struct {
    charge_state_t state;
    charge_fault_t fault;
    uint32_t state_entry_time_ms;
    uint32_t last_tick_time_ms;
    uint16_t vbat_filtered_mv;
    uint16_t ibat_filtered_ma;
    bool vbus_present;
} charger_fsm_t;

/* Апаратні абстракції керування силовим каскадом */
extern void hw_set_charge_current_limit(uint16_t ma);
extern void hw_set_charge_voltage_limit(uint16_t mv);
extern void hw_enable_charging(bool enable);
extern uint32_t hw_get_system_time_ms(void);

void charger_fsm_init(charger_fsm_t *fsm)
{
    if (!fsm) return;
    fsm->state = CHARGE_STATE_IDLE;
    fsm->fault = FAULT_NONE;
    fsm->state_entry_time_ms = hw_get_system_time_ms();
    fsm->last_tick_time_ms = fsm->state_entry_time_ms;
    fsm->vbat_filtered_mv = 0;
    fsm->ibat_filtered_ma = 0;
    fsm->vbus_present = false;

    hw_enable_charging(false);
    hw_set_charge_current_limit(0);
}

static void charger_transition(charger_fsm_t *fsm, charge_state_t new_state)
{
    fsm->state = new_state;
    fsm->state_entry_time_ms = hw_get_system_time_ms();

    switch (new_state) {
    case CHARGE_STATE_IDLE:
        hw_enable_charging(false);
        hw_set_charge_current_limit(0);
        break;

    case CHARGE_STATE_TRICKLE:
        hw_set_charge_voltage_limit(VBAT_PRECHG_THRESH_MV);
        hw_set_charge_current_limit(CURRENT_TRICKLE_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_PRECHARGE:
        hw_set_charge_voltage_limit(VBAT_PRECHG_THRESH_MV);
        hw_set_charge_current_limit(CURRENT_PRECHARGE_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_CONSTANT_CURRENT:
        hw_set_charge_voltage_limit(VBAT_REG_TARGET_MV);
        hw_set_charge_current_limit(CURRENT_FAST_CC_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_CONSTANT_VOLTAGE:
        /* Регулятор автоматично тримає напругу та знижує струм */
        hw_set_charge_voltage_limit(VBAT_REG_TARGET_MV);
        hw_set_charge_current_limit(CURRENT_FAST_CC_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_TERMINATION:
    case CHARGE_STATE_FAULT_LATCH:
        hw_enable_charging(false);
        hw_set_charge_current_limit(0);
        break;
    }
}

void charger_fsm_process(charger_fsm_t *fsm, uint16_t vbat_raw_mv, uint16_t ibat_raw_ma, bool vbus_ok)
{
    uint32_t now_ms = hw_get_system_time_ms();
    fsm->last_tick_time_ms = now_ms;
    fsm->vbus_present = vbus_ok;

    /* Простий експоненційний фільтр шуму АЦП: alpha = 0.25 */
    fsm->vbat_filtered_mv = (uint16_t)(((uint32_t)fsm->vbat_filtered_mv * 3U + vbat_raw_mv) / 4U);
    fsm->ibat_filtered_ma = (uint16_t)(((uint32_t)fsm->ibat_filtered_ma * 3U + ibat_raw_ma) / 4U);

    /* Аварійне скидання при відключенні кабелю VBUS */
    if (!vbus_ok) {
        if (fsm->state != CHARGE_STATE_IDLE && fsm->state != CHARGE_STATE_FAULT_LATCH) {
            charger_transition(fsm, CHARGE_STATE_IDLE);
        }
        return;
    }

    uint32_t time_in_state_ms = now_ms - fsm->state_entry_time_ms;

    switch (fsm->state) {
    case CHARGE_STATE_IDLE:
        if (fsm->vbat_filtered_mv < VBAT_SHORT_THRESH_MV) {
            charger_transition(fsm, CHARGE_STATE_TRICKLE);
        } else if (fsm->vbat_filtered_mv < VBAT_PRECHG_THRESH_MV) {
            charger_transition(fsm, CHARGE_STATE_PRECHARGE);
        } else if (fsm->vbat_filtered_mv < (VBAT_REG_TARGET_MV - 50U)) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_CURRENT);
        }
        break;

    case CHARGE_STATE_TRICKLE:
        /* Якщо батарея набрала 1.5 В — переходимо до передзаряду */
        if (fsm->vbat_filtered_mv >= VBAT_SHORT_THRESH_MV) {
            charger_transition(fsm, CHARGE_STATE_PRECHARGE);
        }
        break;

    case CHARGE_STATE_PRECHARGE:
        /* Перевірка таймера безпеки: чи не зависла комірка */
        if (time_in_state_ms > PRECHARGE_TIMEOUT_MS) {
            fsm->fault = FAULT_PRECHARGE_TIMEOUT;
            charger_transition(fsm, CHARGE_STATE_FAULT_LATCH);
            return;
        }

        /* Перехід у фазу CC з урахуванням гістерезису для захисту від брязкоту */
        if (fsm->vbat_filtered_mv >= (VBAT_PRECHG_THRESH_MV + VBAT_HYST_MV)) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_CURRENT);
        }
        break;

    case CHARGE_STATE_CONSTANT_CURRENT:
        /* Захисний відкат у передзаряд при раптовому просіданні напруги */
        if (fsm->vbat_filtered_mv < (VBAT_PRECHG_THRESH_MV - VBAT_HYST_MV)) {
            charger_transition(fsm, CHARGE_STATE_PRECHARGE);
            return;
        }

        /* Досягнення напруги стабілізації CV */
        if (fsm->vbat_filtered_mv >= VBAT_REG_TARGET_MV) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_VOLTAGE);
        }
        break;

    case CHARGE_STATE_CONSTANT_VOLTAGE:
        /* Термінація заряду за спаданням струму */
        if (fsm->ibat_filtered_ma < CURRENT_TERM_MA && time_in_state_ms > DEBOUNCE_DELAY_MS) {
            charger_transition(fsm, CHARGE_STATE_TERMINATION);
        }
        break;

    case CHARGE_STATE_TERMINATION:
        /* Автоматичний перезапуск заряду при саморозряді нижче 4.05 В */
        if (fsm->vbat_filtered_mv < (VBAT_REG_TARGET_MV - 150U)) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_CURRENT);
        }
        break;

    case CHARGE_STATE_FAULT_LATCH:
        /* Вихід лише через фізичне відключення та повторне підключення VBUS */
        break;
    }
}
```
```cpp
#include <chrono>
#include <cstdint>
#include <concepts>
#include <expected>
#include <optional>

namespace power {

using namespace std::chrono_literals;

/* Суворо типізовані одиниці вимірювання для запобігання плутанині */
struct Millivolts {
    uint16_t value{0};
    constexpr auto operator<=>(const Millivolts&) const = default;
};

struct Milliamps {
    uint16_t value{0};
    constexpr auto operator<=>(const Milliamps&) const = default;
};

enum class ChargeState : uint8_t {
    Idle = 0,
    Trickle,
    Precharge,
    ConstantCurrent,
    ConstantVoltage,
    Termination,
    FaultLatch
};

enum class ChargeFault : uint8_t {
    None = 0,
    PrechargeTimeout,
    Overvoltage,
    Overtemperature
};

struct ChargerConfig {
    Millivolts vbat_short_thresh{1500};
    Millivolts vbat_prechg_thresh{3000};
    Millivolts vbat_hysteresis{100};
    Millivolts vbat_target{4200};
    Milliamps current_trickle{30};
    Milliamps current_precharge{150};
    Milliamps current_fast_cc{1000};
    Milliamps current_termination{100};
    std::chrono::milliseconds precharge_timeout{45min};
    std::chrono::milliseconds debounce_delay{200ms};
};

/* Апаратний інтерфейс драйвера силового каскаду за принципом RAII */
class IChargerHardware {
public:
    virtual ~IChargerHardware() = default;
    virtual void set_current_limit(Milliamps ma) = 0;
    virtual void set_voltage_limit(Millivolts mv) = 0;
    virtual void enable_power_stage(bool enable) = 0;
    [[nodiscard]] virtual std::chrono::milliseconds get_steady_time() const = 0;
};

class PrechargeFsmController {
public:
    explicit PrechargeFsmController(IChargerHardware& hw, ChargerConfig cfg = {})
        : hw_{hw}, cfg_{cfg}
    {
        hw_.enable_power_stage(false);
        hw_.set_current_limit(Milliamps{0});
    }

    void process(Millivolts vbat_raw, Milliamps ibat_raw, bool vbus_ok)
    {
        const auto now = hw_.get_steady_time();
        vbus_present_ = vbus_ok;

        /* Експоненційне згладжування шумів АЦП */
        vbat_filtered_.value = static_cast<uint16_t>((static_cast<uint32_t>(vbat_filtered_.value) * 3U + vbat_raw.value) / 4U);
        ibat_filtered_.value = static_cast<uint16_t>((static_cast<uint32_t>(ibat_filtered_.value) * 3U + ibat_raw.value) / 4U);

        if (!vbus_ok) {
            if (state_ != ChargeState::Idle && state_ != ChargeState::FaultLatch) {
                transition_to(ChargeState::Idle, now);
            }
            return;
        }

        const auto time_in_state = now - state_entry_time_;

        switch (state_) {
        case ChargeState::Idle:
            if (vbat_filtered_ < cfg_.vbat_short_thresh) {
                transition_to(ChargeState::Trickle, now);
            } else if (vbat_filtered_ < cfg_.vbat_prechg_thresh) {
                transition_to(ChargeState::Precharge, now);
            } else if (vbat_filtered_ < Millivolts{static_cast<uint16_t>(cfg_.vbat_target.value - 50U)}) {
                transition_to(ChargeState::ConstantCurrent, now);
            }
            break;

        case ChargeState::Trickle:
            if (vbat_filtered_ >= cfg_.vbat_short_thresh) {
                transition_to(ChargeState::Precharge, now);
            }
            break;

        case ChargeState::Precharge:
            if (time_in_state > cfg_.precharge_timeout) {
                fault_ = ChargeFault::PrechargeTimeout;
                transition_to(ChargeState::FaultLatch, now);
                return;
            }

            if (vbat_filtered_ >= Millivolts{static_cast<uint16_t>(cfg_.vbat_prechg_thresh.value + cfg_.vbat_hysteresis.value)}) {
                transition_to(ChargeState::ConstantCurrent, now);
            }
            break;

        case ChargeState::ConstantCurrent:
            if (vbat_filtered_ < Millivolts{static_cast<uint16_t>(cfg_.vbat_prechg_thresh.value - cfg_.vbat_hysteresis.value)}) {
                transition_to(ChargeState::Precharge, now);
                return;
            }

            if (vbat_filtered_ >= cfg_.vbat_target) {
                transition_to(ChargeState::ConstantVoltage, now);
            }
            break;

        case ChargeState::ConstantVoltage:
            if (ibat_filtered_ < cfg_.current_termination && time_in_state > cfg_.debounce_delay) {
                transition_to(ChargeState::Termination, now);
            }
            break;

        case ChargeState::Termination:
            if (vbat_filtered_ < Millivolts{static_cast<uint16_t>(cfg_.vbat_target.value - 150U)}) {
                transition_to(ChargeState::ConstantCurrent, now);
            }
            break;

        case ChargeState::FaultLatch:
            /* Блокування скидається тільки апаратним перезапуском VBUS */
            break;
        }
    }

    [[nodiscard]] ChargeState state() const noexcept { return state_; }
    [[nodiscard]] ChargeFault fault() const noexcept { return fault_; }
    [[nodiscard]] Millivolts filtered_voltage() const noexcept { return vbat_filtered_; }

private:
    void transition_to(ChargeState new_state, std::chrono::milliseconds now)
    {
        state_ = new_state;
        state_entry_time_ = now;

        switch (new_state) {
        case ChargeState::Idle:
            hw_.enable_power_stage(false);
            hw_.set_current_limit(Milliamps{0});
            break;

        case ChargeState::Trickle:
            hw_.set_voltage_limit(cfg_.vbat_prechg_thresh);
            hw_.set_current_limit(cfg_.current_trickle);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::Precharge:
            hw_.set_voltage_limit(cfg_.vbat_prechg_thresh);
            hw_.set_current_limit(cfg_.current_precharge);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::ConstantCurrent:
            hw_.set_voltage_limit(cfg_.vbat_target);
            hw_.set_current_limit(cfg_.current_fast_cc);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::ConstantVoltage:
            hw_.set_voltage_limit(cfg_.vbat_target);
            hw_.set_current_limit(cfg_.current_fast_cc);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::Termination:
        case ChargeState::FaultLatch:
            hw_.enable_power_stage(false);
            hw_.set_current_limit(Milliamps{0});
            break;
        }
    }

    IChargerHardware& hw_;
    ChargerConfig cfg_;
    ChargeState state_{ChargeState::Idle};
    ChargeFault fault_{ChargeFault::None};
    std::chrono::milliseconds state_entry_time_{0};
    Millivolts vbat_filtered_{0};
    Milliamps ibat_filtered_{0};
    bool vbus_present_{false};
};

} // namespace power
```
:::

### Інженерні пастки при розробці прошивки передзаряду

Під час практичного впровадження алгоритму передзаряду в реальне вбудоване залізо розробники найчастіше стикаються з чотирма критичними апаратними пастками, які можуть звести нанівець роботу будь-якої системи керування живленням.

#### 1. Омічний стрибок напруги (IR-Drop) та релаксаційний відскок

Внутрішній опір глибоко розрядженої комірки `R_int` (сума омічного опору електроліту `R_ohm` та опору перенесення заряду `R_ct`) значно перевищує номінальний і може сягати 200–500 мОм. Коли контролер вмикає струм передзаряду `I_pre = 150 мА`, напруга на клемах вимірювального вузла миттєво підскакує на величину:

```
ΔU_step = I_pre · (R_int + R_pcb + R_fuse) = 0.15 А · 0.4 Ом = 60 мВ
```

Ще небезпечніша зворотна ситуація: якщо напруга без струму становила 2.95 В, подача струму CC силою 1.0 А викликає стрибок `ΔU = 1.0 · 0.4 = 400 мВ`, і виміряне значення миттєво стає 3.35 В. Якщо контролер спробує вимкнути струм для вимірювання напруги розімкненого ланцюга (OCV), напруга впаде назад до 2.95 В. 

Без належного програмного гістерезису (`VBAT_HYST_MV = 100 мВ`) та експоненційного фільтра АЦП це викликає високочастотний автоколивний брязкіт (англ. *chattering*) між станами `PRECHARGE` та `CONSTANT_CURRENT`, що перегріває силові ключі перетворювача.

#### 2. Пробудження з режиму 0 В та динаміка зворотних діодів

Коли напруга літієвої комірки падає нижче порогу UVLO первинного чипа захисту (наприклад, DW01A або BQ2970, де поріг відсічки становить `2.40–2.80 В`), мікросхема захисту закриває розрядний польовий транзистор. На зовнішніх контактах батарейного блока з'являється плаваючий потенціал близько 0 В, хоча сама електрохімічна банка всередині має, наприклад, 2.20 В.

У такому стані зарядний вузол мікроконтролера бачить `U_bat = 0 В`. Якщо алгоритм одразу спробує виміряти внутрішній імпеданс або подати великий струм, схема захисту не встигне відкрити ключі. 

Послідовність пробудження потребує спеціального поводження:
1. Зарядник видає малий струм пробудження через стан `STATE_TRICKLE`. Струм протікає через вбудований паразитний діод закритого розрядного MOSFET-транзистора.
2. Падіння напруги на діоді та виводі `CS/VM` чипа захисту стає від'ємним відносно мінуса комірки (`V_VM < −0.7 В`).
3. Внутрішній компаратор чипа захисту виявляє підключення зовнішнього зарядного пристрою, активує внутрішню схему накачування заряду (англ. *charge pump*) і подає високу напругу на затвори обох MOSFET, повністю відкриваючи прямий шлях струму.
4. Напруга на зовнішніх клемах миттєво підскакує від нуля до реальної напруги комірки (2.20 В).
5. Скінченний автомат детектує це зростання через умову `vbat_filtered >= VBAT_SHORT_THRESH_MV` і безпечно перемикається у стан керованого передзаряду `STATE_PRECHARGE`.

#### 3. Хибне спрацьовування таймера на багатопаралельних батареях

Якщо пристрій живиться від масивного батарейного блоку ємністю 10000–20000 мА·год (наприклад, конфігурація 1S4P із чотирьох банок 18650), а зарядний чип живиться від стандартного порту USB (5 В, 500 мА), струм передзаряду апаратно обмежено значенням 100–150 мА.

Для батареї ємністю 20 А·год струм 100 мА становить лише `0.005C`. Час виходу з глибокого розряду складе:

```
t_actual = (0.02 · 20 А·год) / 0.10 А = 0.40 А·год / 0.10 А = 4.0 години
```

Якщо в прошивці залишено стандартний таймер безпеки `t_PRECHG_MAX = 45 хвилин`, контролер зафіксує аварію `FAULT_PRECHARGE_TIMEOUT` і заблокує абсолютно справну батарею великої ємності. 

Правильне інженерне рішення полягає в динамічному розрахунку таймера або контролі похідної швидкості росту напруги `dU/dt`: якщо напруга стабільно зростає хоча б на 5–10 мВ за 5 хвилин, це підтверджує відсутність внутрішнього КЗ, і таймер безпеки може бути пропорційно подовжений.

#### 4. Короткочасні провали напруги живлення VBUS

Під час підключення потужного навантаження на лінію SYS вхідна напруга USB може короткочасно просідати нижче порогу UVLO на 10–50 мс. Якщо в обробнику прошивки кожне зникнення VBUS повністю скидає накопичений таймер передзаряду в нуль, зловмисна або зашумлена лінія живлення може нескінченно перезапускати таймер передзаряду на пошкодженій батареї із замкненим сепаратором, нівелюючи весь захисний механізм.

Для запобігання цьому таймер передзаряду повинен зупинятися (пауза) під час коротких збоїв живлення і продовжувати відлік після відновлення VBUS, скидаючись у нуль лише при переході в повноцінний стан `CONSTANT_CURRENT` або після тривалого відключення кабелю (понад 5–10 секунд).

### Керування передзарядом у послідовних збірках (2S–16S) та взаємодія з балансирами

У багатокоміркових акумуляторних батареях (від 2S у портативних терміналах до 16S у легкого електротранспорту та накопичувачів енергії) фаза передзаряду набуває додаткової складності, оскільки окремі комірки з'єднані послідовно через один спільний силовий контур струму.

Якщо в батарейному блоці 4S (номінальна напруга 14.8 В) три комірки перебувають у нормальному стані (`U_1 = U_2 = U_3 = 3.20 В`), а одна комірка через підвищений локальний саморозряд або деградацію просіла до `U_4 = 1.80 В`, загальна напруга на клемах батареї становить:

```
U_pack = 3.20 + 3.20 + 3.20 + 1.80 = 11.40 В
```

Якщо зарядний пристрій вимірює лише сумарну напругу збірки `U_pack`, він сприйме значення 11.40 В як цілком безпечний рівень (понад 2.85 В у середньому на комірку) і подасть у ланцюг повний швидкий струм `1.0C` (наприклад, 4.0 А для акумулятора 4000 мА·год). 

Наслідки для слабкої комірки `U_4` будуть катастрофічними:
1. Струм 4.0 А для комірки з напругою 1.80 В викликає миттєвий сплеск перенапруги, масивний ріст мідних дендритів крізь сепаратор та ризик внутрішнього пробою.
2. Внутрішній опір комірки `U_4` при 1.80 В у кілька разів вищий за опір сусідів (`R_int4 ≈ 150 мОм` проти `30 мОм`), що призводить до локального тепловиділення `P = I² · R = 4² · 0.15 = 2.4 Вт` безпосередньо всередині однієї банки в закритому корпусі.

Тому в прошивках BMS із моніторингом окремих комірок через аналоговий фронтенд (AFE, англ. *Analog Front-End*, наприклад мікросхеми класу BQ76952, LTC6813 або ISL94202) скінченний автомат передзаряду застосовує правило **«найслабшої ланки» (англ. *Weakest-Cell Policy*)**:

```
U_cell_min = min(U_cell_1, U_cell_2, ..., U_cell_N)
```

Режим заряду всього батарейного блока визначається виключно значенням `U_cell_min`:
- Якщо хоча б одна комірка має `U_cell_min < 1.50 В`, уся батарея заряджається в режимі `STATE_TRICKLE`.
- Якщо `1.50 В ≤ U_cell_min < 3.00 В`, струм усієї послідовної гілки апаратно примусово обмежується значенням `I_PRECHARGE` (0.05C–0.10C), навіть якщо решта комірок готові приймати максимальний струм.
- Лише після того, як напруга найслабшої комірки надійно перетне поріг `3.00 В + V_HYST`, автомат переводить силове реле або ключі BMS у повнострумовий режим `STATE_CONSTANT_CURRENT`.

Під час передзаряду пасивні балансири (англ. *passive bleed resistors*) мають бути повністю **вимкнені**: шунтувальні резистори розраховані на струми 50–200 мА, і їхнє включення на сусідніх комірках під час дії слабкого струму передзаряду лише марно спалить енергію та викличе спотворення вимірювань напруги на виводах AFE.

### Регістрове керування автономними зарядними контролерами

У більшості сучасних пристроїв мікроконтролер не керує ШІМ-ключами безпосередньо, а налаштовує параметри передзаряду через цифрову шину I2C у спеціалізованому автономному зарядному контролері (наприклад, сімейства BQ2419x, BQ2589x або MP2650).

Типова карта регістрів автономного зарядного чипа містить такі ключові бітові поля для конфігурації фази передзаряду:

1. **`VPRECHG[1:0]` (Регістр напруги передзаряду):** Задає поріг `V_LOWV` між фазою передзаряду та швидким зарядом CC. Типові опції вибору: `2.8 В`, `3.0 В` (за замовчуванням) або `3.2 В`.
2. **`IPRECHG[3:0]` (Регістр струму передзаряду):** Задає абсолютне значення струму у фазі передзаряду з кроком 64 мА або 128 мА (наприклад, від 64 мА до 1024 мА).
3. **`CHG_TIMER[1:0]` та `EN_TIMER` (Конфігурація таймера безпеки):** Вмикає апаратний сторожовий таймер передзаряду та дозволяє встановити максимальний час: `20 хвилин`, `45 хвилин` або `60 хвилин`.
4. **`CHRG_STAT[1:0]` (Регістр поточного статусу):** Біти зворотного зв'язку, які читає мікроконтролер:
   - `00` — Заряд не активний (Not Charging / Idle);
   - `01` — Виконується попередній заряд (Pre-charge);
   - `10` — Швидкий заряд (Fast Charging CC/CV);
   - `11` — Заряд завершено (Charge Termination Done).
5. **`FAULT_STAT` та вивід переривання `/INT`:** Якщо таймер передзаряду вичерпується, чип скидає біти заряду, встановлює біт `PRECHG_FAULT` у регістрі аварій, притягує лінію `/INT` до землі та надсилає апаратне переривання на процесор пристрою.

Прошивка мікроконтролера в обробнику переривання I2C зчитує регістри статусу та негайно фіксує помилку в енергонезалежній пам'яті (EEPROM/Flash), запобігаючи подальшим спробам старту без діагностики.

### Покрокове трасування роботи FSM у трьох типових сценаріях

Щоб наочно проілюструвати логіку взаємодії всіх елементів автомата, розгляньмо покрокове проходження алгоритму під час виникнення реальних експлуатаційних ситуацій.

#### Сценарій 1: Успішне відновлення перерозрядженої батареї
1. **t = 0 с:** Пристрій підключають до USB (5.0 В). Напруга акумулятора `U_bat = 1.80 В`. Стан переходить із `STATE_IDLE` у `STATE_PRECHARGE`.
2. **t = 1 с:** Силовий каскад обмежує струм на рівні `I_pre = 150 мА`. Запускається таймер `t_entry = 1000 мс`.
3. **t = 15 хв (900 с):** Напруга плавно зростає за рахунок інтеркаляції іонів і досягає `U_bat = 2.98 В`. Автомат залишається в `STATE_PRECHARGE`.
4. **t = 16 хв (960 с):** Напруга перевищує `3.00 В + 0.10 В = 3.10 В` (з урахуванням гістерезису).
5. **t = 961 с:** Автомат фіксує безпечний вихід, перемикається в `STATE_CONSTANT_CURRENT`, піднімає струм до `1000 мА`, таймер безпеки скидається.

#### Сценарій 2: Аварійне виявлення внутрішнього короткого замикання (Fault Latch)
1. **t = 0 с:** Підключення USB до акумулятора з пошкодженим сепаратором (`U_bat = 1.60 В`, внутрішній шунт `R_leak = 10 Ом`).
2. **t = 1 с:** Автомат переходить у `STATE_PRECHARGE` (`I_pre = 150 мА`).
3. **t = 10 хв:** Струм 150 мА витікає через шунт `10 Ом`, напруга застрягає на рівні `U_bat = 1.50 В` і більше не росте (`dU/dt = 0`).
4. **t = 45 хв (2700 с):** Час у стані досягає `PRECHARGE_TIMEOUT_MS`.
5. **t = 2701 с:** Автомат генерує аварійну подію `FAULT_PRECHARGE_TIMEOUT`, перемикається у `STATE_FAULT_LATCH`, повністю розмикає силове живлення і вмикає червоний аварійний світлодіод на панелі приладу. Батарею врятовано від займання.

#### Сценарій 3: Брязкіт контакту кабелю живлення (VBUS Glitch)
1. **t = 0 с:** Виконується передзаряд у стані `STATE_PRECHARGE`, таймер нарахував 20 хвилин (1200 с).
2. **t = 1201 с:** Користувач зачіпає розхитаний роз'єм USB, напруга VBUS зникає на 40 мс і відновлюється.
3. **t = 1201.04 с:** Прошивка через фільтр відсікає короткочасну втрату живлення без скидання таймера передзаряду, продовжуючи відлік із позначки 1200 с. Відновлення батареї триває в штатному захищеному режимі.

### Інтеграція профілю JEITA та температурної корекції

У промислових виробах фаза передзаряду обов'язково зв'язується з показниками давача температури акумулятора (NTC-термістора) згідно з міжнародним стандартом JEITA (англ. *Japan Electronics and Information Technology Industries Association*).

Літій-іонні комірки мають фундаментальну фізичну заборону на заряджання при від'ємних температурах (нижче 0 °C): рухливість іонів літію у твердій фазі графіту падає на два порядки, і будь-який струм заряду викликає миттєве осадження металічного літію (англ. *lithium plating*) на поверхні анода замість його інтеркаляції.

Скінченний автомат передзаряду модифікує свої ліміти струму залежно від температурних зон:

```
Зона T < 0 °C (Freeze):
    Заряд повністю ЗАБОРОНЕНО (струм 0 мА, блокування силового каскаду).

Зона 0 °C ≤ T < 10 °C (Cold Precharge):
    Струм передзаряду знижується вдвічі: I_pre_cold = 0.025C–0.05C.
    Поріг виходу у швидкий заряд CC зміщується вгору до 3.10 В.

Зона 10 °C ≤ T < 45 °C (Standard):
    Штатний передзаряд струмом I_pre = 0.05C–0.10C.

Зона 45 °C ≤ T < 60 °C (Hot):
    Струм передзаряду обмежується, цільова напруга заряду знижується до 4.05–4.10 В.

Зона T ≥ 60 °C (Overheat):
    Заряд негайно зупиняється через ризик теплового розгону.
```

### Діагностичне логування та оцінка стану здоров'я (SoH) після передзаряду

Фаза попереднього заряду є унікальним діагностичним вікном для прошивки BMS: саме під час повільного відновлення з глибокого розряду можна отримати достовірні дані про ступінь незворотної деградації комірки.

Контролер фіксує два критичні параметри:
1. **Швидкість наростання напруги `dV/dt` у зоні 2.0–2.8 В:** Здорова комірка демонструє стабільний кулонівський приріст напруги. Якщо ж напруга росте занадто повільно при номінальному струмі передзаряду, це свідчить про високий внутрішній струм саморозряду або паразитні хімічні реакції розкладу електроліту.
2. **Омічний відгук на імпульс перемикання:** У момент переходу від струму передзаряду (150 мА) до повного струму CC (1000 мА) прошивка вимірює стрибок напруги `ΔU_step`. Обчислений динамічний внутрішній опір `R_int = ΔU_step / ΔI` записується в журнал діагностики.

Якщо після завершення передзаряду внутрішній опір комірки перевищує початкове заводське значення у 2.5–3 рази, BMS позначає батарею як деградовану (зниження State of Health) та виставляє користувачеві попередження про необхідність сервісної заміни акумулятора до виникнення аварійних ситуацій.



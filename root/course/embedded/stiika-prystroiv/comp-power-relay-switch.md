# 🔌 Комутатор живлення тестового слота: реле, P-MOSFET та захист від напівпровідникових пасток

Тестова стійка не може покладатися на програмне перезавантаження чи кнопку Reset: єдиний спосіб гарантувати чистий початковий стан плати — фізично розірвати й знову подати живлення на шину VCC. Проте в автоматизованому стенді звичайний механічний тумблер замінюється керованим електронним ключем. Якщо обрати цей комутатор легковажно, стійка зіткнеться з двома апаратними бідами: зварюванням контактів через пусковий струм і паразитним живленням знеструмленого мікроконтролера через сигнальні лінії. У цьому компонентному розборі ми розглянемо схемотехніку надійного комутатора живлення для тестового слота, порівняємо типи ключів та виведемо схему захисту від зворотного підживлення.

## Електромеханічне реле проти твердотільного SSR та P-MOSFET

Для комутації живлення напругою 3.3 В, 5 В або 12 В у тестових стендах застосовують три основні класи комутаторів. Кожен із них має власну ціну, ресурс і фізичні обмеження.

### 1. Електромеханічні реле (EMR)
Електромеханічне реле фізично розмикає металеві контакти в повітряному або азотному проміжку.
- **Переваги:** Справжня гальванічна ізоляція, опір у розімкненому стані практично нескінченний (R_OFF понад 10 ГОм), нульовий струм витоку, низький опір контактів у замкненому стані (R_ON менше 50 мОм), стійкість до короткочасних імпульсних перенапруг.
- **Недоліки:** Механічний знос контактів (типовий ресурс — від 100 000 до 1 000 000 спрацьовувань під навантаженням). Деренчання контактів (contact bounce) тривалістю 1–5 мс при кожному замиканні. Індуктивний викид обмотки керування при вимкненні, що вимагає зворотного діода (flyback diode). Головна загроза — мікроіскріння й зварювання контактів при розряді вхідних ємностей плати, якщо струм не обмежено.

### 2. Твердотільні реле (SSR / PhotoMOS)
PhotoMOS-реле використовують світлодіод для керування двома зустрічно включеними MOSFET-транзисторами через оптичний ізолятор.
- **Переваги:** Повна безшумність, відсутність механічного зносу (ресурс практично необмежений), повна гальванічна ізоляція керувального кола від силового, відсутність контактного деренчання.
- **Недоліки:** Помітний опір у відкритому стані (R_ON від 0.2 до 2 Ом для компактних моделей), що спричиняє падіння напруги на сотні мілівольтів при струмах у сотні міліампер. Наявність невеликого струму витоку в закритому стані (десятки наноампер або одиниці мікроампер).

### 3. Дискретний P-канальний MOSFET (High-Side Switch)
Найпопулярніше та найгнучкіше рішення для автоматизованих стійок, де немає вимоги високовольтної гальванічної розв'язки, але критичні швидкість, опір і плавне керування.
- **Переваги:** Вкрай низький R_DS(on) (від 10 до 30 мОм), нульовий механічний знос, легкість інтеграції схеми плавного наростання напруги (Soft-Start) через керування затвором, мінімальна площа на платі та низька вартість.
- **Недоліки:** Відсутність гальванічної ізоляції між землею комутатора та землею плати (спільний GND), чутливість затвора до електростатичних розрядів, вимога захисного діода від зворотного струму через внутрішній паразитний діод боді-діода (body diode) польового транзистора.

```
Параметри порівняння ключів для тестового слота (струм навантаження 0–2 А):

+--------------------------+---------------------+-------------------+---------------------+
| Параметр                 | Електромеханічне    | PhotoMOS (SSR)    | Дискретний P-MOSFET |
+--------------------------+---------------------+-------------------+---------------------+
| Опір увімкненого R_ON    | < 0.05 Ом           | 0.3 – 1.5 Ом      | 0.015 – 0.04 Ом     |
| Струм витоку I_OFF       | < 1 пА (ідеальний)  | 10 нА – 1 мкА     | 10 нА – 100 нА      |
| Механічний ресурс        | ~500 000 циклів     | Необмежений       | Необмежений         |
| Деренчання контактів     | 1 – 5 мс            | Відсутнє          | Відсутнє            |
| Можливість Soft-Start    | Немає (зовнішня)    | Обмежена          | Ідеальна (RC-ланка) |
| Гальванічна розв'язка    | Так (кілька кВ)     | Так (1.5–5 кВ)    | Ні (спільна земля)  |
+--------------------------+---------------------+-------------------+---------------------+
```

---

## Схемотехніка силового вузла з регульованим Soft-Start

Коли звичайне реле подає напругу на плату з сумарною вхідною ємністю C_IN = 100 мкФ, швидкість наростання напруги обмежена лише паразитним опором дротів (R_wire близько 0.1 Ом). Стрибок струму досягає:

```
I_inrush = V_IN / R_wire = 5 В / 0.1 Ом = 50 А
```

Цей 50-амперний імпульс тривалістю кілька мікросекунд просаджує загальну шину стенда, скидаючи сусідні плати, і поступово руйнує контакти комутатора.

Щоб усунути пусковий струм, затвор P-MOSFET комутується через RC-ланцюг, що перетворює транзистор на кероване джерело струму на час відкриття.

```
Схема P-MOSFET комутатора з керованим часом наростання (Soft-Start):

       V_MAIN (+5V / +12V) ───┬───────────────────────────────┐
                              │                               │ (Source)
                             [R1] 100k                        │
                              │                         ┌─────┴─────┐
       GPIO_EN ──[R3 1k]──┬───┴───────────┐             │  P-MOSFET │
                          │               │             │  AO3401A  │
                         [N-FET]         [C1] 100nF     └─────┬─────┘
                        (2N7002)          │ (Gate)            │ (Drain)
                          │               ├───────────────────┘
                          │              [R2] 10k
                          │               │
                         GND             GND
                                                              │
                                                        ┌─────┴─────┐
                                                        │  Шунт R_S │ (0.05 Ом)
                                                        │  INA219   │─── I2C
                                                        └─────┬─────┘
                                                              │
                                                        VCC_DUT (До плати)
                                                              │
                                                            [TVS] SMAJ5.0A
                                                              │
                                                             GND
```

### Принцип роботи каскаду:
1. **Закритий стан:** Сигнал `GPIO_EN` низький (0 В). Транзистор N-FET закритий. Резистор R1 (100 кОм) підтягує затвор P-MOSFET до напруги джерела V_MAIN. Різниця напруг V_GS = 0 В, P-MOSFET надійно закритий, живлення на DUT не надходить.
2. **Плавне відкриття (Soft-Start):** Сигнал `GPIO_EN` стає високим (3.3 В). Транзистор N-FET відкривається і починає розряджати затвор P-MOSFET на землю через дільник R1, R2 та конденсатор C1.
3. Швидкість зміни напруги на затворі dV_G/dt обмежена постійною часу tau = (R1 || R2) * C1, що приблизно дорівнює 9.1 кОм * 100 нФ = 0.91 мс.
4. Напруга на виході VCC_DUT плавно наростає за час t_rise приблизно 3–5 мс. За цей час вхідна ємність 100 мкФ заряджається постійним помірним струмом:

```
I_charge = C_IN * (dV / dt) = 100 мкФ * (5 В / 4 мс) = 0.125 А = 125 мА
```

Замість руйнівного піку в 50 А комутатор споживає безпечні 125 мА.

---

## Захист від паразитного підживлення (Phantom Powering)

Найпідступніший дефект під час тестування — коли живлення на слоті розімкнено, але мікроконтролер продовжує працювати або зависає в нескинутому стані. Причина — захисні діоди ESD (Electrostatic Discharge), вбудовані в кожен GPIO чипа.

Якщо до знеструмленого DUT під'єднано перетворювач USB-UART або програматор SWD, на лініях `UART_TX`, `SWDIO` або `SWCLK` залишається логічна одиниця (3.3 В). Струм тече через внутрішній верхній захисний діод мікроконтролера в його внутрішню шину живлення V_DD.

### Апаратні засоби розв'язки ліній:
1. **Буфери з функцією Partial Power Down (I_off):**
   Використання мікросхем логічних буферів серії LVC/AUP (наприклад, `SN74LVC1T45` або `74LVC244A`). Ці мікросхеми підтримують характеристику I_off не більше 1 мкА: коли напруга на боці DUT падає до 0 В, виходи буфера переходять у високоімпедансний стан (Hi-Z), перекриваючи зворотний струм.
2. **Цифрові ізолятори з контролем живлення:**
   Ємнісні або магнітні ізолятори (наприклад, `ISO7721` або `ADuM1201`). При знятті живлення з боку V_DD2 виходи на боці DUT знеструмлюються повністю.
3. **Програмний Hi-Z на боці хоста:**
   Перед зняттям живлення зі слота демон керування стійкою зобов'язаний програмно перевести лінії програматора SWD та UART TX у стан входу без підтяжки (Floating Input) або відпустити лінії через драйвер USB-моста.

---

## Програмний драйвер комутатора живлення

Нижче наведено зразок вбудованого драйвера керування силовим слотом на базі мікросхеми розширювача портів PCA9535 / PCA9555 та вимірювача струму INA219. Драйвер контролює послідовність подачі живлення, перевіряє відсутність короткого замикання та стежить за струмом під час холодного рестарту.

:::tabs
```c
// Драйвер комутатора живлення слота стенда (C99)
#include <stdint.h>
#include <stdbool.h>

#define SLOT_MAX_INRUSH_CURRENT_MA  1500U
#define SLOT_STEADY_CURRENT_LIMIT_MA 800U
#define SOFT_START_SETTLE_MS         20U

typedef enum {
    SLOT_PWR_OFF = 0,
    SLOT_PWR_SOFT_START,
    SLOT_PWR_ACTIVE,
    SLOT_PWR_OVERCURRENT_FAULT,
    SLOT_PWR_PARASITIC_LEAK_FAULT
} slot_pwr_state_t;

typedef struct {
    uint8_t slot_id;
    uint8_t i2c_addr_io;
    uint8_t i2c_addr_ina;
    slot_pwr_state_t state;
    uint16_t last_current_ma;
    uint16_t last_voltage_mv;
} slot_switch_t;

// Апаратні заглушки взаємодії з I2C шиною стенда
extern bool i2c_write_reg8(uint8_t dev_addr, uint8_t reg, uint8_t val);
extern bool i2c_read_reg16(uint8_t dev_addr, uint8_t reg, uint16_t *val);
extern void delay_ms(uint32_t ms);

// Ініціалізація слота
void slot_switch_init(slot_switch_t *slot, uint8_t id, uint8_t io_addr, uint8_t ina_addr) {
    slot->slot_id = id;
    slot->i2c_addr_io = io_addr;
    slot->i2c_addr_ina = ina_addr;
    slot->state = SLOT_PWR_OFF;
    slot->last_current_ma = 0;
    slot->last_voltage_mv = 0;
    
    // Переконатися, що силовий ключ закрито при старті
    i2c_write_reg8(slot->i2c_addr_io, 0x02, 0x00); // Output reg: Low
}

// Вимірювання струму через INA219 (LSB = 100 мкА)
bool slot_read_telemetry(slot_switch_t *slot) {
    uint16_t raw_current = 0;
    uint16_t raw_voltage = 0;
    
    if (!i2c_read_reg16(slot->i2c_addr_ina, 0x04, &raw_current)) {
        return false;
    }
    if (!i2c_read_reg16(slot->i2c_addr_ina, 0x02, &raw_voltage)) {
        return false;
    }
    
    slot->last_current_ma = raw_current / 10U; // переведення в мА
    slot->last_voltage_mv = (raw_voltage >> 3) * 4U; // INA219 Bus Voltage
    return true;
}

// Увімкнення живлення слота з контролем струму
bool slot_power_on(slot_switch_t *slot) {
    // 1. Перевірка на паразитне живлення до вмикання
    slot_read_telemetry(slot);
    if (slot->last_voltage_mv > 500U) {
        // На вимкненій платі напруга вища 0.5 В — витік через UART/SWD!
        slot->state = SLOT_PWR_PARASITIC_LEAK_FAULT;
        return false;
    }
    
    // 2. Подача сигналу на відкриття P-MOSFET
    slot->state = SLOT_PWR_SOFT_START;
    i2c_write_reg8(slot->i2c_addr_io, 0x02, (uint8_t)(1U << slot->slot_id));
    
    // 3. Очікування часу Soft-Start
    delay_ms(SOFT_START_SETTLE_MS);
    
    // 4. Перевірка струму після пуску
    slot_read_telemetry(slot);
    if (slot->last_current_ma > SLOT_MAX_INRUSH_CURRENT_MA) {
        // Струмовий удар / коротке замикання — аварійне вимкнення
        i2c_write_reg8(slot->i2c_addr_io, 0x02, 0x00);
        slot->state = SLOT_PWR_OVERCURRENT_FAULT;
        return false;
    }
    
    slot->state = SLOT_PWR_ACTIVE;
    return true;
}

// Вимкнення живлення слота (Hard Reset / Power Cycle)
void slot_power_off(slot_switch_t *slot) {
    i2c_write_reg8(slot->i2c_addr_io, 0x02, 0x00);
    slot->state = SLOT_PWR_OFF;
}
```
```cpp
// Ідіоматичний C++20 драйвер комутатора живлення слота стенда
#include <cstdint>
#include <expected>
#include <chrono>
#include <thread>
#include <concepts>

enum class SlotError {
    I2cCommunicationFailure,
    ParasiticBackfeedingDetected,
    InrushOvercurrentFault,
    SustainedOvercurrentFault
};

enum class PowerState {
    Off,
    SoftStarting,
    Active,
    Faulted
};

template <typename I2cBusType>
class SlotPowerSwitch {
public:
    static constexpr std::uint16_t MaxInrushCurrentMa = 1500;
    static constexpr std::uint16_t ParasiticThresholdMv = 500;
    static constexpr std::chrono::milliseconds SoftStartDuration{20};

    explicit constexpr SlotPowerSwitch(I2cBusType& bus, std::uint8_t slotId,
                                      std::uint8_t ioAddr, std::uint8_t inaAddr) noexcept
        : i2c_(bus), slotId_(slotId), ioAddr_(ioAddr), inaAddr_(inaAddr), state_(PowerState::Off) {}

    [[nodiscard]] std::expected<void, SlotError> powerOn() noexcept {
        auto telem = readTelemetry();
        if (!telem.has_value()) {
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        // Перевірка залишкової напруги від паразитного підживлення
        if (telem->voltageMv > ParasiticThresholdMv) {
            state_ = PowerState::Faulted;
            return std::unexpected(SlotError::ParasiticBackfeedingDetected);
        }

        state_ = PowerState::SoftStarting;
        if (!i2c_.writeReg8(ioAddr_, 0x02, static_cast<std::uint8_t>(1U << slotId_))) {
            state_ = PowerState::Faulted;
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        std::this_thread::sleep_for(SoftStartDuration);

        auto postTelem = readTelemetry();
        if (!postTelem.has_value()) {
            emergencyCutoff();
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        if (postTelem->currentMa > MaxInrushCurrentMa) {
            emergencyCutoff();
            return std::unexpected(SlotError::InrushOvercurrentFault);
        }

        state_ = PowerState::Active;
        return {};
    }

    void powerOff() noexcept {
        emergencyCutoff();
        state_ = PowerState::Off;
    }

    [[nodiscard]] PowerState state() const noexcept { return state_; }

    struct Telemetry {
        std::uint16_t voltageMv{0};
        std::uint16_t currentMa{0};
    };

    [[nodiscard]] std::expected<Telemetry, SlotError> readTelemetry() noexcept {
        std::uint16_t rawCurrent{0};
        std::uint16_t rawVoltage{0};

        if (!i2c_.readReg16(inaAddr_, 0x04, rawCurrent) ||
            !i2c_.readReg16(inaAddr_, 0x02, rawVoltage)) {
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        return Telemetry{
            .voltageMv = static_cast<std::uint16_t>((rawVoltage >> 3) * 4U),
            .currentMa = static_cast<std::uint16_t>(rawCurrent / 10U)
        };
    }

private:
    void emergencyCutoff() noexcept {
        i2c_.writeReg8(ioAddr_, 0x02, 0x00);
        state_ = PowerState::Off;
    }

    I2cBusType& i2c_;
    std::uint8_t slotId_;
    std::uint8_t ioAddr_;
    std::uint8_t inaAddr_;
    PowerState state_;
};
```
:::

Реалізація схемотехніки на базі P-MOSFET із RC-ланцюгом затвора та буферами з підтримкою I_off перетворює ненадійний хаотичний стенд на детермінований конвеєр, здатний тисячі разів поспіль виконувати холодний перезапуск без ризику зависань та деградації контактів.

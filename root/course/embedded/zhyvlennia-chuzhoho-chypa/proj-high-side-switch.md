# ⚙️ Реалізація High-Side комутатора живлення периферії

Повне відключення живлення периферійного чипа вимагає комутації у верхньому плечі (High-Side), щоб не розривати спільний нульовий потенціал землі. Якщо в момент зняття живлення сигнальні лінії мікроконтролера залишаються в стані високого логічного рівня або активних підтяжок, струм починає паразитно живити чип через його захисні ESD-діоди. Нижче наведено схему дискретного комутатора на P-канальному MOSFET з контролем швидкості наростання напруги, критерії вибору компонентів та повнофункціональний драйвер керування доменом живлення, який гарантує ізоляцію шин перед переходом у глибокий сон.

---

### Принципова електрична схема комутатора

Схема складається з силового P-канального транзистора `Q1` (наприклад, DMG2305UX, AO3401A або Si2301CDS з опором відкритого каналу `R_DS(on) < 50 мОм`), керівного N-канального MOSFET `Q2` (2N7002 або BSS138), інтегруючого ланцюжка плавного пуску `R2-C1` та вихідного розрядного резистора `R4`.

```
          V_IN (3.3 В .. 5 В)
           │
           ├───[ R1: 100 кОм ]───┬──────────────┐
           │                     │              │
           │                     ├──[ C1: 10 нФ ]
           │                     │
           ├───[ S ]             │
           │    │                │
           │   [Q1: P-MOSFET]    │
           │    │                │
           │   [ G ]─────────────┴──────┐
           │    │                       │
           └───[ D ]───┬───────────┐    │
                       │           │    │
                       │          [ R4: 100 кОм ]
                       │           │    │
                       │          GND   │
                       │                │
                  V_SWITCHED            │
                  (до периферії)       [ R2: 10 кОм ]
                                        │
                                       [ D ]
                                        │
                         GPIO_EN ──[Q2: N-MOSFET]
                                        │
                                       [ S ]
                                        │
                                       GND
```

---

### Фізика роботи та розрахунок елементів схеми

#### 1. Критерії вибору силового P-MOSFET (Q1)
- **Порогова напруга затвора (V_GS(th)):** транзистор повинен гарантовано відкриватися при доступній напрузі живлення `V_IN`. Якщо `V_IN = 3.3 В` або `2.5 В`, поріг `V_GS(th)` має бути в діапазоні від `-0.6 В` до `-1.2 В` (Logic-Level MOSFET). Якщо взяти стандартний польовик із порогом `-2.5 В`, при напрузі 3.3 В він опиниться в напіввідкритому лінійному режимі з високим опором каналу і буде грітися.
- **Опір відкритого каналу (R_DS(on)):** визначає статичне падіння напруги на ключі `V_drop = I_load · R_DS(on)`. Для навантаження з піковим струмом `I_load = 500 мА` транзистор з `R_DS(on) = 0.04 Ом` створить падіння всього `20 мВ`, що не впливає на стабільність логіки.
- **Потужність розсіювання:** у відкритому стані `P = I² · R_DS(on) = (0.5 А)² · 0.04 Ом = 10 мВт`, що легко розсіюється компактним корпусом SOT-23 без нагріву.

#### 2. Керівний N-MOSFET (Q2) та підтяжка затвора (R1)
- **Резистор R1 (100 кОм):** утримує напругу `V_GS = 0 В` на затворі `Q1`, коли `Q2` закритий. Великий опір обрано для мінімізації струму споживання у ввімкненому стані: через `R1` та `R2` на землю тече струм `I_ctrl = V_IN / (R1 + R2) = 3.3 В / 110 кОм ≈ 30 мкА`.
- **Транзистор Q2:** дозволяє розв'язати напругу керування від напруги живлення. Навіть якщо комутується шина акумулятора `V_IN = 4.2 В`, а мікроконтролер працює від 1.8 В, низьковольтний логічний сигнал на затворі `Q2` надійно притягує затвор `Q1` до землі, створюючи повну напругу `V_GS = -4.2 В`.

#### 3. Контроль швидкості наростання та обмеження пускового струму (R2, C1)
Коли ключ замикається на розряджений банк вихідних конденсаторів `C_load` (наприклад, 47–100 мкФ), миттєве відкриття транзистора викликає стрибок струму короткого замикання:

```
I_inrush = C_load · (dV / dt)
```

Без обмеження швидкості наростання `dV/dt` може перевищувати `10 В/мкс`, що створює пусковий струм понад 50 А, викликаючи просадку головної шини живлення `V_IN` і скидання мікроконтролера за Brown-Out Reset.

Конденсатор `C1` і резистор `R2` формують інтегратор Міллера на затворі `Q1`. Швидкість розряду ємності затвора обмежується постійною часу:

```
τ = R2 · C1 = 10 кОм · 10 нФ = 100 мкс
```

Це розтягує наростання напруги на виході `V_SWITCHED` до часу `t_rise ≈ 3 · τ = 300 мкс`. Для ємності `C_load = 47 мкФ` пусковий струм знижується до безпечного значення:

```
I_inrush = 47 · 10⁻⁶ Ф · (3.3 В / 300 · 10⁻⁶ с) ≈ 0.51 А
```

Такий імпульс легко компенсується вхідними конденсаторами перед ключем без просідання шини `V_IN`.

#### 4. Швидкий розряд вихідної ємності (R4)
Після закриття силового ключа `Q1` вихідна шина `V_SWITCHED` залишається зарядженою, якщо навантаження споживає мікроамперні струми. Без розрядного резистора напруга на периферії спадає секундами. Якщо мікроконтролер спробує повторно увімкнути живлення через 100 мс, чип не пройде цикл Power-On Reset.

Резистор `R4 = 100 кОм` забезпечує примусовий експоненційний розряд вихідних конденсаторів:

```
t_discharge ≈ 3 · R4 · C_load = 3 · 100 кОм · 47 мкФ ≈ 14.1 с
```

Якщо потрібне швидке вимкнення за мілісекунди, замість пасивного резистора 100 кОм використовують інтегральні ключі живлення з активною схемою швидкого розряду (Quick Output Discharge, QOD), де внутрішній транзистор 50–100 Ом підключається паралельно виходу в момент вимкнення.

---

### Порівняння: дискретний комутатор чи інтегральна мікросхема (Load Switch IC)

На практиці інженер обирає між дискретною схемою на двох транзисторах та спеціалізованою мікросхемою комутатора навантаження (наприклад, TI TPS22918, TPS22919 або Diodes AP22802):

| Параметр | Дискретний ключ (P-MOSFET + N-MOSFET) | Інтегральний Load Switch (TPS22918) |
|---|---|---|
| **Площа на платі** | 15–25 мм² (4–5 компонентів) | 2–4 мм² (корпус WLCSP або SOT-23-6) |
| **Керування Slew Rate** | Фіксоване через зовнішні `R2-C1` | Настроюване одним зовнішнім конденсатором `C_SR` |
| **Швидкий розряд (QOD)** | Повільний через резистор (струм спокою) | Активний внутрішній розрядний FET 50 Ом |
| **Захист від зворотного струму** | Відсутній (струм тече через body-діод Q1) | Вбудований True Reverse Current Blocking |
| **Тепловий та струмовий захист** | Відсутній (вимагає зовнішніх запобіжників) | Вбудоване обмеження струму (Current Limit) та Thermal Shutdown |
| **Вартість BOM** | Дуже низька, масові транзистори | Помірна, спеціалізований компонент |

---

### Драйвер керування доменом живлення

Програмна реалізація повинна гарантувати суворе дотримання таймінгів переходів між станами. Якщо мікроконтролер почне передавати дані по I2C до того, як вихідна напруга досягне номіналу, або залишить піни в стані Push-Pull High під час вимкнення, виникне паразитна інжекція струму в незакриті діоди периферії.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Абстракція платформно-залежних викликів GPIO */
extern void hal_gpio_write(uint32_t pin, bool level);
extern void hal_gpio_set_mode_output(uint32_t pin);
extern void hal_gpio_set_mode_input_floating(uint32_t pin);
extern void hal_gpio_set_mode_periph(uint32_t pin);
extern void hal_delay_ms(uint32_t ms);
extern bool hal_i2c_probe_device(uint8_t address);

typedef struct {
    uint32_t pwr_en_pin;
    uint32_t sda_pin;
    uint32_t scl_pin;
    uint8_t  device_i2c_addr;
    uint32_t startup_delay_ms;
    uint32_t discharge_delay_ms;
} PowerDomainConfig;

typedef enum {
    POWER_DOMAIN_OK = 0,
    POWER_DOMAIN_ERR_PROBE_FAILED,
    POWER_DOMAIN_ERR_INVALID_PARAM
} PowerDomainResult;

void power_domain_init(const PowerDomainConfig *cfg) {
    if (!cfg) return;

    /* Початковий безпечний стан: ключ закрито, шини ізольовано */
    hal_gpio_set_mode_output(cfg->pwr_en_pin);
    hal_gpio_write(cfg->pwr_en_pin, false);

    hal_gpio_set_mode_input_floating(cfg->sda_pin);
    hal_gpio_set_mode_input_floating(cfg->scl_pin);
}

PowerDomainResult power_domain_enable(const PowerDomainConfig *cfg) {
    if (!cfg) return POWER_DOMAIN_ERR_INVALID_PARAM;

    /* Крок 1: Відкриваємо High-Side ключ */
    hal_gpio_write(cfg->pwr_en_pin, true);

    /* Крок 2: Чекаємо заряджання ємностей та ініціалізацію POR чипа */
    hal_delay_ms(cfg->startup_delay_ms);

    /* Крок 3: Переводимо піни МК у робочий режим периферійної шини */
    hal_gpio_set_mode_periph(cfg->sda_pin);
    hal_gpio_set_mode_periph(cfg->scl_pin);

    /* Крок 4: Перевіряємо відповідь мікросхеми на шині */
    if (!hal_i2c_probe_device(cfg->device_i2c_addr)) {
        /* Якщо пристрій не відповів, вимикаємо живлення для безпеки */
        hal_gpio_set_mode_input_floating(cfg->sda_pin);
        hal_gpio_set_mode_input_floating(cfg->scl_pin);
        hal_gpio_write(cfg->pwr_en_pin, false);
        return POWER_DOMAIN_ERR_PROBE_FAILED;
    }

    return POWER_DOMAIN_OK;
}

void power_domain_disable(const PowerDomainConfig *cfg) {
    if (!cfg) return;

    /* Крок 1: ІЗОЛЯЦІЯ ШИН перед вимкненням живлення.
       Переводимо піни в High-Z, щоб усунути паразитно відкриті ESD-діоди. */
    hal_gpio_set_mode_input_floating(cfg->sda_pin);
    hal_gpio_set_mode_input_floating(cfg->scl_pin);

    /* Крок 2: Розмикаємо High-Side ключ */
    hal_gpio_write(cfg->pwr_en_pin, false);

    /* Крок 3: Витримуємо час для повного розряду вихідних конденсаторів */
    hal_delay_ms(cfg->discharge_delay_ms);
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <expected>
#include <span>

/* Абстракція апаратного інтерфейсу GPIO */
namespace hal {
    enum class PinMode { Output, InputFloating, Peripheral };

    void set_pin_mode(uint32_t pin, PinMode mode) noexcept;
    void write_pin(uint32_t pin, bool state) noexcept;
    void delay(std::chrono::milliseconds ms) noexcept;
    bool i2c_probe(uint8_t address) noexcept;
}

enum class PowerDomainError {
    DeviceNotResponding,
    InvalidConfiguration
};

struct PowerDomainPins {
    uint32_t pwr_en;
    uint32_t sda;
    uint32_t scl;
    uint8_t  device_addr;
};

class PeripheralPowerDomain {
public:
    constexpr PeripheralPowerDomain(PowerDomainPins pins,
                                    std::chrono::milliseconds startup_delay = std::chrono::milliseconds(15),
                                    std::chrono::milliseconds discharge_delay = std::chrono::milliseconds(30)) noexcept
        : pins_(pins), startup_delay_(startup_delay), discharge_delay_(discharge_delay), is_powered_(false) {}

    ~PeripheralPowerDomain() noexcept {
        if (is_powered_) {
            power_off();
        }
    }

    /* Заборона небезпечного копіювання керування доменом */
    PeripheralPowerDomain(const PeripheralPowerDomain&) = delete;
    PeripheralPowerDomain& operator=(const PeripheralPowerDomain&) = delete;

    PeripheralPowerDomain(PeripheralPowerDomain&& other) noexcept
        : pins_(other.pins_), startup_delay_(other.startup_delay_),
          discharge_delay_(other.discharge_delay_), is_powered_(other.is_powered_) {
        other.is_powered_ = false;
    }

    void init() const noexcept {
        hal::set_pin_mode(pins_.pwr_en, hal::PinMode::Output);
        hal::write_pin(pins_.pwr_en, false);
        isolate_bus();
    }

    [[nodiscard]] std::expected<void, PowerDomainError> power_on() noexcept {
        /* Крок 1: Замикаємо P-MOSFET ключ */
        hal::write_pin(pins_.pwr_en, true);

        /* Крок 2: Очікуємо стабілізації напруги і завершення POR */
        hal::delay(startup_delay_);

        /* Крок 3: Підключаємо цифрові інтерфейси МК */
        hal::set_pin_mode(pins_.sda, hal::PinMode::Peripheral);
        hal::set_pin_mode(pins_.scl, hal::PinMode::Peripheral);

        /* Крок 4: Верифікація зв'язку */
        if (!hal::i2c_probe(pins_.device_addr)) {
            power_off();
            return std::unexpected(PowerDomainError::DeviceNotResponding);
        }

        is_powered_ = true;
        return {};
    }

    void power_off() noexcept {
        /* Крок 1: Ізоляція сигнальних ліній для усунення фантомного живлення */
        isolate_bus();

        /* Крок 2: Розмикання силового ключа */
        hal::write_pin(pins_.pwr_en, false);
        is_powered_ = false;

        /* Крок 3: Пауза на повний розряд вихідної ємності через R_dis */
        hal::delay(discharge_delay_);
    }

    [[nodiscard]] bool is_active() const noexcept {
        return is_powered_;
    }

private:
    void isolate_bus() const noexcept {
        hal::set_pin_mode(pins_.sda, hal::PinMode::InputFloating);
        hal::set_pin_mode(pins_.scl, hal::PinMode::InputFloating);
    }

    PowerDomainPins pins_;
    std::chrono::milliseconds startup_delay_;
    std::chrono::milliseconds discharge_delay_;
    bool is_powered_;
};

/* RAII-обгортка для сесійного опитування давача з гарантованим вимкненням */
class ScopedPowerSession {
public:
    explicit ScopedPowerSession(PeripheralPowerDomain& domain)
        : domain_(domain), status_(domain_.power_on()) {}

    ~ScopedPowerSession() noexcept {
        if (status_.has_value()) {
            domain_.power_off();
        }
    }

    [[nodiscard]] bool is_valid() const noexcept {
        return status_.has_value();
    }

    [[nodiscard]] PowerDomainError error() const noexcept {
        return status_.error();
    }

private:
    PeripheralPowerDomain& domain_;
    std::expected<void, PowerDomainError> status_;
};
```
:::

Використання RAII-класу `ScopedPowerSession` дозволяє виконувати сесійні вимірювання за один лаконічний виклик. Навіть якщо під час обміну даними станеться помилка шини або передчасний вихід із функції, деструктор гарантовано розімкне силовий ключ і переведе всі лінії зв'язку в безпечний високоімпедансний стан, унеможливлюючи паразитно відкриті діоди під час сну.

---

### Пастка зворотного струму через паразитний body-діод

Кожен дискретний MOSFET має внутрішній технологічний p-n перехід підкладки — так званий body-діод. У P-канальному транзисторі цей діод підключений анодом до стоку (`Drain`, вихід `V_SWITCHED`), а катодом до витоку (`Source`, вхід `V_IN`).

Якщо периферійний модуль має власне джерело енергії (наприклад, підключений USB-кабель програмування, зовнішній акумулятор або сонячну панель), напруга на виході `V_SWITCHED` може перевищити напругу головної шини `V_IN`. У цьому випадку струм потече у зворотному напрямку через відкритий body-діод транзистора `Q1` прямо в шину `V_IN` мікроконтролера, навіть якщо ключ вимкнено програмно.

Для усунення цього ефекту застосовують одне з двох рішень:
1. **Зустрічне ввімкнення транзисторів (Back-to-Back P-MOSFET):** послідовно встановлюють два P-MOSFET зі з'єднаними разом витоками або стоками. Їхні внутрішні діоди спрямовані назустріч один одному, що повністю блокує струм в обох напрямках при закритих затворах.
2. **Інтегральний Load Switch із захистом TRCB (True Reverse Current Blocking):** спеціалізовані мікросхеми відстежують різницю напруг `V_OUT - V_IN` і миттєво розривають внутрішній зв'язок підкладки при виявленні зворотного перепаду понад 10–20 мВ.

---

### Інженерна перевірка перехідного процесу осцилографом

Перед випуском плати в серію роботу комутатора перевіряють на макеті під реальним навантаженням за наступною методикою:
1. **Канал 1 осцилографа (жовтий):** підключають до керуючого піна `GPIO_EN` (синхронізація за наростаючим фронтом).
2. **Канал 2 осцилографа (синій):** підключають до комутованої шини `V_SWITCHED` через щуп із пружинною насадкою землі.
3. **Канал 3 осцилографа (зелений):** підключають у режимі закритого входу (AC Coupling) до вхідної шини живлення `V_IN`.
4. **Струмовий пробник:** фіксує пусковий струм `I_inrush` у розриві провідника до витоку `Q1`.

**Критерії придатності схеми:**
- Наростання напруги на каналі 2 є строго монотонним, без сходинок, резонансного дзвіна та викидів перенапруги.
- Просадка напруги на вхідній шині `V_IN` (канал 3) у момент старту не перевищує 50 мВ.
- Піковий пусковий струм через транзистор не перевищує 1.0 А для конденсаторного банку 47–100 мкФ.
- Після зняття сигналу `GPIO_EN` вихідна напруга плавно спадає до строго нульового рівня без зависання на проміжних потенціалах.

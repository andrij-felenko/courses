# ⚙️ Налаштування режимів виводу й безпечне керування навантаженням

Цей проєктний розбір демонструє, як у низькорівневому коді прошивки мікроконтролера правильно конфігурувати електричні параметри вихідного каскаду GPIO: керувати швидкістю наростання фронту *(slew rate / output speed)* для усунення перешкод і пікових струмів, налаштовувати навантажувальну здатність *(Drive Strength)*, обирати між двотактним режимом Push-Pull та відкритим стоком Open-Drain, а також реалізовувати безпечні апаратні абстракції на мовах C та ідіоматичному C++.

---

## 1. Регістри керування вихідним каскадом GPIO (на прикладі ARM Cortex-M)

У сучасних 32-бітних мікроконтролерах (зокрема сімейства STM32) кожен порт вводу-виводу керується набором спеціалізованих 32-розрядних регістрів. Розуміння їхнього призначення дозволяє безпосередньо впливати на електричний стан транзисторів вихідного каскаду:

1. **`MODER` (GPIO Port Mode Register):** визначає базовий режим роботи кожного виводу:
   - `00` — цифровий вхід *(Input / Hi-Z)*;
   - `01` — універсальний вихід загального призначення *(General Purpose Output)*;
   - `10` — альтернативна функція периферії *(Alternate Function: SPI, UART, PWM, I2C)*;
   - `11` — аналоговий режим *(Analog Mode)*, де вхідний цифровий тригер Шмітта повністю відключається для усунення струмів витоку під час вимірювань АЦП.
2. **`OTYPER` (GPIO Port Output Type Register):** конфігурує структуру вихідного каскаду:
   - `0` — двотактний вихід *(Push-Pull)*, де активні обидва транзистори (P-MOSFET і N-MOSFET);
   - `1` — відкритий стік *(Open-Drain)*, де верхній P-MOSFET вимкнений, а вивід комутується лише на землю.
3. **`OSPEEDR` (GPIO Port Output Speed Register):** задає струм керування затворами вихідних MOSFET, визначаючи швидкість наростання напруги *(Slew Rate)*:
   - `00` — низька швидкість *(Low Speed, 2…4 МГц)*;
   - `01` — середня швидкість *(Medium Speed, 10…25 МГц)*;
   - `10` — висока швидкість *(High Speed, 50 МГц)*;
   - `11` — максимальна швидкість *(Very High Speed, 100…180 МГц)*.
4. **`PUPDR` (GPIO Port Pull-Up/Pull-Down Register):** вмикає внутрішні високоомні резистори (номіналом 30…50 кОм) до шини `V_DD` або `V_SS`.
5. **`BSRR` (Bit Set/Reset Register):** регістр атомарного встановлення та скидання стану виводів. Запис у молодші 16 біт встановлює пін у «1», а в старші 16 біт — скидає у «0» за один машинний такт без потреби повільних операцій читання-модифікації-запису *(Read-Modify-Write)*.

---

## 2. Чому швидкість наростання фронту (Slew Rate) має значення

Поширена помилка — завжди виставляти максимальну швидкість `Very High Speed` для всіх виводів. Проте надто крутий фронт сигналу з часом наростання `t_r ≈ 1…2 нс` створює високу швидкість зміни струму `di/dt`.

Паразитна індуктивність провідників друкованої плати та контактних провідників корпусу мікросхеми `L_trace ≈ 5…15 нГн` у поєднанні з крутим фронтом струму породжує індуктивний сплеск напруги на внутрішніх шинах живлення та землі *(Ground Bounce / VDD Sag)*:

```
V_bounce = L_trace · (di/dt)
```

Крім того, ємність навантаження `C_L` (навіть 30…50 пФ від траси та вхідного контакту приймача) під час швидкого перемикання генерує піковий струм перезаряджання:

```
i_peak = C_L · (dv/dt)
```

При перепаді 3.3 В за 1 нс струм перезаряджання ємності 50 пФ становить `50·10⁻¹² · (3.3 / 10⁻⁹) = 165 мА`, що багаторазово перевищує допустимий ліміт виводу.

> 🔧 **Інженерне правило:** для індикаторних світлодіодів, сигналів увімкнення реле, ліній скидання та низькочастотних інтерфейсів (< 100 кГц) **завжди** налаштовуйте `Low Speed`. Це усуває паразитичні дзвінки на лініях, зменшує імпульсний струм споживання та мінімізує електромагнітне випромінювання *(EMI)*.

---

## 3. Драйвер безпечного виводу: порівняння реалізацій на C та ідіоматичному C++

Розгляньмо практичну реалізацію драйвера керування дискретним навантаженням на базі мікроконтролера STM32 (режим Push-Pull, мінімальна швидкість наростання `Low Speed`, захист від невизначеного стану).

:::tabs
```c
/* Файл: gpio_driver.c — Реалізація мовою C (STM32 LL API) */
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"
#include <stdbool.h>

/* Структура конфігурації піна */
typedef struct {
    GPIO_TypeDef *port;
    uint32_t pin_mask;
    bool active_low;
} GpioOutputConfig;

/* Ініціалізація виводу в безпечному режимі з мінімальною швидкістю */
void gpio_output_init(const GpioOutputConfig *cfg)
{
    /* 1. Тактування порту */
    if (cfg->port == GPIOA) {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    } else if (cfg->port == GPIOB) {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
    } else if (cfg->port == GPIOC) {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOC);
    }

    /* 2. Початковий безпечний стан виводу ДО ввімкнення режиму OUTPUT */
    if (cfg->active_low) {
        LL_GPIO_SetOutputPin(cfg->port, cfg->pin_mask);   /* Пасивний стан: 3.3 В */
    } else {
        LL_GPIO_ResetOutputPin(cfg->port, cfg->pin_mask); /* Пасивний стан: 0 В */
    }

    /* 3. Налаштування вихідного каскаду */
    LL_GPIO_InitTypeDef init_struct;
    init_struct.Pin        = cfg->pin_mask;
    init_struct.Mode       = LL_GPIO_MODE_OUTPUT;
    init_struct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    init_struct.Speed      = LL_GPIO_SPEED_FREQ_LOW; /* Захист від Ground Bounce! */
    init_struct.Pull       = LL_GPIO_PULL_NO;

    LL_GPIO_Init(cfg->port, &init_struct);
}

void gpio_output_set(const GpioOutputConfig *cfg, bool turn_on)
{
    bool drive_high = cfg->active_low ? !turn_on : turn_on;
    if (drive_high) {
        LL_GPIO_SetOutputPin(cfg->port, cfg->pin_mask);
    } else {
        LL_GPIO_ResetOutputPin(cfg->port, cfg->pin_mask);
    }
}
```
```cpp
// Файл: gpio_driver.hpp — Ідіоматичний C++20 (RAII, Compile-Time Safety, Zero-Overhead)
#pragma once
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"
#include <cstdint>
#include <concepts>

namespace embedded::hw {

enum class OutputSpeed : uint32_t {
    Low      = LL_GPIO_SPEED_FREQ_LOW,
    Medium   = LL_GPIO_SPEED_FREQ_MEDIUM,
    High     = LL_GPIO_SPEED_FREQ_HIGH,
    VeryHigh = LL_GPIO_SPEED_FREQ_VERY_HIGH
};

enum class LogicPolarity : uint8_t {
    ActiveHigh, // Логічна 1 вмикає навантаження (Sourcing)
    ActiveLow   // Логічний 0 вмикає навантаження (Sinking)
};

// Шаблонний клас дискретного виводу з повною перевіркою параметрів під час компіляції
template <uintptr_t PortBase, uint32_t PinMask, LogicPolarity Polarity = LogicPolarity::ActiveHigh>
class SafeOutputPin {
public:
    constexpr SafeOutputPin() noexcept = default;

    // Ресурс апаратного виводу унікальний — забороняємо небезпечне копіювання
    SafeOutputPin(const SafeOutputPin&) = delete;
    SafeOutputPin& operator=(const SafeOutputPin&) = delete;

    // Дозволяємо безпечне переміщення
    SafeOutputPin(SafeOutputPin&&) noexcept = default;
    SafeOutputPin& operator=(SafeOutputPin&&) noexcept = default;

    ~SafeOutputPin() noexcept {
        // Гарантоване переведення навантаження в безпечний вимкнений стан при знищенні об'єкта
        turn_off();
    }

    void init(OutputSpeed speed = OutputSpeed::Low) noexcept {
        enable_port_clock();

        // Встановлюємо безпечний вихідний рівень ДО конфігурації напрямку виводу
        turn_off();

        LL_GPIO_InitTypeDef init_struct{};
        init_struct.Pin        = PinMask;
        init_struct.Mode       = LL_GPIO_MODE_OUTPUT;
        init_struct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
        init_struct.Speed      = static_cast<uint32_t>(speed);
        init_struct.Pull       = LL_GPIO_PULL_NO;

        LL_GPIO_Init(port(), &init_struct);
    }

    void turn_on() noexcept {
        if constexpr (Polarity == LogicPolarity::ActiveHigh) {
            LL_GPIO_SetOutputPin(port(), PinMask);
        } else {
            LL_GPIO_ResetOutputPin(port(), PinMask);
        }
    }

    void turn_off() noexcept {
        if constexpr (Polarity == LogicPolarity::ActiveHigh) {
            LL_GPIO_ResetOutputPin(port(), PinMask);
        } else {
            LL_GPIO_SetOutputPin(port(), PinMask);
        }
    }

    void toggle() noexcept {
        LL_GPIO_TogglePin(port(), PinMask);
    }

private:
    [[nodiscard]] static GPIO_TypeDef* port() noexcept {
        return reinterpret_cast<GPIO_TypeDef*>(PortBase);
    }

    static void enable_port_clock() noexcept {
        if constexpr (PortBase == GPIOA_BASE) {
            LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
        } else if constexpr (PortBase == GPIOB_BASE) {
            LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
        } else if constexpr (PortBase == GPIOC_BASE) {
            LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOC);
        }
    }
};

} // namespace embedded::hw
```
:::

---

## 4. Конфігурація відкритого стоку (Open-Drain) для шин I2C та змішаних напруг

Коли вивід повинен взаємодіяти з лінією, напруга якої відрізняється від напруги живлення мікроконтролера (наприклад, лінія I2C з підтяжкою до 5 В або модуль із власним живленням), використовується режим відкритого стоку *(Open-Drain)*. У цьому режимі вивід ніколи не формує активну «1» за допомогою P-MOSFET, а відпускає лінію у високоомний стан.

:::tabs
```c
/* Файл: gpio_opendrain.c — C реалізація відкритого стоку */
#include "stm32f4xx_ll_gpio.h"

void gpio_init_open_drain(GPIO_TypeDef *port, uint32_t pin)
{
    LL_GPIO_InitTypeDef init;
    init.Pin        = pin;
    init.Mode       = LL_GPIO_MODE_OUTPUT;
    init.OutputType = LL_GPIO_OUTPUT_OPENDRAIN; /* Відкритий стік */
    init.Speed      = LL_GPIO_SPEED_FREQ_MEDIUM;   /* Помірна швидкість */
    init.Pull       = LL_GPIO_PULL_NO;          /* Зовнішня підтяжка на платі */

    LL_GPIO_Init(port, &init);

    /* За замовчуванням відпускаємо вивід у стан Hi-Z (високий рівень від зовнішнього резистора) */
    LL_GPIO_SetOutputPin(port, pin);
}
```
```cpp
// Файл: gpio_opendrain.hpp — Ідіоматичний C++20 Open-Drain драйвер
#pragma once
#include "stm32f4xx_ll_gpio.h"
#include <concepts>

namespace embedded::hw {

template <uintptr_t PortBase, uint32_t PinMask>
class OpenDrainLine {
public:
    static void init(OutputSpeed speed = OutputSpeed::Medium) noexcept {
        auto* port = reinterpret_cast<GPIO_TypeDef*>(PortBase);

        LL_GPIO_InitTypeDef init{};
        init.Pin        = PinMask;
        init.Mode       = LL_GPIO_MODE_OUTPUT;
        init.OutputType = LL_GPIO_OUTPUT_OPENDRAIN;
        init.Speed      = static_cast<uint32_t>(speed);
        init.Pull       = LL_GPIO_PULL_NO;

        LL_GPIO_Init(port, &init);
        release_bus();
    }

    // Притягнути лінію до землі (активний стан 0 В)
    static void drive_low() noexcept {
        LL_GPIO_ResetOutputPin(reinterpret_cast<GPIO_TypeDef*>(PortBase), PinMask);
    }

    // Відпустити лінію у Hi-Z (високий рівень забезпечує зовнішній Pull-Up резистор)
    static void release_bus() noexcept {
        LL_GPIO_SetOutputPin(reinterpret_cast<GPIO_TypeDef*>(PortBase), PinMask);
    }
};

} // namespace embedded::hw
```
:::

---

## 5. Програмне керування навантажувальною здатністю (Drive Capability на ESP-IDF)

У мікроконтролерах сімейства ESP32 реалізовано можливість динамічного програмного вибору максимального струму вихідного каскаду *(Drive Strength)* за допомогою функції `gpio_set_drive_capability()`.

Доступні чотири градації струму:
- `GPIO_DRIVE_CAP_0` — мінімальний струм (близько 5 мА);
- `GPIO_DRIVE_CAP_1` — слабкий струм (близько 10 мА);
- `GPIO_DRIVE_CAP_2` — стандартний струм за замовчуванням (близько 20 мА);
- `GPIO_DRIVE_CAP_3` — максимальний струм (до 40 мА).

Зменшення сили струму до рівня `CAP_0` або `CAP_1` для ліній світлодіодів та повільних сигналів забезпечує суттєве зниження рівня високочастотних шумів на платі та захищає мікроконтролер від надмірних струмових перевантажень у разі випадкового короткого замикання на землю під час налагодження.

---

## 6. Крайовий випадок: поведінка виводів під час апаратного скидання (Reset State)

Критично важливим аспектом схемотехнічного проєктування є стан виводів мікроконтролера в момент утримання лінії `NRST / RESET` на землі та перших мікросекунд після зняття сигналу скидання, доки прошивка не встигла виконати конфігурацію периферії:

1. **Всі виводи за замовчуванням перебувають у стані цифрового входу з високим імпедансом *(Input Hi-Z)*.** Внутрішні MOSFET-ключі повністю закриті.
2. Якщо зовнішній транзисторний ключ (наприклад, польовий N-MOSFET силового нагрівача чи мотора) затвором підключений до піна GPIO без **зовнішнього стягувального резистора**, затвор залишається електрично «підвішеним» у повітрі.
3. Будь-яка електростатична наводка або ємнісний зв'язок від сусідніх ліній зарядить затвор польового транзистора, і силовий ключ самовільно відкриється на повну потужність у момент скидання процесора!

> 🔧 **Правило надійного проєктування:** ніколи не покладайтеся на програмні підтяжки `PUPDR` для критичних виконавчих механізмів. На затворі будь-якого зовнішнього силового транзистора повинен стояти фізичний резистор підтяжки (носієм 10…47 кОм) до безпечного рівня, який гарантує надійне утримання навантаження у вимкненому стані незалежно від стану мікроконтролера.

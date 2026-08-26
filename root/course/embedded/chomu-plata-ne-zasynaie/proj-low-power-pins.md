# ⚙️ Прошивка підготовки GPIO, периферії та налагоджувача до глибокого сну

Переведення мікроконтролера в режим глибокого сну вимагає детермінованого керування апаратними регістрами введення-виведення, периферійними інтерфейсами та блоками трасування ядра. Проста зупинка процесорного ядра інструкцією очікування переривання залишає активними вхідні буфери, внутрішні підтяжки та тактові генератори, зводячи нанівець енергетичну ефективність виробу.

Цей інженерний проект містить модульний драйвер керування низькоспоживаними станами виводів (Low-Power Pin & Power Manager) для мікроконтролерів архітектури ARM Cortex-M (на прикладі сімейства STM32) та систем на кристалі ESP32. Драйвер реалізує повний життєвий цикл переходу у сон: коректне скидання буферів інтерфейсів, знеструмлення зовнішніх датчиків, ізоляцію цифрових шин, конфігурацію невживаних ніжок у режим Analog, вимкнення блоку налагодження `DBGMCU` та коректне відновлення після пробудження.

## Послідовність операцій перед виконанням WFI / Deep Sleep

Процес присипляння плати повинен виконуватися у строго визначеному порядку. Порушення послідовності (наприклад, знеструмлення датчика до скидання вихідного піна в LOW) викликає короткочасний сплеск струму через захисні діоди або зависання цифрової шини.

```text
1. Очікування завершення передачі по UART/SPI/I2C (перевірка прапорців TXE / TC / BSY)
2. Програмне переведення датчиків у режим Standby / Power-Down по шині
3. Переведення сигнальних ліній шин (TX, MOSI, SCK, CS, SDA, SCL) у стан LOW або Hi-Z
4. Зняття напруги з датчиків розмиканням силового ключа (Load Switch / P-MOSFET)
5. Переведення всіх непідключених та плаваючих виводів GPIO в режим Analog (без підтяжок)
6. Налаштування джерел пробудження (зовнішній пін EXTI / Wakeup Pin або будильник RTC)
7. Очищення регістрів налагодження ядра (DBGMCU->CR = 0)
8. Виконання інструкції входу в цільовий режим сну (__WFI / __WFE)
```

## Інженерний розбір критичних ділянок коду

### Очищення буферів послідовних інтерфейсів

Поширена помилка при переході в сон полягає у виклику інструкції сну одразу після запису останнього байта в буфер передавача UART або SPI. У більшості мікроконтролерів прапорець спустошення регістра передачі (TXE — Transmit Data Register Empty) виставляється в одиницю, щойно байт переміщується з буферного регістра у внутрішній зсувний регістр передавача. 

Якщо в цей момент знеструмити периферію або зупинити тактування, останній передаваний байт обривається на середині кадру, викликаючи помилку кадрування (Framing Error) на стороні приймача. Драйвер зобов'язаний очікувати встановлення прапорця повного завершення передачі (TC — Transmission Complete) та скидання прапорця зайнятості шини (BSY — Busy Flag).

### Розряд блокувальних конденсаторів периферії

Кожен зовнішній датчик має власні блокувальні конденсатори по шині живлення ємністю від 0.1 до 10 мкФ. Після розмикання силового ключа P-MOSFET залишкова напруга на шині живлення датчика спадає за експоненційним законом з постійною часу:

```text
tau = R_discharge * C_decoupling
```

Якщо внутрішня схема датчика переходить у високоімпедансний стан, розряд ємностей через мікроамперні витоки може тривати десятки або сотні мілісекунд. Якщо перевести сигнальні виводи мікроконтролера в нуль до повного розряду цих ємностей, енергія, накопичена в конденсаторах, почне стікати в мікроконтролер через нижні захисні діоди. Тому якісний силовий ключ повинен містити схему примусового активного розряду (Quick Output Discharge, QOD), або прошивка повинна витримувати необхідну паузу.

### Регістрова конфігурація виводів STM32

У мікроконтролерах STM32 стан виводів керується чотирма основними 32-бітними регістрами:

1. `MODER` — визначає функціональне призначення (00: цифровий вхід, 01: цифровий вихід загального призначення, 10: альтернативна функція периферії, 11: аналоговий режим). Запис значення `11b` повністю відключає вхідний тригер Шмітта від зовнішнього виводу.
2. `PUPDR` — керує внутрішніми резисторами підтяжки (00: без підтяжки, 01: підтяжка до VDD, 10: підтяжка до землі GND). У режимі сну цей регістр скидається в нуль для виключення паразитного протікання струму.
3. `ODR` та `BSRR` — керують рівнями вихідних сигналів. Атомарний запис у регістр `BSRR` дозволяє встановлювати або скидати біти без ризику виникнення гонки станів (Race Condition) з перериваннями.

## Реалізація низькорівневого менеджера сну

Наведений код реалізує керування виводами портів GPIOA, GPIOB, GPIOC та спеціальними регістрами налагодження.

:::tabs
@tab c
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів STM32 (регістровий рівень) */
#define DBGMCU_BASE_ADDR   0xE0042000UL
#define DBGMCU_CR_REG      (*(volatile uint32_t *)(DBGMCU_BASE_ADDR + 0x04UL))

#define GPIOA_BASE_ADDR    0x48000000UL
#define GPIOB_BASE_ADDR    0x48000400UL
#define GPIOC_BASE_ADDR    0x48000800UL

typedef struct {
    volatile uint32_t MODER;    /* Режим виводу: 00-Input, 01-Output, 10-AF, 11-Analog */
    volatile uint32_t OTYPER;   /* Тип виходу: 0-Push-Pull, 1-Open-Drain */
    volatile uint32_t OSPEEDR;  /* Швидкість перемикання */
    volatile uint32_t PUPDR;    /* Підтяжки: 00-Floating, 01-Pull-up, 10-Pull-down */
    volatile uint32_t IDR;      /* Вхідні дані */
    volatile uint32_t ODR;      /* Вихідні дані */
    volatile uint32_t BSRR;     /* Встановлення/скидання бітів */
    volatile uint32_t LCKR;     /* Блокування конфігурації */
    volatile uint32_t AFR[2];   /* Альтернативні функції */
    volatile uint32_t BRR;      /* Скидання бітів виходу */
} LowPower_GPIO_TypeDef;

#define LP_GPIOA ((LowPower_GPIO_TypeDef *)GPIOA_BASE_ADDR)
#define LP_GPIOB ((LowPower_GPIO_TypeDef *)GPIOB_BASE_ADDR)
#define LP_GPIOC ((LowPower_GPIO_TypeDef *)GPIOC_BASE_ADDR)

/* Маски збережених пінів (наприклад, пін пробудження PA0 та пін ключа живлення PB12) */
#define PIN_WAKEUP_PA0       (1U << 0)
#define PIN_LOAD_SWITCH_PB12 (1U << 12)

typedef struct {
    uint32_t moder_a;
    uint32_t pupdr_a;
    uint32_t moder_b;
    uint32_t pupdr_b;
    uint32_t moder_c;
    uint32_t pupdr_c;
} GpioBackupContext;

static GpioBackupContext g_gpio_backup;

/**
 * @brief Вимкнення силового ключа периферії
 */
void power_switch_set(bool enable)
{
    if (enable) {
        /* P-MOSFET відкривається нулем (активний LOW) */
        LP_GPIOB->BSRR = (PIN_LOAD_SWITCH_PB12 << 16U);
    } else {
        /* P-MOSFET закривається одиницею */
        LP_GPIOB->BSRR = PIN_LOAD_SWITCH_PB12;
    }
}

/**
 * @brief Підготовка всіх виводів до сну: переведення в Analog mode
 */
void low_power_pins_enter_sleep(void)
{
    /* 1. Збереження поточної конфігурації для відновлення після сну */
    g_gpio_backup.moder_a = LP_GPIOA->MODER;
    g_gpio_backup.pupdr_a = LP_GPIOA->PUPDR;
    g_gpio_backup.moder_b = LP_GPIOB->MODER;
    g_gpio_backup.pupdr_b = LP_GPIOB->PUPDR;
    g_gpio_backup.moder_c = LP_GPIOC->MODER;
    g_gpio_backup.pupdr_c = LP_GPIOC->PUPDR;

    /* 2. Ізоляція сигнальних ліній периферії (зведення в LOW) */
    LP_GPIOA->ODR &= ~((1U << 2) | (1U << 3) | (1U << 5) | (1U << 7)); /* UART TX/RX, SPI MOSI/SCK */

    /* 3. Знеструмлення зовнішніх датчиків */
    power_switch_set(false);

    /* 4. Переведення виводів у режим Analog (MODER = 0xFFFFFFFF, PUPDR = 0x00000000)
          Виняток: пін пробудження PA0 та пін силового ключа PB12 залишаються у визначеному стані */
    
    /* Порт A: всі в Analog, крім PA0 (Wakeup) */
    LP_GPIOA->MODER = 0xFFFFFFFCUL | (g_gpio_backup.moder_a & 0x03UL);
    LP_GPIOA->PUPDR = 0x00000000UL | (g_gpio_backup.pupdr_a & 0x03UL);

    /* Порт B: всі в Analog, крім PB12 (Load Switch Output High) */
    uint32_t pb12_moder_mask = (3U << (12 * 2));
    LP_GPIOB->MODER = (~pb12_moder_mask) | (g_gpio_backup.moder_b & pb12_moder_mask);
    LP_GPIOB->PUPDR = 0x00000000UL;

    /* Порт C: всі виводи в чистий Analog */
    LP_GPIOC->MODER = 0xFFFFFFFFUL;
    LP_GPIOC->PUPDR = 0x00000000UL;

    /* 5. Вимкнення тактування блоку налагодження під час зупинки ядра */
    DBGMCU_CR_REG = 0x00000000UL;
}

/**
 * @brief Відновлення конфігурації виводів після виходу зі сну
 */
void low_power_pins_restore(void)
{
    /* Відновлення конфігурації портів з резервної копії */
    LP_GPIOA->MODER = g_gpio_backup.moder_a;
    LP_GPIOA->PUPDR = g_gpio_backup.pupdr_a;

    LP_GPIOB->MODER = g_gpio_backup.moder_b;
    LP_GPIOB->PUPDR = g_gpio_backup.pupdr_b;

    LP_GPIOC->MODER = g_gpio_backup.moder_c;
    LP_GPIOC->PUPDR = g_gpio_backup.pupdr_c;

    /* Повторне ввімкнення живлення периферії */
    power_switch_set(true);
}
```
@tab cpp
```cpp
#include <cstdint>
#include <array>
#include <span>

namespace LowPower {

/* Регістровий опис портів введення-виведення */
struct GpioRegisters {
    volatile std::uint32_t moder;
    volatile std::uint32_t otyper;
    volatile std::uint32_t ospeedr;
    volatile std::uint32_t pupdr;
    volatile std::uint32_t idr;
    volatile std::uint32_t odr;
    volatile std::uint32_t bsrr;
    volatile std::uint32_t lckr;
    volatile std::uint32_t afr[2];
    volatile std::uint32_t brr;
};

inline auto& gpio_a = *reinterpret_cast<GpioRegisters*>(0x48000000UL);
inline auto& gpio_b = *reinterpret_cast<GpioRegisters*>(0x48000400UL);
inline auto& gpio_c = *reinterpret_cast<GpioRegisters*>(0x48000800UL);
inline auto& dbgmcu_cr = *reinterpret_cast<volatile std::uint32_t*>(0xE0042004UL);

enum class PinMode : std::uint32_t {
    Input  = 0b00,
    Output = 0b01,
    AltFn  = 0b10,
    Analog = 0b11
};

enum class PullMode : std::uint32_t {
    Floating = 0b00,
    PullUp   = 0b01,
    PullDown = 0b10
};

struct PortBackup {
    std::uint32_t moder{0xFFFFFFFFUL};
    std::uint32_t pupdr{0x00000000UL};
};

class SleepManager {
public:
    constexpr SleepManager() noexcept = default;

    /* RAII-сторож низькоспоживаного стану */
    class SleepScopeGuard {
    public:
        explicit SleepScopeGuard(SleepManager& manager) noexcept : manager_(manager) {
            manager_.enter_sleep_configuration();
        }

        ~SleepScopeGuard() noexcept {
            manager_.restore_active_configuration();
        }

        SleepScopeGuard(const SleepScopeGuard&) = delete;
        SleepScopeGuard& operator=(const SleepScopeGuard&) = delete;

    private:
        SleepManager& manager_;
    };

    [[nodiscard]] SleepScopeGuard guard() noexcept {
        return SleepScopeGuard{*this};
    }

    void set_load_switch(bool enabled) noexcept {
        constexpr std::uint32_t switch_pin_mask = (1U << 12);
        if (enabled) {
            gpio_b.bsrr = (switch_pin_mask << 16U); /* Reset pin -> Active Low ON */
        } else {
            gpio_b.bsrr = switch_pin_mask;          /* Set pin -> OFF */
        }
    }

    void enter_sleep_configuration() noexcept {
        backup_[0] = { .moder = gpio_a.moder, .pupdr = gpio_a.pupdr };
        backup_[1] = { .moder = gpio_b.moder, .pupdr = gpio_b.pupdr };
        backup_[2] = { .moder = gpio_c.moder, .pupdr = gpio_c.pupdr };

        /* 1. Ізоляція шин даних */
        gpio_a.odr &= ~((1U << 2) | (1U << 3) | (1U << 5) | (1U << 7));

        /* 2. Знеструмлення периферії */
        set_load_switch(false);

        /* 3. Переведення пінів у чистий Analog, зберігаючи пін пробудження PA0 */
        gpio_a.moder = 0xFFFFFFFCUL | (backup_[0].moder & 0x03UL);
        gpio_a.pupdr = 0x00000000UL | (backup_[0].pupdr & 0x03UL);

        /* Зберігаємо вихідний пін ключа живлення PB12 */
        constexpr std::uint32_t pb12_mask = (0b11U << (12 * 2));
        gpio_b.moder = (~pb12_mask) | (backup_[1].moder & pb12_mask);
        gpio_b.pupdr = 0x00000000UL;

        /* Порт C повністю переводиться в Analog */
        gpio_c.moder = 0xFFFFFFFFUL;
        gpio_c.pupdr = 0x00000000UL;

        /* 4. Вимкнення блоку налагодження ядра */
        dbgmcu_cr = 0x00000000UL;
    }

    void restore_active_configuration() noexcept {
        gpio_a.moder = backup_[0].moder;
        gpio_a.pupdr = backup_[0].pupdr;

        gpio_b.moder = backup_[1].moder;
        gpio_b.pupdr = backup_[1].pupdr;

        gpio_c.moder = backup_[2].moder;
        gpio_c.pupdr = backup_[2].pupdr;

        set_load_switch(true);
    }

private:
    std::array<PortBackup, 3> backup_{};
};

} // namespace LowPower
```
:::

## Інтеграція в цикл глибокого сну

Приклад використання менеджера сну в головному циклі програми з використанням об'єктно-орієнтованого RAII-підходу на C++ та функціонального підходу на C:

:::tabs
@tab c
```c
void enter_deep_sleep_cycle(void)
{
    /* 1. Підготовка виводів та апаратури */
    low_power_pins_enter_sleep();

    /* 2. Вхід у режим Stop/Standby */
    __asm volatile("wfi");

    /* 3. Відновлення після пробудження перериванням від RTC або EXTI */
    low_power_pins_restore();
}
```
@tab cpp
```cpp
void enter_deep_sleep_cycle(LowPower::SleepManager& sleep_manager) noexcept
{
    {
        /* RAII-об'єкт ізолює піни при створенні та автоматично відновлює при виході з блоку */
        auto sleep_guard = sleep_manager.guard();

        /* Ядро засинає */
        asm volatile("wfi");
    }
    /* Тут усі піни вже гарантовано відновлені у вихідний робочий стан */
}
```
:::

## Специфіка систем на кристалі ESP32

Для мікроконтролерів сімейства ESP32 (ESP32-S3, ESP32-C3, ESP32-C6) керування виводами під час сну має архітектурну особливість: виводи поділені на стандартні цифрові GPIO та виводи домену RTC (RTC-GPIO). 

У стані глибокого сну (Deep Sleep) основне цифрове ядро та периферія повністю знеструмлюються, а стан звичайних виводів втрачається, переходячи у стан високого імпедансу. Якщо зовнішня схема вимагає утримання фіксованого логічного рівня під час сну (наприклад, для утримання силового ключа P-MOSFET у закритому стані напругою 3.3 В), такий вивід повинен належати до домену RTC-GPIO.

В ESP-IDF для цього застосовуються функції фіксації та ізоляції:

1. `rtc_gpio_isolate(gpio_num)` — повністю відключає внутрішні підтяжки та цифрові вхідні буфери RTC-піна для усунення наскрізних струмів витоку.
2. `gpio_hold_en(gpio_num)` та `gpio_deep_sleep_hold_en()` — апаратно фіксують поточний вихідний логічний стан виводу (рівень HIGH або LOW) на весь час перебування кристала в глибокому сні, запобігаючи мимовільному відкриттю силових ключів.

## Підводні камені та типові помилки реалізації

1. **Зависання входу в сон через активні прапорці переривань.** Якщо перед виконанням інструкції `WFI` у черзі контролера NVIC присутній незамаскований активний прапорець (pending interrupt), ядро миттєво прокидається без переходу тактового дерева в стан зупинки. Перед входом у сон рекомендується очищати прапорці зовнішніх переривань або застосовувати пару інструкцій `__disable_irq()` та `__enable_irq()` довкола `WFI`.
2. **Ізоляція піна пробудження.** Якщо вивід, призначений для пробудження за фронтом сигналу (наприклад, пін підключення акселерометра чи кнопки), випадково перевести в режим `GPIO_MODE_ANALOG`, вхідний тригер Шмітта відключається і мікроконтролер перетворюється на «цеглину», не реагуючи на зовнішні події до повного апаратного скидання живлення.
3. **Недостатній час розряду ємностей периферії.** Якщо після знеструмлення датчика силовими ключами не дочекатися падіння залишкової напруги на його блокувальних конденсаторах і почати перемикати сигнальні виводи, залишкова енергія може викликати замикання діодів захисту (тиристорний ефект або latch-up).
4. **Зависання шини I2C у стані розриву транзакції.** Якщо датчик був знеструмлений або переведений у сон у момент, коли він передавав біт підтвердження (ACK) і утримував лінію SDA в нулі, після пробудження шина I2C залишається заблокованою. Процедура відновлення вимагає генерації дев'яти тактових імпульсів на лінії SCL у режимі ручного перемикання GPIO (Bit-Banging) перед повторною ініціалізацією апаратного модуля I2C.

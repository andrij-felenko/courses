# ⚙️ Автономний драйвер периферії на голих регістрах

Для повного контролю над мікроконтролером без накладних витрат сторонніх бібліотек HAL розробники створюють компактні драйвери, що напряму маніпулюють бітами в регістрах. Бібліотеки рівня HAL часто додають багаторівневі перевірки вказівників, динамічний розрахунок зміщень і громіздкі структури зворотних викликів, що уповільнює реакцію на апаратні події та збільшує обсяг бінарного коду у Flash-пам'яті. Робота на рівні «голих регістрів» позбавлена цих недоліків: кожна дія є прозорою, передбачуваною за часом виконання й детермінованою до окремого такту шини.

Нижче наведено повністю завершений, автономний модуль керування виводом загального призначення (GPIO) та базовим апаратним таймером (на прикладі мікроконтролера архітектури ARM Cortex-M із шинною матрицею AHB/APB). Модуль не використовує жодних сторонніх заголовних файлів вендора чи бібліотек виробника кристала, покладаючись виключно на базові цілочисельні типи фіксованої ширини стандарту ISO C (`<stdint.h>`) та ISO C++ (`<cstdint>`).

## Архітектурний розподіл адрес і створення структур

Для взаємодії з апаратурою оголошуються структури з обов'язковим модифікатором `volatile`, де порядок і розмір полів строго відповідають карті зміщень регістрів у технічній документації на кристал. Завдяки модифікатору `volatile` компілятор позбавляється права оптимізувати або об'єднувати звернення до полів цієї структури: кожне читання чи запис перетворюється на реальну машинну інструкцію системної шини.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові адреси шинних контролерів і периферійних модулів */
#define PERIPH_BASE        (0x40000000UL)
#define APB1PERIPH_BASE    (PERIPH_BASE)
#define AHB1PERIPH_BASE    (PERIPH_BASE + 0x00020000UL)

#define RCC_BASE           (AHB1PERIPH_BASE + 0x3800UL)
#define GPIOA_BASE         (AHB1PERIPH_BASE + 0x0000UL)
#define TIM6_BASE          (APB1PERIPH_BASE + 0x1000UL)

/* Структура контролера тактування (RCC) */
typedef struct {
    volatile uint32_t CR;            /* +0x00: Тактування та PLL */
    volatile uint32_t PLLCFGR;       /* +0x04: Конфігурація PLL */
    volatile uint32_t CFGR;          /* +0x08: Дільники шин */
    volatile uint32_t CIR;           /* +0x0C: Переривання тактування */
    volatile uint32_t AHB1RSTR;      /* +0x10: Скидання AHB1 */
    volatile uint32_t AHB2RSTR;      /* +0x14: Скидання AHB2 */
    volatile uint32_t AHB3RSTR;      /* +0x18: Скидання AHB3 */
    uint32_t          RESERVED0;     /* +0x1C: Зарезервовано */
    volatile uint32_t APB1RSTR;      /* +0x20: Скидання APB1 */
    volatile uint32_t APB2RSTR;      /* +0x24: Скидання APB2 */
    uint32_t          RESERVED1[2];  /* +0x28 - +0x2C */
    volatile uint32_t AHB1ENR;       /* +0x30: Увімкнення тактування AHB1 */
    volatile uint32_t AHB2ENR;       /* +0x34: Увімкнення тактування AHB2 */
    volatile uint32_t AHB3ENR;       /* +0x38: Увімкнення тактування AHB3 */
    uint32_t          RESERVED2;     /* +0x3C */
    volatile uint32_t APB1ENR;       /* +0x40: Увімкнення тактування APB1 */
    volatile uint32_t APB2ENR;       /* +0x44: Увімкнення тактування APB2 */
} RCC_TypeDef;

/* Структура модуля GPIO */
typedef struct {
    volatile uint32_t MODER;         /* +0x00: Режим роботи пінів (2 біти на пін) */
    volatile uint32_t OTYPER;        /* +0x04: Тип виходу (Push-Pull / Open-Drain) */
    volatile uint32_t OSPEEDR;       /* +0x08: Швидкість наростання фронту */
    volatile uint32_t PUPDR;         /* +0x0C: Внутрішні підтяжки Pull-Up / Pull-Down */
    volatile uint32_t IDR;           /* +0x10: Регістр вхідних даних (ReadOnly) */
    volatile uint32_t ODR;           /* +0x14: Регістр вихідних даних (ReadWrite) */
    volatile uint32_t BSRR;          /* +0x18: Атомарне встановлення / скидання (WriteOnly) */
    volatile uint32_t LCKR;          /* +0x1C: Блокування конфігурації */
    volatile uint32_t AFR[2];        /* +0x20 - +0x24: Альтернативні функції пінів */
} GPIO_TypeDef;

/* Структура базового таймера (TIM6) */
typedef struct {
    volatile uint32_t CR1;           /* +0x00: Регістр керування 1 (вмикання, автоперезавантаження) */
    volatile uint32_t CR2;           /* +0x04: Регістр керування 2 (тригери) */
    uint32_t          RESERVED0;     /* +0x08 */
    volatile uint32_t DIER;          /* +0x0C: Дозвіл переривань та DMA */
    volatile uint32_t SR;            /* +0x10: Регістр статусу (прапорці оновлення) */
    volatile uint32_t EGR;           /* +0x14: Генерація подій */
    uint32_t          RESERVED1[3];  /* +0x18 - +0x20 */
    volatile uint32_t CNT;           /* +0x24: Лічильник поточного значення */
    volatile uint32_t PSC;           /* +0x28: Дільник частоти (Prescaler) */
    volatile uint32_t ARR;           /* +0x2C: Межа автоперезавантаження */
} TIM_TypeDef;

#define RCC    ((RCC_TypeDef *)RCC_BASE)
#define GPIOA  ((GPIO_TypeDef *)GPIOA_BASE)
#define TIM6   ((TIM_TypeDef *)TIM6_BASE)
```
```cpp
#include <cstdint>
#include <concepts>

/* Базові адреси периферійних блоків */
namespace MemoryMap {
    inline constexpr std::uintptr_t PeriphBase     = 0x40000000UL;
    inline constexpr std::uintptr_t Apb1Base       = PeriphBase;
    inline constexpr std::uintptr_t Ahb1Base       = PeriphBase + 0x00020000UL;

    inline constexpr std::uintptr_t RccBase        = Ahb1Base + 0x3800UL;
    inline constexpr std::uintptr_t GpioABase      = Ahb1Base + 0x0000UL;
    inline constexpr std::uintptr_t Tim6Base       = Apb1Base + 0x1000UL;
}

/* Шаблонна типізована обгортка апаратного регістра з нульовою ціною абстракції */
template <std::uintptr_t Address, typename T = std::uint32_t>
struct HardwareRegister {
    static void write(T value) noexcept {
        *reinterpret_cast<volatile T*>(Address) = value;
    }

    [[nodiscard]] static T read() noexcept {
        return *reinterpret_cast<volatile T*>(Address);
    }

    static void setBits(T mask) noexcept {
        *reinterpret_cast<volatile T*>(Address) = read() | mask;
    }

    static void clearBits(T mask) noexcept {
        *reinterpret_cast<volatile T*>(Address) = read() & ~mask;
    }
};

/* Опис зміщень регістрів GPIO */
struct GpioRegisters {
    volatile std::uint32_t MODER;
    volatile std::uint32_t OTYPER;
    volatile std::uint32_t OSPEEDR;
    volatile std::uint32_t PUPDR;
    volatile std::uint32_t IDR;
    volatile std::uint32_t ODR;
    volatile std::uint32_t BSRR;
    volatile std::uint32_t LCKR;
    volatile std::uint32_t AFR[2];
};

/* Опис зміщень регістрів базового таймера */
struct TimerRegisters {
    volatile std::uint32_t CR1;
    volatile std::uint32_t CR2;
    std::uint32_t          RESERVED0;
    volatile std::uint32_t DIER;
    volatile std::uint32_t SR;
    volatile std::uint32_t EGR;
    std::uint32_t          RESERVED1[3];
    volatile std::uint32_t CNT;
    volatile std::uint32_t PSC;
    volatile std::uint32_t ARR;
};
```
:::

## Покроковий процес ініціалізації периферії

Процедура запуску периферійного модуля складається з шести послідовних кроків, кожен із яких спирається на фізичну схемотехніку модуля на кристалі:

1. **Подача тактування на модуль**. Системний блок RCC (Reset and Clock Control) містить регістри дозволу тактування периферії (`AHB1ENR`, `APB1ENR`). Без увімкнення відповідного біта цифрова логіка модуля знеструмлена, а будь-яке звернення до його адрес викличе апаратну помилку шини `BusFault`.
2. **Захист від затримки поширення тактування (Read-back)**. Після запису в регістр контролера тактування шинний міст може витратити кілька тактів на увімкнення тактових дерев. Щоб наступні інструкції не звернулися до модуля, чиє тактування ще не стабілізувалося, виконується фіктивне зчитування того самого регістра тактування `(void)RCC->AHB1ENR;`.
3. **Конфігурація режиму роботи ліній (MODER)**. Для порту GPIO виконується маскування та встановлення двійкового коду режиму. Очищення бітів виконується логічним множенням із маскою нулів `&= ~`, після чого потрібне значення встановлюється логічним додаванням `|=`.
4. **Конфігурація типу виходу та підтяжок**. Регістр `OTYPER` налаштовує тип вихідного каскаду (Push-Pull чи Open-Drain), а регістр `PUPDR` підключає внутрішні резистори підтяжки номіналом 40 кОм.
5. **Налаштування таймера (Prescaler та Auto-Reload)**. Дільник частоти `PSC` знижує частоту шини до базового кроку (наприклад, 1 кГц), а регістр `ARR` задає період переповнення лічильника.
6. **Примусове завантаження тіньових регістрів (Event Generation)**. Запис у біт `UG` регістра `EGR` генерує апаратну подію оновлення, яка негайно переносить значення з буферного регістра `PSC` в активний лічильний регістр дільника без необхідності чекати першого циклу переповнення.

:::tabs
```c
/* Бітові маски контролера тактування */
#define RCC_AHB1ENR_GPIOAEN   (1UL << 0)
#define RCC_APB1ENR_TIM6EN    (1UL << 4)

/* Бітові маски таймера TIM6 */
#define TIM_CR1_CEN           (1UL << 0)
#define TIM_CR1_URS           (1UL << 2)
#define TIM_SR_UIF            (1UL << 0)
#define TIM_EGR_UG            (1UL << 0)

/* Ініціалізація виводу PA5 (світлодіод) */
void gpio_pa5_init(void) {
    /* 1. Увімкнути тактування порту GPIOA на шині AHB1 */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    /* Коротке читання назад для очікування завершення шинної транзакції */
    (void)RCC->AHB1ENR;

    /* 2. Налаштувати пін 5 на вихід (MODER5 = 01) */
    GPIOA->MODER &= ~(3UL << (5 * 2));   /* Очистити біти 11:10 */
    GPIOA->MODER |=  (1UL << (5 * 2));   /* Встановити режим 01 (General purpose output) */

    /* 3. Тип виходу: Push-Pull (0 у біті 5 регістра OTYPER) */
    GPIOA->OTYPER &= ~(1UL << 5);

    /* 4. Швидкість фронту: Low speed (00 у бітах 11:10 OSPEEDR) */
    GPIOA->OSPEEDR &= ~(3UL << (5 * 2));

    /* 5. Без підтяжок: No pull-up, no pull-down (00 у бітах 11:10 PUPDR) */
    GPIOA->PUPDR &= ~(3UL << (5 * 2));
}

/* Атомарне керування станом виводу PA5 */
void gpio_pa5_set_high(void) {
    /* Запис 1 у біт 5 регістра BSRR вмикає вихід без зміни інших пінів */
    GPIOA->BSRR = (1UL << 5);
}

void gpio_pa5_set_low(void) {
    /* Запис 1 у біт (5 + 16) регістра BSRR скидає вихід в 0 */
    GPIOA->BSRR = (1UL << (5 + 16));
}

/* Ініціалізація таймера TIM6 для відліку мілісекунд (за тактової частоти шини APB1 = 16 МГц) */
void timer6_init_ms(void) {
    /* 1. Увімкнути тактування таймера TIM6 на шині APB1 */
    RCC->APB1ENR |= RCC_APB1ENR_TIM6EN;
    (void)RCC->APB1ENR;

    /* 2. Встановити дільник Prescaler: 16 000 000 / 16 000 = 1000 Гц (1 такт = 1 мс) */
    TIM6->PSC = 16000UL - 1UL;

    /* 3. Встановити максимальний період (Auto-Reload) */
    TIM6->ARR = 0xFFFFUL;

    /* 4. Згенерувати подію оновлення для негайного завантаження значення дільника у тіньовий регістр */
    TIM6->EGR |= TIM_EGR_UG;

    /* 5. Очистити прапорець оновлення, піднятий примусовою подією UG */
    TIM6->SR &= ~TIM_SR_UIF;

    /* 6. Запустити таймер (Counter Enable) */
    TIM6->CR1 |= TIM_CR1_CEN;
}

/* Блокуюча мілісекундна затримка з коректною обробкою переповнення лічильника */
void delay_ms(uint16_t ms) {
    uint16_t start = (uint16_t)TIM6->CNT;
    while ((uint16_t)(TIM6->CNT - start) < ms) {
        /* Циклічна арифметика беззнакових чисел гарантує правильний відлік навіть при переході через 0xFFFF */
    }
}
```
```cpp
#include <cstdint>

enum class PinMode : std::uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

enum class OutputType : std::uint32_t {
    PushPull  = 0,
    OpenDrain = 1
};

class GpioPin {
private:
    GpioRegisters* const port_;
    const std::uint8_t pin_;

public:
    constexpr GpioPin(std::uintptr_t portBase, std::uint8_t pin) noexcept
        : port_(reinterpret_cast<GpioRegisters*>(portBase)), pin_(pin) {}

    void configure(PinMode mode, OutputType otype) const noexcept {
        const std::uint32_t shift2 = pin_ * 2;

        /* Налаштування режиму (MODER) */
        port_->MODER = (port_->MODER & ~(0b11UL << shift2)) | (static_cast<std::uint32_t>(mode) << shift2);

        /* Налаштування типу виходу (OTYPER) */
        if (otype == OutputType::OpenDrain) {
            port_->OTYPER |= (1UL << pin_);
        } else {
            port_->OTYPER &= ~(1UL << pin_);
        }
    }

    /* Атомарне встановлення високого рівня (Set) */
    void setHigh() const noexcept {
        port_->BSRR = (1UL << pin_);
    }

    /* Атомарне встановлення низького рівня (Reset) */
    void setLow() const noexcept {
        port_->BSRR = (1UL << (pin_ + 16));
    }
};

class HardwareTimer {
private:
    TimerRegisters* const timer_;

public:
    explicit constexpr HardwareTimer(std::uintptr_t baseAddress) noexcept
        : timer_(reinterpret_cast<TimerRegisters*>(baseAddress)) {}

    void initPrescaler(std::uint32_t busClockHz, std::uint32_t targetFrequencyHz) const noexcept {
        timer_->PSC = (busClockHz / targetFrequencyHz) - 1UL;
        timer_->ARR = 0xFFFFUL;
        timer_->EGR = 1UL;              /* Примусове оновлення тіньового регістра */
        timer_->SR  = 0UL;              /* Скидання прапорця оновлення */
        timer_->CR1 |= (1UL << 0);       /* Вмикання лічильника (CEN) */
    }

    void delayMilliseconds(std::uint16_t ms) const noexcept {
        const auto start = static_cast<std::uint16_t>(timer_->CNT);
        while (static_cast<std::uint16_t>(timer_->CNT - start) < ms) {
            /* Опитування апаратного регістра з обробкою переходу через нуль */
        }
    }
};
```
:::

## Аналіз крайових випадків, переривання та налагодження

При практичній експлуатації драйвера на рівні регістрів важливо враховувати специфічні апаратні крайові випадки:

1. **Переповнення лічильника (Counter Wrap-around)**. Якщо під час виконання затримки значення регістра `CNT` перетинає значення `ARR` (`0xFFFF`) і скидається в `0`, наївна перевірка `while (CNT < target)` призведе до зависання на цілий додатковий цикл лічильника (понад 65 секунд затримки). Використання беззнакової різниці `(uint16_t)(TIM6->CNT - start)` повністю вирішує проблему переповнення завдяки властивостям двійкової арифметики за модулем `2¹⁶`.
2. **Захист налагоджувальних ліній (JTAG / SWD)**. Виводи PA13 (JTMS/SWDIO), PA14 (JTCK/SWCLK) та PB3 (JTDO) після скидання чипа перебувають у режимі альтернативної функції для забезпечення зв'язку з апаратним програматором-відлагоджувачем. Випадкове переналаштування порту `GPIOA` через груповий запис у `MODER` без маскування цих ліній миттєво відключає чип від відлагоджувача (SWD Fault). Для безпечної зміни конфігурації використовують побітове маскування з урахуванням вихідного стану регістра.
3. **Синхронізація шинних буферів у перериваннях**. При переході від опитування до обробки подій через переривання скидання прапорця події в регістрі статусу `SR` повинно супроводжуватися операцією читання назад (Read-back):

:::tabs
```c
/* Обробник переривання таймера TIM6 на мові C */
void TIM6_DAC_IRQHandler(void) {
    if (TIM6->SR & TIM_SR_UIF) {
        /* Очищення прапорця переривання */
        TIM6->SR &= ~TIM_SR_UIF;
        
        /* Читання назад для очікування очищення лінії в NVIC */
        (void)TIM6->SR;

        /* Корисна дія: перемикання стану виводу */
        GPIOA->BSRR = (1UL << 5);
    }
}
```
```cpp
/* Обробник переривання таймера TIM6 на мові C++ */
extern "C" void TIM6_DAC_IRQHandler() noexcept {
    auto* timer = reinterpret_cast<TimerRegisters*>(MemoryMap::Tim6Base);
    auto* gpio  = reinterpret_cast<GpioRegisters*>(MemoryMap::GpioABase);

    if (timer->SR & 0x01UL) {
        timer->SR &= ~0x01UL;
        (void)timer->SR; // Синхронізація шини APB

        gpio->BSRR = (1UL << 5);
    }
}
```
:::

Без операції `(void)TIM6->SR;` сигнал скидання прапорця може затриматися в шинному мості APB через буферизацію збереження в ядрі. Внаслідок цього контролер переривань (NVIC) викличе функцію обробника вдруге на ту саму подію таймера (так званий баг хибного ланцюжкового виклику — tail-chaining race).

4. **Апаратний моніторинг сигналів логічним аналізатором**. При прямому записі в регістр `BSRR` час відпрацювання інструкції складає лише 1 такт процесора (близько 6 наносекунд на частоті 168 МГц). Завдяки відсутності проміжних шарів HAL джитер (тремтіння фронтів сигналу) практично дорівнює нулю, що дозволяє формувати високошвидкісні часові діаграми протоколів 1-Wire, WS2812 або програмного SPI.

Код на мові C++ завдяки використанню `constexpr` конструкторів та інлайн-методів повністю оптимізується компілятором: об'єктна обгортка розгортається в ті самі одинарні інструкції запису в пам'ять, що й чистий C, але забезпечує строгий контроль типів на етапі компіляції та унеможливлює помилкову передачу недійсних числових параметрів.

# ⚙️ Практичне вимірювання латентності переривань: DWT та осцилограф

Вимірювання реальної латентності переривання — це спосіб перевірити теоретичні розрахунки на живому кремнії. Документація ARM заявляє 12 тактів для Cortex-M3/M4, але в реальній платі між фізичним фронтом напруги на ніжці мікроконтролера та зміною стану вихідного піна в обробнику завжди виникають додаткові затримки: ємність ліній, синхронізатори GPIO, стан конвеєра та проміжні шинні мости. Цей проєкт містить два взаємодоповнювальні методи вимірювання — апаратний (за допомогою осцилографа) та внутрішньопроцесорний (за допомогою лічильника циклів DWT) — із повними прикладами на C та ідіоматичному C++.

## Архітектура стенда вимірювання

Для вимірювання потрібні два фізичні виводи мікроконтролера:

1. **Вхідний пін (Trigger In, наприклад `PA0`):** налаштований на зовнішнє переривання EXTI по наростаючому фронту. На нього подається тестовий прямокутний імпульс від генератора сигналів або таймера.
2. **Вихідний пін (Response Out, наприклад `PA1`):** швидкісний GPIO-вихід, який обробник `EXTI0_IRQHandler` перемикає в стан логічної одиниці найпершою інструкцією.

```
+-------------------+             +----------------------------------+
| Генератор сигналу | ---(Фронт)->| PA0 (Вхід EXTI)                  |
|  (або Таймер МК)  |             |                                  |
+-------------------+             |  Cortex-M4 Ядро                  |
         |                        |   1. Синхронізація (2T)          |
         | Канал 1                |   2. NVIC Арбітраж (2T)          |
         v                        |   3. Auto-stacking + VTOR (6T)   |
  +--------------+                |   4. Fetch & ISR Entry (2T)      |
  |  Осцилограф  |                |   5. STR BSRR -> Вихід PA1       |
  |              |                |                                  |
  |   Канал 2    |                |                                  |
  +--------------+ <---(Відгук)---| PA1 (Вихідний строб)             |
                                  +----------------------------------+
```

Різниця в часі між фронтом на Каналі 1 та наростаючим фронтом на Каналі 2 на екрані осцилографа показує **повну системну затримку** (System-Level Latency), яка включає апаратну латентність ядра, затримку вхідного фільтра GPIO та затримку шини виводу.

---

## Метод 1: Вимірювання осцилографом на C та C++

Нижче наведено повний вихідний код ініціалізації та обробника переривання для сімейства STM32 (Cortex-M4).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Адреси базових регістрів для STM32F4 (AHB1: GPIOA, APB2: SYSCFG/EXTI) */
#define RCC_AHB1ENR   (*(volatile uint32_t *)0x40023830U)
#define RCC_APB2ENR   (*(volatile uint32_t *)0x40023844U)

#define GPIOA_MODER   (*(volatile uint32_t *)0x40020000U)
#define GPIOA_OSPEEDR (*(volatile uint32_t *)0x40020008U)
#define GPIOA_BSRR    (*(volatile uint32_t *)0x40020018U)

#define SYSCFG_EXTICR1 (*(volatile uint32_t *)0x40013808U)
#define EXTI_IMR      (*(volatile uint32_t *)0x40013C00U)
#define EXTI_RTSR     (*(volatile uint32_t *)0x40013C08U)
#define EXTI_PR       (*(volatile uint32_t *)0x40013C14U)

#define NVIC_ISER0    (*(volatile uint32_t *)0xE000E100U)

/* Ініціалізація виводів: PA0 (вхід EXTI), PA1 (надшвидкий вихід) */
void latency_gpio_init(void) {
    /* Вмикаємо тактування GPIOA та SYSCFG */
    RCC_AHB1ENR |= (1U << 0);
    RCC_APB2ENR |= (1U << 14);

    /* PA0: вхід (MODER[1:0] = 00) */
    GPIOA_MODER &= ~(3U << 0);

    /* PA1: вихід (MODER[3:2] = 01) з максимальною швидкістю (OSPEEDR[3:2] = 11) */
    GPIOA_MODER &= ~(3U << 2);
    GPIOA_MODER |= (1U << 2);
    GPIOA_OSPEEDR |= (3U << 2);

    /* Скидаємо PA1 в низький рівень */
    GPIOA_BSRR = (1U << (1 + 16));

    /* Налаштовуємо EXTI0 на лінію PA0 */
    SYSCFG_EXTICR1 &= ~0x000FU;

    /* Дозволяємо переривання по лінії 0 та вибираємо наростаючий фронт */
    EXTI_IMR |= (1U << 0);
    EXTI_RTSR |= (1U << 0);

    /* Дозволяємо вектор EXTI0 (IRQn = 6) у NVIC */
    NVIC_ISER0 = (1U << 6);
}

/* Обробник переривання EXTI0 */
void EXTI0_IRQHandler(void) {
    /* НАЙПЕРША ІНСТРУКЦІЯ: миттєво піднімаємо PA1 у логічну 1 через BSRR */
    GPIOA_BSRR = (1U << 1);

    /* Скидаємо прапорець переривання EXTI0 (запис 1 у PR очищає запит) */
    EXTI_PR = (1U << 0);

    /* Опускаємо PA1 назад для формування вимірювального імпульсу */
    GPIOA_BSRR = (1U << (1 + 16));
}
```
```cpp
#include <cstdint>
#include <span>
#include <concepts>

namespace mcu {

/* Типобезпечні структури апаратних регістрів */
struct GpioPort {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AF[2];
};

struct ExtiController {
    volatile uint32_t IMR;
    volatile uint32_t EMR;
    volatile uint32_t RTSR;
    volatile uint32_t FTSR;
    volatile uint32_t SWIER;
    volatile uint32_t PR;
};

struct RccController {
    volatile uint32_t CR;
    volatile uint32_t PLLCFGR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t AHB1RSTR;
    volatile uint32_t AHB2RSTR;
    volatile uint32_t AHB3RSTR;
    uint32_t reserved0;
    volatile uint32_t APB1RSTR;
    volatile uint32_t APB2RSTR;
    uint32_t reserved1[2];
    volatile uint32_t AHB1ENR;
    volatile uint32_t AHB2ENR;
    volatile uint32_t AHB3ENR;
    uint32_t reserved2;
    volatile uint32_t APB1ENR;
    volatile uint32_t APB2ENR;
};

/* Апаратні адреси периферії STM32F4 */
inline auto& rcc   = *reinterpret_cast<RccController*>(0x40023800U);
inline auto& gpioa = *reinterpret_cast<GpioPort*>(0x40020000U);
inline auto& exti  = *reinterpret_cast<ExtiController*>(0x40013C00U);
inline auto& nvic_iser0 = *reinterpret_cast<volatile uint32_t*>(0xE000E100U);

/* RAII-контролер імпульсу вимірювання */
class LatencyBenchmark {
public:
    static void init() noexcept {
        /* Увімкнення тактування шин AHB1 (GPIOA) та APB2 (SYSCFG) */
        rcc.AHB1ENR |= (1U << 0);
        rcc.APB2ENR |= (1U << 14);

        /* Налаштування PA0 як входу */
        gpioa.MODER &= ~(3U << 0);

        /* Налаштування PA1 як швидкісного виходу */
        gpioa.MODER &= ~(3U << 2);
        gpioa.MODER |= (1U << 2);
        gpioa.OSPEEDR |= (3U << 2);

        /* Початковий низький рівень на PA1 */
        gpioa.BSRR = (1U << (1 + 16));

        /* Налаштування маски переривань EXTI */
        exti.IMR |= (1U << 0);
        exti.RTSR |= (1U << 0);

        /* Увімкнення переривання в NVIC */
        nvic_iser0 = (1U << 6);
    }

    [[gnu::always_inline]] static inline void trigger_high() noexcept {
        gpioa.BSRR = (1U << 1);
    }

    [[gnu::always_inline]] static inline void trigger_low() noexcept {
        gpioa.BSRR = (1U << (1 + 16));
    }

    [[gnu::always_inline]] static inline void clear_exti() noexcept {
        exti.PR = (1U << 0);
    }
};

} // namespace mcu

/* C++ обробник переривання */
extern "C" void EXTI0_IRQHandler() {
    /* Миттєвий строб без накладних витрат виклику функцій */
    mcu::LatencyBenchmark::trigger_high();
    mcu::LatencyBenchmark::clear_exti();
    mcu::LatencyBenchmark::trigger_low();
}
```
:::

---

## Метод 2: Внутрішньопроцесорний вимір через лічильник DWT

Блок трасування DWT (Data Watchpoint and Trace) містить апаратний 32-бітний лічильник `CYCCNT`, який інкрементується кожен такт ядра без залучення системних шин. Для вимірювання генерується програмне переривання через NVIC, фіксується початковий такт і порівнюється зі значенням усередині обробника.

:::tabs
```c
#include <stdint.h>

/* Регістри трасування Cortex-M (CoreDebug та DWT) */
#define CoreDebug_DEMCR (*(volatile uint32_t *)0xE000EDFCU)
#define DWT_CTRL        (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT      (*(volatile uint32_t *)0xE0001004U)

#define NVIC_ISPR0      (*(volatile uint32_t *)0xE000E200U)
#define NVIC_ISER0      (*(volatile uint32_t *)0xE000E100U)

static volatile uint32_t g_t_start = 0;
static volatile uint32_t g_t_isr = 0;
static volatile uint32_t g_measured_latency = 0;
static volatile uint32_t g_dwt_overhead = 0;

void dwt_init(void) {
    /* 1. Дозволяємо роботу блоку трасування (біт TRCENA = 24 в DEMCR) */
    CoreDebug_DEMCR |= (1U << 24);

    /* 2. Скидаємо лічильник циклів у 0 */
    DWT_CYCCNT = 0;

    /* 3. Вмикаємо лічильник циклів (біт CYCCNTENA = 0 в DWT_CTRL) */
    DWT_CTRL |= (1U << 0);

    /* Дозволяємо переривання EXTI0 (номер 6) */
    NVIC_ISER0 = (1U << 6);

    /* Калібрування накладних витрат самого читання DWT */
    uint32_t t1 = DWT_CYCCNT;
    uint32_t t2 = DWT_CYCCNT;
    g_dwt_overhead = t2 - t1;
}

void measure_software_latency(void) {
    /* Захоплюємо стартовий час і негайно виставляємо Pending у NVIC */
    g_t_start = DWT_CYCCNT;
    NVIC_ISPR0 = (1U << 6);

    /* Бар'єр пам'яті для гарантії порядку запису */
    __asm volatile("dsb" ::: "memory");
    __asm volatile("isb" ::: "memory");
}

/* Обробник переривання для DWT-тесту */
void EXTI0_IRQHandler_DWT(void) {
    /* Перший крок: негайно зафіксувати такти */
    g_t_isr = DWT_CYCCNT;

    /* Обчислення чистої різниці тактів з урахуванням накладних витрат */
    g_measured_latency = (g_t_isr - g_t_start) - g_dwt_overhead;
}
```
```cpp
#include <cstdint>
#include <atomic>

namespace mcu::debug {

struct DwtUnit {
    volatile uint32_t CTRL;
    volatile uint32_t CYCCNT;
    volatile uint32_t CPICNT;
    volatile uint32_t EXCCNT;
    volatile uint32_t SLEEPCNT;
    volatile uint32_t LSUCNT;
    volatile uint32_t FOLDCNT;
    volatile uint32_t PCSR;
};

inline auto& core_debug_demcr = *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
inline auto& dwt = *reinterpret_cast<DwtUnit*>(0xE0001000U);
inline auto& nvic_ispr0 = *reinterpret_cast<volatile uint32_t*>(0xE000E200U);
inline auto& nvic_iser0 = *reinterpret_cast<volatile uint32_t*>(0xE000E100U);

class CycleProfiler {
public:
    static void enable() noexcept {
        /* Дозвіл трасування (TRCENA) */
        core_debug_demcr |= (1U << 24);
        dwt.CYCCNT = 0;
        dwt.CTRL |= (1U << 0);
        nvic_iser0 = (1U << 6);

        /* Визначення базової затримки читання регістра */
        const uint32_t t1 = dwt.CYCCNT;
        const uint32_t t2 = dwt.CYCCNT;
        overhead_ = t2 - t1;
    }

    [[nodiscard, gnu::always_inline]] static inline uint32_t now() noexcept {
        return dwt.CYCCNT;
    }

    [[nodiscard]] static inline uint32_t overhead() noexcept {
        return overhead_;
    }

    static inline void trigger_irq(uint8_t irq_num) noexcept {
        nvic_ispr0 = (1U << irq_num);
        asm volatile("dsb 0xF" ::: "memory");
        asm volatile("isb 0xF" ::: "memory");
    }

private:
    static inline uint32_t overhead_{0};
};

/* Збереження результатів профілювання */
struct LatencyReport {
    uint32_t start_cycles{0};
    uint32_t isr_entry_cycles{0};
    uint32_t total_latency{0};
};

inline LatencyReport global_report{};

} // namespace mcu::debug

extern "C" void EXTI0_IRQHandler_DWT_Cpp() {
    const uint32_t entry = mcu::debug::CycleProfiler::now();
    mcu::debug::global_report.isr_entry_cycles = entry;
    mcu::debug::global_report.total_latency = (entry - mcu::debug::global_report.start_cycles) 
                                            - mcu::debug::CycleProfiler::overhead();
}
```
:::

---

## Детальний аналіз накладних витрат і джерел похибки

Під час зіставлення результатів між осцилографом та внутрішнім лічильником DWT розробник стикається з типовими розбіжностями. На практиці на мікроконтролері STM32F401 (частота 84 МГц) осцилограф фіксує **18–22 такти** (214–262 нс), тоді як DWT показує **14–16 тактів**.

Розгляньмо, куди саме витрачаються такти на кожному фізичному кроці:

```
+-------------------------------------------------------------+----------+
| Компонент затримки                                          | Такти    |
+-------------------------------------------------------------+----------+
| 1. Апаратна латентність NVIC і автостекінг (базова)         | 12 тактів|
| 2. Синхронізатор фронту на вході GPIO (EXTI edge detector)  | +2 такти |
| 3. Затримка конвеєра при вибірці інструкції LDR / STR BSRR  | +2 такти |
| 4. Затримка мосту шини APB/AHB при записі в регістр BSRR    | +2 такти |
| 5. Прохід через вихідний каскадний драйвер GPIO (Slew rate) | ~5–10 нс |
+-------------------------------------------------------------+----------+
| Фактичний час відгуку на осцилографі                        | 18–20 T  |
+-------------------------------------------------------------+----------+
```

### Фізичні причини затримок:

1. **Затримка синхронізації вхідного тригера:** Сигнал на ніжці `PA0` не потрапляє в NVIC миттєво. Щоб захистити цифрову логіку ядра від метастабільності, контролер `EXTI` затримує наростаючий фронт на два такти шини APB2.
2. **Шинна буферизація запису:** Інструкція `STR` в тілі обробника записує біт у регістр `GPIOA->BSRR`. Однак зміна електричного потенціалу на фізичному виводі `PA1` стається лише після того, як транзакція пройде шинний інтерконект AHB1 та потрапить у вихідні транзистори порту.
3. **Ємнісне навантаження щупа осцилографа:** Звичайний пасивний щуп осцилографа з дільником 1:10 вносить паразитну ємність близько 10–15 пФ. Разом із внутрішнім опором вихідного каскаду мікроконтролера це утворює RC-ланцюг, що затягує швидкість наростання фронту (Slew Rate) на додаткові 3–8 нс. Для надточних вимірювань слід використовувати активні щупи або мінімізувати довжину земляного провідника (використовувати пружинний земляний контакт замість довгого дроту з крокодилом).
4. **Рівень оптимізації компілятора:** При компіляції з прапорцем `-O0` компілятор перед записом у BSRR генерує зайві інструкції прологу (збереження покажчика фрейму `R7`, вирівнювання стека). При оптимізації `-O2` або `-O3` першою виконуваною інструкцією стає прямий `STR R1, [R0]`, що зменшує час до мінімуму.
5. **Роль бар'єрів пам'яті (DSB та ISB):** Інструкція `DSB` (Data Synchronization Barrier) гарантує, що запис у регістр `NVIC_ISPR0` завершився на рівні шинного контролера до того, як ядро продовжить виконання. Інструкція `ISB` (Instruction Synchronization Barrier) скидає конвеєр вибірки команд, примушуючи ядро негайно перевірити наявність активних переривань. Без цих бар'єрів запис може затриматися в буфері запису (Store Buffer) ядра на 1–3 такти, створюючи штучний джитер у тестах.
6. **Налаштування тригера осцилографа:** Для точного зіставлення часових інтервалів поріг спрацьовування тригера осцилографа (Trigger Level) слід виставляти рівно на рівні 50% амплітуди логічного сигналу (1.65 В для 3.3 В логіки). Також слід вимкнути обмеження смуги пропускання 20 MHz Bandwidth Limit на осцилографі, щоб не спотворювати швидкі фронти з часом наростання менше 2 нс.
7. **Вплив вкладених переривань і SysTick:** Якщо під час вимірювань активний системний таймер SysTick або інші периферійні джерела, випадковий збіг у часі призводить до виникнення Late Arrival або вкладеного витіснення. Для отримання чистого базового значення латентності на час тестування слід тимчасово вимкнути всі фонові таймери або встановити досліджуваному вектору найвищий пріоритет (рівень 0).

### Зведена таблиця вимірювань за різних конфігурацій

Нижче наведено результати практичних тестів на мікроконтролері Cortex-M4 (STM32F4, 84 МГц, 2 WS Flash):

| Конфігурація пам'яті та коду | Рівень оптимізації | Замір DWT (такти) | Замір осцилографа (такти / нс) |
| :--- | :--- | :--- | :--- |
| Flash (з увімкненим кешем ART) | `-O3` | 14 тактів | 19 тактів (226 нс) |
| Flash (без кешу, з промахом) | `-O3` | 18 тактів | 23 такти (274 нс) |
| Вектори й ISR у SRAM (0 WS) | `-O3` | 12 тактів | 16 тактів (190 нс) |
| Flash (без оптимізації) | `-O0` | 21 такт | 28 тактів (333 нс) |

Як свідчать результати, перенесення таблиці векторів `VTOR` та тіла ISR у швидку внутрішню пам'ять SRAM або CCMRAM дозволяє досягти абсолютно детермінованого відгуку, наближеного до теоретичної межі в 12 тактів.

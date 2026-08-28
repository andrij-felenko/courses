# ⚙️ Виробничий драйвер тактування на регістрах із CSS

Виробничий драйвер тактової системи виконує поетапну ініціалізацію зовнішнього кварцового генератора (HSE), обчислює та програмує затримки Flash-пам'яті, налаштовує контур фазового автопідстроювання частоти (PLL) та активує апаратну систему захисту тактування (Clock Security System) без ризику нескінченного блокування процесора при апаратних збоях.

На відміну від навчальних прикладів, де очікування прапорців готовності часто записують у вигляді нескінченного циклу `while (!(RCC->CR & RCC_CR_HSERDY))`, промисловий код повинен гарантувати детермінований час виходу з підпрограми за таймаутом і мати аварійний сценарій роботи на внутрішньому RC-генераторі (HSI) у разі фізичного пошкодження кварцу.

## Архітектурні етапи підняття тактової системи

Повний цикл переведення мікроконтролера на максимальну робочу частоту складається з послідовних кроків, кожен із яких спирається на апаратний стан попереднього:

1. **Конфігурація Flash-контролера та живлення ядра:** Перш ніж підвищити частоту тактування, необхідно забезпечити, щоб матриця Flash-пам'яті встигала вичитувати інструкції. Для роботи на частоті 168 МГц при напрузі живлення 3.3 В вимагається встановити 5 тактів очікування (5 Wait States) у регістрі `FLASH_ACR`. Одночасно активуються блоки попередньої вибірки (Prefetch) та кешування інструкцій і даних (ART Accelerator).
2. **Запуск зовнішнього генератора HSE:** У регістрі `RCC_CR` встановлюється біт `HSEON`. Генератор Пірса починає розгойдувати кварцовий кристал. Програма входить у цикл очікування прапорця `HSERDY` із захисним лічильником таймауту.
3. **Налаштування переддільників шин AHB, APB1, APB2:** У регістрі `RCC_CFGR` конфігуруються коефіцієнти ділення для системних магістралей. Для шини APB1 встановлюється дільник `/4` (частота 42 МГц при ліміті 45 МГц), для шини APB2 — дільник `/2` (частота 84 МГц при ліміті 90 МГц), для шини AHB — дільник `/1` (168 МГц).
4. **Запис коефіцієнтів контуру PLL:** У регістр `RCC_PLLCFGR` записуються розраховані значення дільників `M`, `N`, `P`, `Q` та обирається джерело тактування HSE.
5. **Запуск та стабілізація PLL:** Встановлюється біт `PLLON` у регістрі `RCC_CR`. Програма очікує підняття прапорця `PLLRDY`, що сигналізує про завершення фазового захоплення контуру.
6. **Перемикання системного мультиплексора SYSCLK:** У біти `SW` регістра `RCC_CFGR` записується код вибору джерела PLL. Програма очікує, поки апаратний комутатор підтвердить перемикання оновленням бітів статусу `SWS`.
7. **Активація системи Clock Security System (CSS):** Встановлення біта `CSSON` у регістрі `RCC_CR` вмикає безперервний апаратний моніторинг цілісності тактового сигналу HSE.

## Регістрова карта тактового дерева та Flash

Для прямого керування апаратними вузлами без сторонніх бібліотек використовуються системні регістри мікроконтролера:

- **`FLASH_ACR` (Flash Access Control Register):**
  - Біти `0..2` (`LATENCY`): Кількість тактів очікування (0–7 WS).
  - Біт `8` (`PRFTEN`): Дозвіл попередньої вибірки інструкцій (Prefetch Enable).
  - Біт `9` (`ICEN`): Увімкнення апаратного кешу інструкцій.
  - Біт `10` (`DCEN`): Увімкнення апаратного кешу константних даних.
  - Біти `11..12` (`ICRST`, `DCRST`): Скидання кеш-пам'яті при динамічній зміні частоти.
- **`PWR_CR` (Power Control Register):**
  - Біти `14..15` (`VOS`): Регулювання внутрішньої напруги ядра (Voltage Output Scaling). Для максимальних частот встановлюється режим високої продуктивності Scale 1 (1.2 В).
- **`RCC_CR` (Clock Control Register):**
  - Біт `0` (`HSION`) та біт `1` (`HSIRDY`): Увімкнення та статус готовності внутрішнього 16 МГц RC-генератора.
  - Біт `16` (`HSEON`) та біт `17` (`HSERDY`): Увімкнення та статус готовності кварцового резонатора HSE.
  - Біт `18` (`HSEBYP`): Вимкнення інвертора генератора Пірса для активного тактового сигналу (Bypass).
  - Біт `19` (`CSSON`): Увімкнення апаратної системи безпеки тактування CSS.
  - Біт `24` (`PLLON`) та біт `25` (`PLLRDY`): Керування та статус захоплення петлі PLL.
- **`RCC_PLLCFGR` (PLL Configuration Register):**
  - Біти `0..5` (`PLLM`): Вхідний дільник (2–63).
  - Біти `6..14` (`PLLN`): Множник генератора VCO (50–432).
  - Біти `16..17` (`PLLP`): Системний вихідний дільник ядра (`00` = /2, `01` = /4, `10` = /6, `11` = /8).
  - Біт `22` (`PLLSRC`): Джерело тактування PLL (`0` = HSI, `1` = HSE).
  - Біти `24..27` (`PLLQ`): Вихідний дільник шини USB 48 МГц (2–15).
- **`RCC_CFGR` (Clock Configuration Register):**
  - Біти `0..1` (`SW`): Запит на перемикання джерела `SYSCLK` (`00` = HSI, `01` = HSE, `10` = PLL).
  - Біти `2..3` (`SWS`): Статус поточного активного джерела `SYSCLK`.
  - Біти `4..7` (`HPRE`): Переддільник шини AHB (від `/1` до `/512`).
  - Біти `10..12` (`PPRE1`): Переддільник низькошвидкісної шини APB1 (від `/1` до `/16`).
  - Біти `13..15` (`PPRE2`): Переддільник високошвидкісної шини APB2 (від `/1` до `/16`).
- **`RCC_CIR` (Clock Interrupt Register):**
  - Біт `7` (`CSSF`): Прапорець переривання системи безпеки CSS (1 = зафіксовано зрив генерації кварцу).
  - Біт `23` (`CSSC`): Біт скидання прапорця переривання CSS (запис 1 очищує `CSSF`).

## Реалізація драйвера тактування

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Оголошення адрес регістрів CMSIS */
#define RCC_BASE        (0x40023800UL)
#define FLASH_R_BASE    (0x40023C00UL)
#define PWR_BASE        (0x40007000UL)

#define RCC_CR          (*(volatile uint32_t *)(RCC_BASE + 0x00))
#define RCC_PLLCFGR     (*(volatile uint32_t *)(RCC_BASE + 0x04))
#define RCC_CFGR        (*(volatile uint32_t *)(RCC_BASE + 0x08))
#define RCC_CIR         (*(volatile uint32_t *)(RCC_BASE + 0x0C))
#define FLASH_ACR       (*(volatile uint32_t *)(FLASH_R_BASE + 0x00))
#define PWR_CR          (*(volatile uint32_t *)(PWR_BASE + 0x00))

/* Бітові маски керування тактуванням */
#define RCC_CR_HSION         (1UL << 0)
#define RCC_CR_HSIRDY        (1UL << 1)
#define RCC_CR_HSEON         (1UL << 16)
#define RCC_CR_HSERDY        (1UL << 17)
#define RCC_CR_CSSON         (1UL << 19)
#define RCC_CR_PLLON         (1UL << 24)
#define RCC_CR_PLLRDY        (1UL << 25)

#define RCC_PLLCFGR_PLLSRC_HSE (1UL << 22)
#define RCC_CFGR_SW_PLL      (2UL << 0)
#define RCC_CFGR_SWS_PLL     (2UL << 2)
#define RCC_CFGR_HPRE_DIV1   (0UL << 4)
#define RCC_CFGR_PPRE1_DIV4  (5UL << 10)
#define RCC_CFGR_PPRE2_DIV2  (4UL << 13)

#define FLASH_ACR_LATENCY_5WS (5UL << 0)
#define FLASH_ACR_PRFTEN     (1UL << 8)
#define FLASH_ACR_ICEN       (1UL << 9)
#define FLASH_ACR_DCEN       (1UL << 10)

#define RCC_CIR_CSSF         (1UL << 7)
#define RCC_CIR_CSSC         (1UL << 23)

#define HSE_STARTUP_TIMEOUT  (0x5000UL)
#define PLL_STARTUP_TIMEOUT  (0x5000UL)

typedef enum {
    CLOCK_OK = 0,
    CLOCK_ERR_HSE_TIMEOUT,
    CLOCK_ERR_PLL_TIMEOUT,
    CLOCK_ERR_SW_TIMEOUT
} ClockStatus;

/* Повна ініціалізація тактування: Кварц 8 МГц -> SYSCLK 168 МГц */
ClockStatus SystemClock_Configure_8MHz_to_168MHz(void)
{
    volatile uint32_t timeout = 0;

    /* 1. Конфігурація затримок Flash: 5 тактів очікування + кеш інструкцій та даних */
    FLASH_ACR = FLASH_ACR_LATENCY_5WS | FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN;

    /* 2. Запуск зовнішнього високошвидкісного кварцу (HSE) */
    RCC_CR |= RCC_CR_HSEON;
    timeout = HSE_STARTUP_TIMEOUT;
    while (!(RCC_CR & RCC_CR_HSERDY)) {
        if (--timeout == 0) {
            /* Кварц не запустився: безпечно залишаємося на внутрішньому HSI */
            return CLOCK_ERR_HSE_TIMEOUT;
        }
    }

    /* 3. Налаштування дільників шин AHB (/1 = 168 МГц), APB1 (/4 = 42 МГц), APB2 (/2 = 84 МГц) */
    RCC_CFGR = RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;

    /* 4. Налаштування PLL: M=4 (f_PFD=2 МГц), N=168 (f_VCO=336 МГц), P=2 (SYSCLK=168 МГц), Q=7 (USB=48 МГц) */
    RCC_PLLCFGR = (4UL << 0) | (168UL << 6) | (0UL << 16) | RCC_PLLCFGR_PLLSRC_HSE | (7UL << 24);

    /* 5. Увімкнення PLL та очікування стабілізації фази */
    RCC_CR |= RCC_CR_PLLON;
    timeout = PLL_STARTUP_TIMEOUT;
    while (!(RCC_CR & RCC_CR_PLLRDY)) {
        if (--timeout == 0) {
            return CLOCK_ERR_PLL_TIMEOUT;
        }
    }

    /* 6. Перемикання системного джерела SYSCLK на вихід PLL */
    RCC_CFGR = (RCC_CFGR & ~0x03UL) | RCC_CFGR_SW_PLL;
    timeout = PLL_STARTUP_TIMEOUT;
    while ((RCC_CFGR & 0x0CUL) != RCC_CFGR_SWS_PLL) {
        if (--timeout == 0) {
            return CLOCK_ERR_SW_TIMEOUT;
        }
    }

    /* 7. Активація апаратного монітора захисту тактування (Clock Security System) */
    RCC_CR |= RCC_CR_CSSON;

    return CLOCK_OK;
}

/* Обробник немаскованого переривання при аварійному зриві генерації кварцу */
void NMI_Handler(void)
{
    /* Перевіряємо, чи переривання NMI викликане саме системою CSS */
    if (RCC_CIR & RCC_CIR_CSSF) {
        /* Апаратний автомат RCC уже самостійно перемкнув SYSCLK на HSI (16 МГц) і вимкнув PLL */
        
        /* Крок 1: Негайне знеструмлення критичних виконавчих механізмів */
        /* (вимкнення виходів ШІМ моторів, переведення силових ключів у безпечний стан) */
        
        /* Крок 2: Очищення прапорця переривання CSS записом одиниці у біт CSSC */
        RCC_CIR |= RCC_CIR_CSSC;

        /* Крок 3: Фіксація аварії в енергонезалежному журналі подій та безпечне зависання */
        while (1) {
            /* Очікування спрацьовування сторожового таймера (Watchdog) для повного перезапуску */
        }
    }
}
```
```cpp
#include <cstdint>
#include <concepts>

namespace bsp::clock {

/* Типобезпечні структури адрес та бітових полів */
inline constexpr std::uintptr_t rcc_base     = 0x40023800UL;
inline constexpr std::uintptr_t flash_r_base = 0x40023C00UL;

struct RccRegisters {
    volatile std::uint32_t cr;
    volatile std::uint32_t pllcfgr;
    volatile std::uint32_t cfgr;
    volatile std::uint32_t cir;
};

struct FlashRegisters {
    volatile std::uint32_t acr;
};

inline auto& rcc   = *reinterpret_cast<RccRegisters*>(rcc_base);
inline auto& flash = *reinterpret_cast<FlashRegisters*>(flash_r_base);

enum class Status : std::uint8_t {
    Ok = 0,
    HseTimeout,
    PllTimeout,
    SwitchTimeout
};

struct PllConfig {
    std::uint32_t m;
    std::uint32_t n;
    std::uint32_t p;
    std::uint32_t q;
};

class ClockController {
public:
    static constexpr std::uint32_t default_timeout = 0x5000UL;

    /* Розрахунок та встановлення тактування */
    static Status init_8mhz_to_168mhz() noexcept {
        // 1. Встановлюємо 5 тактів очікування Flash + кеш інструкцій та даних
        flash.acr = (5UL << 0) | (1UL << 8) | (1UL << 9) | (1UL << 10);

        // 2. Вмикаємо зовнішній кварц HSE
        rcc.cr |= (1UL << 16);
        if (!wait_for_bit(rcc.cr, (1UL << 17))) {
            return Status::HseTimeout;
        }

        // 3. Дільники шин: AHB /1, APB1 /4, APB2 /2
        rcc.cfgr = (0UL << 4) | (5UL << 10) | (4UL << 13);

        // 4. Запис дільників PLL (M=4, N=168, P=2, Q=7, Джерело=HSE)
        constexpr PllConfig cfg{ .m = 4, .n = 168, .p = 0 /* /2 */, .q = 7 };
        rcc.pllcfgr = (cfg.m << 0) | (cfg.n << 6) | (cfg.p << 16) | (1UL << 22) | (cfg.q << 24);

        // 5. Запуск PLL
        rcc.cr |= (1UL << 24);
        if (!wait_for_bit(rcc.cr, (1UL << 25))) {
            return Status::PllTimeout;
        }

        // 6. Перемикання на вихід PLL
        rcc.cfgr = (rcc.cfgr & ~0x03UL) | 0x02UL;
        if (!wait_for_mask(rcc.cfgr, 0x0CUL, 0x08UL)) {
            return Status::SwitchTimeout;
        }

        // 7. Вмикаємо апаратну безпеку тактування CSS
        rcc.cr |= (1UL << 19);

        return Status::Ok;
    }

private:
    static bool wait_for_bit(const volatile std::uint32_t& reg, std::uint32_t mask) noexcept {
        std::uint32_t t = default_timeout;
        while (!(reg & mask)) {
            if (--t == 0) return false;
        }
        return true;
    }

    static bool wait_for_mask(const volatile std::uint32_t& reg, std::uint32_t mask, std::uint32_t expected) noexcept {
        std::uint32_t t = default_timeout;
        while ((reg & mask) != expected) {
            if (--t == 0) return false;
        }
        return true;
    }
};

} // namespace bsp::clock

extern "C" void NMI_Handler() {
    using namespace bsp::clock;
    if (rcc.cir & (1UL << 7)) { // CSSF прапорець
        // Аварійний перехід у безпечний режим
        rcc.cir |= (1UL << 23); // Скидання CSSC
        while (true) {
            // Очікування перезапуску Watchdog
        }
    }
}
```
:::

## Динамічна зміна частоти під час роботи (DVFS)

У пристроях із батарейним живленням часто виникає потреба динамічно змінювати тактову частоту: скидати її до 16 МГц під час очікування подій для економії енергії та знову піднімати до 168 МГц для виконання важких обчислень (Dynamic Voltage and Frequency Scaling — DVFS).

При зниженні частоти порядок операцій є строго зворотним:

:::tabs
```c
/* 1. Перемикання мультиплексора SYSCLK на HSI */
RCC->CFGR = (RCC->CFGR & ~0x03UL) | 0x00UL; // SW = HSI
while ((RCC->CFGR & 0x0CUL) != 0x00UL);     // Очікування SWS = HSI

/* 2. Вимкнення контуру PLL для економії струму */
RCC->CR &= ~RCC_CR_PLLON;

/* 3. Зменшення затримок Flash-пам'яті */
FLASH_ACR = (FLASH_ACR & ~0x07UL) | 0x00UL; // 0 WS при 16 МГц
```
```cpp
// 1. Перемикання системного джерела SYSCLK на внутрішній HSI
rcc.cfgr = (rcc.cfgr & ~0x03UL) | 0x00UL;
while ((rcc.cfgr & 0x0CUL) != 0x00UL) {
    // Очікування підтвердження комутації
}

// 2. Вимкнення контуру PLL
rcc.cr &= ~(1UL << 24);

// 3. Зменшення затримок Flash-пам'яті до 0 WS
flash.acr = (flash.acr & ~0x07UL) | 0x00UL;
```
:::

Якщо спробувати зменшити затримки `FLASH_ACR` до перемикання `SYSCLK`, процесор зависне у винятку `HardFault`, оскільки ядро на частоті 168 МГц не зможе зчитати жодної інструкції з Flash при 0 WS.

## Апаратна верифікація тактового сигналу через вивід MCO

Осцилографічна перевірка роботи тактового дерева на реальній платі ніколи не виконується безпосередньо на виводах кварцового резонатора `OSC_IN` чи `OSC_OUT`. Ємність щупа (10–15 пФ) порушує баланс фаз у генераторі Пірса і зриває коливання.

Для безпечного вимірювання використовується апаратний тестовий вивід `MCO1` (Microcontroller Clock Output 1), розташований на піні `PA8`:

:::tabs
```c
/* Конфігурація виводу PA8 (MCO1) для моніторингу виходу PLL з діленням на 4 */
void MCO1_Init_PLL_Div4(void)
{
    /* 1. Увімкнення тактування порту GPIOA */
    RCC_AHB1ENR |= (1UL << 0);

    /* 2. Конфігурація піна PA8 в режим альтернативної функції (MODER8 = 10b) */
    GPIOA_MODER &= ~(3UL << 16);
    GPIOA_MODER |=  (2UL << 16);

    /* 3. Вибір альтернативної функції AF0 (MCO1) у регістрі AFR[1] */
    GPIOA_AFR1 &= ~(0xFUL << 0); // AF0

    /* 4. Налаштування виходу на максимальну швидкість (OSPEEDR8 = 11b) */
    GPIOA_OSPEEDR |= (3UL << 16);

    /* 5. Конфігурація вибору джерела MCO1 у регістрі RCC_CFGR:
          Біти 21..22 = 11b (джерело PLL), Біти 24..26 = 110b (дільник /4) */
    RCC_CFGR &= ~((3UL << 21) | (7UL << 24));
    RCC_CFGR |=  ((3UL << 21) | (6UL << 24));
}
```
```cpp
namespace bsp::debug {

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
};

inline auto& gpioa = *reinterpret_cast<GpioRegisters*>(0x40020000UL);
inline auto& rcc_ahb1enr = *reinterpret_cast<volatile std::uint32_t*>(0x40023830UL);

inline void init_mco1_pll_div4() noexcept {
    // 1. Тактування GPIOA
    rcc_ahb1enr |= (1UL << 0);

    // 2. Режим AF (10b) на піні PA8
    gpioa.moder &= ~(3UL << 16);
    gpioa.moder |=  (2UL << 16);

    // 3. AF0 (MCO1)
    gpioa.afr[1] &= ~(0xFUL << 0);

    // 4. High Speed (11b)
    gpioa.ospeedr |= (3UL << 16);

    // 5. Джерело PLL, дільник /4
    bsp::clock::rcc.cfgr &= ~((3UL << 21) | (7UL << 24));
    bsp::clock::rcc.cfgr |=  ((3UL << 21) | (6UL << 24));
}

} // namespace bsp::debug
```
:::

При правильній роботі драйвера на виводі `PA8` спостерігається ідеальний прямокутний цифровий сигнал CMOS із частотою `168 МГц / 4 = 42.0 МГц` та розмахом 3.3 В. Це дає стовідсоткову гарантію того, що контур PLL надійно зафіксував частоту і вся внутрішня цифрова магістраль працює на розрахункових параметрах.

# ⚙️ Діагностичний каркас і чеклист міграції прошивки на власне залізо

Діагностичний каркас безпечного запуску прошивки на щойно змонтованій власній платі запобігає апаратним зависанням процесора при відмові зовнішнього кварцового резонатора, витокам струму через висячі виводи входу та блокуванню системної шини при відключеному відлагоджувальному зонді. Коли код переносять з оціночної девборди (STM32 Nucleo чи ESP32 DevKit) на серійну друковану плату, звичні бібліотечні виклики ініціалізації часто входять у нескінченні цикли `while`, а неналаштовані виводи мікроконтролера споживають міліампери паразитного струму. Нижче наведено завершений модуль апаратної діагностики для Cortex-M (на базі CMSIS/STM32) та покроковий інженерний чеклист перевірки перед першим заливанням робочого бінарного образу.

---

## Чому бібліотечний код девборди ламається на власному залізі

Стандартний код ініціалізації периферії, згенерований графічними конфігураторами виробників мікроконтролерів (наприклад, STM32CubeMX для Cortex-M або ESP-IDF Project Generator), розрахований на «ідеальний стенд» — фірмову девборду. На девборді всі компоненти гарантовано змонтовані, номінали відповідають схемі, кварцові генератори мають стабільне збудження, а відлагоджувач завжди підключений до шини.

Коли той самий код запускають на першій тестовій ревізії власної друкованої плати, прошивка потрапляє в принципово інші умови:
1. **Відхилення параметрів генератора Пірса:** номінали навантажувальних конденсаторів зовнішнього кварцу можуть не відповідати паспортній ємності навантаження кристала `C_L`, а паразитна ємність трасування доріжок на новому стеку шарів PCB може перевищувати очікувану. За таких умов кварцовий автогенератор або зриває генерацію, або потребує значно більшого часу на запуск (десятків мілісекунд замість кількох сотень мікросекунд). Наївний виклик `SystemClock_Config()` зависає в очікуванні прапорця `HSERDY` назавжди.
2. **Паразитний наскрізний струм CMOS-інверторів:** у більших корпусах мікроконтролерів (наприклад, LQFP64 чи QFN48) значна частина виводів GPIO залишається нерозведеною на платі або призначена під майбутні розширення. За замовчуванням після скидання більшість чипів залишають виводи в режимі цифрового плаваючого входу (`Input Floating`). Плаваючий потенціал утворює наскрізний канал витоку між шиною живлення та землею, збільшуючи струм споживання в тисячі разів.
3. **Блокування логування за відсутності приймача:** стандартні функції форматованого виведення `printf`, перенаправлені в апаратний порт ITM або блокуючий передавач UART, входять у нескінченне очікування звільнення апаратного буфера, якщо зонд відключений або термінальна програма не підняла лінію готовності.

Діагностичний каркас вирішує ці проблеми через детерміновані, захищені таймаутами функції низькорівневої ініціалізації.

---

## Інтерфейсний контракт каркаса діагностики

Модуль надає автономний апаратний інтерфейс, який викликається на самому початку виконання функції `main()`, ще до старту планувальника завдань операційної системи реального часу (RTOS) та конфігурації високорівневих драйверів.

:::tabs
```c
/* bsp_bringup.h — Каркас безпечного запуску для Cortex-M / STM32 (C) */
#ifndef BSP_BRINGUP_H
#define BSP_BRINGUP_H

#include <stdint.h>
#include <stdbool.h>

/* Статуси джерела системного тактування */
typedef enum {
    CLOCK_SOURCE_HSI_FALLBACK = 0, /* Аварійний запуск від внутрішнього RC-генератора */
    CLOCK_SOURCE_HSE_CRYSTAL  = 1, /* Успішний запуск від зовнішнього кварцу */
    CLOCK_SOURCE_ERROR_TIMEOUT = 2  /* Таймаут збудження зовнішнього контуру */
} clock_source_status_t;

/* Причини останнього скидання мікроконтролера */
typedef enum {
    RESET_CAUSE_UNKNOWN      = 0,
    RESET_CAUSE_POWER_ON     = 1, /* Штатне увімкнення живлення (POR/PDR) */
    RESET_CAUSE_BROWNOUT     = 2, /* Аварійне просідання напруги живлення (BOR) */
    RESET_CAUSE_WATCHDOG     = 3, /* Спрацьовування сторожового таймера (IWDG/WWDG) */
    RESET_CAUSE_SOFTWARE     = 4  /* Програмне скидання ядра (NVIC_SystemReset) */
} reset_cause_t;

/* Структура телеметрії апаратного здоров'я плати */
typedef struct {
    uint32_t core_frequency_hz;       /* Реальна виміряна частота системної шини SYSCLK */
    clock_source_status_t clock_status; /* Поточне активне джерело тактування */
    reset_cause_t reset_reason;        /* Причина попереднього перезавантаження */
    bool debugger_connected;          /* Прапорець наявності активного підключення SWD/JTAG */
} hardware_health_t;

/* Безпечна ініціалізація тактування з фіксованим таймаутом і Fallback-механізмом */
clock_source_status_t bsp_clock_init_safe(uint32_t hse_timeout_cycles);

/* Паркування невикористаних виводів у режим Analog для усунення струмів витоку */
void bsp_gpio_park_unused_pins(void);

/* Неблокуюче виведення діагностичного повідомлення в ITM SWO або буфер логування */
void bsp_diag_log(const char* message);

/* Опитування регістра стану скидання RCC_CSR та збір діагностичного звіту */
hardware_health_t bsp_check_hardware_health(void);

#endif /* BSP_BRINGUP_H */
```
```cpp
// bsp_bringup.hpp — Ідіоматичний каркас безпечного запуску для C++20
#pragma once

#include <cstdint>
#include <string_view>
#include <expected>

namespace bsp {

enum class ClockSourceStatus : uint8_t {
    HsiFallback = 0,
    HseCrystal  = 1,
    ErrorTimeout = 2
};

enum class ResetCause : uint8_t {
    Unknown   = 0,
    PowerOn   = 1,
    Brownout  = 2,
    Watchdog  = 3,
    Software  = 4
};

struct HardwareHealth {
    uint32_t core_frequency_hz{0};
    ClockSourceStatus clock_status{ClockSourceStatus::HsiFallback};
    ResetCause reset_reason{ResetCause::Unknown};
    bool debugger_connected{false};
};

class BringupManager {
public:
    // Безпечний запуск системи тактування з обмеженим числом ітерацій
    [[nodiscard]] static std::expected<ClockSourceStatus, ClockSourceStatus> 
    init_clock_safe(uint32_t hse_timeout_cycles = 0x5000) noexcept;

    // Переведення плаваючих входів у безпечний аналоговий стан (енергозбереження)
    static void park_unused_pins() noexcept;

    // Неблокуюча передача рядка в доступний канал трасування (ITM/RTT/UART)
    static void log(std::string_view message) noexcept;

    // Опитування стану апаратного здоров'я плати та причин скидання
    [[nodiscard]] static HardwareHealth check_health() noexcept;
};

} // namespace bsp
```
:::

---

## Реалізація низькорівневих діагностичних механізмів

Наведений нижче код реалізує прямий доступ до апаратних регістрів мікроконтролера Cortex-M (на прикладі сімейства STM32F4/G4). Кожен модуль вирішує конкретну фізичну проблему роботи на власній платі.

:::tabs
```c
/* bsp_bringup.c — Реалізація мовою C */
#include "bsp_bringup.h"
#include <string.h>

/* Базові адреси регістрів периферії (RCC, GPIO, CoreDebug, ITM) */
#define RCC_BASE_ADDR      (0x40023800UL)
#define RCC_CR_REG         (*((volatile uint32_t*)(RCC_BASE_ADDR + 0x00UL)))
#define RCC_CFGR_REG       (*((volatile uint32_t*)(RCC_BASE_ADDR + 0x08UL)))
#define RCC_CSR_REG        (*((volatile uint32_t*)(RCC_BASE_ADDR + 0x74UL)))

#define GPIOA_MODER_REG    (*((volatile uint32_t*)(0x40020000UL)))
#define GPIOB_MODER_REG    (*((volatile uint32_t*)(0x40020400UL)))
#define GPIOC_MODER_REG    (*((volatile uint32_t*)(0x40020800UL)))

#define CoreDebug_DHCSR    (*((volatile uint32_t*)(0xE000EDF0UL)))
#define ITM_PORT0_U8       (*((volatile uint8_t*)(0xE0000000UL)))
#define ITM_TER_REG        (*((volatile uint32_t*)(0xE0000E00UL)))

/* Бітові маски керування тактуванням */
#define RCC_CR_HSION_BIT   (1UL << 0)
#define RCC_CR_HSIRDY_BIT  (1UL << 1)
#define RCC_CR_HSEON_BIT   (1UL << 16)
#define RCC_CR_HSERDY_BIT  (1UL << 17)

/* Бітові маски причин скидання в регістрі RCC_CSR */
#define RCC_CSR_RMVF_BIT   (1UL << 24) /* Очищення прапорців скидання */
#define RCC_CSR_BORRSTF    (1UL << 25) /* Brown-out Reset */
#define RCC_CSR_PORRSTF    (1UL << 27) /* Power-on Reset */
#define RCC_CSR_SFTRSTF    (1UL << 28) /* Software Reset */
#define RCC_CSR_IWDGRSTF   (1UL << 29) /* Independent Watchdog Reset */

#define DHCSR_C_DEBUGEN    (1UL << 0)  /* Прапорець підключеного відлагоджувача */

clock_source_status_t bsp_clock_init_safe(uint32_t hse_timeout_cycles) {
    /* 1. Гарантовано активуємо внутрішній високошвидкісний RC-генератор HSI (16 МГц).
          Внутрішній генератор не залежить від зовнішніх компонентів і завжди запускається. */
    RCC_CR_REG |= RCC_CR_HSION_BIT;
    while (!(RCC_CR_REG & RCC_CR_HSIRDY_BIT)) {
        /* HSI стабілізується за 2-4 мікросекунди */
    }

    /* 2. Спроба ввімкнення зовнішнього кварцового автогенератора HSE */
    RCC_CR_REG |= RCC_CR_HSEON_BIT;
    uint32_t countdown = hse_timeout_cycles;

    /* Обмежений цикл очікування готовності кварцу з декрементом лічильника */
    while (!(RCC_CR_REG & RCC_CR_HSERDY_BIT) && (countdown > 0)) {
        countdown--;
    }

    /* 3. Якщо кварц не вийшов на стабільний режим — переходимо на Fallback */
    if (countdown == 0) {
        /* Вимикаємо контур HSE, щоб не споживати зайвий струм через зірвану генерацію */
        RCC_CR_REG &= ~RCC_CR_HSEON_BIT;

        /* Перемикаємо мультиплексор SYSCLK на HSI */
        RCC_CFGR_REG &= ~0x03UL; /* SW = 00 (HSI) */
        while ((RCC_CFGR_REG & 0x0CUL) != 0x00UL) {
            /* Очікуємо підтвердження перемикання */
        }
        return CLOCK_SOURCE_HSI_FALLBACK;
    }

    /* 4. Кварц успішно стабілізувався — перемикаємо системну шину на HSE */
    RCC_CFGR_REG &= ~0x03UL;
    RCC_CFGR_REG |= 0x01UL; /* SW = 01 (HSE) */
    while ((RCC_CFGR_REG & 0x0CUL) != 0x04UL) {
        /* Очікуємо прапорець SWS = HSE */
    }

    return CLOCK_SOURCE_HSE_CRYSTAL;
}

void bsp_gpio_park_unused_pins(void) {
    /* Фізичний механізм: у режимі Analog (0x3 в MODER) цифровий тригер Шмітта 
       та інвертор вхідного каскаду апаратно відключаються від контактної площадки.
       Струм наскрізного витоку на висячих виводах падає з ~1 мА до < 1 нА. */

    uint32_t moder_a = GPIOA_MODER_REG;
    moder_a |= 0x03FFFFFFUL; /* Переводимо PA0-PA12 в Analog */

    /* КРИТИЧНО: Зберігаємо виводи відлагоджувача SWD:
       PA13 = SWDIO (MODER13 = 10, Alternate Function)
       PA14 = SWCLK (MODER14 = 10, Alternate Function) */
    moder_a &= ~(0x3UL << (13 * 2));
    moder_a |=  (0x2UL << (13 * 2));
    moder_a &= ~(0x3UL << (14 * 2));
    moder_a |=  (0x2UL << (14 * 2));
    GPIOA_MODER_REG = moder_a;

    /* Порти B і C повністю переводимо в аналоговий режим (0xFFFFFFFF) */
    GPIOB_MODER_REG = 0xFFFFFFFFUL;
    GPIOC_MODER_REG = 0xFFFFFFFFUL;
}

void bsp_diag_log(const char* message) {
    if (!message) return;

    /* Захист від зависання: запис у порт ITM виконується ТІЛЬКИ тоді,
       коли апаратний відлагоджувач фізично підключений до процесора 
       і дозволив трасування через регістр ITM_TER (Trace Enable Register). */
    if ((CoreDebug_DHCSR & DHCSR_C_DEBUGEN) && (ITM_TER_REG & 0x01UL)) {
        size_t len = strlen(message);
        for (size_t i = 0; i < len; ++i) {
            /* Неблокуючий запис одного байта в Stimulus Port 0 */
            ITM_PORT0_U8 = (uint8_t)message[i];
        }
    }
}

hardware_health_t bsp_check_hardware_health(void) {
    hardware_health_t health;
    uint32_t csr = RCC_CSR_REG;

    /* Визначаємо причину останнього скидання процесора */
    if (csr & RCC_CSR_BORRSTF) {
        health.reset_reason = RESET_CAUSE_BROWNOUT;
    } else if (csr & RCC_CSR_PORRSTF) {
        health.reset_reason = RESET_CAUSE_POWER_ON;
    } else if (csr & RCC_CSR_IWDGRSTF) {
        health.reset_reason = RESET_CAUSE_WATCHDOG;
    } else if (csr & RCC_CSR_SFTRSTF) {
        health.reset_reason = RESET_CAUSE_SOFTWARE;
    } else {
        health.reset_reason = RESET_CAUSE_UNKNOWN;
    }

    /* Очищаємо прапорці скидання для фіксації наступної події */
    RCC_CSR_REG |= RCC_CSR_RMVF_BIT;

    /* Опитуємо стан відлагоджувача та активного джерела тактування */
    health.debugger_connected = (CoreDebug_DHCSR & DHCSR_C_DEBUGEN) != 0;
    health.clock_status = (RCC_CR_REG & RCC_CR_HSERDY_BIT) 
                          ? CLOCK_SOURCE_HSE_CRYSTAL 
                          : CLOCK_SOURCE_HSI_FALLBACK;

    health.core_frequency_hz = (health.clock_status == CLOCK_SOURCE_HSE_CRYSTAL) 
                               ? 25000000UL 
                               : 16000000UL;

    return health;
}
```
```cpp
// bsp_bringup.cpp — Реалізація мовою C++
#include "bsp_bringup.hpp"
#include <span>

namespace bsp {

namespace {
    // Типізоване зв'язування з апаратними регістрами Cortex-M
    inline volatile uint32_t& reg_rcc_cr     = *reinterpret_cast<volatile uint32_t*>(0x40023800UL);
    inline volatile uint32_t& reg_rcc_cfgr   = *reinterpret_cast<volatile uint32_t*>(0x40023808UL);
    inline volatile uint32_t& reg_rcc_csr    = *reinterpret_cast<volatile uint32_t*>(0x40023874UL);

    inline volatile uint32_t& reg_gpioa_mod  = *reinterpret_cast<volatile uint32_t*>(0x40020000UL);
    inline volatile uint32_t& reg_gpiob_mod  = *reinterpret_cast<volatile uint32_t*>(0x40020400UL);
    inline volatile uint32_t& reg_gpioc_mod  = *reinterpret_cast<volatile uint32_t*>(0x40020800UL);

    inline volatile uint32_t& reg_dhcsr      = *reinterpret_cast<volatile uint32_t*>(0xE000EDF0UL);
    inline volatile uint8_t&  reg_itm_port0  = *reinterpret_cast<volatile uint8_t*>(0xE0000000UL);
    inline volatile uint32_t& reg_itm_ter    = *reinterpret_cast<volatile uint32_t*>(0xE0000E00UL);

    constexpr uint32_t hsi_on_bit    = 1UL << 0;
    constexpr uint32_t hsi_rdy_bit   = 1UL << 1;
    constexpr uint32_t hse_on_bit    = 1UL << 16;
    constexpr uint32_t hse_rdy_bit   = 1UL << 17;

    constexpr uint32_t csr_rmvf_bit  = 1UL << 24;
    constexpr uint32_t csr_bor_bit   = 1UL << 25;
    constexpr uint32_t csr_por_bit   = 1UL << 27;
    constexpr uint32_t csr_sft_bit   = 1UL << 28;
    constexpr uint32_t csr_iwdg_bit  = 1UL << 29;

    constexpr uint32_t debug_en_bit  = 1UL << 0;
}

std::expected<ClockSourceStatus, ClockSourceStatus> 
BringupManager::init_clock_safe(uint32_t hse_timeout_cycles) noexcept {
    // 1. Активація внутрішнього генератора HSI
    reg_rcc_cr |= hsi_on_bit;
    while (!(reg_rcc_cr & hsi_rdy_bit)) {
        // Очікування стабілізації HSI
    }

    // 2. Спроба запуску зовнішнього кварцового генератора HSE
    reg_rcc_cr |= hse_on_bit;
    uint32_t countdown = hse_timeout_cycles;

    while (!(reg_rcc_cr & hse_rdy_bit) && (countdown > 0)) {
        --countdown;
    }

    if (countdown == 0) {
        // Аварійне вимкнення контуру HSE після таймауту
        reg_rcc_cr &= ~hse_on_bit;
        reg_rcc_cfgr &= ~0x03UL; // SW = HSI
        return std::unexpected(ClockSourceStatus::HsiFallback);
    }

    // 3. Перемикання системної шини на HSE
    reg_rcc_cfgr = (reg_rcc_cfgr & ~0x03UL) | 0x01UL;
    while ((reg_rcc_cfgr & 0x0CUL) != 0x04UL) {
        // Очікування готовності мультиплексора
    }

    return ClockSourceStatus::HseCrystal;
}

void BringupManager::park_unused_pins() noexcept {
    // Зберігаємо виводи SWD (PA13, PA14) при глобальному переводі в аналоговий стан
    auto moder_a = reg_gpioa_mod;
    moder_a |= 0x03FFFFFFUL;
    moder_a &= ~(0x3UL << (13 * 2));
    moder_a |=  (0x2UL << (13 * 2)); // PA13 -> AF
    moder_a &= ~(0x3UL << (14 * 2));
    moder_a |=  (0x2UL << (14 * 2)); // PA14 -> AF
    reg_gpioa_mod = moder_a;

    reg_gpiob_mod = 0xFFFFFFFFUL; // Analog mode для порту B
    reg_gpioc_mod = 0xFFFFFFFFUL; // Analog mode для порту C
}

void BringupManager::log(std::string_view message) noexcept {
    if ((reg_dhcsr & debug_en_bit) && (reg_itm_ter & 0x01UL)) {
        for (const char ch : message) {
            reg_itm_port0 = static_cast<uint8_t>(ch);
        }
    }
}

HardwareHealth BringupManager::check_health() noexcept {
    HardwareHealth health{};
    const uint32_t csr = reg_rcc_csr;

    if (csr & csr_bor_bit) {
        health.reset_reason = ResetCause::Brownout;
    } else if (csr & csr_por_bit) {
        health.reset_reason = ResetCause::PowerOn;
    } else if (csr & csr_iwdg_bit) {
        health.reset_reason = ResetCause::Watchdog;
    } else if (csr & csr_sft_bit) {
        health.reset_reason = ResetCause::Software;
    } else {
        health.reset_reason = ResetCause::Unknown;
    }

    reg_rcc_csr |= csr_rmvf_bit;

    health.debugger_connected = (reg_dhcsr & debug_en_bit) != 0;
    health.clock_status = (reg_rcc_cr & hse_rdy_bit) 
                          ? ClockSourceStatus::HseCrystal 
                          : ClockSourceStatus::HsiFallback;

    health.core_frequency_hz = (health.clock_status == ClockSourceStatus::HseCrystal) 
                               ? 25'000'000UL 
                               : 16'000'000UL;

    return health;
}

} // namespace bsp
```
:::

---

## Розбір фізичних механізмів та крайових випадків

### 1. Розрахунок генератора Пірса та від'ємного опору

Автогенератор Пірса вбудовано безпосередньо в кремній мікроконтролера між виводами `OSC_IN` та `OSC_OUT`. Він складається з інвертуючого підсилювача з крутизною передавальної характеристики `g_m` та внутрішнього резистора зворотного зв'язку `R_F`.

Зовнішній кварц еквівалентний послідовному резонансному коливальному контуру з індуктивністю модального коливання `L_1`, ємністю `C_1`, динамічним опором втрат `R_ESR` та статичною паразитною ємністю виводів і корпусу `C_0`.

Щоб коливання в контурі наростали після подачі живлення, активна частина генератора зобов'язана створювати **від'ємний опір (Negative Resistance)** `R_a`, модуль якого суттєво перевищує втрати в кристалі:

```
|Ra| = gm / ( (2 · π · f)² · C_L1 · C_L2 )

Критерій надійного запуску генератора (Safety Margin):
|Ra| ≥ 3 · R_ESR  (для звичайних застосунків)
|Ra| ≥ 5 · R_ESR  (для промислових та автомобільних пристроїв)
```

На власній платі поширені дві протилежні помилки:
- **Завищена ємність навантаження (`C_L1`, `C_L2` занадто великі):** величина від'ємного опору `|R_a|` падає пропорційно квадрату ємності. Модуль `|R_a|` стає меншим за `R_ESR`, підсилювач не може компенсувати втрати енергії в кварці, і генерація не розпочинається взагалі.
- **Занижена ємність навантаження:** частота генерації зміщується вгору від номіналу, а амплітуда коливань на виводі `OSC_IN` зростає настільки, що потужність розсіювання на кристалі `P_drive` перевищує допустиму паспортну межу (зазвичай 50–100 мкВт), викликаючи прискорену механічну деградацію та мікротріщини в кварцовій пластині.

### 2. Механіка наскрізного струму у вхідних каскадах CMOS

Вхідний цифровий буфер будь-якого виводу GPIO загального призначення містить інвертор на двох польових транзисторах. 

Коли на вхід подано логічний нуль (0 В), верхній P-MOS транзистор відкритий, нижній N-MOS закритий, струм від шини `V_DD` до землі не тече. Коли подано логічну одиницю (3.3 В), P-MOS закритий, N-MOS відкритий, струм знову дорівнює нулю.

Проте, якщо вивід залишено висячим у повітрі («floating»), його потенціал через наведення та витоки підкладки дрейфує в діапазоні 1.2–1.8 В (половина напруги живлення). У цьому проміжку напруга затвор-витік обох транзисторів перевищує їхні порогові напруги відкриття (`V_GS,N > V_th,N` та `|V_GS,P| > |V_th,P|`). Обидва ключі одночасно відкриваються, утворюючи низькоомний міст між шиною живлення та землею.

Переведення виводів у режим `Analog Mode` замикає вхідний тригер Шмітта на внутрішню фіксовану шину або повністю знеструмлює компаратор входу, усуваючи наскрізний витік струму.

---

## Покроковий інженерний чеклист верифікації заліза

Перед завантаженням скомпільованого образу на першу виготовлену плату пройдіть послідовність верифікації за сімома ключовими доменами:

```
┌────────────────────────────────────────────────────────────────────────┐
│             ЧЕКЛИСТ МІГРАЦІЇ ПРОШИВКИ (BOARD BRING-UP)                 │
└────────────────────────────────────────────────────────────────────────┘
 [ ] 1. ПЕРЕВІРКА НАПРУГИ ТА ЛІНІЇ VTREF
     • Чи підключено вивід VTref роз'єму SWD до шини VDD цільового МК?
     • Чи відповідає напруга VDD діапазону роботи внутрішньої Flash-пам'яті (зазвичай 1.8...3.6 В)?
     • Чи обмежено струм лабораторного БЖ до 50 мА на першому ввімкненні?

 [ ] 2. СТАН STRAPPING-ПІНІВ ТА ЛІНІЇ СКИДАННЯ
     • STM32: чи підтягнуто пін BOOT0 до GND через резистор 10 кОм (або 0 Ом)?
     • ESP32: чи забезпечено рівень HIGH на GPIO0 та GPIO2 під час виходу з EN?
     • Чи встановлено керамічний конденсатор 100 нФ між NRST та GND біля процесора?

 [ ] 3. ТАКТУВАННЯ ТА КРИСТАЛИ
     • Чи встановлено програмний таймаут для очікування HSERDY замість нескінченного while?
     • Чи налаштовано обчислення частоти PLL під реальний розпаяний кварц (наприклад, 25 МГц замість 8 МГц на Nucleo)?
     • Чи активовано внутрішній генератор HSI як аварійне резервне джерело?

 [ ] 4. ВІДЛАГОДЖУВАЛЬНИЙ ТАЙМЕР ПЕРЕД DEEP SLEEP
     • Чи додано безумовну паузу (2000 мс) у самому початку main() перед першим входом у сон?
     • Чи захищено виводи SWDIO/SWCLK від випадкової реконфігурації в звичайний GPIO?

 [ ] 5. КАНАЛ ДІАГНОСТИКИ ТА ВИВЕДЕННЯ ЛОГІВ
     • Чи замінено бібліотечні виклики printf() через USB-CDC на ITM SWO, SEGGER RTT або фізичний UART?
     • Чи налаштовано UART на режим DMA або кільцевий буфер без блокування процесора при відключеному приймачі?

 [ ] 6. ПАРКУВАННЯ НЕВИКОРИСТАНИХ ВИВОДІВ
     • Чи переведено всі вільні вхідні ніжки мікроконтролера в режим Analog або Input з Pull-down?
     • Чи вимкнено тактування нерозпаяних периферійних блоків (I2C2, SPI3, CAN, USB)?

 [ ] 7. ПЕРЕВІРКА МЕЖІ BROWNOUT RESET (BOR)
     • Чи активовано в Option Bytes апаратний детектор просідання напруги (BOR Level)?
     • Чи налаштовано рівень відключення вище за критичну напругу відмови Flash-контролера?
```

Впровадження цього каркаса в базовий шар підтримки плати (BSP) перетворює перше вмикання власної друкованої плати на керований та повністю контрольований інженерний процес.

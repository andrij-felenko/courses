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

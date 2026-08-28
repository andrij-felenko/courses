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

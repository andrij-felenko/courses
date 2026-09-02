#include "mcu_regs.h"
#include "startup.h"

/* Кварц на платі й цільова частота ядра */
#define HSE_HZ    8000000UL
#define HSI_HZ    16000000UL
#define SYSCLK_HZ 168000000UL

/* PLL: VCO_in = HSE / M = 1 МГц, VCO_out = ×N = 336 МГц,
   SYSCLK = VCO_out / P = 168 МГц, гілка USB = VCO_out / Q = 48 МГц */
#define PLL_M 8UL
#define PLL_N 336UL
#define PLL_P 2UL /* поле PLLP кодує дільник 2 як 0b00 */
#define PLL_Q 7UL

/* Скільки разів опитуємо прапорець готовності, перш ніж визнати відмову.
   Лічильник, а не таймер: на цьому етапі таймерів іще немає. */
#define RCC_TIMEOUT 0x00050000UL

uint32_t SystemCoreClock = HSI_HZ;

static bool wait_cr_flag(uint32_t mask)
{
    for (uint32_t guard = 0; guard < RCC_TIMEOUT; ++guard) {
        if ((RCC_CR & mask) != 0U) {
            return true;
        }
    }
    return false;
}

/* Повернення дерева тактування до заводського стану. Після програмного
   скидання регістри RCC зберігають налаштування попереднього запуску —
   заводити PLL поверх чужої конфігурації не можна. */
static void reset_clock_tree(void)
{
    RCC_CR |= RCC_CR_HSION;   /* внутрішній RC лишається запасним завжди */
    RCC_CFGR = 0UL;           /* SYSCLK = HSI, дільники шин = 1 */
    RCC_CR &= ~(RCC_CR_HSEON | RCC_CR_CSSON | RCC_CR_PLLON);
    RCC_PLLCFGR = RCC_PLLCFGR_RESET;
    RCC_CR &= ~RCC_CR_HSEBYP;
    RCC_CIR = 0UL;            /* усі переривання RCC вимкнено й очищено */
}

bool SystemInit(void)
{
    reset_clock_tree();

    RCC_CR |= RCC_CR_HSEON;
    if (!wait_cr_flag(RCC_CR_HSERDY)) {
        /* Кварц не завівся: не розпаяний, тріснув або замерз. Лишаємось
           на HSI — 16 МГц повільно, зате прошивка жива й може про це
           повідомити. Затримки Flash на такій частоті не потрібні. */
        FLASH_ACR = FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN;
        SystemCoreClock = HSI_HZ;
        return false;
    }

    /* Затримки Flash ставимо ДО підняття частоти: на 168 МГц пам'ять
       фізично не встигає віддати слово за один такт, і ядро читало б
       сміття замість інструкцій. */
    FLASH_ACR = FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN
              | FLASH_ACR_LATENCY_5WS;

    /* Дільники шин: AHB 168 МГц, APB1 42 МГц (стеля 42), APB2 84 МГц */
    RCC_CFGR = RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;

    RCC_PLLCFGR = PLL_M | (PLL_N << 6) | (((PLL_P >> 1) - 1UL) << 16)
                | RCC_PLLCFGR_SRC_HSE | (PLL_Q << 24);

    RCC_CR |= RCC_CR_PLLON;
    if (!wait_cr_flag(RCC_CR_PLLRDY)) {
        /* PLL не захопився. Лишаємось на HSI: зайві такти очікування
           Flash на 16 МГц нікому не шкодять, лише трохи гальмують. */
        SystemCoreClock = HSI_HZ;
        return false;
    }

    RCC_CFGR = (RCC_CFGR & ~RCC_CFGR_SW_MASK) | RCC_CFGR_SW_PLL;
    for (uint32_t guard = 0; guard < RCC_TIMEOUT; ++guard) {
        /* Перемикач SW лише просить; підтверджує перемикання поле SWS */
        if ((RCC_CFGR & RCC_CFGR_SWS_MASK) == RCC_CFGR_SWS_PLL) {
            SystemCoreClock = SYSCLK_HZ;
            RCC_CR |= RCC_CR_CSSON; /* тепер стежимо за зривом кварцу */
            return true;
        }
    }

    SystemCoreClock = HSI_HZ;
    return false;
}

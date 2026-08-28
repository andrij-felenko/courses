#include "FreeRTOS.h"
#include "task.h"
#include "stm32l4xx.h"

// Параметри низькочастотного тактування
#define LSE_FREQUENCY_HZ            32768UL
#define LPTIM_PRESCALER_DIV         32UL
#define LPTIM_COUNTS_PER_SECOND     (LSE_FREQUENCY_HZ / LPTIM_PRESCALER_DIV) // 1024 Гц

// Розрахунок максимального допустимого інтервалу сну (16-бітний лічильник LPTIM)
#define LPTIM_MAX_COUNTS            0xFFFFUL
#define MAXIMUM_SUPPRESSED_TICKS    ((LPTIM_MAX_COUNTS * configTICK_RATE_HZ) / LPTIM_COUNTS_PER_SECOND)

// Апаратна компенсація часу пробудження стабілізатора й PLL (у тактах LPTIM)
#define WAKEUP_OVERHEAD_LPTIM_TICKS 3UL

// Прототип функції відновлення тактового дерева після виходу з режиму Stop 1
extern void SystemClock_RestoreAfterStop(void);

void vPortSuppressTicksAndSleep(TickType_t xExpectedIdleTime)
{
    uint32_t ulLPTIMTargetCounts;
    uint32_t ulCompletedSysTicks;
    uint32_t ulLPTIMElapsedCounts;
    eSleepModeStatus eSleepStatus;

    // 1. Обмежуємо час сну максимальною розрядністю 16-бітного апаратного таймера
    if (xExpectedIdleTime > MAXIMUM_SUPPRESSED_TICKS)
    {
        xExpectedIdleTime = MAXIMUM_SUPPRESSED_TICKS;
    }

    // 2. Зупиняємо SysTick, щоб унеможливити переривання під час налаштувань
    SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;

    // 3. Обчислюємо цільову кількість імпульсів LPTIM із врахуванням апаратної затримки
    ulLPTIMTargetCounts = (xExpectedIdleTime * LPTIM_COUNTS_PER_SECOND) / configTICK_RATE_HZ;
    if (ulLPTIMTargetCounts > WAKEUP_OVERHEAD_LPTIM_TICKS)
    {
        ulLPTIMTargetCounts -= WAKEUP_OVERHEAD_LPTIM_TICKS;
    }
    else
    {
        ulLPTIMTargetCounts = 1UL;
    }

    // 4. Входимо в критичну секцію ядра (маскуємо переривання)
    __disable_irq();
    __DSB();
    __ISB();

    // 5. Переконуємося, що планувальник все ще дозволяє перехід у сон
    eSleepStatus = eTaskConfirmSleepModeStatus();
    if (eSleepStatus == eAbortSleep)
    {
        // З'явилася готова задача: відновлюємо SysTick і негайно виходимо
        SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;
        __enable_irq();
        return;
    }

    // 6. Програмуємо таймер LPTIM1 в однократному режимі (Single Mode)
    LPTIM1->CR |= LPTIM_CR_ENABLE;
    LPTIM1->ICR = LPTIM_ICR_ARRMCF | LPTIM_ICR_CMPMCF; // Очищення попередніх прапорців
    LPTIM1->ARR = ulLPTIMTargetCounts;
    LPTIM1->IER |= LPTIM_IER_ARRMIE;                    // Дозвіл переривання за автоперезавантаженням
    LPTIM1->CR |= LPTIM_CR_SNGSTRT;                     // Старт відліку

    // 7. Налаштовуємо енергозберігаючий стан Stop 1 у контролері PWR
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | PWR_CR1_LPMS_STOP1;
    SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;                  // Біт глибокого сну ядра

    // 8. Перехід у глибокий енергозберігаючий сон
    __WFI();

    // =========================================================================
    // ПРОБУДЖЕННЯ ЯДРА (від переривання LPTIM або зовнішньої периферії EXTI)
    // =========================================================================

    // 9. Скидаємо прапорець глибокого сну та відновлюємо тактову частоту 80 МГц PLL
    SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    SystemClock_RestoreAfterStop();

    // 10. Зчитуємо фактично відрахований час із регістра LPTIM_CNT.
    // Оскільки LPTIM працює від асинхронного генератора LSE, використовуємо подвійну вибірку
    uint32_t val1 = LPTIM1->CNT;
    uint32_t val2 = LPTIM1->CNT;
    while (val1 != val2)
    {
        val1 = val2;
        val2 = LPTIM1->CNT;
    }
    ulLPTIMElapsedCounts = val1;

    // Зупиняємо таймер LPTIM1
    LPTIM1->CR &= ~LPTIM_CR_ENABLE;

    // 11. Розраховуємо кількість повних системних тактів RTOS, проведених у сні
    ulCompletedSysTicks = ((ulLPTIMElapsedCounts + WAKEUP_OVERHEAD_LPTIM_TICKS) * configTICK_RATE_HZ)
                          / LPTIM_COUNTS_PER_SECOND;

    if (ulCompletedSysTicks > xExpectedIdleTime)
    {
        ulCompletedSysTicks = xExpectedIdleTime;
    }

    // 12. Компенсуємо системний час у планувальнику FreeRTOS
    vTaskStepTick(ulCompletedSysTicks);

    // 13. Перезапускаємо системний таймер SysTick
    SysTick->VAL = 0UL;
    SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;

    // 14. Відкриваємо глобальні переривання: накопичені переривання обробляються негайно
    __enable_irq();
}

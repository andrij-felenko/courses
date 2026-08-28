#include "FreeRTOS.h"
#include "task.h"
#include "stm32l4xx.h"

#define LSE_FREQUENCY_HZ        32768UL
#define LPTIM_CLOCK_PRESCALER   32UL
#define LPTIM_COUNTS_PER_SEC    (LSE_FREQUENCY_HZ / LPTIM_CLOCK_PRESCALER) // 1024 Гц
#define COUNTS_PER_TICK         (LPTIM_COUNTS_PER_SEC / configTICK_RATE_HZ) // 1024 / 1000 ≈ 1

// Максимальний час сну, обмежений 16-бітним регістром ARR таймера LPTIM
#define MAXIMUM_SUPPRESSED_TICKS ((0xFFFFUL) / COUNTS_PER_TICK)

// Затримка на вихід із глибокого сну та стабілізацію генераторів (у тактах LPTIM)
#define WAKEUP_COMPENSATION_COUNTS  3

void vPortSuppressTicksAndSleep(TickType_t xExpectedIdleTime)
{
    uint32_t ulLPTIMCounts;
    uint32_t ulCompletedSysTicks;
    enum eSleepModeStatus eSleepStatus;

    // Обмежуємо час сну максимальною ємністю 16-бітного апаратного лічильника
    if (xExpectedIdleTime > MAXIMUM_SUPPRESSED_TICKS) {
        xExpectedIdleTime = MAXIMUM_SUPPRESSED_TICKS;
    }

    // 1. Зупиняємо SysTick, щоб уникнути переривань під час розрахунку
    SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;

    // 2. Розраховуємо кількість тактів LPTIM для заданого періоду сну
    ulLPTIMCounts = (xExpectedIdleTime * LPTIM_COUNTS_PER_SEC) / configTICK_RATE_HZ;
    if (ulLPTIMCounts > WAKEUP_COMPENSATION_COUNTS) {
        ulLPTIMCounts -= WAKEUP_COMPENSATION_COUNTS;
    } else {
        ulLPTIMCounts = 1;
    }

    // 3. Входимо в критичну секцію (маскуємо переривання на рівні ядра)
    __disable_irq();
    __DSB();
    __ISB();

    // 4. Перевіряємо, чи не з'явилися нові готові задачі перед сном
    eSleepStatus = eTaskConfirmSleepModeStatus();
    if (eSleepStatus == eAbortSleep) {
        // Задача стала готовою: відновлюємо SysTick і виходимо
        SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;
        __enable_irq();
        return;
    }

    // 5. Програмуємо LPTIM1 на однократний відлік інтервалу
    LPTIM1->CR |= LPTIM_CR_ENABLE;
    LPTIM1->ICR = LPTIM_ICR_ARRMCF | LPTIM_ICR_CMPMCF; // Очищення прапорців
    LPTIM1->ARR = ulLPTIMCounts;
    LPTIM1->IER |= LPTIM_IER_ARRMIE;                    // Дозвіл переривання за ARR
    LPTIM1->CR |= LPTIM_CR_SNGSTRT;                     // Старт в однократному режимі

    // 6. Налаштовуємо режим низького енергоспоживання ядра (Stop 1 Mode)
    PWR->CR1 &= ~PWR_CR1_LPMS;
    PWR->CR1 |= PWR_CR1_LPMS_STOP1;                     // Вибір режиму Stop 1
    SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;                  // Встановлення біта DeepSleep

    // 7. Вхід у глибокий сон
    __WFI();

    // ================= ЯДРО ПРОКИНУЛОСЯ =================

    // 8. Скидаємо прапорець DeepSleep та відновлюємо базову частоту HSI/PLL
    SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    SystemClock_RestoreAfterStop();

    // 9. Зчитуємо фактично відрахований час із LPTIM
    // Для узгодження тактових доменів зчитування виконується двічі
    uint32_t count1 = LPTIM1->CNT;
    uint32_t count2 = LPTIM1->CNT;
    while (count1 != count2) {
        count1 = count2;
        count2 = LPTIM1->CNT;
    }

    // Зупиняємо LPTIM1
    LPTIM1->CR &= ~LPTIM_CR_ENABLE;

    // 10. Розраховуємо кількість повних тактів RTOS, проведених у сні
    ulCompletedSysTicks = (count1 + WAKEUP_COMPENSATION_COUNTS) * configTICK_RATE_HZ / LPTIM_COUNTS_PER_SEC;

    if (ulCompletedSysTicks > xExpectedIdleTime) {
        ulCompletedSysTicks = xExpectedIdleTime;
    }

    // 11. Компенсуємо системний час RTOS
    vTaskStepTick(ulCompletedSysTicks);

    // 12. Перезапускаємо системний таймер SysTick
    SysTick->VAL = 0UL;
    SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;

    // 13. Відкриваємо переривання: накопичені переривання обробляються негайно
    __enable_irq();
}

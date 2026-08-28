#include "FreeRTOS.h"
#include "task.h"
#include "stm32l4xx.h"
#include <cstdint>
#include <concepts>

namespace rtos::power {

// RAII-обгортка для атомарного блокування переривань процесора
class CriticalSection {
public:
    CriticalSection() noexcept {
        __disable_irq();
        __DSB();
        __ISB();
    }
    ~CriticalSection() noexcept {
        __enable_irq();
    }
    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;
};

// Апаратний драйвер низькоспоживаючого таймера LPTIM1
class LowPowerTimer {
public:
    static constexpr std::uint32_t LseFrequencyHz = 32768UL;
    static constexpr std::uint32_t Prescaler = 32UL;
    static constexpr std::uint32_t CountsPerSec = LseFrequencyHz / Prescaler; // 1024 Гц
    static constexpr std::uint32_t CountsPerTick = CountsPerSec / configTICK_RATE_HZ;
    static constexpr std::uint32_t MaxSleepTicks = 0xFFFFUL / CountsPerTick;
    static constexpr std::uint32_t WakeupOverheadCounts = 3;

    static void init() noexcept {
        RCC->APB1ENR1 |= RCC_APB1ENR1_LPTIM1EN;
        LPTIM1->CFGR = LPTIM_CFGR_PRESC_2; // Prescaler /32
    }

    static void startTimeout(std::uint32_t counts) noexcept {
        LPTIM1->CR |= LPTIM_CR_ENABLE;
        LPTIM1->ICR = LPTIM_ICR_ARRMCF | LPTIM_ICR_CMPMCF;
        LPTIM1->ARR = counts;
        LPTIM1->IER |= LPTIM_IER_ARRMIE;
        LPTIM1->CR |= LPTIM_CR_SNGSTRT;
    }

    static std::uint32_t stopAndReadElapsed() noexcept {
        // Узгодження асинхронного зчитування між доменами LSE та APB
        std::uint32_t c1 = LPTIM1->CNT;
        std::uint32_t c2 = LPTIM1->CNT;
        while (c1 != c2) {
            c1 = c2;
            c2 = LPTIM1->CNT;
        }
        LPTIM1->CR &= ~LPTIM_CR_ENABLE;
        return c1;
    }
};

// Контролер режимів низького енергоспоживання
class PowerController {
public:
    static void configureStopMode() noexcept {
        PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | PWR_CR1_LPMS_STOP1;
        SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
    }

    static void enterDeepSleep() noexcept {
        __WFI();
    }

    static void restoreClocksAfterWakeup() noexcept {
        SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
        // Відновлення генераторів PLL/HSI після виходу зі Stop 1
        SystemClock_RestoreAfterStop();
    }
};

// Диспетчер безтикового режиму
class TicklessManager {
public:
    static void suppressTicksAndSleep(TickType_t expectedIdleTicks) noexcept {
        const std::uint32_t boundedTicks = (expectedIdleTicks > LowPowerTimer::MaxSleepTicks)
            ? LowPowerTimer::MaxSleepTicks
            : static_cast<std::uint32_t>(expectedIdleTicks);

        // Зупинка системного таймера SysTick
        SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;

        std::uint32_t targetCounts = (boundedTicks * LowPowerTimer::CountsPerSec) / configTICK_RATE_HZ;
        targetCounts = (targetCounts > LowPowerTimer::WakeupOverheadCounts)
            ? (targetCounts - LowPowerTimer::WakeupOverheadCounts)
            : 1UL;

        {
            CriticalSection lock;

            if (eTaskConfirmSleepModeStatus() == eAbortSleep) {
                SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;
                return;
            }

            LowPowerTimer::startTimeout(targetCounts);
            PowerController::configureStopMode();
            PowerController::enterDeepSleep();

            // Ядро прокинулося
            PowerController::restoreClocksAfterWakeup();

            const std::uint32_t elapsedCounts = LowPowerTimer::stopAndReadElapsed();
            std::uint32_t completedTicks = ((elapsedCounts + LowPowerTimer::WakeupOverheadCounts) * configTICK_RATE_HZ)
                / LowPowerTimer::CountsPerSec;

            if (completedTicks > boundedTicks) {
                completedTicks = boundedTicks;
            }

            vTaskStepTick(completedTicks);

            SysTick->VAL = 0UL;
            SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;
        }
    }
};

} // namespace rtos::power

extern "C" void vPortSuppressTicksAndSleep(TickType_t xExpectedIdleTime) {
    rtos::power::TicklessManager::suppressTicksAndSleep(xExpectedIdleTime);
}

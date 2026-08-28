#include "FreeRTOS.h"
#include "task.h"
#include "stm32l4xx.h"
#include <cstdint>
#include <concepts>

namespace rtos::power {

// RAII-менеджер критичної секції ядра
class KernelInterruptLock {
public:
    KernelInterruptLock() noexcept {
        __disable_irq();
        __DSB();
        __ISB();
    }

    ~KernelInterruptLock() noexcept {
        __enable_irq();
    }

    KernelInterruptLock(const KernelInterruptLock&) = delete;
    KernelInterruptLock& operator=(const KernelInterruptLock&) = delete;
    KernelInterruptLock(KernelInterruptLock&&) = delete;
    KernelInterruptLock& operator=(KernelInterruptLock&&) = delete;
};

// Апаратний драйвер низькоспоживаючого таймера LPTIM1
class LowPowerTimer {
public:
    static constexpr std::uint32_t LseFrequencyHz = 32768UL;
    static constexpr std::uint32_t Prescaler = 32UL;
    static constexpr std::uint32_t CountsPerSec = LseFrequencyHz / Prescaler; // 1024 Гц
    static constexpr std::uint32_t MaxRawCounts = 0xFFFFUL;
    static constexpr std::uint32_t MaxSleepTicks = (MaxRawCounts * configTICK_RATE_HZ) / CountsPerSec;
    static constexpr std::uint32_t WakeupOverheadCounts = 3UL;

    static void init() noexcept {
        RCC->APB1ENR1 |= RCC_APB1ENR1_LPTIM1EN;
        LPTIM1->CFGR = LPTIM_CFGR_PRESC_2; // Дільник частоти /32
    }

    static void startTimeout(std::uint32_t counts) noexcept {
        LPTIM1->CR |= LPTIM_CR_ENABLE;
        LPTIM1->ICR = LPTIM_ICR_ARRMCF | LPTIM_ICR_CMPMCF;
        LPTIM1->ARR = counts;
        LPTIM1->IER |= LPTIM_IER_ARRMIE;
        LPTIM1->CR |= LPTIM_CR_SNGSTRT;
    }

    static std::uint32_t stopAndReadElapsedCounts() noexcept {
        // Подвійне зчитування для усунення метастабільності асинхронного домену LSE
        std::uint32_t sample1 = LPTIM1->CNT;
        std::uint32_t sample2 = LPTIM1->CNT;
        while (sample1 != sample2) {
            sample1 = sample2;
            sample2 = LPTIM1->CNT;
        }
        LPTIM1->CR &= ~LPTIM_CR_ENABLE;
        return sample1;
    }
};

// Контролер конфігурації енергозберігаючих режимів кристала
class PowerController {
public:
    static void configureStopMode() noexcept {
        PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | PWR_CR1_LPMS_STOP1;
        SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
    }

    static void clearSleepDeep() noexcept {
        SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    }

    static void enterSleep() noexcept {
        __WFI();
    }
};

// Головний диспетчер безтикового режиму
class TicklessManager {
public:
    static void processSleep(TickType_t expectedIdleTicks) noexcept {
        const std::uint32_t boundedTicks = (expectedIdleTicks > LowPowerTimer::MaxSleepTicks)
            ? LowPowerTimer::MaxSleepTicks
            : static_cast<std::uint32_t>(expectedIdleTicks);

        // Зупиняємо системний таймер ядра
        SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;

        std::uint32_t targetCounts = (boundedTicks * LowPowerTimer::CountsPerSec) / configTICK_RATE_HZ;
        targetCounts = (targetCounts > LowPowerTimer::WakeupOverheadCounts)
            ? (targetCounts - LowPowerTimer::WakeupOverheadCounts)
            : 1UL;

        {
            KernelInterruptLock lock;

            if (eTaskConfirmSleepModeStatus() == eAbortSleep) {
                SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;
                return;
            }

            LowPowerTimer::startTimeout(targetCounts);
            PowerController::configureStopMode();
            PowerController::enterSleep();

            // ЯДРО ПРОКИНУЛОСЯ
            PowerController::clearSleepDeep();
            SystemClock_RestoreAfterStop();

            const std::uint32_t elapsedCounts = LowPowerTimer::stopAndReadElapsedCounts();
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
    rtos::power::TicklessManager::processSleep(xExpectedIdleTime);
}

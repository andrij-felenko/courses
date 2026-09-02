#include "PowerManager.hpp"
#include "Mcu.hpp"
#include "SystemTick.hpp"
#include "WakeupTimer.hpp"

#include "stm32l4xx.h"

namespace emb::pm {

using std::chrono::milliseconds;

void PowerManager::init() noexcept
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;
    static_cast<void>(RCC->APB1ENR1);
    // Невичищений прапорець пробудження обриває наступний вхід у STOP одразу ж.
    PWR->SCR = PWR_SCR_CWUF;
    hal::WakeupTimer::init();
}

bool PowerManager::registerClient(IPowerClient* client) noexcept
{
    if (client == nullptr || m_clientCount >= MaxClients) {
        return false;
    }
    m_clients[m_clientCount++] = client;
    return true;
}

void PowerManager::acquireLock(Lock lock) noexcept
{
    const auto idx = static_cast<std::size_t>(lock);
    if (idx < static_cast<std::size_t>(Lock::Count)) {
        m_lockCounters[idx].fetch_add(1, std::memory_order_acq_rel);
    }
}

void PowerManager::releaseLock(Lock lock) noexcept
{
    const auto idx = static_cast<std::size_t>(lock);
    if (idx >= static_cast<std::size_t>(Lock::Count)) {
        return;
    }
    auto current = m_lockCounters[idx].load(std::memory_order_relaxed);
    while (current > 0
           && !m_lockCounters[idx].compare_exchange_weak(current, current - 1,
                                                         std::memory_order_acq_rel,
                                                         std::memory_order_relaxed)) {
    }
    if (current == 0) {
        ++m_underflows;
    }
}

std::uint32_t PowerManager::lockCount(Lock lock) const noexcept
{
    const auto idx = static_cast<std::size_t>(lock);
    return idx < static_cast<std::size_t>(Lock::Count)
             ? m_lockCounters[idx].load(std::memory_order_relaxed)
             : 0u;
}

Mode PowerManager::deepestAllowedMode() const noexcept
{
    if (lockCount(Lock::NoSleep) > 0)   return Mode::Active;
    if (lockCount(Lock::NoStop) > 0)    return Mode::Sleep;
    if (lockCount(Lock::NoStandby) > 0) return Mode::Stop;
    return Mode::Standby;
}

bool PowerManager::prepareClients(Mode targetMode) noexcept
{
    const auto list = clients();
    for (std::size_t i = 0; i < list.size(); ++i) {
        if (!list[i]->preSleep(targetMode)) {
            // Відкат у зворотному порядку — так само, як розкручують стек.
            for (std::size_t j = i; j-- > 0;) {
                list[j]->postWakeup(targetMode);
            }
            return false;
        }
    }
    return true;
}

void PowerManager::restoreClients(Mode fromMode) noexcept
{
    const auto list = clients();
    for (std::size_t i = list.size(); i-- > 0;) {
        list[i]->postWakeup(fromMode);
    }
}

void PowerManager::enterLowPower(Mode mode) noexcept
{
    const std::uint32_t lpms = (mode == Mode::Standby) ? PWR_CR1_LPMS_STANDBY
                                                       : PWR_CR1_LPMS_STOP1;
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | lpms;
    PWR->SCR = PWR_SCR_CWUF;

    SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
    hal::waitForInterrupt();
    // Сюди повертаємося лише зі STOP: зі STANDBY виходять через рестарт.
    SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
}

void PowerManager::sleepIfIdle(milliseconds expectedIdle) noexcept
{
    Mode target = deepestAllowedMode();

    if (target == Mode::Active) {
        return;
    }
    if (target == Mode::Standby) {
        target = Mode::Stop; // втрату SRAM диспетчер сам не призначає
    }
    if (target == Mode::Sleep || expectedIdle < Breakeven) {
        hal::waitForInterrupt(); // легкий сон: перше ж переривання підніме ядро
        return;
    }

    if (!prepareClients(target)) {
        return; // драйвер відмовив, підготовлені вже відкочені
    }

    hal::SystemTick::suspend();
    const auto horizon = hal::WakeupTimer::arm(expectedIdle);

    milliseconds slept{0};
    {
        hal::CriticalSection cs;

        // Перевірка після хуків: переривання могло взяти блокування, поки
        // драйвери готувалися, і тоді засинати вже не можна.
        if (atLeastAsDeep(deepestAllowedMode(), target)) {
            enterLowPower(target);
            slept = hal::WakeupTimer::elapsedSinceArm();
        }
        hal::WakeupTimer::disarm();

        // Спершу частота, потім лічильник часу — і лише тоді ISR.
        static_cast<void>(hal::SystemClock::restoreAfterStop());
        hal::SystemTick::resume(slept);

        if (slept + milliseconds{1} < horizon) {
            ++m_earlyWakeups; // підняв не таймер, а периферія
        }
    } // тут PRIMASK відпускається, і накопичені ISR ідуть уже на 80 МГц

    restoreClients(target);
}

bool PowerManager::enterStandby(milliseconds wakeupAfter) noexcept
{
    if (!prepareClients(Mode::Standby)) {
        return false;
    }
    hal::SystemTick::suspend();
    static_cast<void>(hal::WakeupTimer::arm(wakeupAfter));

    {
        hal::CriticalSection cs;
        enterLowPower(Mode::Standby);

        // Якщо ми тут — STANDBY не відбувся (наприклад, висів невичищений WUF).
        // Повертаємо систему в робочий стан, а не лишаємо напівмертвою.
        hal::WakeupTimer::disarm();
        static_cast<void>(hal::SystemClock::restoreAfterStop());
        hal::SystemTick::resume(milliseconds{0});
    }
    restoreClients(Mode::Standby);
    return false;
}

} // namespace emb::pm

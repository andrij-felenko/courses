/* ============================================================================
 * PowerManager.cpp — Реалізація диспетчера на C++20
 * ============================================================================ */
#include "PowerManager.hpp"

namespace emb::pm {

namespace {

inline void disableInterrupts() noexcept {
    __asm volatile ("cpsid i" : : : "memory");
}

inline void enableInterrupts() noexcept {
    __asm volatile ("cpsie i" : : : "memory");
}

inline void dataSyncBarrier() noexcept {
    __asm volatile ("dsb 0xF" ::: "memory");
}

inline void instrSyncBarrier() noexcept {
    __asm volatile ("isb 0xF" ::: "memory");
}

inline void waitForInterrupt() noexcept {
    __asm volatile ("wfi");
}

} // anonymous namespace

bool PowerManager::prepareClients(Mode targetMode) noexcept {
    size_t prepared = 0;
    for (size_t i = 0; i < m_clientCount; ++i) {
        if (m_clients[i] && !m_clients[i]->preSleep(targetMode)) {
            // Відкат у зворотному порядку для вже підготовлених драйверів
            for (size_t j = prepared; j > 0; --j) {
                m_clients[j - 1]->postWakeup(targetMode);
            }
            return false;
        }
        ++prepared;
    }
    return true;
}

void PowerManager::restoreClients(Mode fromMode) noexcept {
    for (size_t i = 0; i < m_clientCount; ++i) {
        if (m_clients[i]) {
            m_clients[i]->postWakeup(fromMode);
        }
    }
}

void PowerManager::restoreClockTree() noexcept {
    // 1. Увімкнення зовнішнього кварцового генератора (HSE)
    // 2. Очікування прапорця стабілізації HSERDY
    // 3. Запуск контуру фазового автопідстроювання PLL
    // 4. Перемикання системної шини на PLL
}

void PowerManager::executeHardwareSleep(Mode mode, uint32_t idleMs) noexcept {
    (void)idleMs;

    disableInterrupts();

    // Повторна атомарна перевірка блокувань
    if (deepestAllowedMode() >= mode) {
        if (mode == Mode::Stop) {
            // Встановлення біта SLEEPDEEP у системному регістрі Cortex-M SCB->SCR
            dataSyncBarrier();
            instrSyncBarrier();
        }

        waitForInterrupt();

        if (mode == Mode::Stop) {
            // Скидання біта SLEEPDEEP
        }
    }

    if (mode == Mode::Stop) {
        restoreClockTree();
    }

    enableInterrupts();
}

void PowerManager::sleepIfIdle(uint32_t expectedIdleMs) noexcept {
    const Mode target = deepestAllowedMode();

    if (target == Mode::Active) {
        return;
    }

    if (target == Mode::Sleep) {
        waitForInterrupt();
        return;
    }

    if (!prepareClients(target)) {
        return;
    }

    executeHardwareSleep(target, expectedIdleMs);

    restoreClients(target);
}

} // namespace emb::pm

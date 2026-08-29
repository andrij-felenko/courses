#pragma once

/*
 * Критична секція FreeRTOS у вигляді звичайної політики блокування:
 * той самий CriticalSectionGuard, лише інші примітиви всередині.
 *
 * taskENTER_CRITICAL() з обробника переривання спрацьовує configASSERT()
 * і зупиняє систему; для ISR існує пара *_FROM_ISR, яка повертає й приймає
 * збережене значення BASEPRI. Усередині секції не можна кликати
 * блокувальний API — планувальник у цей час вимкнений.
 */

#include <cstdint>
#include <utility>

#include "FreeRTOS.h"
#include "task.h"

#include "critical_section.hpp"

namespace embedded::rtos {

struct RtosSectionState {
    UBaseType_t isr_state{0};
    bool        from_isr{false};
};

class RtosLockPolicy {
public:
    using StateType = RtosSectionState;

    [[nodiscard]] static StateType enter() noexcept
    {
        StateType state{};
        state.from_isr = sync::in_interrupt_context();
        if (state.from_isr) {
            state.isr_state = taskENTER_CRITICAL_FROM_ISR();
        } else {
            taskENTER_CRITICAL();
        }
        return state;
    }

    static void exit(StateType state) noexcept
    {
        if (state.from_isr) {
            taskEXIT_CRITICAL_FROM_ISR(state.isr_state);
        } else {
            taskEXIT_CRITICAL();
        }
    }
};
static_assert(sync::LockPolicy<RtosLockPolicy>);

/* Один вартовий на обидва контексти: код методу не питає, звідки його звуть. */
using RtosGuard = sync::CriticalSectionGuard<RtosLockPolicy>;

/*
 * Приклад спільного стану: лічильники радіолінка, які чіпає і задача
 * передавача, і обробник переривання UART.
 */
class LinkStats {
public:
    void add_frame(bool crc_ok) noexcept
    {
        const RtosGuard lock;
        ++frames_;
        if (!crc_ok) {
            ++crc_errors_;
        }
    }

    [[nodiscard]] std::pair<std::uint32_t, std::uint32_t> read() const noexcept
    {
        const RtosGuard lock;
        return {frames_, crc_errors_};
    }

private:
    std::uint32_t frames_{0};
    std::uint32_t crc_errors_{0};
};

}  // namespace embedded::rtos

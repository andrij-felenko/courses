#pragma once

#include <cstddef>

#include "evse/controller.hpp"
#include "evse/event.hpp"
#include "evse/event_queue.hpp"
#include "evse/soft_timer.hpp"

#include "host_board.hpp"

/*
 * Корінь композиції: тут і лише тут вибирається конкретна плата й зводяться
 * докупи черга, служба таймерів і контролер. Усі шаблони нижче цього рядка
 * стають конкретними типами, і далі жоден модуль не має вибору, з чим
 * працювати.
 */
namespace app {

using Board = evse::HostBoard;

/*
 * Виробників у черги кілька — кнопка, системний таймер, приймач UART,
 * компаратор струму, — і на різних рівнях пріоритету NVIC один може витіснити
 * іншого рівно між читанням індексу запису та його оновленням. Тому політикою
 * виробника підставляється справжня критична секція плати, а не NoLock.
 */
using Queue = evse::EventQueue<evse::Stamped, 16, Board::IrqLock>;

using Timers = evse::TimerService<evse::TimerId,
                                  static_cast<std::size_t>(evse::TimerId::Count),
                                  Board::IrqLock>;

using Controller = evse::EvseController<Board>;

inline Board& board() noexcept { return Board::instance(); }

inline Queue  g_queue{};
inline Timers g_timers{};

/* Помічник для обробників переривань: подія плюс мітка часу. */
inline bool post(const evse::Event& event) noexcept
{
    return g_queue.push(evse::Stamped{event, board().now()});
}

} // namespace app

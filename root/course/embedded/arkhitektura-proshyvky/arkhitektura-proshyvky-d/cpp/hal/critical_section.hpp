// hal/critical_section.hpp — критична секція як об'єкт із часом життя.
// У C доводиться пам'ятати про парний виклик hal_critical_exit() у КОЖНІЙ
// гілці виходу, включно з ранніми return. Тут вихід із секції робить
// деструктор, і забути його неможливо навіть у складному розгалуженні.
#pragma once

#include <cstdint>

namespace hal {

// Реалізують порти: на Cortex-M це збереження PRIMASK і cpsid i,
// на комп'ютері розробника — порожні функції.
std::uint32_t critical_enter() noexcept;
void          critical_exit(std::uint32_t saved_state) noexcept;

class CriticalSection {
public:
    CriticalSection() noexcept : saved_{critical_enter()} {}
    ~CriticalSection() { critical_exit(saved_); }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;
    CriticalSection(CriticalSection&&) = delete;
    CriticalSection& operator=(CriticalSection&&) = delete;

private:
    std::uint32_t saved_;
};

} // namespace hal

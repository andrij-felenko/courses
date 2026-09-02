#include "diag_pin.hpp"

#include <algorithm>

namespace flight::control {

/* На платі це два записи в регістр порту, по кілька тактів кожен:
       GPIOB->BSRR = (1u << 7);         // фронт
       GPIOB->BSRR = (1u << (7 + 16));  // спад
   Пін навмисно смикають ДО й ПІСЛЯ всієї роботи такту, а не всередині: інакше
   виміряна ширина імпульсу перестане відповідати затримці, яку бачить мотор.
   На хості замість піна беремо монотонний годинник — той самий інтервал. */

void DiagPin::raise() noexcept {
    if (armed_)
        return;  // пін уже піднято — повторний фронт нічого не означає
    rise_ = std::chrono::steady_clock::now();
    armed_ = true;
}

void DiagPin::lower() noexcept {
    if (!armed_)
        return;  // спаду без фронту не буває: цього такту пілот нічого не робив
    last_ = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now() - rise_);
    worst_ = std::max(worst_, last_);
    ++pulses_;
    armed_ = false;
}

DiagPin& diag_pin() noexcept {
    static DiagPin pin;
    return pin;
}

}  // namespace flight::control

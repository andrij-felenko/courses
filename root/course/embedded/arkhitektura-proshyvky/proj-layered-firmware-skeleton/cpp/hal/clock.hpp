// hal/clock.hpp — джерело часу в одиницях std::chrono, а не в голих числах.
// Тип не дає переплутати мілісекунди з тиками: це не коментар, це помилка компіляції.
#pragma once

#include <chrono>
#include <cstdint>

namespace hal {

class IClock {
public:
    using duration = std::chrono::milliseconds;
    using time_point = std::chrono::milliseconds;  // Час від старту, монотонний

    virtual ~IClock() = default;

    IClock() = default;
    IClock(const IClock&) = delete;
    IClock& operator=(const IClock&) = delete;

    virtual time_point now() const = 0;
    virtual void sleep_for(duration d) = 0;

    duration elapsed_since(time_point earlier) const { return now() - earlier; }
};

}  // namespace hal

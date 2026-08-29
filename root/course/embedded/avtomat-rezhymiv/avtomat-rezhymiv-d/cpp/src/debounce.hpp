#pragma once

#include <optional>

#include "params.hpp"

namespace fm {

/* Асиметричний фільтр деренчання. Умови борту балансують на межі порога й
   миготять з частотою такту; автомат мусить бачити стійкий стан.

   Асиметрія навмисна: перехід у бік дозволу вимагає витримки rise, перехід у
   бік заборони — витримки fall, і для охоронців fall дорівнює нулю. Небезпеку
   визнаємо миттєво, безпеку — лише витриману. */
class Debounce {
public:
    explicit Debounce(bool initial = false) noexcept : state_{initial}, candidate_{initial} {}

    bool update(bool raw, TimePoint now, Millis rise, Millis fall) noexcept
    {
        if (!primed_) {
            // Перший такт: часової бази ще немає, витримувати нема від чого.
            primed_       = true;
            state_        = raw;
            candidate_    = raw;
            candidateAt_  = now;
            stateAt_      = now;
            return state_;
        }

        if (raw == state_) {
            // Повернення до стійкого стану спалює накопичену витримку —
            // саме це й гасить деренчання на межі порога.
            candidate_   = raw;
            candidateAt_ = now;
            return state_;
        }

        if (raw != candidate_) {
            candidate_   = raw;
            candidateAt_ = now;
        }

        const Millis need = raw ? rise : fall;

        if (now - candidateAt_ >= need) {
            state_   = raw;
            stateAt_ = now;
        }
        return state_;
    }

    [[nodiscard]] bool state() const noexcept { return state_; }

    /* Скільки поточний стійкий стан уже тримається; поки фільтр не бачив
       жодного такту, відповіді немає — і це не те саме, що «нуль». */
    [[nodiscard]] std::optional<Millis> heldFor(TimePoint now) const noexcept
    {
        if (!primed_) {
            return std::nullopt;
        }
        return std::chrono::duration_cast<Millis>(now - stateAt_);
    }

    void reset(bool initial) noexcept
    {
        state_     = initial;
        candidate_ = initial;
        primed_    = false;
    }

private:
    bool      state_{};
    bool      candidate_{};
    bool      primed_{};
    TimePoint candidateAt_{};
    TimePoint stateAt_{};
};

}  // namespace fm

#pragma once

#include <chrono>

#include "guards.hpp"
#include "mode.hpp"
#include "params.hpp"
#include "telemetry.hpp"

namespace fm {

using Seconds = std::chrono::duration<float>;

/* Наскільки стік розходиться з поточною тягою (0..1). */
[[nodiscard]] float throttleMismatch(const VehicleState& s) noexcept;

/* Заслінка газу: перехід з режиму з автоматичною тягою в режим прямої тяги
   дозволено лише тоді, коли фізичне положення стіка вже збігається з тим, що
   видає регулятор. Інакше вихід стрибне з тяги висіння в нуль за один такт. */
[[nodiscard]] GuardResult throttleInterlock(Mode current, Mode target,
                                            const VehicleState& s, const Params& p,
                                            bool inAir) noexcept;

/* Обмежувач швидкості наростання: навіть після дозволеного переходу вихід не
   має права змінюватися стрибком. */
class SlewLimiter {
public:
    explicit SlewLimiter(float initial = 0.0F) noexcept : output_{initial} {}

    void reset(float value) noexcept
    {
        output_ = value;
        primed_ = true;
    }

    [[nodiscard]] float step(float target, Seconds dt, float ratePerS) noexcept;
    [[nodiscard]] float output() const noexcept { return output_; }

private:
    float output_{};
    bool  primed_{true};
};

}  // namespace fm

// Розмазування навантаження в часі: початковий джитер і повтори за
// Decorrelated Jitter. Тут же сівба генератора — саме на ній ламаються
// кампанії, коли тисяча вузлів дістає однакову «випадкову» затримку.
#pragma once

#include "cohort.hpp"

#include <chrono>
#include <cstdint>
#include <random>

namespace fleet {

using Millis = std::chrono::milliseconds;

class Rng {
public:
    // Сівба з апаратних джерел ентропії ПЛЮС ідентифікатор кристала.
    explicit Rng(const DeviceId& id);

    // Рівномірний розподіл без зсуву за модулем.
    [[nodiscard]] std::uint32_t below(std::uint32_t bound);
    [[nodiscard]] Millis between(Millis lo, Millis hi);

private:
    std::mt19937 engine_;
};

// Початкова затримка вузла в межах вікна фази: пік перетворюється на потік.
[[nodiscard]] Millis initial_jitter(Rng& rng, Millis window);

// t = min(T_max, Uniform(T_base, t_попередній · 3))
class DecorrelatedBackoff {
public:
    DecorrelatedBackoff(Millis base, Millis max) noexcept;

    [[nodiscard]] Millis next(Rng& rng);
    void reset() noexcept { previous_ = base_; attempts_ = 0; }
    [[nodiscard]] unsigned attempts() const noexcept { return attempts_; }

private:
    Millis base_;
    Millis max_;
    Millis previous_;
    unsigned attempts_{0};
};

} // namespace fleet

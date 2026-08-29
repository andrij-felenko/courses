#pragma once

/*
 * Політика-заглушка для хостових тестів: замість PRIMASK — атомарні
 * лічильники. Вартовий, вкладеність і винятки перевіряються на x86,
 * без плати й без жодної інструкції ARM.
 */

#include <atomic>
#include <cstdint>

#include "../critical_section.hpp"

namespace embedded::test {

class MockLockPolicy {
public:
    using StateType = std::uint32_t;   // 0 — переривання дозволені

    static inline std::atomic<std::uint32_t> masked{0};
    static inline std::atomic<std::uint32_t> depth{0};
    static inline std::atomic<std::uint32_t> max_depth{0};
    static inline std::atomic<std::uint32_t> enters{0};
    static inline std::atomic<std::uint32_t> exits{0};

    [[nodiscard]] static StateType enter() noexcept
    {
        const StateType saved = masked.exchange(1U);
        const std::uint32_t current = depth.fetch_add(1U) + 1U;

        std::uint32_t seen = max_depth.load();
        while (current > seen && !max_depth.compare_exchange_weak(seen, current)) {
            // seen оновлено обміном — пробуємо ще раз
        }
        ++enters;
        return saved;
    }

    static void exit(StateType saved) noexcept
    {
        masked.store(saved);
        depth.fetch_sub(1U);
        ++exits;
    }

    static void reset() noexcept
    {
        masked.store(0U);
        depth.store(0U);
        max_depth.store(0U);
        enters.store(0U);
        exits.store(0U);
    }

    [[nodiscard]] static bool locked() noexcept { return masked.load() != 0U; }
};

static_assert(sync::LockPolicy<MockLockPolicy>);

}  // namespace embedded::test

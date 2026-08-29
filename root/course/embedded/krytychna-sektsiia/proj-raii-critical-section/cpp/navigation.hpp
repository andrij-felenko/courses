#pragma once

#include <cstdint>
#include <optional>

#include "critical_section.hpp"

namespace flight {

struct NavigationData {
    std::int32_t  latitude{0};      // 1e-7 градуса
    std::int32_t  longitude{0};     // 1e-7 градуса
    std::int32_t  altitude_mm{0};
    std::uint64_t timestamp_us{0};
};

/*
 * Політика блокування — параметр шаблона: на платі це PRIMASK, у хостових
 * тестах — заглушка. Код класу від цього не змінюється жодним рядком.
 */
template <embedded::sync::LockPolicy Policy>
class NavigationManager {
public:
    using Guard = embedded::sync::CriticalSectionGuard<Policy>;

    /* Контекст: обробник переривання GNSS, приблизно 100 Гц. */
    void update(const NavigationData& fix) noexcept
    {
        const Guard lock;
        data_    = fix;
        has_fix_ = true;
        ++updates_;
    }

    /* Контекст: фонова задача телеметрії. */
    [[nodiscard]] std::optional<NavigationData> snapshot() const noexcept
    {
        const Guard lock;
        if (!has_fix_) {
            // Достроковий вихід з-під блокування: деструктор вартового
            // спрацює й тут, тому «забути відновити маску» неможливо.
            return std::nullopt;
        }
        return data_;
    }

    void reset() noexcept
    {
        const Guard lock;
        has_fix_ = false;
        updates_ = 0U;
    }

    /* Вирівняне 32-бітне читання на Cortex-M атомарне — секція тут зайва. */
    [[nodiscard]] std::uint32_t updates() const noexcept { return updates_; }

private:
    NavigationData data_{};
    bool           has_fix_{false};
    std::uint32_t  updates_{0};
};

#if defined(__ARM_ARCH)

using Navigation = NavigationManager<embedded::sync::PrimaskLockPolicy>;

inline Navigation g_navigation{};

/* Драйвери плати. */
bool gnss_read_fix(NavigationData& out) noexcept;
void radio_send(const NavigationData& fix) noexcept;

/* Тіло обробника переривання; у векторній таблиці стоїть extern "C"
   перехідник, який кличе цю функцію. */
inline void on_gnss_irq() noexcept
{
    NavigationData fix;
    if (gnss_read_fix(fix)) {   // битий кадр лишає старий фікс чинним
        g_navigation.update(fix);
    }
}

inline void telemetry_step() noexcept
{
    if (const auto snapshot = g_navigation.snapshot()) {
        radio_send(*snapshot);   // передача — ПОЗА критичною секцією
    }
}

#endif  // __ARM_ARCH

}  // namespace flight

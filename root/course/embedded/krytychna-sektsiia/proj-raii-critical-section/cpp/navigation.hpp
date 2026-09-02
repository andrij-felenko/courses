#pragma once

/*
 * Телеметрія навігації: клас нічого не знає ні про плату, ні про PRIMASK —
 * політика блокування приходить параметром шаблона. На платі це PRIMASK,
 * у хостових тестах — заглушка, і код класу від цього не змінюється.
 */

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

template <embedded::sync::LockPolicy Policy>
class NavigationManager {
public:
    using Guard = embedded::sync::CriticalSectionGuard<Policy>;

    /* Контекст: обробник переривання GNSS, приблизно 100 Гц.
       Чотири поля й 64-бітна мітка — це кілька окремих STR; переривання
       посеред них віддало б читачеві пакет із двох різних фіксів. */
    void update(const NavigationData& fix) noexcept
    {
        const Guard lock;
        data_    = fix;
        has_fix_ = true;
        ++updates_;   // читання-зміна-запис: неподільний лише під маскою
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

    /* Секція тут зайва: вирівняне 32-бітне читання на Cortex-M неподільне.
       Але без volatile компілятор мав би право лишити значення в регістрі
       й крутити фоновий цикл на числі, яке ISR давно змінив. */
    [[nodiscard]] std::uint32_t updates() const noexcept { return updates_; }

private:
    NavigationData         data_{};
    bool                   has_fix_{false};
    volatile std::uint32_t updates_{0};
};

/*
 * Драйвери плати: реалізує BSP апарата (у хостовому тесті вони не потрібні,
 * бо тест працює з NavigationManager напряму).
 */
bool gnss_read_fix(NavigationData& out) noexcept;
void radio_send(const NavigationData& fix) noexcept;

/* Тіло обробника переривання GNSS; у векторній таблиці стоїть extern "C"
   перехідник GNSS_IRQHandler, який кличе цю функцію. */
void on_gnss_irq() noexcept;

/* Крок фонового циклу: віддати радіоканалу узгоджений знімок. */
void telemetry_step() noexcept;

}  // namespace flight

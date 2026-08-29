#pragma once

#include <array>
#include <atomic>
#include <bitset>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace autopilot::failsafe {

/* Номер біта і є ідентифікатором відмови: маска, таблиця порогів і
 * таблиця пріоритетів індексуються одним і тим самим значенням. */
enum class Fault : std::size_t {
    RcLost = 0,   // Втрата сигналу пульта керування
    GcsLost,      // Втрата телеметрії наземної станції
    GnssGlitch,   // Стрибок HDOP / втрата 3D Fix
    BatteryLow,   // Перший поріг розряду (попередження)
    BatteryCrit,  // Критичний поріг розряду
    Geofence,     // Вихід за межі дозволеного радіуса чи стелі
    Actuator,     // Відмова мотора, ESC або сервоприводу
    AttitudeLoss, // Втрата розрахунку просторової орієнтації
    Count
};

inline constexpr std::size_t kFaultCount = static_cast<std::size_t>(Fault::Count);

using FaultMask = std::bitset<kFaultCount>;

[[nodiscard]] constexpr std::size_t index(Fault f) noexcept {
    return static_cast<std::size_t>(f);
}

[[nodiscard]] constexpr std::uint32_t bit(Fault f) noexcept {
    return 1u << index(f);
}

/* Дії впорядковані за суворістю — на цьому порядку тримається заборона
 * самовільного пом'якшення, тож переставляти елементи не можна. */
enum class Action : std::uint8_t {
    None = 0,       // Штатний політ
    Warn,           // Лише індикація, режим не змінюємо
    AltHold,        // Утримання висоти за барометром
    ReturnToLaunch, // Автономне повернення на точку старту
    Land,           // Контрольований спуск на місці
    Terminate       // Відсікання приводів або парашут
};

[[nodiscard]] constexpr std::string_view name(Action a) noexcept {
    switch (a) {
    case Action::None:           return "NONE";
    case Action::Warn:           return "WARN";
    case Action::AltHold:        return "ALTHOLD";
    case Action::ReturnToLaunch: return "RTL";
    case Action::Land:           return "LAND";
    case Action::Terminate:      return "TERMINATE";
    }
    return "?";
}

[[nodiscard]] constexpr std::string_view name(Fault f) noexcept {
    constexpr std::array<std::string_view, kFaultCount> kNames{
        "RC_LOST", "GCS_LOST", "GNSS_GLITCH", "BATT_LOW",
        "BATT_CRIT", "GEOFENCE", "ACTUATOR", "ATTITUDE_LOSS"};
    return index(f) < kFaultCount ? kNames[index(f)] : "?";
}

/* ---------------------------------------------------------------------
 * Поштова скринька драйверів: біти ставлять обробники переривань і задача
 * оцінки орієнтації, читає — задача арбітра. Одне атомарне слово замість
 * м'ютекса, бо в ISR блокування недоречне, а інверсія пріоритетів у
 * контурі керування коштує апарата.
 * ------------------------------------------------------------------- */
class FaultInbox {
public:
    void report(Fault f, bool active) noexcept {
        const std::uint32_t flag = bit(f);
        if (active) {
            bits_.fetch_or(flag, std::memory_order_release);
        } else {
            bits_.fetch_and(~flag, std::memory_order_release);
        }
    }

    // Знімок за один такт: усі правила мусять дивитися на ту саму маску.
    [[nodiscard]] FaultMask snapshot() const noexcept {
        return FaultMask{bits_.load(std::memory_order_acquire)};
    }

private:
    std::atomic<std::uint32_t> bits_{0};
    static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
                  "маска мусить оновлюватися без блокувань — її чіпає ISR");
};

} // namespace autopilot::failsafe

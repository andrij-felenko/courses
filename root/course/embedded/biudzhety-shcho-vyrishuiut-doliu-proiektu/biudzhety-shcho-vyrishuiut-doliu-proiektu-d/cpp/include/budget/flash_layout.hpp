#pragma once

// Розкладка Flash під безвідмовне оновлення по повітрю.
//
// Розрахунок чистий і повністю constexpr: розкладку перевіряє компілятор ще
// на етапі збірки, а не пристрій у полі. Неможливість OTA — не «код -1», а
// std::unexpected із набором порушених бюджетів.

#include "budget/flags.hpp"

#include <cstdint>
#include <expected>

namespace budget {

struct FlashLayout {
    std::uint32_t total_bytes{0};
    std::uint32_t sector_bytes{0};      // гранула стирання
    std::uint32_t bootloader_bytes{0};  // незмінний сектор перевірки підпису
    std::uint32_t nvs_bytes{0};         // ключі, сертифікати, калібрування
    std::uint32_t image_bytes{0};       // розмір скомпільованого образу
};

struct FlashPlan {
    std::uint32_t slot_bytes{0};      // розмір кожного зі слотів A і B
    std::uint32_t slot_free_bytes{0}; // запас під майбутні версії
    std::uint32_t unusable_bytes{0};  // залишок поза парою слотів
    double        image_share{0.0};   // частка образу від повного Flash
    bool          tight{false};       // образ перетнув 45 % обсягу
};

// Золоте правило: образ не більший за 45 % повного Flash.
inline constexpr double kImageShareLimit = 0.45;

[[nodiscard]] constexpr std::expected<FlashPlan, Budget> plan_flash(
    const FlashLayout& layout) noexcept
{
    if (layout.total_bytes == 0 || layout.sector_bytes == 0) {
        return std::unexpected{Budget::FlashNoOta};
    }

    const std::uint32_t overhead = layout.bootloader_bytes + layout.nvs_bytes;
    if (overhead >= layout.total_bytes) {
        return std::unexpected{Budget::FlashNoOta};
    }

    const std::uint32_t for_slots = layout.total_bytes - overhead;

    // Слот кратний сектору стирання, інакше стирання зачепить сусіда.
    const std::uint32_t slot =
        (for_slots / 2) / layout.sector_bytes * layout.sector_bytes;

    const double share = static_cast<double>(layout.image_bytes) /
                         static_cast<double>(layout.total_bytes);
    const bool tight = share > kImageShareLimit;

    if (slot == 0 || layout.image_bytes > slot) {
        return std::unexpected{tight ? (Budget::FlashNoOta | Budget::FlashTight)
                                     : Budget::FlashNoOta};
    }

    return FlashPlan{
        .slot_bytes      = slot,
        .slot_free_bytes = slot - layout.image_bytes,
        .unusable_bytes  = for_slots - slot * 2,
        .image_share     = share,
        .tight           = tight
    };
}

} // namespace budget

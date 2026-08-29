// Детерміноване розбиття парку на когорти 0..99.
// Вузол рахує свій номер сам; сіль кампанії приходить у маніфесті, тож наступна
// кампанія перетасовує парк заново.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>
#include <vector>

namespace fleet {

inline constexpr std::uint8_t kBuckets = 100;

using DeviceId = std::array<std::byte, 16>;

// Унікальний ідентифікатор кристала (STM32 — 96 біт за 0x1FFF7A10).
[[nodiscard]] DeviceId chip_id();

enum class HashKind {
    Sha256,   // основний варіант
    Fnv1a     // для кристалів без прискорювача криптографії
};

class CohortAssigner {
public:
    explicit CohortAssigner(std::string_view campaign_salt, HashKind kind = HashKind::Sha256);

    [[nodiscard]] std::uint8_t bucket(const DeviceId& id) const noexcept;

    // Фаза 1% — це кошик 0, фаза 25% — кошики 0..24.
    [[nodiscard]] bool eligible(const DeviceId& id, std::uint8_t stage_percent) const noexcept;

    struct Distribution {
        std::array<std::uint32_t, kBuckets> counts{};
        std::uint32_t total{};
        std::uint32_t min{};
        std::uint32_t max{};
        double chi_square{};

        // Критичне значення хі-квадрат для 99 ступенів вільності на рівні 0.01.
        [[nodiscard]] bool acceptable() const noexcept;
    };

    // Зріз по всій множині серійних номерів парку — рахується на стенді, поки
    // кампанія ще не почалася.
    [[nodiscard]] Distribution survey(std::span<const DeviceId> fleet) const;

private:
    std::vector<std::byte> salt_;
    HashKind kind_;
};

} // namespace fleet

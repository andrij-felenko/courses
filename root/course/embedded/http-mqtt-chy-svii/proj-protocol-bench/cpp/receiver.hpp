// Приймальний бік власного протоколу: шлюз або серверний демон (C++23).
#pragma once

#include "telemetry.hpp"

#include <cstdint>
#include <expected>
#include <optional>
#include <span>

namespace telem {

// Стан звʼязку з ОДНИМ вузлом: лічильник послідовності має сенс лише в парі
// з конкретним відправником, тож на сервері такий обʼєкт заводять на кожен
// ідентифікатор пристрою.
class Receiver {
public:
    struct Frame {
        Sample sample{};
        std::uint16_t seq{};
    };

    struct Stats {
        std::uint32_t accepted{};
        std::uint32_t too_short{};
        std::uint32_t bad_magic{};
        std::uint32_t bad_type{};
        std::uint32_t bad_crc{};
        std::uint32_t replay{};
    };

    // Чотири перевірки поспіль: довжина, синхробайт, CRC, номер послідовності.
    [[nodiscard]] std::expected<Frame, DecodeError> accept(std::span<const std::uint8_t> raw) noexcept;

    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    std::optional<std::uint16_t> last_seq_{};
    Stats stats_{};
};

}  // namespace telem

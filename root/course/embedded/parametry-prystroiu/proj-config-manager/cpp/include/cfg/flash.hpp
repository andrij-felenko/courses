#pragma once
// flash.hpp — модель двох секторів Flash: стерте це 0xFF, а програмування
// вміє лише гасити біти (1 → 0).

#include "cfg/config.hpp"

#include <expected>

namespace cfg {

class Flash {
public:
    static constexpr std::size_t kSlots = 2;   // Slot A і Slot B

    Flash() noexcept { wipe(); }

    void wipe() noexcept;                      // стан пам'яті з конвеєра
    void erase(std::size_t slot) noexcept;
    std::expected<void, Error> program(std::size_t slot, std::size_t offset,
                                       std::span<const std::byte> src) noexcept;
    [[nodiscard]] std::span<const std::byte> read(std::size_t slot) const noexcept;

private:
    std::array<std::array<std::byte, kSectorSize>, kSlots> sectors_{};
};

}  // namespace cfg

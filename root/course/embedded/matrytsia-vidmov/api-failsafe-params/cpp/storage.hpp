#pragma once

// Двозбірне зберігання конфігурації в секторі NOR Flash.
// Свіжіший банк визначається лічильником транзакцій, а не окремим прапорцем.

#include "params.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <vector>

namespace autopilot::failsafe {

inline constexpr std::size_t   kSectorSize    = 256;
inline constexpr std::uint32_t kParamMagic    = 0x30425346u;  // "FSB0"
inline constexpr std::uint16_t kSchemaVersion = 3;
inline constexpr std::size_t   kHeaderSize    = 12;  // magic + schema + count + seq

enum class StoreError {
    Erased,        // сектор стертий: суцільні 0xFF
    BadMagic,
    BadCrc,
    FutureSchema,  // запис новішої прошивки
    FlashFailure,  // запис не підтвердився зчитуванням
    NoValidBank    // жодна копія не придатна
};

std::string_view toString(StoreError e) noexcept;

std::uint32_t crc32(std::span<const std::byte> data) noexcept;

// Мок драйвера NOR: гасити біти вміє лише стирання сектора.
class FlashSector {
public:
    FlashSector() : mem_(kSectorSize, std::byte{0xFF}) {}

    std::span<const std::byte> read() const noexcept { return mem_; }
    void erase() noexcept;
    [[nodiscard]] bool program(std::span<const std::byte> src) noexcept;
    void flipBit(std::size_t byteOffset, int bit) noexcept;  // стендове псування комірки

private:
    std::vector<std::byte> mem_;
};

class ParamStore {
public:
    struct Loaded {
        ParamBlock  block;
        std::size_t bank;
        std::size_t clamped;  // скільки значень довелося замінити заводськими
    };

    std::expected<Loaded, StoreError>  load();
    std::expected<void, StoreError>    save(const ParamBlock& block);

    FlashSector& bank(std::size_t i) noexcept { return banks_[i]; }
    std::size_t  activeBank() const noexcept { return active_; }
    std::uint32_t sequence() const noexcept { return seq_; }

private:
    struct Decoded {
        ParamBlock    block;
        std::uint32_t seq;
        std::size_t   clamped;
    };
    std::expected<Decoded, StoreError> decode(const FlashSector& sector) const;

    std::array<FlashSector, 2> banks_{};
    std::size_t                active_{0};
    std::uint32_t              seq_{0};
};

} // namespace autopilot::failsafe

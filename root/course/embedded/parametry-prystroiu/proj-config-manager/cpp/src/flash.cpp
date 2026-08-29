#include "cfg/flash.hpp"

namespace cfg {

void Flash::wipe() noexcept
{
    for (auto& sector : sectors_) {
        sector.fill(std::byte{0xFF});
    }
}

void Flash::erase(std::size_t slot) noexcept
{
    if (slot < kSlots) {
        sectors_[slot].fill(std::byte{0xFF});
    }
}

std::expected<void, Error> Flash::program(std::size_t slot, std::size_t offset,
                                          std::span<const std::byte> src) noexcept
{
    if (slot >= kSlots || offset > kSectorSize || src.size() > kSectorSize - offset) {
        return std::unexpected(Error::FlashWriteRejected);
    }

    const std::span page{sectors_[slot].data() + offset, src.size()};

    // Спершу перевіряємо всю сторінку: відмова не має лишати запис наполовину.
    for (std::size_t i = 0; i < src.size(); ++i) {
        if ((page[i] & src[i]) != src[i]) {
            return std::unexpected(Error::FlashWriteRejected);  // біт 0 → 1 вміє лише стирання
        }
    }
    for (std::size_t i = 0; i < src.size(); ++i) {
        page[i] &= src[i];
    }
    return {};
}

std::span<const std::byte> Flash::read(std::size_t slot) const noexcept
{
    if (slot >= kSlots) {
        return {};
    }
    return std::span<const std::byte>{sectors_[slot]};
}

}  // namespace cfg

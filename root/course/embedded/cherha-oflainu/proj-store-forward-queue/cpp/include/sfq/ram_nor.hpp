// ram_nor.hpp — модель NOR у ОЗП.
//
// Потрібна не «щоб потестувати», а щоб на занятті показати те, чого на
// живій платі не покажеш: зникнення живлення посеред програмування
// сторінки. Семантика справжня — програмування лише гасить біти,
// стирання піднімає сектор у 0xFF, — тож обірваний кадр лишає по собі
// рівно те саме сміття, що й у кристалі.
//
// Пам'ять — std::array всередині об'єкта: жодного динамічного байта.
#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "sfq/flash.hpp"

namespace sfq {

template <std::size_t Sectors, std::size_t SectorSize = 4096, std::size_t PageSize = 256>
class RamNorFlash {
public:
    static constexpr std::size_t kCapacity = Sectors * SectorSize;

    RamNorFlash() noexcept { bulk_erase(); }

    [[nodiscard]] Geometry geometry() const noexcept
    {
        return Geometry{
            .sector_size = static_cast<std::uint32_t>(SectorSize),
            .page_size = static_cast<std::uint32_t>(PageSize),
            .capacity = static_cast<std::uint32_t>(kCapacity),
        };
    }

    [[nodiscard]] FlashResult read(std::uint32_t addr, std::span<std::byte> dst) noexcept
    {
        if (addr + dst.size() > kCapacity) {
            return std::unexpected(FlashError::OutOfRange);
        }
        if (!powered_) {
            return std::unexpected(FlashError::Io);
        }
        std::ranges::copy(std::span{mem_}.subspan(addr, dst.size()), dst.begin());
        return {};
    }

    [[nodiscard]] FlashResult program(std::uint32_t addr, std::span<const std::byte> src) noexcept
    {
        if (addr + src.size() > kCapacity) {
            return std::unexpected(FlashError::OutOfRange);
        }
        if (!powered_) {
            return std::unexpected(FlashError::Io);
        }

        ++programs_;
        for (std::size_t i = 0; i < src.size(); ++i) {
            if (write_budget_ == 0) {
                // Напруга просіла посеред сторінки: байти, що вже пішли
                // в кристал, там і лишились — саме ця половинка кадру
                // потім не зійдеться за CRC.
                powered_ = false;
                return std::unexpected(FlashError::Io);
            }
            if (write_budget_ != kUnlimited) {
                --write_budget_;
            }
            mem_[addr + i] &= src[i];  // програмування вміє лише гасити біти
        }
        return {};
    }

    [[nodiscard]] FlashResult erase_sector(std::uint32_t addr) noexcept
    {
        if (addr % SectorSize != 0) {
            return std::unexpected(FlashError::NotAligned);
        }
        if (addr + SectorSize > kCapacity) {
            return std::unexpected(FlashError::OutOfRange);
        }
        if (!powered_) {
            return std::unexpected(FlashError::Io);
        }
        std::ranges::fill(std::span{mem_}.subspan(addr, SectorSize), std::byte{0xFF});
        ++erases_;
        return {};
    }

    // --- важелі заняття ---

    void bulk_erase() noexcept
    {
        std::ranges::fill(mem_, std::byte{0xFF});
        ++erases_;
    }

    void cut_power_after(std::uint32_t bytes) noexcept { write_budget_ = bytes; }

    // Вміст лишається таким, яким його застало зникнення напруги.
    void power_up() noexcept
    {
        powered_ = true;
        write_budget_ = kUnlimited;
    }

    [[nodiscard]] std::uint32_t erase_count() const noexcept { return erases_; }
    [[nodiscard]] std::uint32_t program_count() const noexcept { return programs_; }

private:
    static constexpr std::uint32_t kUnlimited = 0xFFFFFFFFu;

    std::array<std::byte, kCapacity> mem_{};
    std::uint32_t write_budget_{kUnlimited};
    std::uint32_t erases_{};
    std::uint32_t programs_{};
    bool powered_{true};
};

}  // namespace sfq

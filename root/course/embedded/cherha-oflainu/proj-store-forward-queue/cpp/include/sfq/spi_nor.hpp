// spi_nor.hpp — драйвер SPI NOR (W25Qxx / MX25Lxx) поверх довільної шини.
//
// Драйвер існує заради трьох речей, яких черга бачити не повинна:
//   * запис не має права перетнути межу сторінки в 256 байтів — мікросхема
//     не перейде на наступну, а загорне адресу на початок тієї самої
//     сторінки й тихо затре власний початок кадру;
//   * WREN скидається після кожної операції й потрібен щоразу;
//   * після програмування чи стирання треба дочекатися зняття BUSY.
//
// CS тримає RAII-вартовий: у C ця пара select/deselect розсипана по
// кожній гілці виходу, і саме там її забувають.
#pragma once

#include <algorithm>
#include <array>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "sfq/flash.hpp"

namespace sfq {

template <class B>
concept SpiBus = requires(B& bus, std::span<const std::byte> tx, std::span<std::byte> rx) {
    { bus.select() } -> std::same_as<void>;
    { bus.deselect() } -> std::same_as<void>;
    { bus.write(tx) } -> std::same_as<bool>;
    { bus.read(rx) } -> std::same_as<bool>;
    { bus.now_ms() } -> std::same_as<std::uint32_t>;
};

template <SpiBus Bus>
class SpiNorFlash {
public:
    static constexpr std::uint32_t kSectorSize = 4096;
    static constexpr std::uint32_t kPageSize = 256;

    // Паспортні максимуми W25Q128: сторінка 3 мс, сектор 400 мс.
    static constexpr std::uint32_t kProgramTimeoutMs = 10;
    static constexpr std::uint32_t kEraseTimeoutMs = 800;

    SpiNorFlash(Bus& bus, std::uint32_t capacity) noexcept : bus_{bus}, capacity_{capacity} {}

    // Читає JEDEC ID: нулі або одиниці означають не мікросхему, а
    // непідключений CS.
    [[nodiscard]] std::expected<std::array<std::uint8_t, 3>, FlashError> probe() noexcept
    {
        std::array<std::byte, 3> raw{};
        {
            const ChipSelect cs{bus_};
            if (!command(0x9Fu) || !bus_.read(raw)) {
                return std::unexpected(FlashError::Io);
            }
        }

        std::array<std::uint8_t, 3> id{};
        for (std::size_t i = 0; i < id.size(); ++i) {
            id[i] = std::to_integer<std::uint8_t>(raw[i]);
        }
        if (id[0] == 0x00u || id[0] == 0xFFu) {
            return std::unexpected(FlashError::Io);
        }
        return id;
    }

    [[nodiscard]] Geometry geometry() const noexcept
    {
        return Geometry{.sector_size = kSectorSize, .page_size = kPageSize, .capacity = capacity_};
    }

    [[nodiscard]] FlashResult read(std::uint32_t addr, std::span<std::byte> dst) noexcept
    {
        if (addr + dst.size() > capacity_) {
            return std::unexpected(FlashError::OutOfRange);
        }
        if (auto ready = wait_ready(kEraseTimeoutMs); !ready) {
            return ready;
        }

        const ChipSelect cs{bus_};
        if (!command_with_address(0x03u, addr) || !bus_.read(dst)) {
            return std::unexpected(FlashError::Io);
        }
        return {};
    }

    [[nodiscard]] FlashResult program(std::uint32_t addr, std::span<const std::byte> src) noexcept
    {
        if (addr + src.size() > capacity_) {
            return std::unexpected(FlashError::OutOfRange);
        }

        // Кадр черги (до 536 байтів) майже завжди перетинає межу
        // сторінки. Ріжемо тут — і більше ніде про це не думаємо.
        while (!src.empty()) {
            const std::uint32_t page_left = kPageSize - (addr % kPageSize);
            const std::size_t chunk = std::min<std::size_t>(src.size(), page_left);

            if (auto done = program_page(addr, src.first(chunk)); !done) {
                return done;
            }
            addr += static_cast<std::uint32_t>(chunk);
            src = src.subspan(chunk);
        }
        return {};
    }

    [[nodiscard]] FlashResult erase_sector(std::uint32_t addr) noexcept
    {
        if (addr % kSectorSize != 0) {
            return std::unexpected(FlashError::NotAligned);
        }
        if (addr + kSectorSize > capacity_) {
            return std::unexpected(FlashError::OutOfRange);
        }
        if (auto enabled = write_enable(); !enabled) {
            return enabled;
        }

        {
            const ChipSelect cs{bus_};
            if (!command_with_address(0x20u, addr)) {
                return std::unexpected(FlashError::Io);
            }
        }
        return wait_ready(kEraseTimeoutMs);
    }

private:
    // CS опускається на час однієї команди й піднімається на будь-якому
    // виході з області видимості, включно з винятком.
    class ChipSelect {
    public:
        explicit ChipSelect(Bus& bus) noexcept : bus_{bus} { bus_.select(); }
        ~ChipSelect() { bus_.deselect(); }
        ChipSelect(const ChipSelect&) = delete;
        ChipSelect& operator=(const ChipSelect&) = delete;

    private:
        Bus& bus_;
    };

    [[nodiscard]] bool command(std::uint8_t code) noexcept
    {
        const std::byte frame[1]{static_cast<std::byte>(code)};
        return bus_.write(frame);
    }

    [[nodiscard]] bool command_with_address(std::uint8_t code, std::uint32_t addr) noexcept
    {
        const std::byte frame[4]{
            static_cast<std::byte>(code),
            static_cast<std::byte>((addr >> 16) & 0xFFu),
            static_cast<std::byte>((addr >> 8) & 0xFFu),
            static_cast<std::byte>(addr & 0xFFu),
        };
        return bus_.write(frame);
    }

    [[nodiscard]] std::expected<std::uint8_t, FlashError> read_status() noexcept
    {
        std::array<std::byte, 1> status{};
        const ChipSelect cs{bus_};
        if (!command(0x05u) || !bus_.read(status)) {
            return std::unexpected(FlashError::Io);
        }
        return std::to_integer<std::uint8_t>(status[0]);
    }

    // Опитування статусу, не переривання: працює й тоді, коли планувальник
    // уже зупинено, а журнал ще треба дописати.
    [[nodiscard]] FlashResult wait_ready(std::uint32_t timeout_ms) noexcept
    {
        const std::uint32_t start = bus_.now_ms();
        for (;;) {
            const auto status = read_status();
            if (!status) {
                return std::unexpected(status.error());
            }
            if ((*status & 0x01u) == 0u) {  // BUSY знято
                return {};
            }
            if (bus_.now_ms() - start > timeout_ms) {
                return std::unexpected(FlashError::Timeout);
            }
        }
    }

    // Мовчазне ігнорування WREN — класична ознака непропаяного CS,
    // тому перевіряємо, що біт WEL справді піднявся.
    [[nodiscard]] FlashResult write_enable() noexcept
    {
        {
            const ChipSelect cs{bus_};
            if (!command(0x06u)) {
                return std::unexpected(FlashError::Io);
            }
        }
        const auto status = read_status();
        if (!status) {
            return std::unexpected(status.error());
        }
        if ((*status & 0x02u) == 0u) {
            return std::unexpected(FlashError::Io);
        }
        return {};
    }

    [[nodiscard]] FlashResult program_page(std::uint32_t addr,
                                           std::span<const std::byte> src) noexcept
    {
        if (auto enabled = write_enable(); !enabled) {
            return enabled;
        }
        {
            const ChipSelect cs{bus_};
            if (!command_with_address(0x02u, addr) || !bus_.write(src)) {
                return std::unexpected(FlashError::Io);
            }
        }
        return wait_ready(kProgramTimeoutMs);
    }

    Bus& bus_;
    std::uint32_t capacity_;
};

}  // namespace sfq

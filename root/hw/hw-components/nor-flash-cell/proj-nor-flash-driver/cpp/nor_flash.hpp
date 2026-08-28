// nor_flash.hpp — Ідіоматичний C++20 драйвер для SPI/QSPI NOR Flash
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include <chrono>

namespace memory::flash {

inline constexpr size_t PageSize    = 256;
inline constexpr size_t SectorSize  = 4096;
inline constexpr size_t BlockSize   = 65536;

enum class Command : uint8_t {
    ReadId          = 0x9F,
    WriteEnable     = 0x06,
    WriteDisable    = 0x04,
    ReadStatus1     = 0x05,
    FastRead        = 0x0B,
    PageProgram     = 0x02,
    SectorErase4K   = 0x20,
    BlockErase64K   = 0xD8,
    ChipErase       = 0xC7
};

enum class Error : uint8_t {
    Timeout,
    InvalidAddress,
    DeviceNotResponding,
    WriteProtected
};

struct JedecId {
    uint8_t manufacturer;
    uint8_t memory_type;
    uint8_t capacity_code;

    [[nodiscard]] constexpr size_t capacityBytes() const noexcept {
        if (capacity_code >= 0x10 && capacity_code <= 0x22) {
            return size_t{1} << capacity_code;
        }
        return 0;
    }
};

/* Концепт апаратного SPI транспорту */
template <typename T>
concept SpiBus = requires(T bus, uint8_t byte, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.select() } -> std::same_as<void>;
    { bus.deselect() } -> std::same_as<void>;
    { bus.transfer(byte) } -> std::same_as<uint8_t>;
    { bus.write(tx) } -> std::same_as<void>;
    { bus.read(rx) } -> std::same_as<void>;
    { bus.delay(std::chrono::microseconds{}) } -> std::same_as<void>;
};

template <SpiBus Bus>
class NorFlashDriver {
public:
    explicit NorFlashDriver(Bus& bus) noexcept : bus_(bus) {}

    [[nodiscard]] std::expected<JedecId, Error> init() noexcept {
        bus_.deselect();
        bus_.delay(std::chrono::milliseconds{1});

        auto id = readJedecId();
        if ((id.manufacturer == 0x00 && id.capacity_code == 0x00) ||
            (id.manufacturer == 0xFF && id.capacity_code == 0xFF)) {
            return std::unexpected(Error::DeviceNotResponding);
        }

        total_size_ = id.capacityBytes();
        if (auto res = waitBusy(std::chrono::milliseconds{100}); !res) {
            return std::unexpected(res.error());
        }

        return id;
    }

    [[nodiscard]] std::expected<void, Error> read(uint32_t address,
                                                  std::span<uint8_t> dest) noexcept {
        if (address + dest.size() > total_size_) {
            return std::unexpected(Error::InvalidAddress);
        }
        if (auto res = waitBusy(std::chrono::milliseconds{200}); !res) {
            return res;
        }

        auto lock = makeBusLock();
        bus_.transfer(static_cast<uint8_t>(Command::FastRead));
        sendAddress(address);
        bus_.transfer(0xFF); // 1 Dummy byte
        bus_.read(dest);

        return {};
    }

    [[nodiscard]] std::expected<void, Error> eraseSector(uint32_t sector_addr) noexcept {
        sector_addr &= ~(SectorSize - 1);
        if (sector_addr >= total_size_) {
            return std::unexpected(Error::InvalidAddress);
        }
        if (auto res = waitBusy(std::chrono::milliseconds{200}); !res) {
            return res;
        }

        writeEnable();

        {
            auto lock = makeBusLock();
            bus_.transfer(static_cast<uint8_t>(Command::SectorErase4K));
            sendAddress(sector_addr);
        }

        return waitBusy(std::chrono::milliseconds{500});
    }

    [[nodiscard]] std::expected<void, Error> write(uint32_t address,
                                                   std::span<const uint8_t> data) noexcept {
        if (address + data.size() > total_size_) {
            return std::unexpected(Error::InvalidAddress);
        }

        size_t offset = 0;
        while (offset < data.size()) {
            uint32_t current_addr = address + static_cast<uint32_t>(offset);
            uint32_t page_offset  = current_addr % PageSize;
            size_t chunk_len      = std::min(data.size() - offset, PageSize - page_offset);

            if (auto res = programPage(current_addr, data.subspan(offset, chunk_len)); !res) {
                return res;
            }

            offset += chunk_len;
        }
        return {};
    }

private:
    Bus& bus_;
    size_t total_size_{0};

    struct BusLock {
        Bus& b;
        explicit BusLock(Bus& bus) noexcept : b(bus) { b.select(); }
        ~BusLock() noexcept { b.deselect(); }
        BusLock(const BusLock&) = delete;
        BusLock& operator=(const BusLock&) = delete;
    };

    [[nodiscard]] BusLock makeBusLock() noexcept { return BusLock(bus_); }

    void sendAddress(uint32_t addr) noexcept {
        bus_.transfer(static_cast<uint8_t>(addr >> 16));
        bus_.transfer(static_cast<uint8_t>(addr >> 8));
        bus_.transfer(static_cast<uint8_t>(addr >> 0));
    }

    void writeEnable() noexcept {
        auto lock = makeBusLock();
        bus_.transfer(static_cast<uint8_t>(Command::WriteEnable));
    }

    [[nodiscard]] JedecId readJedecId() noexcept {
        auto lock = makeBusLock();
        bus_.transfer(static_cast<uint8_t>(Command::ReadId));
        return JedecId{
            .manufacturer  = bus_.transfer(0xFF),
            .memory_type   = bus_.transfer(0xFF),
            .capacity_code = bus_.transfer(0xFF)
        };
    }

    [[nodiscard]] std::expected<void, Error> waitBusy(std::chrono::milliseconds timeout) noexcept {
        const auto deadline_us = std::chrono::duration_cast<std::chrono::microseconds>(timeout).count();
        int64_t elapsed_us = 0;

        while (elapsed_us <= deadline_us) {
            uint8_t status = 0;
            {
                auto lock = makeBusLock();
                bus_.transfer(static_cast<uint8_t>(Command::ReadStatus1));
                status = bus_.transfer(0xFF);
            }

            if ((status & 0x01) == 0) { // WIP == 0
                return {};
            }

            bus_.delay(std::chrono::microseconds{50});
            elapsed_us += 50;
        }
        return std::unexpected(Error::Timeout);
    }

    [[nodiscard]] std::expected<void, Error> programPage(uint32_t addr,
                                                         std::span<const uint8_t> chunk) noexcept {
        if (auto res = waitBusy(std::chrono::milliseconds{100}); !res) {
            return res;
        }

        writeEnable();

        {
            auto lock = makeBusLock();
            bus_.transfer(static_cast<uint8_t>(Command::PageProgram));
            sendAddress(addr);
            bus_.write(chunk);
        }

        return waitBusy(std::chrono::milliseconds{10});
    }
};

} // namespace memory::flash

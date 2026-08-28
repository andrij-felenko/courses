// atomic_storage.hpp — Транзакційне C++20 сховище з безпечною типізацією
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>
#include <array>
#include <concepts>
#include <cstring>

namespace embedded::storage {

inline constexpr uint32_t MagicWord    = 0x54534F4CU; // "LOST"
inline constexpr uint32_t CommitMarker = 0xA55A1234U;
inline constexpr size_t   MaxPayload   = 256;

enum class StorageError : uint8_t {
    InvalidParameter,
    FlashIoError,
    NoValidData,
    PayloadTooLarge,
    CrcMismatch
};

struct FlashDriver {
    bool (*read)(uint32_t address, std::span<std::byte> dest);
    bool (*write)(uint32_t address, std::span<const std::byte> src);
    bool (*erase_sector)(uint32_t address);
    size_t sector_size;
};

struct alignas(4) SectorHeader {
    uint32_t magic{MagicWord};
    uint32_t generation{0};
    uint16_t payload_len{0};
    uint16_t reserved{0xFFFF};
    uint32_t payload_crc32{0};
    uint32_t commit_marker{0xFFFFFFFF};
};

class AtomicStorage {
public:
    constexpr AtomicStorage(FlashDriver driver, uint32_t sec_a, uint32_t sec_b) noexcept
        : driver_{driver}, sector_a_{sec_a}, sector_b_{sec_b} {}

    [[nodiscard]] std::expected<void, StorageError> init() noexcept;
    
    [[nodiscard]] std::expected<size_t, StorageError> read(std::span<std::byte> dest) const noexcept;
    
    [[nodiscard]] std::expected<void, StorageError> write(std::span<const std::byte> src) noexcept;

    template <typename T>
        requires std::is_trivially_copyable_v<T>
    [[nodiscard]] std::expected<void, StorageError> writeObject(const T& obj) noexcept {
        auto span = std::as_bytes(std::span{&obj, 1});
        return write(span);
    }

    template <typename T>
        requires std::is_trivially_copyable_v<T>
    [[nodiscard]] std::expected<T, StorageError> readObject() const noexcept {
        T obj{};
        auto span = std::as_writable_bytes(std::span{&obj, 1});
        auto res = read(span);
        if (!res) return std::unexpected(res.error());
        return obj;
    }

private:
    [[nodiscard]] static uint32_t calculateCrc32(std::span<const std::byte> data) noexcept;
    [[nodiscard]] std::optional<SectorHeader> validateSector(uint32_t sector_addr) const noexcept;

    FlashDriver driver_;
    uint32_t sector_a_;
    uint32_t sector_b_;
    uint32_t active_sector_{0};
    uint32_t current_generation_{0};
    bool is_initialized_{false};
};

} // namespace embedded::storage

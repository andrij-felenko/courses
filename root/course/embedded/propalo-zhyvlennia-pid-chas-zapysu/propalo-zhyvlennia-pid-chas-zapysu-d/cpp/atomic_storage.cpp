// atomic_storage.cpp — Реалізація методів класу AtomicStorage
#include "atomic_storage.hpp"

namespace embedded::storage {

uint32_t AtomicStorage::calculateCrc32(std::span<const std::byte> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (std::byte b : data) {
        crc ^= static_cast<uint8_t>(b);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc = (crc >> 1);
            }
        }
    }
    return ~crc;
}

std::optional<SectorHeader> AtomicStorage::validateSector(uint32_t sector_addr) const noexcept {
    SectorHeader hdr{};
    auto hdr_span = std::as_writable_bytes(std::span{&hdr, 1});
    if (!driver_.read(sector_addr, hdr_span)) {
        return std::nullopt;
    }

    if (hdr.magic != MagicWord || hdr.commit_marker != CommitMarker) {
        return std::nullopt;
    }
    if (hdr.payload_len > MaxPayload) {
        return std::nullopt;
    }

    std::array<std::byte, MaxPayload> buffer{};
    auto payload_span = std::span{buffer.data(), hdr.payload_len};
    uint32_t payload_addr = sector_addr + sizeof(SectorHeader);

    if (!driver_.read(payload_addr, payload_span)) {
        return std::nullopt;
    }

    if (calculateCrc32(payload_span) != hdr.payload_crc32) {
        return std::nullopt;
    }

    return hdr;
}

std::expected<void, StorageError> AtomicStorage::init() noexcept {
    if (!driver_.read || !driver_.write || !driver_.erase_sector) {
        return std::unexpected(StorageError::InvalidParameter);
    }

    auto val_a = validateSector(sector_a_);
    auto val_b = validateSector(sector_b_);

    if (val_a && val_b) {
        if (static_cast<int32_t>(val_a->generation - val_b->generation) >= 0) {
            active_sector_ = sector_a_;
            current_generation_ = val_a->generation;
        } else {
            active_sector_ = sector_b_;
            current_generation_ = val_b->generation;
        }
    } else if (val_a) {
        active_sector_ = sector_a_;
        current_generation_ = val_a->generation;
    } else if (val_b) {
        active_sector_ = sector_b_;
        current_generation_ = val_b->generation;
    } else {
        active_sector_ = 0;
        current_generation_ = 0;
    }

    is_initialized_ = true;
    return {};
}

std::expected<size_t, StorageError> AtomicStorage::read(std::span<std::byte> dest) const noexcept {
    if (!is_initialized_) return std::unexpected(StorageError::InvalidParameter);
    if (active_sector_ == 0) return std::unexpected(StorageError::NoValidData);

    SectorHeader hdr{};
    auto hdr_span = std::as_writable_bytes(std::span{&hdr, 1});
    if (!driver_.read(active_sector_, hdr_span)) {
        return std::unexpected(StorageError::FlashIoError);
    }

    const size_t copy_len = std::min(dest.size(), static_cast<size_t>(hdr.payload_len));
    const uint32_t payload_addr = active_sector_ + sizeof(SectorHeader);

    if (!driver_.read(payload_addr, dest.subspan(0, copy_len))) {
        return std::unexpected(StorageError::FlashIoError);
    }

    return hdr.payload_len;
}

std::expected<void, StorageError> AtomicStorage::write(std::span<const std::byte> src) noexcept {
    if (!is_initialized_) return std::unexpected(StorageError::InvalidParameter);
    if (src.size() > MaxPayload) return std::unexpected(StorageError::PayloadTooLarge);

    const uint32_t target_addr = (active_sector_ == sector_a_) ? sector_b_ : sector_a_;

    // 1. Стирання дзеркального сектора
    if (!driver_.erase_sector(target_addr)) {
        return std::unexpected(StorageError::FlashIoError);
    }

    // 2. Формування заголовка без Commit Marker
    SectorHeader hdr{
        .magic = MagicWord,
        .generation = current_generation_ + 1,
        .payload_len = static_cast<uint16_t>(src.size()),
        .reserved = 0xFFFF,
        .payload_crc32 = calculateCrc32(src),
        .commit_marker = 0xFFFFFFFFU
    };

    // 3. Запис заголовка
    auto hdr_span = std::as_bytes(std::span{&hdr, 1});
    if (!driver_.write(target_addr, hdr_span)) {
        return std::unexpected(StorageError::FlashIoError);
    }

    // 4. Запис корисного навантаження
    const uint32_t payload_addr = target_addr + sizeof(SectorHeader);
    if (!driver_.write(payload_addr, src)) {
        return std::unexpected(StorageError::FlashIoError);
    }

    // 5. Атомарний комміт
    const uint32_t commit = CommitMarker;
    const uint32_t commit_offset = target_addr + offsetof(SectorHeader, commit_marker);
    auto commit_span = std::as_bytes(std::span{&commit, 1});
    if (!driver_.write(commit_offset, commit_span)) {
        return std::unexpected(StorageError::FlashIoError);
    }

    // 6. Оновлення стану в RAM
    active_sector_ = target_addr;
    current_generation_ = hdr.generation;

    return {};
}

} // namespace embedded::storage

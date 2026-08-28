// FlashRingQueue.hpp
#pragma once

#include "FlashRingBuffer.hpp"
#include <optional>
#include <algorithm>

namespace embedded::storage {

template <FlashDriver Driver, uint32_t SectorCount, bool OverwriteOnFull = true>
class FlashRingQueue {
public:
    explicit FlashRingQueue(Driver& driver, uint32_t start_addr)
        : driver_(driver), start_addr_(start_addr) {}

    std::expected<void, RingError> init() noexcept {
        uint32_t max_seq = 0;
        int head = -1, tail = -1;

        for (uint32_t i = 0; i < SectorCount; ++i) {
            SectorHeader hdr{};
            if (driver_.read(get_sector_addr(i), reinterpret_cast<uint8_t*>(&hdr), sizeof(hdr)) != 0) {
                return std::unexpected(RingError::IoError);
            }
            if (hdr.magic == FlashSectorMagic) {
                if (hdr.sector_seq >= max_seq) {
                    max_seq = hdr.sector_seq;
                    head = static_cast<int>(i);
                }
                if (tail == -1 || hdr.sector_seq < next_sector_seq_) {
                    tail = static_cast<int>(i);
                }
            }
        }

        if (head == -1) {
            head_idx_ = tail_idx_ = 0;
            head_offset_ = tail_offset_ = sizeof(SectorHeader);
            format_sector(0, 1);
            next_sector_seq_ = 2;
            return {};
        }

        head_idx_ = static_cast<uint32_t>(head);
        tail_idx_ = static_cast<uint32_t>(tail);
        next_sector_seq_ = max_seq + 1;
        recover_head_offset();
        return {};
    }

    std::expected<void, RingError> push(std::span<const uint8_t> payload, uint8_t priority = 0) noexcept {
        const uint32_t rec_size = sizeof(RecordHeader) + static_cast<uint32_t>(payload.size());
        if (rec_size > (FlashSectorSize - sizeof(SectorHeader))) {
            return std::unexpected(RingError::InvalidParameter);
        }

        if (head_offset_ + rec_size > FlashSectorSize) {
            const uint32_t next_head = (head_idx_ + 1) % SectorCount;
            if (next_head == tail_idx_) {
                if constexpr (!OverwriteOnFull) {
                    return std::unexpected(RingError::Full);
                }
                tail_idx_ = (tail_idx_ + 1) % SectorCount;
                tail_offset_ = sizeof(SectorHeader);
            }
            head_idx_ = next_head;
            format_sector(head_idx_, next_sector_seq_++);
            head_offset_ = sizeof(SectorHeader);
        }

        RecordHeader rec{
            .record_magic = FlashRecordMagic,
            .payload_len = static_cast<uint16_t>(payload.size()),
            .record_seq = next_record_seq_++,
            .status_flag = static_cast<uint8_t>(RecordStatus::Writing),
            .priority = priority,
            .reserved = 0,
            .payload_crc32 = compute_crc(payload)
        };

        const uint32_t rec_addr = get_sector_addr(head_idx_) + head_offset_;
        driver_.write_page(rec_addr, reinterpret_cast<const uint8_t*>(&rec), sizeof(rec));
        driver_.write_page(rec_addr + sizeof(rec), payload.data(), payload.size());

        // Атомарна фіксація (коміт)
        const uint8_t commit_val = static_cast<uint8_t>(RecordStatus::Committed);
        driver_.write_page(rec_addr + offsetof(RecordHeader, status_flag), &commit_val, 1);

        head_offset_ += rec_size;
        return {};
    }

    struct PeekResult {
        uint32_t record_seq;
        uint16_t payload_len;
    };

    std::expected<PeekResult, RingError> peek(std::span<uint8_t> out_buf) noexcept {
        while (true) {
            if (tail_idx_ == head_idx_ && tail_offset_ >= head_offset_) {
                return std::unexpected(RingError::Empty);
            }

            const uint32_t addr = get_sector_addr(tail_idx_) + tail_offset_;
            RecordHeader rec{};
            driver_.read(addr, reinterpret_cast<uint8_t*>(&rec), sizeof(rec));

            if (rec.record_magic != FlashRecordMagic || tail_offset_ + sizeof(rec) > FlashSectorSize) {
                if (tail_idx_ == head_idx_) return std::unexpected(RingError::Empty);
                tail_idx_ = (tail_idx_ + 1) % SectorCount;
                tail_offset_ = sizeof(SectorHeader);
                continue;
            }

            if (rec.status_flag == static_cast<uint8_t>(RecordStatus::Consumed)) {
                tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
                continue;
            }

            if (rec.status_flag == static_cast<uint8_t>(RecordStatus::Committed)) {
                if (out_buf.size() < rec.payload_len) {
                    return std::unexpected(RingError::InvalidParameter);
                }
                driver_.read(addr + sizeof(rec), out_buf.data(), rec.payload_len);
                if (compute_crc(out_buf.subspan(0, rec.payload_len)) != rec.payload_crc32) {
                    mark_consumed(addr);
                    tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
                    continue;
                }
                return PeekResult{rec.record_seq, rec.payload_len};
            }
            tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
        }
    }

    std::expected<void, RingError> commit_pop() noexcept {
        const uint32_t addr = get_sector_addr(tail_idx_) + tail_offset_;
        RecordHeader rec{};
        driver_.read(addr, reinterpret_cast<uint8_t*>(&rec), sizeof(rec));
        if (rec.record_magic == FlashRecordMagic) {
            mark_consumed(addr);
            tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
            return {};
        }
        return std::unexpected(RingError::Corrupted);
    }

private:
    Driver&  driver_;
    uint32_t start_addr_{0};
    uint32_t head_idx_{0};
    uint32_t tail_idx_{0};
    uint32_t head_offset_{sizeof(SectorHeader)};
    uint32_t tail_offset_{sizeof(SectorHeader)};
    uint32_t next_record_seq_{1};
    uint32_t next_sector_seq_{1};

    [[nodiscard]] constexpr uint32_t get_sector_addr(uint32_t idx) const noexcept {
        return start_addr_ + (idx * FlashSectorSize);
    }

    void format_sector(uint32_t idx, uint32_t seq) noexcept {
        const uint32_t addr = get_sector_addr(idx);
        driver_.erase_sector(addr);
        SectorHeader hdr{
            .magic = FlashSectorMagic,
            .sector_seq = seq,
            .state_flag = static_cast<uint8_t>(RecordStatus::Committed),
            .reserved = {0, 0, 0},
            .header_crc32 = 0
        };
        hdr.header_crc32 = compute_crc(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr) - 4));
        driver_.write_page(addr, reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr));
    }

    void mark_consumed(uint32_t rec_addr) noexcept {
        const uint8_t consumed = static_cast<uint8_t>(RecordStatus::Consumed);
        driver_.write_page(rec_addr + offsetof(RecordHeader, status_flag), &consumed, 1);
    }

    void recover_head_offset() noexcept {
        uint32_t offset = sizeof(SectorHeader);
        const uint32_t base = get_sector_addr(head_idx_);
        while (offset + sizeof(RecordHeader) <= FlashSectorSize) {
            RecordHeader rec{};
            driver_.read(base + offset, reinterpret_cast<uint8_t*>(&rec), sizeof(rec));
            if (rec.record_magic == 0xFFFFU && rec.status_flag == static_cast<uint8_t>(RecordStatus::Free)) {
                break;
            }
            if (rec.record_magic == FlashRecordMagic) {
                next_record_seq_ = std::max(next_record_seq_, rec.record_seq + 1);
                offset += sizeof(RecordHeader) + rec.payload_len;
            } else {
                break;
            }
        }
        head_offset_ = offset;
        tail_offset_ = sizeof(SectorHeader);
    }

    static uint32_t compute_crc(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t b : data) {
            crc ^= b;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (0 - (crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace embedded::storage

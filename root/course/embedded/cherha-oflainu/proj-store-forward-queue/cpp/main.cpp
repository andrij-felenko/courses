#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <concepts>
#include <algorithm>

namespace embedded::storage {

enum class Priority : uint8_t {
    Low = 0,    // High-rate telemetry (50 Hz)
    Normal = 1, // Periodic status (1 Hz)
    High = 2    // Critical alarms and faults
};

enum class QueueError {
    FlashReadFailed,
    FlashWriteFailed,
    FlashEraseFailed,
    PayloadTooLarge,
    QueueFull,
    InvalidRecord,
    CrcMismatch
};

#pragma pack(push, 1)
struct RecordHeader {
    uint16_t magic{0xAA55};
    uint8_t  type{0};
    Priority priority{Priority::Normal};
    uint32_t seq{0};
    uint64_t timestamp_ms{0};
    uint16_t payload_len{0};
    uint16_t reserved{0};
};
#pragma pack(pop)

template <typename FlashDriver>
class StoreForwardQueue {
public:
    static constexpr size_t SectorSize = 4096;
    static constexpr size_t PageSize   = 256;
    static constexpr size_t MaxPayload = 512;
    static constexpr uint16_t Magic    = 0xAA55;

    struct Config {
        uint32_t base_addr;
        uint32_t sector_count;
    };

    explicit StoreForwardQueue(FlashDriver& driver, const Config& cfg)
        : driver_(driver), base_addr_(cfg.base_addr), sector_count_(cfg.sector_count) {}

    // Ініціалізація та сканування секторів для відновлення покажчика голови
    std::expected<void, QueueError> init() {
        uint32_t highest_seq = 0;
        uint32_t best_head_sec = 0;
        uint32_t best_head_off = 0;

        for (uint32_t s = 0; s < sector_count_; ++s) {
            uint32_t off = 0;
            while (off + sizeof(RecordHeader) <= SectorSize) {
                RecordHeader hdr{};
                const uint32_t phys_addr = base_addr_ + s * SectorSize + off;
                
                if (!driver_.read(phys_addr, std::as_writable_bytes(std::span{&hdr, 1}))) {
                    break;
                }

                if (hdr.magic != Magic || hdr.payload_len > MaxPayload) {
                    break;
                }

                const size_t total_size = sizeof(RecordHeader) + hdr.payload_len + sizeof(uint32_t);
                if (off + total_size > SectorSize) {
                    break;
                }

                std::array<std::byte, sizeof(RecordHeader) + MaxPayload + sizeof(uint32_t)> raw_buf{};
                auto slice = std::span{raw_buf.data(), total_size};

                if (driver_.read(phys_addr, slice)) {
                    uint32_t stored_crc = 0;
                    std::copy_n(raw_buf.data() + total_size - sizeof(uint32_t), sizeof(uint32_t),
                                reinterpret_cast<std::byte*>(&stored_crc));

                    const uint32_t calculated_crc = compute_crc32(slice.first(total_size - sizeof(uint32_t)));
                    if (calculated_crc == stored_crc) {
                        if (hdr.seq >= highest_seq) {
                            highest_seq = hdr.seq;
                            best_head_sec = s;
                            best_head_off = off + total_size;
                        }
                    } else {
                        break; // Перерваний запис внаслідок знеструмлення
                    }
                }
                off += total_size;
            }
        }

        if (highest_seq > 0) {
            head_sector_ = best_head_sec;
            head_offset_ = best_head_off;
            next_seq_ = highest_seq + 1;
        }

        return {};
    }

    // Запис нового кадру з випереджальним стиранням
    std::expected<uint32_t, QueueError> push(uint8_t type, Priority prio, uint64_t ts_ms,
                                            std::span<const std::byte> payload) {
        if (payload.size() > MaxPayload) {
            return std::unexpected(QueueError::PayloadTooLarge);
        }

        const size_t record_size = sizeof(RecordHeader) + payload.size() + sizeof(uint32_t);

        if (head_offset_ + record_size > SectorSize) {
            const uint32_t next_sec = (head_sector_ + 1) % sector_count_;

            if (next_sec == tail_sector_) {
                if (prio == Priority::Low) {
                    return std::unexpected(QueueError::QueueFull);
                }
                // Для важливих даних звільняємо найстаріший сектор
                tail_sector_ = (tail_sector_ + 1) % sector_count_;
                tail_offset_ = 0;
            }

            if (!driver_.erase_sector(next_sec)) {
                return std::unexpected(QueueError::FlashEraseFailed);
            }
            head_sector_ = next_sec;
            head_offset_ = 0;
        }

        const uint32_t assigned_seq = next_seq_++;
        RecordHeader hdr{
            .magic = Magic,
            .type = type,
            .priority = prio,
            .seq = assigned_seq,
            .timestamp_ms = ts_ms,
            .payload_len = static_cast<uint16_t>(payload.size()),
            .reserved = 0
        };

        std::array<std::byte, sizeof(RecordHeader) + MaxPayload + sizeof(uint32_t)> write_buf{};
        std::copy_n(reinterpret_cast<const std::byte*>(&hdr), sizeof(hdr), write_buf.data());
        std::copy(payload.begin(), payload.end(), write_buf.data() + sizeof(hdr));

        const uint32_t crc = compute_crc32(std::span{write_buf.data(), sizeof(hdr) + payload.size()});
        std::copy_n(reinterpret_cast<const std::byte*>(&crc), sizeof(crc),
                    write_buf.data() + sizeof(hdr) + payload.size());

        const uint32_t target_addr = base_addr_ + head_sector_ * SectorSize + head_offset_;
        if (!driver_.write(target_addr, std::span{write_buf.data(), record_size})) {
            return std::unexpected(QueueError::FlashWriteFailed);
        }

        head_offset_ += record_size;
        return assigned_seq;
    }

    // Квитування доставки порції записів (ACK commit)
    void commit_ack(uint32_t acked_seq) {
        while (tail_sector_ != head_sector_ || tail_offset_ < head_offset_) {
            RecordHeader hdr{};
            const uint32_t phys_addr = base_addr_ + tail_sector_ * SectorSize + tail_offset_;

            if (!driver_.read(phys_addr, std::as_writable_bytes(std::span{&hdr, 1})) || hdr.magic != Magic) {
                tail_sector_ = (tail_sector_ + 1) % sector_count_;
                tail_offset_ = 0;
                break;
            }

            if (hdr.seq <= acked_seq) {
                const size_t total = sizeof(RecordHeader) + hdr.payload_len + sizeof(uint32_t);
                tail_offset_ += total;
                if (tail_offset_ + sizeof(RecordHeader) > SectorSize) {
                    tail_sector_ = (tail_sector_ + 1) % sector_count_;
                    tail_offset_ = 0;
                }
            } else {
                break;
            }
        }
    }

private:
    FlashDriver& driver_;
    uint32_t base_addr_{0};
    uint32_t sector_count_{0};

    uint32_t head_sector_{0};
    uint32_t head_offset_{0};
    uint32_t tail_sector_{0};
    uint32_t tail_offset_{0};
    uint32_t next_seq_{1};

    static uint32_t compute_crc32(std::span<const std::byte> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (auto b : data) {
            crc ^= static_cast<uint8_t>(b);
            for (int k = 0; k < 8; ++k) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<int32_t>(crc & 1))));
            }
        }
        return ~crc;
    }
};

} // namespace embedded::storage

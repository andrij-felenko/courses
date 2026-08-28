#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <atomic>
#include <expected>
#include <algorithm>
#include <chrono>

enum class StreamId : uint8_t {
    ImuRaw      = 0x01,
    CurrentAdc  = 0x02,
    Acoustic    = 0x03
};

enum class LogError {
    PayloadTooLarge,
    BufferOverflow,
    StorageWriteFailed
};

#pragma pack(push, 1)
struct LogFrameHeader {
    uint16_t magic{0xAA55};
    StreamId stream_id{StreamId::ImuRaw};
    uint8_t  flags{0};
    uint32_t seq_num{0};
    uint64_t timestamp_us{0};
    uint16_t payload_len{0};
};
#pragma pack(pop)

template <size_t SectorSize = 512, size_t MaxPayload = 240>
class DoubleBufferLogger {
public:
    static constexpr uint16_t Magic = 0xAA55;

    DoubleBufferLogger() = default;

    // Запис вибірки у високому пріоритеті (без динамічного виділення пам'яті)
    std::expected<void, LogError> pushSample(
        StreamId stream,
        std::chrono::microseconds timestamp,
        std::span<const uint8_t> payload) noexcept 
    {
        if (payload.size() > MaxPayload) {
            return std::unexpected(LogError::PayloadTooLarge);
        }

        const uint8_t active = active_idx_.load(std::memory_order_relaxed);
        const size_t frame_size = sizeof(LogFrameHeader) + payload.size() + sizeof(uint32_t);

        if (write_pos_[active] + frame_size > SectorSize) {
            buffer_ready_[active].store(true, std::memory_order_release);

            const uint8_t next = active ^ 1;
            if (buffer_ready_[next].load(std::memory_order_acquire)) {
                dropped_frames_.fetch_add(1, std::memory_order_relaxed);
                return std::unexpected(LogError::BufferOverflow);
            }

            active_idx_.store(next, std::memory_order_relaxed);
            write_pos_[next] = 0;
            return writeFrameToBuffer(next, stream, timestamp, payload, frame_size);
        }

        return writeFrameToBuffer(active, stream, timestamp, payload, frame_size);
    }

    // Фонове скидання на диск через функціональний інтерфейс
    template <typename StorageWriter>
    std::expected<size_t, LogError> flushPending(StorageWriter&& writeSector) noexcept {
        size_t flushed_count = 0;
        for (size_t i = 0; i < 2; ++i) {
            if (buffer_ready_[i].load(std::memory_order_acquire)) {
                std::span<const uint8_t, SectorSize> sector_view(buffers_[i]);
                if (!writeSector(sector_view)) {
                    return std::unexpected(LogError::StorageWriteFailed);
                }
                buffer_ready_[i].store(false, std::memory_order_release);
                flushed_count++;
            }
        }
        return flushed_count;
    }

    [[nodiscard]] uint32_t droppedFrames() const noexcept {
        return dropped_frames_.load(std::memory_order_relaxed);
    }

private:
    std::expected<void, LogError> writeFrameToBuffer(
        uint8_t buf_idx,
        StreamId stream,
        std::chrono::microseconds timestamp,
        std::span<const uint8_t> payload,
        size_t frame_size) noexcept 
    {
        uint8_t* const dest = buffers_[buf_idx].data() + write_pos_[buf_idx];

        LogFrameHeader hdr{
            .magic = Magic,
            .stream_id = stream,
            .flags = 0,
            .seq_num = global_seq_++,
            .timestamp_us = static_cast<uint64_t>(timestamp.count()),
            .payload_len = static_cast<uint16_t>(payload.size())
        };

        std::copy_n(reinterpret_cast<const uint8_t*>(&hdr), sizeof(LogFrameHeader), dest);
        std::copy(payload.begin(), payload.end(), dest + sizeof(LogFrameHeader));

        const uint32_t crc = calculateCrc32(std::span<const uint8_t>(dest, sizeof(LogFrameHeader) + payload.size()));
        std::copy_n(reinterpret_cast<const uint8_t*>(&crc), sizeof(uint32_t), 
                    dest + sizeof(LogFrameHeader) + payload.size());

        write_pos_[buf_idx] += frame_size;
        return {};
    }

    static uint32_t calculateCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
            }
        }
        return ~crc;
    }

    std::array<std::array<uint8_t, SectorSize>, 2> buffers_{};
    std::array<size_t, 2> write_pos_{0, 0};
    std::atomic<uint8_t> active_idx_{0};
    std::array<std::atomic<bool>, 2> buffer_ready_{false, false};
    uint32_t global_seq_{0};
    std::atomic<uint32_t> dropped_frames_{0};
};

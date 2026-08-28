#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>
#include <variant>
#include <algorithm>

namespace embedded::storage {

inline constexpr size_t FlashSectorSize    = 4096;
inline constexpr size_t FlashTotalSectors  = 1024;
inline constexpr uint16_t FrameMagic       = 0xA55A;
inline constexpr uint32_t CommitTokenValid = 0xAA55AA55;
inline constexpr uint32_t CommitTokenEmpty = 0xFFFFFFFF;

inline constexpr uint32_t BackoffBaseSec   = 10;
inline constexpr uint32_t BackoffMaxSec    = 3600;
inline constexpr size_t BulkBatchSize      = 16;

enum class RecordClass : uint16_t {
    Normal    = 0x01,
    Decimated = 0x02,
    Alarm     = 0x04,
    Summary   = 0x08
};

enum class StorageError {
    FlashHardwareFailure,
    SectorFull,
    BufferOverflow,
    CrcMismatch,
    RadioTimeout
};

#pragma pack(push, 1)
struct FrameHeader {
    uint16_t magic{FrameMagic};
    uint32_t seq_num{0};
    uint32_t timestamp{0};
    RecordClass flags{RecordClass::Normal};
    uint16_t payload_len{0};
};

struct FrameFooter {
    uint32_t crc32{0};
    uint32_t commit_token{CommitTokenEmpty};
};
#pragma pack(pop)

/* Типізовані стани автомата синхронізації */
struct StateOnline {};
struct StateBackoffSleep { uint32_t remaining_sec{0}; uint32_t attempt{0}; };
struct StateProbeLink { uint32_t attempt{0}; };
struct StateSendLive {};
struct StateBulkSync {};

using SyncState = std::variant<StateOnline, StateBackoffSleep, StateProbeLink, StateSendLive, StateBulkSync>;

class FlashStorageManager {
public:
    FlashStorageManager() = default;

    [[nodiscard]] std::expected<void, StorageError> write_record(
        RecordClass rclass, uint32_t timestamp, std::span<const uint8_t> payload) 
    {
        const size_t total_size = sizeof(FrameHeader) + payload.size() + sizeof(FrameFooter);
        
        if (head_offset_ + total_size > FlashSectorSize) {
            uint32_t next_sec = (head_sector_ + 1) % FlashTotalSectors;
            
            if (next_sec == tail_sector_) {
                if (static_cast<uint16_t>(rclass) & static_cast<uint16_t>(RecordClass::Alarm)) {
                    tail_sector_ = (tail_sector_ + 1) % FlashTotalSectors;
                    tail_offset_ = 0;
                    if (!erase_sector(next_sec)) return std::unexpected(StorageError::FlashHardwareFailure);
                } else {
                    return std::unexpected(StorageError::BufferOverflow);
                }
            }
            
            head_sector_ = next_sec;
            head_offset_ = 0;
            
            uint32_t erase_ahead = (head_sector_ + 1) % FlashTotalSectors;
            if (erase_ahead != tail_sector_) {
                erase_sector(erase_ahead);
            }
        }

        const uint32_t base_addr = head_sector_ * FlashSectorSize + head_offset_;
        FrameHeader hdr{
            .magic = FrameMagic,
            .seq_num = next_seq_num_++,
            .timestamp = timestamp,
            .flags = rclass,
            .payload_len = static_cast<uint16_t>(payload.size())
        };

        uint32_t crc = calculate_crc32(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)));
        crc = calculate_crc32_accumulate(crc, payload);

        FrameFooter ftr{
            .crc32 = crc,
            .commit_token = CommitTokenEmpty
        };

        if (!raw_write(base_addr, std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)))) {
            return std::unexpected(StorageError::FlashHardwareFailure);
        }
        if (!raw_write(base_addr + sizeof(hdr), payload)) {
            return std::unexpected(StorageError::FlashHardwareFailure);
        }
        if (!raw_write(base_addr + sizeof(hdr) + payload.size(), 
                       std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&ftr), sizeof(ftr)))) {
            return std::unexpected(StorageError::FlashHardwareFailure);
        }

        /* Атомарний коміт запису */
        uint32_t commit_val = CommitTokenValid;
        uint32_t commit_addr = base_addr + sizeof(hdr) + payload.size() + offsetof(FrameFooter, commit_token);
        if (!raw_write(commit_addr, std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&commit_val), sizeof(commit_val)))) {
            return std::unexpected(StorageError::FlashHardwareFailure);
        }

        head_offset_ += total_size;
        buffered_records_count_++;
        return {};
    }

    void process_cycle(uint32_t current_time, std::span<const uint8_t> latest_sample) {
        std::visit([this, current_time, latest_sample](auto& st) {
            handle_state(st, current_time, latest_sample);
        }, current_state_);
    }

private:
    SyncState current_state_{StateOnline{}};
    uint32_t head_sector_{0};
    uint32_t head_offset_{0};
    uint32_t tail_sector_{0};
    uint32_t tail_offset_{0};
    uint32_t next_seq_num_{1};
    size_t buffered_records_count_{0};

    static uint32_t calculate_backoff(uint32_t attempt) {
        uint32_t max_interval = BackoffBaseSec << std::min(attempt, 10u);
        max_interval = std::min(max_interval, BackoffMaxSec);
        return random_uniform(BackoffBaseSec, max_interval);
    }

    void handle_state(StateOnline&, uint32_t current_time, std::span<const uint8_t> sample) {
        if (!transmit_packet(sample, 500)) {
            write_record(RecordClass::Normal, current_time, sample);
            current_state_ = StateBackoffSleep{.remaining_sec = calculate_backoff(1), .attempt = 1};
        }
    }

    void handle_state(StateBackoffSleep& st, uint32_t current_time, std::span<const uint8_t> sample) {
        write_record(RecordClass::Normal, current_time, sample);
        if (st.remaining_sec > 60) {
            st.remaining_sec -= 60;
        } else {
            current_state_ = StateProbeLink{.attempt = st.attempt};
        }
    }

    void handle_state(StateProbeLink& st, uint32_t, std::span<const uint8_t>) {
        const uint8_t probe_byte = 0x7E;
        if (transmit_packet(std::span(&probe_byte, 1), 1000)) {
            current_state_ = StateSendLive{};
        } else {
            uint32_t next_att = st.attempt + 1;
            current_state_ = StateBackoffSleep{.remaining_sec = calculate_backoff(next_att), .attempt = next_att};
        }
    }

    void handle_state(StateSendLive&, uint32_t, std::span<const uint8_t> sample) {
        if (transmit_packet(sample, 500)) {
            if (buffered_records_count_ > 0) {
                current_state_ = StateBulkSync{};
            } else {
                current_state_ = StateOnline{};
            }
        } else {
            current_state_ = StateBackoffSleep{.remaining_sec = calculate_backoff(1), .attempt = 1};
        }
    }

    void handle_state(StateBulkSync&, uint32_t, std::span<const uint8_t>) {
        uint8_t batch_buf[512];
        size_t batch_len = 0;
        size_t count = 0;
        uint32_t read_offset = tail_offset_;

        while (count < BulkBatchSize && buffered_records_count_ > 0) {
            FrameHeader hdr;
            uint32_t addr = tail_sector_ * FlashSectorSize + read_offset;
            if (!raw_read(addr, std::span(reinterpret_cast<uint8_t*>(&hdr), sizeof(hdr)))) break;
            if (hdr.magic != FrameMagic) break;

            size_t frame_len = sizeof(FrameHeader) + hdr.payload_len + sizeof(FrameFooter);
            if (batch_len + frame_len > sizeof(batch_buf)) break;

            raw_read(addr, std::span(batch_buf + batch_len, frame_len));
            batch_len += frame_len;
            read_offset += frame_len;
            count++;
        }

        if (batch_len > 0 && transmit_packet(std::span(batch_buf, batch_len), 1500)) {
            tail_offset_ = read_offset;
            if (tail_offset_ >= FlashSectorSize) {
                tail_sector_ = (tail_sector_ + 1) % FlashTotalSectors;
                tail_offset_ = 0;
            }
            buffered_records_count_ -= count;
            if (buffered_records_count_ == 0) {
                current_state_ = StateOnline{};
            }
        } else {
            current_state_ = StateBackoffSleep{.remaining_sec = calculate_backoff(1), .attempt = 1};
        }
    }

    /* Низькорівневі драйверні зв'язки */
    static bool raw_write(uint32_t addr, std::span<const uint8_t> data);
    static bool raw_read(uint32_t addr, std::span<uint8_t> data);
    static bool erase_sector(uint32_t sector_idx);
    static bool transmit_packet(std::span<const uint8_t> data, uint32_t timeout_ms);
    static uint32_t calculate_crc32(std::span<const uint8_t> data);
    static uint32_t calculate_crc32_accumulate(uint32_t prev_crc, std::span<const uint8_t> data);
    static uint32_t random_uniform(uint32_t min, uint32_t max);
};

} // namespace embedded::storage

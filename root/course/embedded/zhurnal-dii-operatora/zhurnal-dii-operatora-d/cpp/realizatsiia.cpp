#include <array>
#include <span>
#include <expected>
#include <cstring>
#include <cstdint>

namespace embedded::audit {

inline constexpr size_t RecordSize = 128;
inline constexpr size_t HashSize = 32;
inline constexpr uint32_t MagicSync = 0x41554454;
inline constexpr uint32_t SectorMagic = 0x53454354;
inline constexpr uint32_t DataSlotsPerSector = 31;
inline constexpr size_t SectorSizeBytes = 4096;

enum class Error : int32_t {
    InvalidParam = -1,
    FlashIo = -2,
    Corrupted = -3,
    NotInitialized = -4
};

#pragma pack(push, 1)
struct Record {
    uint32_t magic{MagicSync};
    uint8_t  version{1};
    uint8_t  flags{0};
    uint8_t  exec_status{0};
    uint8_t  payload_len{0};
    uint64_t sequence_id{0};
    uint64_t timestamp_utc_ms{0};
    uint64_t operator_id{0};
    uint16_t command_id{0};
    uint8_t  subsystem_id{0};
    uint8_t  padding0{0};
    std::array<uint8_t, 32> payload{};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> record_hash{};
};
static_assert(sizeof(Record) == RecordSize);
#pragma pack(pop)

class IFlashDriver {
public:
    virtual ~IFlashDriver() = default;
    virtual bool read(uint32_t addr, std::span<uint8_t> dst) noexcept = 0;
    virtual bool write_page(uint32_t addr, std::span<const uint8_t> src) noexcept = 0;
    virtual bool erase_sector(uint32_t sector_addr) noexcept = 0;
    [[nodiscard]] virtual uint32_t total_size() const noexcept = 0;
};

// Зовнішня функція розрахунку SHA-256
extern void sha256_compute(std::span<const uint8_t> input, std::span<uint8_t, HashSize> output) noexcept;

class AuditLoggerEngine {
public:
    explicit AuditLoggerEngine(IFlashDriver& flash) noexcept 
        : flash_{flash} {}

    [[nodiscard]] std::expected<void, Error> init() noexcept {
        current_seq_ = 0;
        active_sector_addr_ = 0;
        next_slot_idx_ = 1;
        last_hash_.fill(0xAA);

        const uint32_t total_sectors = flash_.total_size() / SectorSizeBytes;
        bool found = false;

        for (uint32_t i = 0; i < total_sectors; ++i) {
            const uint32_t s_addr = i * SectorSizeBytes;
            Record first_slot{};
            auto raw_span = std::as_writable_bytes(std::span{&first_slot, 1});
            
            if (!flash_.read(s_addr, std::span<uint8_t>{reinterpret_cast<uint8_t*>(raw_span.data()), raw_span.size()})) {
                return std::unexpected(Error::FlashIo);
            }

            if (first_slot.magic == SectorMagic) {
                active_sector_addr_ = s_addr;
                found = true;

                for (uint32_t slot = 1; slot <= DataSlotsPerSector; ++slot) {
                    Record rec{};
                    auto rec_span = std::as_writable_bytes(std::span{&rec, 1});
                    flash_.read(s_addr + slot * RecordSize, std::span<uint8_t>{reinterpret_cast<uint8_t*>(rec_span.data()), rec_span.size()});
                    
                    if (rec.magic == MagicSync) {
                        current_seq_ = rec.sequence_id;
                        last_hash_ = rec.record_hash;
                        next_slot_idx_ = slot + 1;
                    } else {
                        next_slot_idx_ = slot;
                        break;
                    }
                }
                break;
            }
        }

        if (!found) {
            flash_.erase_sector(0);
            Record hdr{};
            std::memset(&hdr, 0xFF, sizeof(hdr));
            hdr.magic = SectorMagic;
            auto hdr_span = std::as_bytes(std::span{&hdr, 1});
            flash_.write_page(0, std::span<const uint8_t>{reinterpret_cast<const uint8_t*>(hdr_span.data()), hdr_span.size()});
            active_sector_addr_ = 0;
            next_slot_idx_ = 1;
        }

        ready_ = true;
        return {};
    }

    [[nodiscard]] std::expected<uint64_t, Error> record_command(
        uint64_t timestamp_utc,
        uint64_t operator_id,
        uint16_t command_id,
        uint8_t subsystem_id,
        std::span<const uint8_t> payload
    ) noexcept {
        if (!ready_) return std::unexpected(Error::NotInitialized);
        if (payload.size() > 32) return std::unexpected(Error::InvalidParam);

        if (next_slot_idx_ > DataSlotsPerSector) {
            uint32_t next_sec = active_sector_addr_ + SectorSizeBytes;
            if (next_sec >= flash_.total_size()) {
                next_sec = 0;
            }
            flash_.erase_sector(next_sec);

            Record hdr{};
            std::memset(&hdr, 0xFF, sizeof(hdr));
            hdr.magic = SectorMagic;
            hdr.sequence_id = current_seq_ + 1;
            hdr.prev_hash = last_hash_;
            auto hdr_span = std::as_bytes(std::span{&hdr, 1});
            flash_.write_page(next_sec, std::span<const uint8_t>{reinterpret_cast<const uint8_t*>(hdr_span.data()), hdr_span.size()});

            active_sector_addr_ = next_sec;
            next_slot_idx_ = 1;
        }

        Record rec{};
        rec.magic = MagicSync;
        rec.version = 1;
        rec.payload_len = static_cast<uint8_t>(payload.size());
        rec.sequence_id = ++current_seq_;
        rec.timestamp_utc_ms = timestamp_utc;
        rec.operator_id = operator_id;
        rec.command_id = command_id;
        rec.subsystem_id = subsystem_id;

        if (!payload.empty()) {
            std::memcpy(rec.payload.data(), payload.data(), payload.size());
        }
        rec.prev_hash = last_hash_;

        // Хешування перших 96 байтів структури
        const auto hashable_span = std::span<const uint8_t>{
            reinterpret_cast<const uint8_t*>(&rec), 
            offsetof(Record, record_hash)
        };
        sha256_compute(hashable_span, std::span<uint8_t, HashSize>{rec.record_hash});

        last_hash_ = rec.record_hash;

        const uint32_t slot_addr = active_sector_addr_ + (next_slot_idx_ * RecordSize);
        auto rec_bytes = std::as_bytes(std::span{&rec, 1});
        
        if (!flash_.write_page(slot_addr, std::span<const uint8_t>{reinterpret_cast<const uint8_t*>(rec_bytes.data()), rec_bytes.size()})) {
            return std::unexpected(Error::FlashIo);
        }

        next_slot_idx_++;
        return rec.sequence_id;
    }

private:
    IFlashDriver& flash_;
    uint64_t current_seq_{0};
    uint32_t active_sector_addr_{0};
    uint32_t next_slot_idx_{1};
    std::array<uint8_t, HashSize> last_hash_{};
    bool ready_{false};
};

} // namespace embedded::audit

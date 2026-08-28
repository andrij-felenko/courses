// Ідіоматичний C++20 варіант: RAII, std::span, std::expected
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

namespace storage {

inline constexpr uint32_t RECORD_MAGIC = 0x52454331;
inline constexpr uint32_t COMMIT_FLAG  = 0xA55A5AA5;

enum class StorageError {
    WriteFailed,
    InvalidPayload,
    CrcMismatch,
    UncommittedRecord
};

struct [[gnu::packed]] RecordHeader {
    uint32_t magic{RECORD_MAGIC};
    uint64_t seq_id{0};
    uint32_t payload_len{0};
};

struct [[gnu::packed]] RecordFooter {
    uint32_t crc32{0};
    uint32_t commit_flag{0xFFFFFFFF};
};

// Абстрактний інтерфейс Flash-носія
class IFlashDevice {
public:
    virtual ~IFlashDevice() = default;
    virtual bool write(uint32_t addr, std::span<const std::byte> data) noexcept = 0;
    virtual bool read(uint32_t addr, std::span<std::byte> out) const noexcept = 0;
};

class AtomicRecordWriter {
public:
    explicit AtomicRecordWriter(IFlashDevice& flash) noexcept : flash_(flash) {}

    std::expected<uint32_t, StorageError> write_record(
        uint32_t addr, uint64_t seq, std::span<const std::byte> payload) noexcept {
        
        const RecordHeader hdr{
            .magic = RECORD_MAGIC,
            .seq_id = seq,
            .payload_len = static_cast<uint32_t>(payload.size())
        };

        auto hdr_bytes = std::as_bytes(std::span{&hdr, 1});
        if (!flash_.write(addr, hdr_bytes)) {
            return std::unexpected(StorageError::WriteFailed);
        }

        uint32_t cur = addr + sizeof(RecordHeader);
        if (!flash_.write(cur, payload)) {
            return std::unexpected(StorageError::WriteFailed);
        }
        cur += payload.size();

        uint32_t computed_crc = calculate_crc(hdr_bytes, payload);
        RecordFooter ftr{.crc32 = computed_crc, .commit_flag = 0xFFFFFFFF};

        auto ftr_bytes = std::as_bytes(std::span{&ftr, 1});
        if (!flash_.write(cur, ftr_bytes)) {
            return std::unexpected(StorageError::WriteFailed);
        }

        // Атомарна фіксація прапорцем
        const uint32_t commit_val = COMMIT_FLAG;
        const uint32_t commit_addr = cur + offsetof(RecordFooter, commit_flag);
        if (!flash_.write(commit_addr, std::as_bytes(std::span{&commit_val, 1}))) {
            return std::unexpected(StorageError::WriteFailed);
        }

        return cur + sizeof(RecordFooter);
    }

private:
    IFlashDevice& flash_;

    static uint32_t calculate_crc(std::span<const std::byte> h, std::span<const std::byte> p) noexcept {
        // Поліноміальний розрахунок CRC32 (IEEE 802.3)
        uint32_t crc = 0xFFFFFFFF;
        for (auto b : h) crc = update_crc(crc, static_cast<uint8_t>(b));
        for (auto b : p) crc = update_crc(crc, static_cast<uint8_t>(b));
        return crc ^ 0xFFFFFFFF;
    }

    static uint32_t update_crc(uint32_t crc, uint8_t byte) noexcept {
        crc ^= byte;
        for (int i = 0; i < 8; ++i) crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        return crc;
    }
};

} // namespace storage

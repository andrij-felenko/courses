#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <optional>
#include <cstring>

#pragma pack(push, 1)
struct MissionItemStorage {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    uint16_t command{16};
    uint8_t frame{3};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};

struct MissionStorageHeader {
    uint32_t magic{0x4D495353}; // 'MISS'
    uint16_t version{1};
    uint16_t count{0};
    uint16_t current_seq{0};
    uint16_t crc16{0xFFFF};
    std::array<uint8_t, 20> reserved{};
};
#pragma pack(pop)

static_assert(sizeof(MissionStorageHeader) == 32, "Header must strictly be 32 bytes");

enum class StorageError : uint8_t {
    ReadFailed,
    WriteFailed,
    EraseFailed,
    InvalidMagic,
    CrcMismatch,
    CapacityExceeded,
    CorruptedSlots
};

class FlashHal {
public:
    virtual ~FlashHal() = default;
    [[nodiscard]] virtual bool read(uint32_t addr, std::span<uint8_t> buffer) = 0;
    [[nodiscard]] virtual bool write(uint32_t addr, std::span<const uint8_t> data) = 0;
    [[nodiscard]] virtual bool erase_sector(uint32_t addr) = 0;
};

class TransactionalMissionStorage {
public:
    static constexpr uint32_t POINTER_OFFSET = 0x0000;
    static constexpr uint32_t SLOT_A_OFFSET  = 0x1000;
    static constexpr uint32_t SLOT_B_OFFSET  = 0x10000;
    static constexpr uint16_t MAX_ITEMS      = 1500;

    explicit TransactionalMissionStorage(FlashHal& hal) : m_hal(hal) {}

    [[nodiscard]] std::expected<void, StorageError> init() noexcept {
        uint8_t slot_ptr{1};
        std::array<uint8_t, 1> ptr_buf{};
        if (m_hal.read(POINTER_OFFSET, ptr_buf)) {
            slot_ptr = (ptr_buf[0] == 2) ? 2 : 1;
        }

        const std::array<uint8_t, 2> trial_slots = {
            slot_ptr, 
            static_cast<uint8_t>(slot_ptr == 1 ? 2 : 1)
        };

        for (uint8_t s : trial_slots) {
            uint32_t offset = (s == 1) ? SLOT_A_OFFSET : SLOT_B_OFFSET;
            MissionStorageHeader hdr{};
            
            auto hdr_span = std::as_writable_bytes(std::span{&hdr, 1});
            if (!m_hal.read(offset, hdr_span)) {
                continue;
            }

            if (hdr.magic != 0x4D495353 || hdr.count > MAX_ITEMS) {
                continue;
            }

            // Перевірка цілісності CRC
            uint16_t calculated_crc = 0xFFFF;
            bool read_success = true;
            MissionItemStorage item{};
            auto item_span = std::as_writable_bytes(std::span{&item, 1});

            for (uint16_t i = 0; i < hdr.count; ++i) {
                uint32_t addr = offset + sizeof(MissionStorageHeader) + i * sizeof(MissionItemStorage);
                if (!m_hal.read(addr, item_span)) {
                    read_success = false;
                    break;
                }
                calculated_crc = compute_crc16(item_span, calculated_crc);
            }

            if (read_success && calculated_crc == hdr.crc16) {
                m_active_slot = s;
                m_count = hdr.count;
                m_current_seq = hdr.current_seq;
                m_is_valid = true;
                return {};
            }
        }

        return std::unexpected(StorageError::CorruptedSlots);
    }

    [[nodiscard]] std::expected<void, StorageError> commit(std::span<const MissionItemStorage> items) noexcept {
        if (items.size() > MAX_ITEMS) {
            return std::unexpected(StorageError::CapacityExceeded);
        }

        uint8_t target_slot = (m_active_slot == 1) ? 2 : 1;
        uint32_t target_offset = (target_slot == 1) ? SLOT_A_OFFSET : SLOT_B_OFFSET;

        if (!m_hal.erase_sector(target_offset)) {
            return std::unexpected(StorageError::EraseFailed);
        }

        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < items.size(); ++i) {
            auto item_bytes = std::as_bytes(std::span{&items[i], 1});
            crc = compute_crc16(item_bytes, crc);

            uint32_t addr = target_offset + sizeof(MissionStorageHeader) + i * sizeof(MissionItemStorage);
            if (!m_hal.write(addr, item_bytes)) {
                return std::unexpected(StorageError::WriteFailed);
            }
        }

        MissionStorageHeader hdr{
            .magic = 0x4D495353,
            .version = 1,
            .count = static_cast<uint16_t>(items.size()),
            .current_seq = 0,
            .crc16 = crc
        };

        auto hdr_bytes = std::as_bytes(std::span{&hdr, 1});
        if (!m_hal.write(target_offset, hdr_bytes)) {
            return std::unexpected(StorageError::WriteFailed);
        }

        // Атомарне оновлення покажчика активного слота
        std::array<uint8_t, 1> ptr_data{target_slot};
        if (!m_hal.erase_sector(POINTER_OFFSET) || !m_hal.write(POINTER_OFFSET, ptr_data)) {
            return std::unexpected(StorageError::WriteFailed);
        }

        m_active_slot = target_slot;
        m_count = static_cast<uint16_t>(items.size());
        m_current_seq = 0;
        m_is_valid = true;
        return {};
    }

    [[nodiscard]] uint16_t count() const noexcept { return m_count; }
    [[nodiscard]] uint16_t current_seq() const noexcept { return m_current_seq; }
    [[nodiscard]] bool is_valid() const noexcept { return m_is_valid; }

private:
    static uint16_t compute_crc16(std::span<const uint8_t> data, uint16_t seed = 0xFFFF) noexcept {
        uint16_t crc = seed;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t j = 0; j < 8; ++j) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

    FlashHal& m_hal;
    uint8_t m_active_slot{1};
    uint16_t m_count{0};
    uint16_t m_current_seq{0};
    bool m_is_valid{false};
};

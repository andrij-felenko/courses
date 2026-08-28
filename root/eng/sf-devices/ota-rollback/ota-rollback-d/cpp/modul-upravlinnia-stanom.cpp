// Модуль управління станом завантажувача на C++20
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <algorithm>

namespace bootloader {

inline constexpr uint32_t MagicValue = 0x424F4F54UL; // "BOOT"
inline constexpr uint8_t MaxBootRetries = 3;

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    None  = 0xFF
};

enum class SlotStatus : uint8_t {
    Empty        = 0xFF,
    PendingTest  = 0x01,
    ConfirmedOk  = 0x02,
    MarkedFailed = 0x03
};

struct [[gnu::packed]] BootRecord {
    uint32_t   magic{MagicValue};
    uint32_t   sequence{0};
    SlotId     activeSlot{SlotId::SlotA};
    SlotStatus status{SlotStatus::Empty};
    uint8_t    retriesLeft{0};
    uint8_t    reserved{0};
    uint32_t   crc32{0};
};

enum class FlashError {
    ReadFailed,
    EraseFailed,
    WriteFailed,
    CorruptedRecord
};

// Константний розрахунок CRC32
[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFUL;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
        }
    }
    return ~crc;
}

// Абстракція доступу до апаратної Flash-пам'яті
class IFlashDriver {
public:
    virtual ~IFlashDriver() = default;
    [[nodiscard]] virtual bool read(uint32_t address, std::span<uint8_t> dest) noexcept = 0;
    [[nodiscard]] virtual bool erase_sector(uint32_t sector_address) noexcept = 0;
    [[nodiscard]] virtual bool write(uint32_t address, std::span<const uint8_t> src) noexcept = 0;
};

class MetadataManager {
public:
    static constexpr uint32_t Sector0Addr = 0x08008000UL;
    static constexpr uint32_t Sector1Addr = 0x08009000UL;

    explicit MetadataManager(IFlashDriver& flash) noexcept : m_flash(flash) {}

    [[nodiscard]] bool isValid(const BootRecord& rec) const noexcept {
        if (rec.magic != MagicValue) return false;
        auto span_data = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&rec), sizeof(BootRecord) - sizeof(uint32_t));
        return rec.crc32 == calculate_crc32(span_data);
    }

    [[nodiscard]] std::expected<void, FlashError> writeRecord(BootRecord new_rec) noexcept {
        BootRecord rec0{}, rec1{};
        m_flash.read(Sector0Addr, {reinterpret_cast<uint8_t*>(&rec0), sizeof(BootRecord)});
        m_flash.read(Sector1Addr, {reinterpret_cast<uint8_t*>(&rec1), sizeof(BootRecord)});

        const bool valid0 = isValid(rec0);
        const bool valid1 = isValid(rec1);

        uint32_t target_addr = Sector0Addr;
        uint32_t next_seq = 1;

        if (valid0 && valid1) {
            if (rec0.sequence >= rec1.sequence) {
                target_addr = Sector1Addr;
                next_seq = rec0.sequence + 1;
            } else {
                target_addr = Sector0Addr;
                next_seq = rec1.sequence + 1;
            }
        } else if (valid0) {
            target_addr = Sector1Addr;
            next_seq = rec0.sequence + 1;
        } else if (valid1) {
            target_addr = Sector0Addr;
            next_seq = rec1.sequence + 1;
        }

        new_rec.magic = MagicValue;
        new_rec.sequence = next_seq;
        auto span_to_calc = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&new_rec), sizeof(BootRecord) - sizeof(uint32_t));
        new_rec.crc32 = calculate_crc32(span_to_calc);

        if (!m_flash.erase_sector(target_addr)) return std::unexpected(FlashError::EraseFailed);
        if (!m_flash.write(target_addr, {reinterpret_cast<const uint8_t*>(&new_rec), sizeof(BootRecord)})) {
            return std::unexpected(FlashError::WriteFailed);
        }

        return {};
    }

    [[nodiscard]] SlotId selectBootSlot() noexcept {
        BootRecord rec0{}, rec1{};
        m_flash.read(Sector0Addr, {reinterpret_cast<uint8_t*>(&rec0), sizeof(BootRecord)});
        m_flash.read(Sector1Addr, {reinterpret_cast<uint8_t*>(&rec1), sizeof(BootRecord)});

        const bool valid0 = isValid(rec0);
        const bool valid1 = isValid(rec1);

        BootRecord active{};
        if (valid0 && valid1) {
            active = (rec0.sequence >= rec1.sequence) ? rec0 : rec1;
        } else if (valid0) {
            active = rec0;
        } else if (valid1) {
            active = rec1;
        } else {
            // Аварійна ініціалізація
            active.magic = MagicValue;
            active.sequence = 1;
            active.activeSlot = SlotId::SlotA;
            active.status = SlotStatus::ConfirmedOk;
            active.retriesLeft = 0;
            (void)writeRecord(active);
            return SlotId::SlotA;
        }

        if (active.status == SlotStatus::PendingTest) {
            if (active.retriesLeft > 0) {
                active.retriesLeft--;
                (void)writeRecord(active);
                return active.activeSlot;
            } else {
                active.status = SlotStatus::MarkedFailed;
                const auto fallback = (active.activeSlot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
                active.activeSlot = fallback;
                active.status = SlotStatus::ConfirmedOk;
                active.retriesLeft = 0;
                (void)writeRecord(active);
                return fallback;
            }
        }

        if (active.status == SlotStatus::ConfirmedOk) {
            return active.activeSlot;
        }

        const auto safeSlot = (active.activeSlot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
        active.activeSlot = safeSlot;
        active.status = SlotStatus::ConfirmedOk;
        (void)writeRecord(active);
        return safeSlot;
    }

private:
    IFlashDriver& m_flash;
};

} // namespace bootloader

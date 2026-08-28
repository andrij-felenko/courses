// Повна реалізація симулятора завантажувача з A/B слотами на C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <optional>
#include <expected>
#include <memory>
#include <algorithm>

namespace boot_sim {

inline constexpr size_t FlashTotalSize  = 2 * 1024 * 1024; // 2 МБ
inline constexpr size_t FlashSectorSize = 4096;            // 4 КБ
inline constexpr uint32_t BootMagic     = 0x544F4F42UL;    // "BOOT"
inline constexpr uint8_t  MaxBootTries  = 3;

inline constexpr uint32_t AddrMetadata0 = 0x00008000UL;
inline constexpr uint32_t AddrMetadata1 = 0x00009000UL;
inline constexpr uint32_t AddrSlotA     = 0x00010000UL;
inline constexpr uint32_t AddrSlotB     = 0x00100000UL;

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    None  = 0xFF
};

enum class SlotState : uint8_t {
    Empty         = 0xFF,
    PendingVerify = 0x01,
    Valid         = 0x02,
    MarkedBad     = 0x03
};

struct [[gnu::packed]] BootMetadata {
    uint32_t  magic{BootMagic};
    uint32_t  sequence{0};
    SlotId    activeSlot{SlotId::SlotA};
    SlotState slotState{SlotState::Empty};
    uint8_t   bootAttemptsLeft{0};
    uint8_t   maxBootAttempts{MaxBootTries};
    uint32_t  imageVersion{0};
    uint32_t  imageCrc{0};
    uint32_t  headerCrc{0};
};

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

// Емулятор Flash пам'яті з підтримкою ін'єкції аварійного знеструмлення
class FlashMemory {
public:
    FlashMemory() {
        m_storage.fill(0xFF);
    }

    void reset() noexcept {
        m_storage.fill(0xFF);
        m_faultInjectionEnabled = false;
        m_bytesUntilPowerCut = -1;
        m_powerCutTriggered = false;
    }

    void enablePowerCutAfterBytes(int byteCount) noexcept {
        m_faultInjectionEnabled = true;
        m_bytesUntilPowerCut = byteCount;
        m_powerCutTriggered = false;
    }

    void disableFaultInjection() noexcept {
        m_faultInjectionEnabled = false;
        m_bytesUntilPowerCut = -1;
        m_powerCutTriggered = false;
    }

    [[nodiscard]] bool read(uint32_t address, std::span<uint8_t> dest) const noexcept {
        if (address + dest.size() > FlashTotalSize) return false;
        std::copy_n(m_storage.data() + address, dest.size(), dest.data());
        return true;
    }

    [[nodiscard]] bool eraseSector(uint32_t sectorAddr) noexcept {
        if (sectorAddr % FlashSectorSize != 0 || sectorAddr + FlashSectorSize > FlashTotalSize) {
            return false;
        }
        if (m_faultInjectionEnabled) {
            if (m_bytesUntilPowerCut <= 0) {
                m_powerCutTriggered = true;
                return false;
            }
            if (m_bytesUntilPowerCut < static_cast<int>(FlashSectorSize)) {
                std::fill_n(m_storage.data() + sectorAddr, m_bytesUntilPowerCut, 0xFF);
                m_bytesUntilPowerCut = 0;
                m_powerCutTriggered = true;
                return false;
            }
            m_bytesUntilPowerCut -= FlashSectorSize;
        }
        std::fill_n(m_storage.data() + sectorAddr, FlashSectorSize, 0xFF);
        return true;
    }

    [[nodiscard]] bool write(uint32_t address, std::span<const uint8_t> src) noexcept {
        if (address + src.size() > FlashTotalSize) return false;
        for (size_t i = 0; i < src.size(); ++i) {
            if (m_faultInjectionEnabled) {
                if (m_bytesUntilPowerCut <= 0) {
                    m_powerCutTriggered = true;
                    return false;
                }
                m_bytesUntilPowerCut--;
            }
            m_storage[address + i] &= src[i];
        }
        return true;
    }

    [[nodiscard]] bool wasPowerCutTriggered() const noexcept {
        return m_powerCutTriggered;
    }

private:
    std::array<uint8_t, FlashTotalSize> m_storage{};
    bool m_faultInjectionEnabled{false};
    int  m_bytesUntilPowerCut{-1};
    bool m_powerCutTriggered{false};
};

// Двосекторний менеджер метаданих
class MetadataManager {
public:
    explicit MetadataManager(FlashMemory& flash) noexcept : m_flash(flash) {}

    [[nodiscard]] bool verifyIntegrity(const BootMetadata& meta) const noexcept {
        if (meta.magic != BootMagic) return false;
        auto spanData = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(BootMetadata) - sizeof(uint32_t));
        return meta.headerCrc == calculate_crc32(spanData);
    }

    [[nodiscard]] std::optional<BootMetadata> readActive() const noexcept {
        BootMetadata meta0{}, meta1{};
        m_flash.read(AddrMetadata0, {reinterpret_cast<uint8_t*>(&meta0), sizeof(BootMetadata)});
        m_flash.read(AddrMetadata1, {reinterpret_cast<uint8_t*>(&meta1), sizeof(BootMetadata)});

        const bool valid0 = verifyIntegrity(meta0);
        const bool valid1 = verifyIntegrity(meta1);

        if (valid0 && valid1) {
            return (meta0.sequence >= meta1.sequence) ? meta0 : meta1;
        } else if (valid0) {
            return meta0;
        } else if (valid1) {
            return meta1;
        }
        return std::nullopt;
    }

    [[nodiscard]] bool writeNext(BootMetadata meta) noexcept {
        BootMetadata meta0{}, meta1{};
        m_flash.read(AddrMetadata0, {reinterpret_cast<uint8_t*>(&meta0), sizeof(BootMetadata)});
        m_flash.read(AddrMetadata1, {reinterpret_cast<uint8_t*>(&meta1), sizeof(BootMetadata)});

        const bool valid0 = verifyIntegrity(meta0);
        const bool valid1 = verifyIntegrity(meta1);

        uint32_t targetAddr = AddrMetadata0;
        uint32_t nextSeq = 1;

        if (valid0 && valid1) {
            if (meta0.sequence >= meta1.sequence) {
                targetAddr = AddrMetadata1;
                nextSeq = meta0.sequence + 1;
            } else {
                targetAddr = AddrMetadata0;
                nextSeq = meta1.sequence + 1;
            }
        } else if (valid0) {
            targetAddr = AddrMetadata1;
            nextSeq = meta0.sequence + 1;
        } else if (valid1) {
            targetAddr = AddrMetadata0;
            nextSeq = meta1.sequence + 1;
        }

        meta.magic = BootMagic;
        meta.sequence = nextSeq;
        auto spanData = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(BootMetadata) - sizeof(uint32_t));
        meta.headerCrc = calculate_crc32(spanData);

        if (!m_flash.eraseSector(targetAddr)) return false;
        return m_flash.write(targetAddr, {reinterpret_cast<const uint8_t*>(&meta), sizeof(BootMetadata)});
    }

private:
    FlashMemory& m_flash;
};

// Емулятор завантажувача
class Bootloader {
public:
    explicit Bootloader(MetadataManager& metaMgr) noexcept : m_metaMgr(metaMgr) {}

    [[nodiscard]] SlotId run() noexcept {
        auto activeMetaOpt = m_metaMgr.readActive();
        if (!activeMetaOpt) {
            std::cout << "[Завантажувач] Метадані відсутні! Аварійна ініціалізація на SLOT A.\n";
            BootMetadata initMeta{};
            initMeta.magic = BootMagic;
            initMeta.sequence = 1;
            initMeta.activeSlot = SlotId::SlotA;
            initMeta.slotState = SlotState::Valid;
            initMeta.bootAttemptsLeft = 0;
            initMeta.imageVersion = 100;
            m_metaMgr.writeNext(initMeta);
            return SlotId::SlotA;
        }

        auto meta = *activeMetaOpt;
        std::cout << "[Завантажувач] Слот: " << (meta.activeSlot == SlotId::SlotA ? 'A' : 'B')
                  << ", Стан: " << static_cast<int>(meta.slotState)
                  << ", Залишок спроб: " << static_cast<int>(meta.bootAttemptsLeft)
                  << " (seq: " << meta.sequence << ")\n";

        if (meta.slotState == SlotState::PendingVerify) {
            if (meta.bootAttemptsLeft > 0) {
                meta.bootAttemptsLeft--;
                std::cout << "[Завантажувач] Декремент спроб -> " << static_cast<int>(meta.bootAttemptsLeft) << "\n";
                m_metaMgr.writeNext(meta);
                return meta.activeSlot;
            } else {
                std::cout << "[Завантажувач] Спроби вичерпано! АВТОМАТИЧНИЙ ВІДКАТ.\n";
                meta.slotState = SlotState::MarkedBad;
                const auto fallback = (meta.activeSlot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
                meta.activeSlot = fallback;
                meta.slotState = SlotState::Valid;
                meta.bootAttemptsLeft = 0;
                m_metaMgr.writeNext(meta);
                return fallback;
            }
        }

        if (meta.slotState == SlotState::Valid) {
            return meta.activeSlot;
        }

        const auto safe = (meta.activeSlot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
        meta.activeSlot = safe;
        meta.slotState = SlotState::Valid;
        m_metaMgr.writeNext(meta);
        return safe;
    }

private:
    MetadataManager& m_metaMgr;
};

// Клієнт оновлення застосунку
class OtaClient {
public:
    OtaClient(MetadataManager& metaMgr, FlashMemory& flash) noexcept
        : m_metaMgr(metaMgr), m_flash(flash) {}

    [[nodiscard]] bool installImage(SlotId targetSlot, uint32_t version, std::span<const uint8_t> payload) noexcept {
        const uint32_t targetAddr = (targetSlot == SlotId::SlotA) ? AddrSlotA : AddrSlotB;
        std::cout << "[OTA Client] Запис образу v" << version << " у слот "
                  << (targetSlot == SlotId::SlotA ? 'A' : 'B') << "...\n";

        const size_t sectors = (payload.size() + FlashSectorSize - 1) / FlashSectorSize;
        for (size_t s = 0; s < sectors; ++s) {
            if (!m_flash.eraseSector(targetAddr + static_cast<uint32_t>(s * FlashSectorSize))) {
                return false;
            }
        }

        if (!m_flash.write(targetAddr, payload)) {
            return false;
        }

        BootMetadata meta{};
        if (auto current = m_metaMgr.readActive()) {
            meta = *current;
        }
        meta.activeSlot = targetSlot;
        meta.slotState = SlotState::PendingVerify;
        meta.bootAttemptsLeft = MaxBootTries;
        meta.maxBootAttempts = MaxBootTries;
        meta.imageVersion = version;
        meta.imageCrc = calculate_crc32(payload);

        return m_metaMgr.writeNext(meta);
    }

    [[nodiscard]] bool markValid() noexcept {
        auto active = m_metaMgr.readActive();
        if (!active) return false;
        if (active->slotState == SlotState::PendingVerify) {
            active->slotState = SlotState::Valid;
            active->bootAttemptsLeft = 0;
            std::cout << "[Застосунок] Самотест POST успішний -> закріплено VALID!\n";
            return m_metaMgr.writeNext(*active);
        }
        return true;
    }

private:
    MetadataManager& m_metaMgr;
    FlashMemory&     m_flash;
};

} // namespace boot_sim

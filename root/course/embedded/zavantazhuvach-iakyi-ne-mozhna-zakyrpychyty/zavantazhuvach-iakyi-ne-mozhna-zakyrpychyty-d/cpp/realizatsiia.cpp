#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <concepts>

namespace bootloader {

inline constexpr uint32_t MagicHeader    = 0x424F4F54UL; // 'BOOT'
inline constexpr uint32_t MetadataMagic  = 0x4D455441UL; // 'META'
inline constexpr uint8_t  MaxBootAttempts = 3;

inline constexpr uintptr_t FlashSlotABase = 0x08014000UL;
inline constexpr uintptr_t FlashSlotBBase = 0x0808A000UL;
inline constexpr size_t    FlashSlotSize  = 470 * 1024UL;

inline constexpr uintptr_t SramStartAddr  = 0x20000000UL;
inline constexpr uintptr_t SramEndAddr    = 0x20040000UL; // 256 КБ SRAM

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    None  = 255
};

enum class SlotState : uint8_t {
    Empty     = 0xFF,
    Trial     = 0xAA,
    Confirmed = 0x55,
    Failed    = 0x00
};

enum class BootError {
    InvalidMagic,
    PayloadSizeOutOfBounds,
    ChecksumMismatch,
    InvalidStackPointer,
    NoValidSlotFound
};

#pragma pack(push, 1)
struct ImageHeader {
    uint32_t magic;
    uint32_t version;
    uint32_t security_counter;
    uint32_t payload_size;
    uint32_t payload_crc32;
    std::array<uint8_t, 64> signature;
    uint32_t vector_offset;
    std::array<uint8_t, 136> reserved;
};

struct SlotMetadata {
    SlotState state;
    uint8_t   boot_attempts;
    uint16_t  reserved;
    uint32_t  image_version;
    uint32_t  security_counter;
};

struct BootMetadata {
    uint32_t magic;
    uint32_t sequence;
    std::array<SlotMetadata, 2> slots;
    uint32_t metadata_crc32;
};
#pragma pack(pop)

// constexpr обчислення контрольної суми CRC-32 (IEEE 802.3)
[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept
{
    uint32_t crc = 0xFFFFFFFFUL;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1UL)));
        }
    }
    return ~crc;
}

class BootManager {
public:
    [[nodiscard]] static std::expected<void, BootError> verify_image(uintptr_t slot_base) noexcept
    {
        const auto* hdr = reinterpret_cast<const ImageHeader*>(slot_base);

        if (hdr->magic != MagicHeader) {
            return std::unexpected(BootError::InvalidMagic);
        }

        if (hdr->payload_size == 0 || hdr->payload_size > (FlashSlotSize - sizeof(ImageHeader))) {
            return std::unexpected(BootError::PayloadSizeOutOfBounds);
        }

        const auto* payload_ptr = reinterpret_cast<const uint8_t*>(slot_base + sizeof(ImageHeader));
        std::span<const uint8_t> payload(payload_ptr, hdr->payload_size);

        if (calculate_crc32(payload) != hdr->payload_crc32) {
            return std::unexpected(BootError::ChecksumMismatch);
        }

        // Перевірка коректності покажчика вершини стека в межах SRAM
        uint32_t initial_msp = *reinterpret_cast<const uint32_t*>(payload_ptr);
        if (initial_msp < SramStartAddr || initial_msp > SramEndAddr) {
            return std::unexpected(BootError::InvalidStackPointer);
        }

        return {};
    }

    [[nodiscard]] static std::expected<SlotId, BootError> select_active_slot(BootMetadata& meta) noexcept
    {
        // 1. Пріоритет слоту в стані пробного запуску (TRIAL)
        for (size_t i = 0; i < meta.slots.size(); ++i) {
            if (meta.slots[i].state == SlotState::Trial) {
                uintptr_t base = (i == 0) ? FlashSlotABase : FlashSlotBBase;
                if (meta.slots[i].boot_attempts < MaxBootAttempts && verify_image(base).has_value()) {
                    return static_cast<SlotId>(i);
                }
                // Якщо ліміт спроб вичерпано або бінарник битий — дискваліфікуємо слот
                meta.slots[i].state = SlotState::Failed;
            }
        }

        // 2. Пошук стабільного слоту (CONFIRMED) із найбільшим номером версії
        SlotId candidate = SlotId::None;
        uint32_t highest_version = 0;

        for (size_t i = 0; i < meta.slots.size(); ++i) {
            if (meta.slots[i].state == SlotState::Confirmed) {
                uintptr_t base = (i == 0) ? FlashSlotABase : FlashSlotBBase;
                if (verify_image(base).has_value()) {
                    if (candidate == SlotId::None || meta.slots[i].image_version >= highest_version) {
                        highest_version = meta.slots[i].image_version;
                        candidate = static_cast<SlotId>(i);
                    }
                } else {
                    meta.slots[i].state = SlotState::Failed;
                }
            }
        }

        if (candidate != SlotId::None) {
            return candidate;
        }

        return std::unexpected(BootError::NoValidSlotFound);
    }

    [[noreturn]] static void jump_to_application(uintptr_t slot_base) noexcept
    {
        uintptr_t vector_table = slot_base + sizeof(ImageHeader);
        uint32_t initial_msp = *reinterpret_cast<const volatile uint32_t*>(vector_table);
        uint32_t reset_handler = *reinterpret_cast<const volatile uint32_t*>(vector_table + 4);

        // 1. Апаратне вимкнення всіх переривань
        asm volatile ("cpsid i" : : : "memory");

        // 2. Встановлення зсуву векторів у системному регістрі Cortex-M
        *reinterpret_cast<volatile uint32_t*>(0xE000ED08UL) = vector_table;

        // 3. Встановлення покажчика стека (MSP)
        asm volatile ("msr msp, %0" : : "r"(initial_msp) : "memory");

        // 4. Бар'єри синхронізації інструкцій та даних
        asm volatile ("dsb" : : : "memory");
        asm volatile ("isb" : : : "memory");

        // 5. Виклик точки входу
        using AppEntry = void (*)() noexcept;
        auto entry = reinterpret_cast<AppEntry>(reset_handler);
        entry();

        while (true) { }
    }
};

} // namespace bootloader

#include <cstdint>
#include <span>
#include <optional>
#include <string_view>

namespace BootManager {

struct alignas(4) ImageHeader {
    std::uint32_t magic{0};
    std::uint32_t versionRaw{0};
    std::uint32_t imageSize{0};
    std::uint32_t expectedCrc32{0};
    std::uint32_t flags{0};

    static constexpr std::uint32_t ValidMagic = 0x544F4F42; // "BOOT"
};

class SlotValidator {
public:
    static constexpr std::uintptr_t SlotAAddress = 0x08020000U;
    static constexpr std::uintptr_t SlotBAddress = 0x080A0000U;
    static constexpr std::size_t    SlotMaxCapacity = 512 * 1024;

    [[nodiscard]] static std::optional<std::uintptr_t> resolveBootTarget() noexcept {
        // Спроба валідації слота B (цільового для оновлення)
        if (const auto entryB = validateSlot(SlotBAddress); entryB.has_value()) {
            return entryB;
        }

        // Аварійний відкат на перевірений слот A у разі пошкодження слота B
        if (const auto entryA = validateSlot(SlotAAddress); entryA.has_value()) {
            return entryA;
        }

        return std::nullopt; // Фатальний стан: обидва банки пошкоджено
    }

private:
    [[nodiscard]] static std::optional<std::uintptr_t> validateSlot(std::uintptr_t slotBase) noexcept {
        const auto* header = reinterpret_cast<const ImageHeader*>(slotBase);
        
        if (header->magic != ImageHeader::ValidMagic) {
            return std::nullopt;
        }

        if (header->imageSize == 0 || header->imageSize > (SlotMaxCapacity - sizeof(ImageHeader))) {
            return std::nullopt;
        }

        const auto* payloadPtr = reinterpret_cast<const std::uint8_t*>(slotBase + sizeof(ImageHeader));
        std::span<const std::uint8_t> payloadSpan(payloadPtr, header->imageSize);

        if (calculateCrc32(payloadSpan) != header->expectedCrc32) {
            return std::nullopt; // Пошкодження CRC внаслідок знеструмлення
        }

        return slotBase + sizeof(ImageHeader);
    }

    [[nodiscard]] static std::uint32_t calculateCrc32(std::span<const std::uint8_t> data) noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        for (const auto byte : data) {
            crc ^= byte;
            for (std::uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        return ~crc;
    }
};

} // namespace BootManager

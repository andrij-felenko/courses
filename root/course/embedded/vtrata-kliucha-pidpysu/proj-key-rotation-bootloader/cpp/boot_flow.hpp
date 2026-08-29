#pragma once

#include <cstdint>
#include <expected>

#include "boot_status.hpp"

namespace boot {

// Два банки прошивки: один працює, другий приймає оновлення.
enum class Slot : std::uint32_t { A = 0, B = 1 };

inline constexpr std::uint32_t kBootRecordMagic = 0x41545342U; // "BSTA"
inline constexpr std::uint32_t kStatusConfirmed = 0x434F4E46U; // "CONF"
inline constexpr std::uint32_t kStatusTesting = 0x54455354U;   // "TEST"

// Скільки пробних запусків дозволено, поки застосунок не підтвердив себе.
inline constexpr std::uint32_t kMaxTries = 3;

// Запис стану завантаження в окремій сторінці Flash, накритий CRC-32:
// обрив живлення посеред запису мусить читатися як «зіпсовано», а не як
// довільне сміття у полях.
struct BootRecord {
    Slot activeSlot{Slot::A};
    Slot previousSlot{Slot::A};
    std::uint32_t status{kStatusConfirmed};
    std::uint32_t tryCount{0};
    std::uint32_t pendingRevokeMask{0}; // слоти ключів, які спалити після підтвердження
    std::uint32_t pendingCounter{0};    // до якого значення підняти лічильник

    [[nodiscard]] bool isTesting() const noexcept { return status == kStatusTesting; }

    void markConfirmed(Slot slot) noexcept
    {
        activeSlot = slot;
        previousSlot = slot;
        status = kStatusConfirmed;
        tryCount = 0;
        pendingRevokeMask = 0;
        pendingCounter = 0;
    }
};

class BootFlow {
public:
    // Читає запис; при пошкодженні або чистій сторінці віддає безпечний
    // дефолт «банк A, підтверджено».
    [[nodiscard]] static BootRecord load() noexcept;

    [[nodiscard]] static std::expected<void, Status> store(const BootRecord& record) noexcept;

    // ПЕРША ФАЗА комміту: новий образ уже в іншому банку, позначаємо його
    // пробним. Жодна перемичка не палиться — саме тому крок оборотний.
    [[nodiscard]] static std::expected<void, Status> stageUpdate(Slot newSlot) noexcept;

    // ДРУГА ФАЗА комміту. Викликає САМ ЗАСТОСУНОК після самодіагностики та
    // першого успішного зв'язку з сервером: тільки тут палимо біти відкликання
    // старих ключів і піднімаємо лічильник анти-відкату.
    [[nodiscard]] static std::expected<void, Status> confirmUpdate() noexcept;
};

} // namespace boot

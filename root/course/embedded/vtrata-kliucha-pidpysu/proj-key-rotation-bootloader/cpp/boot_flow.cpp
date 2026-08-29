#include "boot_flow.hpp"

#include <algorithm>
#include <array>
#include <span>

#include "crc32.hpp"
#include "efuse.hpp"

namespace boot {
namespace {

// ------------------------------------------------------------------
//  Мінімальний драйвер Flash: одна сторінка під запис стану.
// ------------------------------------------------------------------

struct FlashRegisters {
    volatile std::uint32_t acr;
    volatile std::uint32_t keyr;
    volatile std::uint32_t optkeyr;
    volatile std::uint32_t sr;
    volatile std::uint32_t cr;
    volatile std::uint32_t ar;
};

inline auto* flashRegs() noexcept
{
    return reinterpret_cast<FlashRegisters*>(0x40022000UL);
}

inline constexpr std::uint32_t kFlashKey1 = 0x45670123UL;
inline constexpr std::uint32_t kFlashKey2 = 0xCDEF89ABUL;

inline constexpr std::uint32_t kCrProgram = 1U << 0;
inline constexpr std::uint32_t kCrPageErase = 1U << 1;
inline constexpr std::uint32_t kCrStart = 1U << 6;
inline constexpr std::uint32_t kCrLock = 1U << 7;

inline constexpr std::uint32_t kSrBusy = 1U << 0;
inline constexpr std::uint32_t kSrProgramError = 1U << 2;
inline constexpr std::uint32_t kSrWriteProtect = 1U << 4;
inline constexpr std::uint32_t kSrEndOfOp = 1U << 5;

inline constexpr std::uintptr_t kStatePage = 0x0800F800UL;
inline constexpr std::uint32_t kFlashTimeout = 400000;
inline constexpr std::size_t kRecordSize = 32;

// Замок Flash знімається на час запису і повертається деструктором — включно
// з гілками, де запис обірвався помилкою.
class FlashUnlocked {
public:
    FlashUnlocked() noexcept
    {
        if ((flashRegs()->cr & kCrLock) != 0) {
            flashRegs()->keyr = kFlashKey1;
            flashRegs()->keyr = kFlashKey2;
        }
    }

    ~FlashUnlocked() noexcept { flashRegs()->cr |= kCrLock; }

    FlashUnlocked(const FlashUnlocked&) = delete;
    FlashUnlocked& operator=(const FlashUnlocked&) = delete;
};

[[nodiscard]] std::expected<void, Status> flashWait() noexcept
{
    for (std::uint32_t spins = 0; spins < kFlashTimeout; ++spins) {
        if ((flashRegs()->sr & kSrBusy) == 0) {
            if ((flashRegs()->sr & (kSrProgramError | kSrWriteProtect)) != 0) {
                flashRegs()->sr = kSrProgramError | kSrWriteProtect | kSrEndOfOp;
                return std::unexpected(Status::StateWriteFailed);
            }
            flashRegs()->sr = kSrEndOfOp;
            return {};
        }
    }
    return std::unexpected(Status::StateWriteFailed);
}

[[nodiscard]] std::expected<void, Status> erasePage() noexcept
{
    if (auto ready = flashWait(); !ready) {
        return ready;
    }

    flashRegs()->cr |= kCrPageErase;
    flashRegs()->ar = static_cast<std::uint32_t>(kStatePage);
    flashRegs()->cr |= kCrStart;

    const auto done = flashWait();
    flashRegs()->cr &= ~(kCrPageErase | kCrStart);
    return done;
}

// Контролер програмує півсловами, тож і пишемо півсловами.
[[nodiscard]] std::expected<void, Status>
writePage(std::span<const std::uint8_t, kRecordSize> bytes) noexcept
{
    auto* target = reinterpret_cast<volatile std::uint16_t*>(kStatePage);

    flashRegs()->cr |= kCrProgram;

    std::expected<void, Status> result{};
    for (std::size_t i = 0; i < bytes.size() / 2; ++i) {
        target[i] = static_cast<std::uint16_t>(bytes[i * 2] |
                                               (bytes[i * 2 + 1] << 8));
        result = flashWait();
        if (!result) {
            break;
        }
    }

    flashRegs()->cr &= ~kCrProgram;
    return result;
}

// ------------------------------------------------------------------
//  Сериалізація запису: розкладка на носії описана тут і більше ніде.
// ------------------------------------------------------------------

void writeU32(std::span<std::uint8_t> bytes, std::size_t offset, std::uint32_t value) noexcept
{
    bytes[offset + 0] = static_cast<std::uint8_t>(value);
    bytes[offset + 1] = static_cast<std::uint8_t>(value >> 8);
    bytes[offset + 2] = static_cast<std::uint8_t>(value >> 16);
    bytes[offset + 3] = static_cast<std::uint8_t>(value >> 24);
}

[[nodiscard]] std::uint32_t readU32(std::span<const std::uint8_t> bytes,
                                    std::size_t offset) noexcept
{
    return static_cast<std::uint32_t>(bytes[offset]) |
           (static_cast<std::uint32_t>(bytes[offset + 1]) << 8) |
           (static_cast<std::uint32_t>(bytes[offset + 2]) << 16) |
           (static_cast<std::uint32_t>(bytes[offset + 3]) << 24);
}

[[nodiscard]] std::array<std::uint8_t, kRecordSize> serialize(const BootRecord& record) noexcept
{
    std::array<std::uint8_t, kRecordSize> bytes{};

    writeU32(bytes, 0, kBootRecordMagic);
    writeU32(bytes, 8, static_cast<std::uint32_t>(record.activeSlot));
    writeU32(bytes, 12, static_cast<std::uint32_t>(record.previousSlot));
    writeU32(bytes, 16, record.status);
    writeU32(bytes, 20, record.tryCount);
    writeU32(bytes, 24, record.pendingRevokeMask);
    writeU32(bytes, 28, record.pendingCounter);
    // CRC накриває все, що йде після самого поля CRC.
    writeU32(bytes, 4, crc32(std::span<const std::uint8_t>{bytes}.subspan(8)));

    return bytes;
}

[[nodiscard]] std::array<std::uint8_t, kRecordSize> readPage() noexcept
{
    std::array<std::uint8_t, kRecordSize> bytes{};
    const auto* page = reinterpret_cast<const std::uint8_t*>(kStatePage);
    std::copy_n(page, kRecordSize, bytes.begin());
    return bytes;
}

} // namespace

BootRecord BootFlow::load() noexcept
{
    const auto bytes = readPage();
    const std::span<const std::uint8_t> view{bytes};

    const bool intact = readU32(view, 0) == kBootRecordMagic &&
                        readU32(view, 4) == crc32(view.subspan(8)) &&
                        readU32(view, 8) <= static_cast<std::uint32_t>(Slot::B) &&
                        readU32(view, 12) <= static_cast<std::uint32_t>(Slot::B) &&
                        (readU32(view, 16) == kStatusConfirmed ||
                         readU32(view, 16) == kStatusTesting);

    if (!intact) {
        // Сторінка чиста або зіпсована обривом живлення. Безпечний дефолт —
        // банк A: він або справді підтверджений, або не пройде верифікацію
        // й нас винесе в аварійний режим.
        return BootRecord{};
    }

    BootRecord record;
    record.activeSlot = static_cast<Slot>(readU32(view, 8));
    record.previousSlot = static_cast<Slot>(readU32(view, 12));
    record.status = readU32(view, 16);
    record.tryCount = readU32(view, 20);
    record.pendingRevokeMask = readU32(view, 24);
    record.pendingCounter = readU32(view, 28);
    return record;
}

std::expected<void, Status> BootFlow::store(const BootRecord& record) noexcept
{
    const auto bytes = serialize(record);

    {
        const FlashUnlocked unlocked;

        if (auto erased = erasePage(); !erased) {
            return erased;
        }
        if (auto written = writePage(bytes); !written) {
            return written;
        }
    } // замок повертається тут

    // Контрольне перечитування: запис мусить бути видимим одразу.
    if (readPage() != bytes) {
        return std::unexpected(Status::StateWriteFailed);
    }

    return {};
}

std::expected<void, Status> BootFlow::stageUpdate(Slot newSlot) noexcept
{
    BootRecord record = load();

    if (record.isTesting()) {
        // Пробний запуск ще не підтверджено: нове оновлення поверх нього
        // стерло б єдиний відомий шлях назад.
        return std::unexpected(Status::NotTesting);
    }

    record.previousSlot = record.activeSlot;
    record.activeSlot = newSlot;
    record.status = kStatusTesting;
    record.tryCount = 0;
    record.pendingRevokeMask = 0;
    record.pendingCounter = 0;

    return store(record);
}

std::expected<void, Status> BootFlow::confirmUpdate() noexcept
{
    BootRecord record = load();

    if (!record.isTesting()) {
        return std::unexpected(Status::NotTesting);
    }

    // Порядок тут не смак, а вимога. Спершу перемички (незворотна частина),
    // і лише коли ЗАЛІЗО підтвердило кожен біт — запис у CONFIRMED.
    // Зворотний порядок дав би стан «підтверджено» при досі чинних ключах.
    for (std::uint8_t slot = 0; slot < kKeySlots; ++slot) {
        if ((record.pendingRevokeMask & (1U << slot)) == 0) {
            continue;
        }
        if (auto burned = Efuse::burnRevocation(slot); !burned) {
            // Перемичка не спалилась: лишаємось у STATUS_TESTING. Застосунок
            // повторить підтвердження пізніше, а завантажувач досі вміє
            // відкотитись на старий банк.
            return burned;
        }
    }

    if (record.pendingCounter != 0) {
        if (auto burned = Efuse::burnCounter(record.pendingCounter); !burned) {
            return burned;
        }
    }

    record.markConfirmed(record.activeSlot);
    return store(record);
}

} // namespace boot

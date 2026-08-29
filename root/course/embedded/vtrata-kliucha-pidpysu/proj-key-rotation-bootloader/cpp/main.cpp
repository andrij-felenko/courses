#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "boot_flow.hpp"
#include "efuse.hpp"
#include "manifest.hpp"
#include "verifier.hpp"

namespace boot {
namespace {

// ------------------------------------------------------------------
//  Карта Flash і мінімальна периферія завантажувача
// ------------------------------------------------------------------

inline constexpr std::uintptr_t kSlotABase = 0x08010000UL;
inline constexpr std::uintptr_t kSlotBBase = 0x08090000UL;
inline constexpr std::size_t kSlotSize = 0x00080000UL;

inline constexpr std::uint32_t kSramBase = 0x20000000UL;
inline constexpr std::uint32_t kSramSize = 0x00020000UL;

struct UartRegisters {
    volatile std::uint32_t sr;
    volatile std::uint32_t dr;
};

inline auto* uartRegs() noexcept
{
    return reinterpret_cast<UartRegisters*>(0x40013800UL);
}

inline constexpr std::uint32_t kUartTxEmpty = 1U << 7;

inline auto& watchdogKey() noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(0x40003000UL);
}

inline auto& vectorTableOffset() noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(0xE000ED08UL);
}

inline constexpr std::uint32_t kWatchdogReload = 0x0000AAAAUL;

void log(std::string_view text) noexcept
{
    for (const char symbol : text) {
        while ((uartRegs()->sr & kUartTxEmpty) == 0) {
            // чекаємо, поки звільниться регістр передавання
        }
        uartRegs()->dr = static_cast<std::uint32_t>(static_cast<unsigned char>(symbol));
    }
}

void log(std::string_view prefix, Status status) noexcept
{
    log(prefix);
    log(": ");
    log(toString(status));
    log("\r\n");
}

[[nodiscard]] std::span<const std::uint8_t> slotView(Slot slot) noexcept
{
    const auto base = (slot == Slot::B) ? kSlotBBase : kSlotABase;
    return {reinterpret_cast<const std::uint8_t*>(base), kSlotSize};
}

// ------------------------------------------------------------------
//  Перевірка банку
// ------------------------------------------------------------------

[[nodiscard]] std::expected<Manifest, Status>
loadAndVerify(Slot slot, const SecureBootVerifier& verifier) noexcept
{
    const auto flash = slotView(slot);

    auto manifest = Manifest::parse(flash);
    if (!manifest) {
        return manifest;
    }

    // Образ мусить стартувати всередині свого ж банку, а не де завгодно.
    const auto base = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(flash.data()));
    if (manifest->loadAddress() < base || manifest->loadAddress() >= base + kSlotSize) {
        return std::unexpected(Status::BadImageLayout);
    }

    if (auto verified = verifier.verify(*manifest, manifest->payload(flash)); !verified) {
        return std::unexpected(verified.error());
    }

    return manifest;
}

// Готуємо, але НЕ виконуємо ротацію: якщо образ підписано старшим слотом,
// усі молодші підлягають відкликанню — але спалимо їх аж тоді, коли застосунок
// доповість про працездатність. До того старий банк лишається шляхом назад.
void planRotation(BootRecord& record, const Manifest& manifest, const EfuseMirror& efuse) noexcept
{
    std::uint32_t mask = 0;
    for (std::uint8_t slot = 0; slot < manifest.keySlotIndex(); ++slot) {
        if (!efuse.isRevoked(slot)) {
            mask |= (1U << slot);
        }
    }
    record.pendingRevokeMask = mask;

    if (manifest.securityVersion() > efuse.monotonicCounter &&
        manifest.securityVersion() <= kCounterBits) {
        record.pendingCounter = manifest.securityVersion();
    } else {
        record.pendingCounter = 0;
        if (manifest.securityVersion() > kCounterBits) {
            // Термометр вичерпано. Це не аварія завантаження: образ чинний,
            // просто піднімати лічильник більше нікуди — і про це має
            // дізнатись виробництво.
            log("efuse: anti-rollback counter exhausted\r\n");
        }
    }
}

// ------------------------------------------------------------------
//  Запуск і аварійний режим
// ------------------------------------------------------------------

[[noreturn]] void spinForever() noexcept
{
    for (;;) {
        watchdogKey() = kWatchdogReload;
    }
}

// Жодного чинного образу немає. Це НЕ привід стирати банки чи палити
// перемички: лишаємось у завантажувачі, годуємо сторожовий таймер і чекаємо
// оновлення по службовому інтерфейсу. Пристрій живий, хай і без застосунку.
[[noreturn]] void enterRecovery(Status reason) noexcept
{
    log("recovery", reason);
    spinForever();
}

[[noreturn]] void jumpToApplication(std::uint32_t loadAddress) noexcept
{
    const auto* vectors = reinterpret_cast<const std::uint32_t*>(loadAddress);
    const std::uint32_t stackPointer = vectors[0];
    const std::uint32_t resetHandler = vectors[1];

    // Вершина стека й вектор скидання мусять вказувати в дозволені області.
    if (stackPointer < kSramBase || stackPointer > kSramBase + kSramSize ||
        resetHandler < loadAddress) {
        log("jump", Status::BadImageLayout);
        spinForever();
    }

    log("boot: jumping to application\r\n");

    asm volatile("cpsid i");
    vectorTableOffset() = loadAddress;
    asm volatile("msr msp, %0" : : "r"(stackPointer) : "memory");
    asm volatile("dsb; isb");

    reinterpret_cast<void (*)()>(resetHandler)();

    spinForever(); // сюди не повертаються
}

} // namespace
} // namespace boot

int main()
{
    using namespace boot;

    initCryptoArena();
    log("\r\nbootloader stage 2\r\n");

    const auto mirror = Efuse::readMirror();
    if (!mirror) {
        // Без кореня довіри перевіряти образ немає чим.
        enterRecovery(mirror.error());
    }

    const SecureBootVerifier verifier{*mirror};
    BootRecord record = BootFlow::load();

    // Пробний образ вичерпав спроби — примусовий відкіт на попередній банк.
    if (record.isTesting() && record.tryCount >= kMaxTries) {
        log("boot: test image failed to confirm, rolling back\r\n");
        record.markConfirmed(record.previousSlot);
        if (auto stored = BootFlow::store(record); !stored) {
            log("state", stored.error());
        }
    }

    Slot candidate = record.activeSlot;
    auto image = loadAndVerify(candidate, verifier);

    if (!image) {
        log("verify", image.error());

        // Активний банк не проходить перевірку. Якщо він був пробним, у нас
        // лишається підтверджений попередник — саме заради цієї гілки ми й
        // не палили перемички наперед.
        if (candidate != record.previousSlot) {
            candidate = record.previousSlot;
            image = loadAndVerify(candidate, verifier);
            if (image) {
                log("boot: fell back to previous bank\r\n");
                record.markConfirmed(candidate);
                if (auto stored = BootFlow::store(record); !stored) {
                    log("state", stored.error());
                }
            } else {
                log("verify(previous)", image.error());
            }
        }
    }

    if (!image) {
        enterRecovery(image.error());
    }

    if (record.isTesting()) {
        record.tryCount += 1;
        planRotation(record, *image, *mirror);

        // Лічильник спроб пишемо ДО стрибка. Інакше застосунок, що падає
        // у HardFault до підтвердження, крутив би нескінченний цикл скидів:
        // tryCount ніколи б не доріс до стелі, і відкат не настав би.
        if (auto stored = BootFlow::store(record); !stored) {
            enterRecovery(stored.error());
        }
        log("boot: test run of staged image\r\n");
    }

    jumpToApplication(image->loadAddress());
}

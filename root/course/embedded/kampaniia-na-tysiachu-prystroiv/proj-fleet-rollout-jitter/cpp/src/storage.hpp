// Карта Flash, запис образу в неактивний банк і стан кампанії в незалежній пам'яті.
//
// Карта повторює розкладку статті: 1 МБ на кристалі Cortex-M, два симетричні
// банки по 432 КБ і два службові сектори.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <utility>

namespace fleet {

enum class Bank : std::uint8_t { A = 0, B = 1 };

constexpr Bank other(Bank b) noexcept { return b == Bank::A ? Bank::B : Bank::A; }
constexpr std::string_view name(Bank b) noexcept { return b == Bank::A ? "A" : "B"; }

inline constexpr std::uint32_t kFlashBase      = 0x08000000u;
inline constexpr std::uint32_t kFlashSize      = 1024u * 1024u;
inline constexpr std::uint32_t kPageSize       = 2048u;
inline constexpr std::uint32_t kWriteQuantum   = 8u;      // подвійне слово

inline constexpr std::uint32_t kBootloaderBase = 0x08000000u;   //  64 КБ
inline constexpr std::uint32_t kNvramBase      = 0x08010000u;   //  16 КБ
inline constexpr std::uint32_t kBankABase      = 0x08014000u;   // 432 КБ
inline constexpr std::uint32_t kBankBBase      = 0x08080000u;   // 432 КБ
inline constexpr std::uint32_t kBankSize       = 0x0006C000u;
inline constexpr std::uint32_t kNvsBase        = 0x080EC000u;   //  80 КБ

inline constexpr std::uint8_t kMaxAllowedCrashes = 3;

constexpr std::uint32_t bank_base(Bank b) noexcept
{
    return b == Bank::A ? kBankABase : kBankBBase;
}

enum class StorageError {
    Locked,        // контролер Flash не відкрився
    Misaligned,    // адреса або довжина не кратні кванту запису
    OutOfBounds,   // за межами банку
    EraseFailed,
    ProgramFailed, // запис у нестерту комірку — PGSERR
    NoRecord,      // жодного цілого запису стану
    CrcMismatch
};

[[nodiscard]] std::string_view describe(StorageError e) noexcept;

// Стан кампанії. Живе в RTC Backup Domain (переживає скидання ядра) і
// дублюється журналом у секторі NVRAM (переживає зникнення живлення). У RAM
// його не тримають: лічильник збоїв, який щоразу починається з нуля, дає
// нескінченну петлю перезавантажень.
struct RolloutState {
    Bank active{Bank::A};
    bool trial_pending{false};
    std::uint8_t boot_failures{0};
    std::uint8_t seq{0};
    std::uint32_t campaign_id{0};
    std::array<std::uint32_t, 2> length{};
    std::array<std::uint32_t, 2> crc{};

    [[nodiscard]] constexpr std::uint32_t& length_of(Bank b) noexcept {
        return length[std::to_underlying(b)];
    }
    [[nodiscard]] constexpr std::uint32_t length_of(Bank b) const noexcept {
        return length[std::to_underlying(b)];
    }
    [[nodiscard]] constexpr std::uint32_t& crc_of(Bank b) noexcept {
        return crc[std::to_underlying(b)];
    }
    [[nodiscard]] constexpr std::uint32_t crc_of(Bank b) const noexcept {
        return crc[std::to_underlying(b)];
    }
};

class StateStore {
public:
    // Backup-регістри → журнал NVRAM → типовий стан першого старту з конвеєра.
    [[nodiscard]] RolloutState load() const;

    // Номер версії запису підвищується всередині: викликач передає свій стан.
    std::expected<void, StorageError> save(RolloutState& st);
};

// RAII замість пари unlock/lock у кожній гілці виходу.
class FlashGuard {
public:
    FlashGuard() noexcept;
    ~FlashGuard();
    FlashGuard(const FlashGuard&) = delete;
    FlashGuard& operator=(const FlashGuard&) = delete;

    [[nodiscard]] bool unlocked() const noexcept { return unlocked_; }

private:
    bool unlocked_;
};

class BankWriter {
public:
    explicit BankWriter(Bank bank) noexcept : bank_(bank) {}

    std::expected<void, StorageError> erase();

    // Запис іде з RAM: у багатьох сімействах запис у Flash блокує вибірку
    // інструкцій з усієї Flash, і переривання, що виконується звідти, вішає
    // ядро на шині.
    std::expected<void, StorageError> write(std::uint32_t offset, std::span<const std::byte> data);

private:
    Bank bank_;
};

[[nodiscard]] std::uint32_t crc32(std::span<const std::byte> data, std::uint32_t seed = 0) noexcept;
[[nodiscard]] std::span<const std::byte> bank_view(Bank bank, std::uint32_t len);
[[nodiscard]] std::uint32_t bank_crc(Bank bank, std::uint32_t len);

} // namespace fleet

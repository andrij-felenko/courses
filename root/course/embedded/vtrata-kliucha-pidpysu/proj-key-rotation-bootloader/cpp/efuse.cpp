#include "efuse.hpp"

#include <bit>

namespace boot {
namespace {

// ------------------------------------------------------------------
//  Порт під наш SoC: карта регістрів контролера перемичок і PMU.
// ------------------------------------------------------------------

struct EfuseRegisters {
    volatile std::uint32_t ctrl;
    volatile std::uint32_t addr;
    volatile std::uint32_t wdata;
    volatile std::uint32_t rdata;
    volatile std::uint32_t status;
    volatile std::uint32_t timing;
};

struct PmuRegisters {
    volatile std::uint32_t status;
    volatile std::uint32_t bodControl;
};

inline auto* efuseRegs() noexcept
{
    return reinterpret_cast<EfuseRegisters*>(0x4008C000UL);
}

inline auto* pmuRegs() noexcept
{
    return reinterpret_cast<PmuRegisters*>(0x40007000UL);
}

inline constexpr std::uint32_t kCtrlReadEnable = 1U << 0;
inline constexpr std::uint32_t kCtrlProgramEnable = 1U << 1;
inline constexpr std::uint32_t kCtrlPumpEnable = 1U << 2;   // генератор підкачування
inline constexpr std::uint32_t kCtrlMarginRead = 1U << 3;   // граничний опорний струм

inline constexpr std::uint32_t kStatusBusy = 1U << 0;
inline constexpr std::uint32_t kStatusProgramError = 1U << 1;
inline constexpr std::uint32_t kStatusPumpReady = 1U << 2;

inline constexpr std::uint32_t kPowerGood = 1U << 0;
inline constexpr std::uint32_t kBodArmed = 1U << 1;

inline constexpr std::uint32_t kRowRevoke = 0x20;
inline constexpr std::uint32_t kRowCounter = 0x21;

[[nodiscard]] constexpr std::uint32_t rowOfDigest(std::uint8_t slot) noexcept
{
    return 0x40U + static_cast<std::uint32_t>(slot) * 8U; // 8 рядків по 4 байти
}

inline constexpr std::uint32_t kPulseCycles = 1152;   // ~12 мкс на 96 МГц
inline constexpr std::uint32_t kBusyTimeout = 200000;
inline constexpr std::uint32_t kPumpTimeout = 50000;

[[nodiscard]] bool powerIsGood() noexcept
{
    // Детектор просідання мусить бути зведений: вимкнений BOD не скаже нам
    // про провал напруги посеред імпульсу, а саме звідти беруться комірки
    // у проміжному стані.
    const std::uint32_t status = pmuRegs()->status;
    return (status & kPowerGood) != 0 && (status & kBodArmed) != 0;
}

[[nodiscard]] std::expected<void, Status> waitNotBusy() noexcept
{
    for (std::uint32_t spins = 0; spins < kBusyTimeout; ++spins) {
        if ((efuseRegs()->status & kStatusBusy) == 0) {
            return {};
        }
    }
    return std::unexpected(Status::EfuseTimeout);
}

// Напруга програмування живе рівно стільки, скільки живе цей об'єкт.
// У C-версії те саме роблять мітка `cleanup:` і goto; тут накачку гарантовано
// знімає деструктор — на будь-якому виході, включно з раннім return.
class ProgrammingPulse {
public:
    ProgrammingPulse() noexcept { efuseRegs()->ctrl = kCtrlPumpEnable; }

    ~ProgrammingPulse() noexcept { efuseRegs()->ctrl = 0; }

    ProgrammingPulse(const ProgrammingPulse&) = delete;
    ProgrammingPulse& operator=(const ProgrammingPulse&) = delete;

    [[nodiscard]] bool waitPumpReady() const noexcept
    {
        for (std::uint32_t spins = 0; spins < kPumpTimeout; ++spins) {
            if ((efuseRegs()->status & kStatusPumpReady) != 0) {
                return true;
            }
        }
        return false;
    }

    void strike(std::uint32_t row, std::uint32_t mask) const noexcept
    {
        efuseRegs()->addr = row;
        efuseRegs()->wdata = mask;
        efuseRegs()->timing = kPulseCycles;
        efuseRegs()->ctrl = kCtrlPumpEnable | kCtrlProgramEnable;
    }
};

[[nodiscard]] std::expected<std::uint32_t, Status> readRow(std::uint32_t row,
                                                           std::uint32_t mode = 0) noexcept
{
    if (auto ready = waitNotBusy(); !ready) {
        return std::unexpected(ready.error());
    }

    efuseRegs()->addr = row;
    efuseRegs()->ctrl = kCtrlReadEnable | mode;

    const auto done = waitNotBusy();
    efuseRegs()->ctrl = 0;
    if (!done) {
        return std::unexpected(done.error());
    }

    return efuseRegs()->rdata;
}

[[nodiscard]] std::expected<void, Status> burnBits(std::uint32_t row,
                                                   std::uint32_t mask) noexcept
{
    if (mask == 0) {
        return {};
    }
    if (!powerIsGood()) {
        return std::unexpected(Status::EfuseBrownout);
    }
    if (auto ready = waitNotBusy(); !ready) {
        return std::unexpected(ready.error());
    }

    {
        const ProgrammingPulse pulse;
        if (!pulse.waitPumpReady()) {
            return std::unexpected(Status::EfuseTimeout);
        }

        pulse.strike(row, mask);

        if (auto done = waitNotBusy(); !done) {
            return std::unexpected(done.error());
        }
        if ((efuseRegs()->status & kStatusProgramError) != 0) {
            return std::unexpected(Status::EfuseMarginal);
        }
    } // тут накачку знято

    // Просідання ПІД ЧАС імпульсу лишає слід у детекторі: комірка могла
    // застигнути в метастабільному стані, і мовчати про це не можна.
    if (!powerIsGood()) {
        return std::unexpected(Status::EfuseBrownout);
    }

    // Контрольне зчитування: спершу на номінальному опорному струмі...
    const auto nominal = readRow(row);
    if (!nominal) {
        return std::unexpected(nominal.error());
    }
    if ((*nominal & mask) != mask) {
        return std::unexpected(Status::EfuseMarginal);
    }

    // ...потім на граничному. Напівспалена перемичка проходить перше читання
    // й провалює друге — саме ця пара відрізняє надійну комірку від хиткої.
    const auto marginal = readRow(row, kCtrlMarginRead);
    if (!marginal) {
        return std::unexpected(marginal.error());
    }
    if ((*marginal & mask) != mask) {
        return std::unexpected(Status::EfuseMarginal);
    }

    return {};
}

} // namespace

std::expected<EfuseMirror, Status> Efuse::readMirror() noexcept
{
    EfuseMirror mirror;

    const auto revoke = readRow(kRowRevoke);
    if (!revoke) {
        return std::unexpected(revoke.error());
    }
    mirror.revocationMask = static_cast<std::uint8_t>(*revoke & 0x0FU);

    const auto counter = readRow(kRowCounter);
    if (!counter) {
        return std::unexpected(counter.error());
    }
    // Термометр рахуємо popcount-ом: перемичку можна лише спалити, тож
    // монотонність лічильника тримає фізика, а не логіка прошивки.
    mirror.monotonicCounter = static_cast<std::uint32_t>(std::popcount(*counter));

    for (std::uint8_t slot = 0; slot < kKeySlots; ++slot) {
        for (std::uint32_t word = 0; word < kDigestSize / 4; ++word) {
            const auto value = readRow(rowOfDigest(slot) + word);
            if (!value) {
                return std::unexpected(value.error());
            }
            auto& digest = mirror.rootKeyDigest[slot];
            digest[word * 4 + 0] = static_cast<std::uint8_t>(*value);
            digest[word * 4 + 1] = static_cast<std::uint8_t>(*value >> 8);
            digest[word * 4 + 2] = static_cast<std::uint8_t>(*value >> 16);
            digest[word * 4 + 3] = static_cast<std::uint8_t>(*value >> 24);
        }
    }

    return mirror;
}

std::expected<void, Status> Efuse::burnRevocation(std::uint8_t slot) noexcept
{
    if (slot >= kKeySlots) {
        return std::unexpected(Status::InvalidSlot);
    }

    const auto current = readRow(kRowRevoke);
    if (!current) {
        return std::unexpected(current.error());
    }

    const std::uint32_t bit = 1U << slot;
    if ((*current & bit) != 0) {
        return {}; // уже відкликано — операція ідемпотентна
    }

    return burnBits(kRowRevoke, bit);
}

std::expected<void, Status> Efuse::burnCounter(std::uint32_t version) noexcept
{
    if (version > kCounterBits) {
        return std::unexpected(Status::EfuseRange);
    }

    const auto current = readRow(kRowCounter);
    if (!current) {
        return std::unexpected(current.error());
    }

    const auto burnt = static_cast<std::uint32_t>(std::popcount(*current));
    if (version <= burnt) {
        return {};
    }

    // По одному біту: обрив живлення посеред серії лишить лічильник на
    // досягнутому значенні, а не зіпсує пів рядка одним широким імпульсом.
    for (std::uint32_t bit = burnt; bit < version; ++bit) {
        if (auto burned = burnBits(kRowCounter, 1U << bit); !burned) {
            return burned;
        }
    }

    return {};
}

} // namespace boot

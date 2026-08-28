// silicon_quirks.hpp / silicon_quirks.cpp - Ідіоматична реалізація мовою C++20
#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <optional>

namespace hardware {

enum class SiliconRev : uint16_t {
    Unknown = 0x0000,
    A0      = 0x1000,
    A1      = 0x1001,
    B0      = 0x2000,
    B1      = 0x2001,
};

enum class Quirk : uint32_t {
    None                = 0,
    I2cStopLock         = (1U << 0),
    UartFifoCorrupt     = (1U << 1),
    TimerExtTrigger     = (1U << 2),
    AdcOffsetDrift      = (1U << 3),
};

constexpr Quirk operator|(Quirk a, Quirk b) noexcept {
    return static_cast<Quirk>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr Quirk operator&(Quirk a, Quirk b) noexcept {
    return static_cast<Quirk>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

constexpr bool has_flag(Quirk mask, Quirk flag) noexcept {
    return (mask & flag) != Quirk::None;
}

struct RevisionMetadata {
    SiliconRev revision;
    std::string_view name;
    Quirk quirks;
};

class SiliconManager {
public:
    static constexpr uintptr_t DbgMcuIdCodeAddr = 0xE0042000UL;
    static constexpr uint32_t DevIdMask         = 0x00000FFFUL;
    static constexpr uint32_t RevIdShift        = 16U;
    static constexpr uint32_t RevIdMask         = 0xFFFF0000UL;

    constexpr SiliconManager() noexcept = default;

    void initialize() noexcept {
        const uint32_t raw_id = read_hardware_register();
        dev_id_ = static_cast<uint16_t>(raw_id & DevIdMask);
        rev_id_ = static_cast<SiliconRev>((raw_id & RevIdMask) >> RevIdShift);

        const auto entry = find_metadata(rev_id_);
        if (entry) {
            active_quirks_ = entry->quirks;
            rev_name_ = entry->name;
        } else {
            active_quirks_ = Quirk::None;
            rev_name_ = "Unknown Silicon Revision";
        }
    }

    [[nodiscard]] bool has_quirk(Quirk quirk) const noexcept {
        return has_flag(active_quirks_, quirk);
    }

    [[nodiscard]] SiliconRev revision() const noexcept { return rev_id_; }
    [[nodiscard]] uint16_t device_id() const noexcept { return dev_id_; }
    [[nodiscard]] std::string_view revision_name() const noexcept { return rev_name_; }

private:
    uint16_t dev_id_{0};
    SiliconRev rev_id_{SiliconRev::Unknown};
    std::string_view rev_name_{"Uninitialized"};
    Quirk active_quirks_{Quirk::None};

    static constexpr std::array<RevisionMetadata, 4> KnownRevisions{{
        {SiliconRev::A0, "Rev A0 (Initial Silicon)",
         Quirk::I2cStopLock | Quirk::UartFifoCorrupt | Quirk::TimerExtTrigger},
        {SiliconRev::A1, "Rev A1 (Metal ECO Fix)",
         Quirk::UartFifoCorrupt | Quirk::TimerExtTrigger},
        {SiliconRev::B0, "Rev B0 (Base Layer Fix)", Quirk::None},
        {SiliconRev::B1, "Rev B1 (Production Optimized)", Quirk::None}
    }};

    static constexpr std::optional<RevisionMetadata> find_metadata(SiliconRev rev) noexcept {
        for (const auto& item : KnownRevisions) {
            if (item.revision == rev) {
                return item;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] static uint32_t read_hardware_register() noexcept {
        // Емуляція читання регістра DBGMCU_IDCODE
        return (0x1000U << RevIdShift) | 0x413U;
    }
};

// Приклад використання в класі драйвера
class I2cMasterDriver {
public:
    explicit I2cMasterDriver(const SiliconManager& silicon) noexcept
        : silicon_(silicon) {}

    void send_stop(volatile uint32_t& cr2_reg) noexcept {
        if (silicon_.has_quirk(Quirk::I2cStopLock)) {
            // Застосування апаратного обходу для дефектних ревізій
            cr2_reg |= (1U << 14);
            const volatile uint32_t dummy = cr2_reg;
            static_cast<void>(dummy);
        }
        cr2_reg |= (1U << 9); // Штатна генерація STOP
    }

private:
    const SiliconManager& silicon_;
};

} // namespace hardware

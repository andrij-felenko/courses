#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <format>
#include <span>
#include <iostream>

namespace avr::tool {

enum class ClockSource : std::uint8_t {
    ExternalClock      = 0x00,
    InternalRc8MHz     = 0x02,
    Internal128kHz     = 0x04,
    ExternalCrystalLow = 0x08,
    ExternalCrystalMed = 0x0A,
    ExternalCrystalHigh= 0x0F
};

enum class StartupTime : std::uint8_t {
    FastRisingPower = 0x00,
    StandardDelay   = 0x01,
    SlowRisingPower = 0x02,
    MaxDelayCeramic = 0x03
};

enum class BodLevel : std::uint8_t {
    Disabled = 0x07,
    V1_8     = 0x06,
    V2_7     = 0x05,
    V4_3     = 0x04
};

enum class BootSize : std::uint8_t {
    Words256  = 0x03, // 512B
    Words512  = 0x02, // 1KB
    Words1024 = 0x01, // 2KB
    Words2048 = 0x00  // 4KB
};

enum class LockMode : std::uint8_t {
    Mode1Open     = 0x03,
    Mode2NoProg   = 0x02,
    Mode3FullLock = 0x00
};

enum class DiagSeverity {
    Info,
    Warning,
    CriticalError
};

struct DiagMessage {
    DiagSeverity severity;
    std::string text;
};

struct FuseBytes {
    std::uint8_t low{0x62};
    std::uint8_t high{0xD9};
    std::uint8_t extended{0xFF};
    std::uint8_t lock{0xFF};

    [[nodiscard]] constexpr bool operator==(const FuseBytes&) const noexcept = default;
};

class FuseBuilder {
private:
    ClockSource  clock_{ClockSource::InternalRc8MHz};
    StartupTime  sut_{StartupTime::MaxDelayCeramic};
    bool         clkout_{false};
    bool         ckdiv8_{true};

    bool         rstdisbl_{false};
    bool         dwen_{false};
    bool         spien_{true};
    bool         wdton_{false};
    bool         eesave_{false};
    BootSize     bootsz_{BootSize::Words2048};
    bool         bootrst_{false};

    BodLevel     bod_{BodLevel::Disabled};
    LockMode     lock_{LockMode::Mode1Open};
    std::uint8_t blb0_{0x03};
    std::uint8_t blb1_{0x03};

public:
    constexpr FuseBuilder() noexcept = default;

    constexpr FuseBuilder& set_clock(ClockSource clk, StartupTime sut, bool div8 = false) noexcept {
        clock_ = clk;
        sut_ = sut;
        ckdiv8_ = div8;
        return *this;
    }

    constexpr FuseBuilder& enable_clock_output(bool enable) noexcept {
        clkout_ = enable;
        return *this;
    }

    constexpr FuseBuilder& set_reset_as_gpio(bool disable_reset) noexcept {
        rstdisbl_ = disable_reset;
        return *this;
    }

    constexpr FuseBuilder& set_debugwire(bool enable) noexcept {
        dwen_ = enable;
        return *this;
    }

    constexpr FuseBuilder& set_isp_enabled(bool enable) noexcept {
        spien_ = enable;
        return *this;
    }

    constexpr FuseBuilder& set_preserve_eeprom(bool preserve) noexcept {
        eesave_ = preserve;
        return *this;
    }

    constexpr FuseBuilder& set_bootloader(BootSize size, bool enable_vector) noexcept {
        bootsz_ = size;
        bootrst_ = enable_vector;
        return *this;
    }

    constexpr FuseBuilder& set_bod(BodLevel level) noexcept {
        bod_ = level;
        return *this;
    }

    constexpr FuseBuilder& set_lock_mode(LockMode mode) noexcept {
        lock_ = mode;
        return *this;
    }

    [[nodiscard]] constexpr FuseBytes build() const noexcept {
        FuseBytes res;

        // Low
        res.low = (ckdiv8_ ? 0x00U : 0x80U) |
                  (clkout_ ? 0x00U : 0x40U) |
                  (static_cast<std::uint8_t>(sut_) << 4) |
                  (static_cast<std::uint8_t>(clock_) & 0x0FU);

        // High
        res.high = (rstdisbl_ ? 0x00U : 0x80U) |
                   (dwen_ ? 0x00U : 0x40U) |
                   (spien_ ? 0x00U : 0x20U) |
                   (wdton_ ? 0x00U : 0x10U) |
                   (eesave_ ? 0x00U : 0x08U) |
                   (static_cast<std::uint8_t>(bootsz_) << 1) |
                   (bootrst_ ? 0x00U : 0x01U);

        // Extended
        res.extended = 0xF8U | (static_cast<std::uint8_t>(bod_) & 0x07U);

        // Lock
        res.lock = 0xC0U |
                   ((blb1_ & 0x03U) << 4) |
                   ((blb0_ & 0x03U) << 2) |
                   static_cast<std::uint8_t>(lock_);

        return res;
    }
};

class FuseValidator {
public:
    [[nodiscard]] static std::expected<std::vector<DiagMessage>, std::string>
    validate(const FuseBytes& bytes, bool allow_hvpp = false) {
        std::vector<DiagMessage> diag;

        // Перевірка 1: RSTDISBL
        if ((bytes.high & 0x80U) == 0) {
            if (!allow_hvpp) {
                return std::unexpected("КРИТИЧНО: RSTDISBL активний без прапорця HVPP. Блокування скидання!");
            }
            diag.push_back({DiagSeverity::Warning, "RSTDISBL увімкнено під захистом HVPP прапорця."});
        }

        // Перевірка 2: SPIEN
        if ((bytes.high & 0x20U) != 0) {
            return std::unexpected("ФАТАЛЬНО: SPIEN стерто в 1. Послідовний ISP інтерфейс вимкнено.");
        }

        // Перевірка 3: DWEN
        if ((bytes.high & 0x40U) == 0) {
            diag.push_back({DiagSeverity::Warning, "debugWIRE активний (DWEN=0). ISP доступ заблоковано до зупинки DW."});
        }

        // Перевірка 4: BOD vs Clock
        const auto cksel = bytes.low & 0x0FU;
        const auto bod   = bytes.extended & 0x07U;
        if (cksel >= 0x08U && bod == static_cast<std::uint8_t>(BodLevel::Disabled)) {
            diag.push_back({DiagSeverity::Warning, "Високочастотний кварц без детектора BOD несе ризик псування пам'яті."});
        }

        return diag;
    }

    [[nodiscard]] static std::string to_avrdude_args(const FuseBytes& bytes, std::string_view chip = "m328p") {
        return std::format("avrdude -c usbasp -p {} -U lfuse:w:0x{:02X}:m -U hfuse:w:0x{:02X}:m -U efuse:w:0x{:02X}:m -U lock:w:0x{:02X}:m",
                           chip, bytes.low, bytes.high, bytes.extended, bytes.lock);
    }
};

} // namespace avr::tool

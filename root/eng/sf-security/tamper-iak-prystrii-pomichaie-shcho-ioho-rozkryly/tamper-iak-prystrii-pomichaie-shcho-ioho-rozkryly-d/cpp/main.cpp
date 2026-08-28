#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

namespace hardware_security {

enum class InitError {
    ZeroSeedNotAllowed,
    HardwareFault
};

class TamperManager {
private:
    static constexpr std::uintptr_t TAMP_BASE = 0x40002800U;

    static volatile std::uint32_t& reg(std::uintptr_t offset) noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(TAMP_BASE + offset);
    }

    static constexpr std::uint32_t CR1_TAMP1E    = (1U << 0);
    static constexpr std::uint32_t CR1_ITAMP1E   = (1U << 16);
    static constexpr std::uint32_t ATCR1_TAMP1AM = (1U << 0);
    static constexpr std::uint32_t IER_TAMP1IE   = (1U << 0);
    static constexpr std::uint32_t SR_TAMP1F     = (1U << 0);
    static constexpr std::uint32_t SCR_CTAMP1F   = (1U << 0);

    static void secure_erase(std::span<volatile std::uint8_t> mem) noexcept {
        for (auto& byte : mem) {
            byte = 0x00U;
        }
    }

public:
    TamperManager() = delete;

    [[nodiscard]] static std::expected<void, InitError> configure(std::uint32_t lfsr_seed) noexcept {
        if (lfsr_seed == 0U) {
            return std::unexpected(InitError::ZeroSeedNotAllowed);
        }

        // 1. Завантаження зерна генератора активної сітки
        reg(0x24U) = lfsr_seed;

        // 2. Увімкнення режиму активного сканування
        reg(0x20U) |= ATCR1_TAMP1AM;

        // 3. Активація переривань та сенсорів (зовнішня сітка + термомонітор)
        reg(0x2CU) |= IER_TAMP1IE;
        reg(0x00U) |= (CR1_TAMP1E | CR1_ITAMP1E);

        return {};
    }

    static void handle_breach() noexcept {
        if (reg(0x30U) & SR_TAMP1F) {
            // Апаратна зероїзація BKP SRAM виконана шиною за 15 наносекунд
            // Додатково очищуємо буфери оперативної пам'яті
            extern std::uint8_t _sdata, _edata, _sbss, _ebss;
            secure_erase(std::span<volatile std::uint8_t>{
                reinterpret_cast<volatile std::uint8_t*>(&_sdata),
                static_cast<std::size_t>(&_edata - &_sdata)
            });
            secure_erase(std::span<volatile std::uint8_t>{
                reinterpret_cast<volatile std::uint8_t*>(&_sbss),
                static_cast<std::size_t>(&_ebss - &_sbss)
            });

            // Підтвердження події в журналі
            reg(0x3CU) = SCR_CTAMP1F;

            // Вічне блокування криптомодуля
            while (true) {
                asm volatile("nop");
            }
        }
    }
};

} // namespace hardware_security

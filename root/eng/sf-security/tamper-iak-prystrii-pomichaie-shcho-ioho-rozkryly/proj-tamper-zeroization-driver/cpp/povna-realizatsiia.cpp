#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace security {

enum class TamperError {
    InvalidSeed,
    AccessDenied,
    KeyTooLarge
};

class TamperController {
private:
    static constexpr std::uintptr_t TAMP_BASE = 0x40002800U;
    static constexpr std::uintptr_t BKP_BASE  = 0x40002850U;
    static constexpr std::uintptr_t PWR_BASE  = 0x40007000U;

    static constexpr std::uint32_t TAMP_CR1_TAMP1E   = (1U << 0);
    static constexpr std::uint32_t TAMP_CR1_ITAMP1E  = (1U << 16);
    static constexpr std::uint32_t TAMP_ATCR1_TAMP1AM= (1U << 0);
    static constexpr std::uint32_t TAMP_ATCR1_ATOSEL = (1U << 8);
    static constexpr std::uint32_t TAMP_IER_TAMP1IE  = (1U << 0);
    static constexpr std::uint32_t TAMP_SR_TAMP1F    = (1U << 0);
    static constexpr std::uint32_t TAMP_SCR_CTAMP1F  = (1U << 0);
    static constexpr std::uint32_t PWR_CR1_DBP       = (1U << 8);

    static constexpr std::size_t MAX_BKP_REGS = 32;

    static volatile std::uint32_t& reg(std::uintptr_t addr) noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(addr);
    }

    static void secure_clear(std::span<volatile std::uint8_t> buffer) noexcept {
        for (auto& byte : buffer) {
            byte = 0U;
        }
    }

public:
    TamperController() = default;

    [[nodiscard]] std::expected<void, TamperError> initialize(std::uint32_t lfsr_seed) noexcept {
        if (lfsr_seed == 0U) {
            return std::unexpected(TamperError::InvalidSeed);
        }

        // 1. Дозвіл доступу до резервного домену
        reg(PWR_BASE + 0x00U) |= PWR_CR1_DBP;

        // 2. Зняття апаратного захисту конфігурації
        reg(TAMP_BASE + 0x10U) = 0xCAU;
        reg(TAMP_BASE + 0x10U) = 0x53U;

        // 3. Ініціалізація псевдовипадкового генератора активної сітки
        reg(TAMP_BASE + 0x24U) = lfsr_seed;

        // 4. Налаштування цифрового фільтра та часу попереднього заряду
        reg(TAMP_BASE + 0x0CU) = (0x02U << 0) | (0x01U << 3);
        reg(TAMP_BASE + 0x20U) = TAMP_ATCR1_TAMP1AM | TAMP_ATCR1_ATOSEL;

        // 5. Активація переривань та моніторингу сітки й температури
        reg(TAMP_BASE + 0x2CU) |= TAMP_IER_TAMP1IE;
        reg(TAMP_BASE + 0x00U) |= (TAMP_CR1_TAMP1E | TAMP_CR1_ITAMP1E);

        return {};
    }

    [[nodiscard]] std::expected<void, TamperError> write_master_key(std::span<const std::uint8_t> key) noexcept {
        if (key.size() > MAX_BKP_REGS * sizeof(std::uint32_t)) {
            return std::unexpected(TamperError::KeyTooLarge);
        }

        const auto* words = reinterpret_cast<const std::uint32_t*>(key.data());
        const std::size_t word_count = (key.size() + sizeof(std::uint32_t) - 1) / sizeof(std::uint32_t);

        for (std::size_t i = 0; i < word_count; ++i) {
            reg(BKP_BASE + (i * sizeof(std::uint32_t))) = words[i];
        }

        return {};
    }

    static void handle_tamper_event() noexcept {
        if (reg(TAMP_BASE + 0x30U) & TAMP_SR_TAMP1F) {
            // Апаратна зероїзація BKP регістрів виконана апаратно шиною Zeroize!
            // Додатково стираємо оперативну пам'ять
            extern std::uint8_t _sdata, _edata, _sbss, _ebss;
            secure_clear(std::span<volatile std::uint8_t>{
                reinterpret_cast<volatile std::uint8_t*>(&_sdata),
                static_cast<std::size_t>(&_edata - &_sdata)
            });
            secure_clear(std::span<volatile std::uint8_t>{
                reinterpret_cast<volatile std::uint8_t*>(&_sbss),
                static_cast<std::size_t>(&_ebss - &_sbss)
            });

            // Фіксація події
            reg(TAMP_BASE + 0x3CU) = TAMP_SCR_CTAMP1F;

            // Вічне блокування системи
            while (true) {
                asm volatile("nop");
            }
        }
    }
};

} // namespace security

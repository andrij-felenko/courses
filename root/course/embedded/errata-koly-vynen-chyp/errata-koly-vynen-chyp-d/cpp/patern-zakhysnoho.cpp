#include <cstdint>
#include <concepts>
#include <expected>

namespace embedded::driver {

enum class Error : uint8_t {
    Timeout,
    BusBusyLockup,
    HardwareFault
};

template <typename RegType>
class DefensiveRegisterPoll {
public:
    static constexpr uint32_t DefaultTimeoutCycles = 50'000U;

    [[nodiscard]] static std::expected<void, Error> wait_for_flag(
        const volatile RegType& reg,
        RegType mask,
        bool wait_for_set,
        uint32_t timeout = DefaultTimeoutCycles) noexcept
    {
        while (timeout > 0) {
            const bool is_set = (reg & mask) != 0U;
            if (is_set == wait_for_set) {
                return {};
            }
            --timeout;
            asm volatile("nop");
        }
        return std::unexpected(Error::Timeout);
    }
};

class DefensiveI2cMaster {
public:
    explicit DefensiveI2cMaster(I2C_TypeDef* instance) noexcept
        : i2c_(instance) {}

    [[nodiscard]] std::expected<void, Error> transmit_byte(uint8_t data) noexcept {
        /* Безпечне очікування готовності передавача */
        const auto result = DefensiveRegisterPoll<uint32_t>::wait_for_flag(
            i2c_->SR1,
            I2C_SR1_TXE,
            true
        );

        if (!result.has_value()) {
            recover_peripheral_lockup();
            return std::unexpected(result.error());
        }

        i2c_->DR = data;
        return {};
    }

private:
    I2C_TypeDef* i2c_;

    void recover_peripheral_lockup() noexcept {
        /* Апаратне перезавантаження модуля через блок скидання RCC */
        RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
        asm volatile("nop; nop; nop;");
        RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;
    }
};

} // namespace embedded::driver

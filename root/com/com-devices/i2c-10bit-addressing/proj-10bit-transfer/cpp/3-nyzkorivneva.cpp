#include "stm32f4xx_ll_i2c.h"
#include <cstdint>
#include <expected>

enum class I2cStatus : uint8_t {
    Ok = 0,
    NackHeader1,
    NackHeader2,
    Timeout
};

class Stm32Ll10BitDriver {
public:
    static std::expected<void, I2cStatus> writeByte(I2C_TypeDef* i2c, uint16_t addr10, uint8_t data) noexcept {
        LL_I2C_GenerateStartCondition(i2c);
        while (!LL_I2C_IsActiveFlag_SB(i2c)) {}

        const uint8_t header1 = static_cast<uint8_t>(0xF0 | (((addr10 >> 8) & 0x03) << 1));
        LL_I2C_TransmitData8(i2c, header1);

        while (!LL_I2C_IsActiveFlag_ADD10(i2c)) {
            if (LL_I2C_IsActiveFlag_AF(i2c)) {
                LL_I2C_ClearFlag_AF(i2c);
                LL_I2C_GenerateStopCondition(i2c);
                return std::unexpected(I2cStatus::NackHeader1);
            }
        }

        const uint8_t header2 = static_cast<uint8_t>(addr10 & 0xFF);
        LL_I2C_TransmitData8(i2c, header2);

        while (!LL_I2C_IsActiveFlag_ADDR(i2c)) {
            if (LL_I2C_IsActiveFlag_AF(i2c)) {
                LL_I2C_ClearFlag_AF(i2c);
                LL_I2C_GenerateStopCondition(i2c);
                return std::unexpected(I2cStatus::NackHeader2);
            }
        }

        LL_I2C_ClearFlag_ADDR(i2c);

        while (!LL_I2C_IsActiveFlag_TXE(i2c)) {}
        LL_I2C_TransmitData8(i2c, data);

        while (!LL_I2C_IsActiveFlag_BTF(i2c)) {}
        LL_I2C_GenerateStopCondition(i2c);

        return {};
    }
};

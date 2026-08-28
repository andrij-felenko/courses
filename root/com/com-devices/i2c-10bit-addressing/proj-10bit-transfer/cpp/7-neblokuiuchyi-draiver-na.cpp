#include "stm32f4xx_ll_i2c.h"
#include <cstdint>
#include <span>

class Stm32Async10BitDriver {
public:
    enum class State : uint8_t {
        Idle = 0,
        Header1,
        Header2,
        DataTx,
        Complete
    };

    void handleEvent(I2C_TypeDef* i2c) noexcept {
        if (LL_I2C_IsActiveFlag_SB(i2c)) {
            const uint8_t h1 = static_cast<uint8_t>(0xF0 | (((addr10_ >> 8) & 0x03) << 1));
            LL_I2C_TransmitData8(i2c, h1);
            state_ = State::Header1;
        } else if (LL_I2C_IsActiveFlag_ADD10(i2c)) {
            const uint8_t h2 = static_cast<uint8_t>(addr10_ & 0xFF);
            LL_I2C_TransmitData8(i2c, h2);
            state_ = State::Header2;
        } else if (LL_I2C_IsActiveFlag_ADDR(i2c)) {
            LL_I2C_ClearFlag_ADDR(i2c);
            state_ = State::DataTx;
        } else if (LL_I2C_IsActiveFlag_TXE(i2c) && state_ == State::DataTx) {
            if (txIndex_ < txData_.size()) {
                LL_I2C_TransmitData8(i2c, txData_[txIndex_++]);
            } else {
                LL_I2C_GenerateStopCondition(i2c);
                LL_I2C_DisableIT_EVT(i2c);
                LL_I2C_DisableIT_BUF(i2c);
                state_ = State::Complete;
            }
        }
    }

    [[nodiscard]] bool isComplete() const noexcept {
        return state_ == State::Complete;
    }

private:
    uint16_t addr10_{0};
    std::span<const uint8_t> txData_{};
    size_t txIndex_{0};
    volatile State state_{State::Idle};
};

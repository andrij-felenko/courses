#include <cstdint>
#include <chrono>
#include <expected>

enum class InitError {
    BusError,
    Timeout,
    WrongId
};

class SensorBringup {
public:
    static constexpr uint8_t RegResetCtrl = 0x06;
    static constexpr uint8_t BitSwReset = 1U << 7;
    static constexpr uint8_t RegStatus = 0x07;
    static constexpr uint8_t BitStatusReady = 1U << 0;
    static constexpr auto SwResetTimeout = std::chrono::milliseconds(50);
    static constexpr auto ResetWaitStep = std::chrono::milliseconds(2);

    std::expected<void, InitError> software_reset(uint8_t dev_addr) {
        // 1. Відправляємо команду скидання
        if (!i2c_write_reg(dev_addr, RegResetCtrl, BitSwReset)) {
            return std::unexpected(InitError::BusError);
        }

        // 2. Обов'язкова апаратна пауза на перезавантаження внутрішнього ядра
        delay_for(std::chrono::milliseconds(5));

        // 3. Цикл опитування готовності з таймаутом
        const auto start_time = std::chrono::steady_clock::now();
        while (true) {
            uint8_t reset_reg_val = 0;
            uint8_t status_val = 0;

            if (i2c_read_reg(dev_addr, RegResetCtrl, reset_reg_val) &&
                i2c_read_reg(dev_addr, RegStatus, status_val)) {
                
                const bool reset_done = (reset_reg_val & BitSwReset) == 0;
                const bool device_ready = (status_val & BitStatusReady) != 0;

                if (reset_done && device_ready) {
                    return {}; // Успіх
                }
            }

            if (std::chrono::steady_clock::now() - start_time >= SwResetTimeout) {
                return std::unexpected(InitError::Timeout);
            }

            delay_for(ResetWaitStep);
        }
    }

private:
    bool i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t val);
    bool i2c_read_reg(uint8_t addr, uint8_t reg, uint8_t &val);
    void delay_for(std::chrono::milliseconds dur);
};

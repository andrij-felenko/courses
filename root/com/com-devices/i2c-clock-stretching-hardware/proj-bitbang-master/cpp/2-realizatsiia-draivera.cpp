#include <cstdint>
#include <chrono>
#include <expected>
#include <span>
#include <concepts>

enum class I2cError {
    Nack,
    SclTimeout,
    BusBusy,
    BufferOverflow
};

// Концепт апаратного інтерфейсу керування лініями GPIO
template <typename T>
concept I2cGpioHal = requires(T hal) {
    { hal.set_scl_low() } -> std::same_as<void>;
    { hal.set_scl_high_z() } -> std::same_as<void>;
    { hal.read_scl() } -> std::same_as<bool>;
    { hal.set_sda_low() } -> std::same_as<void>;
    { hal.set_sda_high_z() } -> std::same_as<void>;
    { hal.read_sda() } -> std::same_as<bool>;
    { hal.delay_half_period() } -> std::same_as<void>;
    { hal.current_time_us() } -> std::same_as<uint32_t>;
};

template <I2cGpioHal Hal>
class I2cBitBangMaster {
public:
    explicit I2cBitBangMaster(Hal hal, uint32_t stretch_timeout_us = 25000)
        : hal_(hal), stretch_timeout_us_(stretch_timeout_us) {}

    std::expected<void, I2cError> start() {
        hal_.set_sda_high_z();
        if (auto res = wait_scl_high(); !res) return res;
        hal_.delay_half_period();

        if (!hal_.read_sda()) {
            return std::unexpected(I2cError::BusBusy);
        }

        hal_.set_sda_low();
        hal_.delay_half_period();
        hal_.set_scl_low();
        hal_.delay_half_period();
        return {};
    }

    std::expected<void, I2cError> stop() {
        hal_.set_sda_low();
        hal_.delay_half_period();
        if (auto res = wait_scl_high(); !res) return res;
        hal_.delay_half_period();

        hal_.set_sda_high_z();
        hal_.delay_half_period();
        return {};
    }

    std::expected<void, I2cError> write_byte(uint8_t byte) {
        for (uint8_t i = 0; i < 8; ++i) {
            if (byte & 0x80) {
                hal_.set_sda_high_z();
            } else {
                hal_.set_sda_low();
            }
            byte <<= 1;
            hal_.delay_half_period();

            if (auto res = wait_scl_high(); !res) return res;
            hal_.delay_half_period();
            hal_.set_scl_low();
        }

        hal_.set_sda_high_z();
        hal_.delay_half_period();
        if (auto res = wait_scl_high(); !res) return res;

        bool nack = hal_.read_sda();
        hal_.delay_half_period();
        hal_.set_scl_low();
        hal_.delay_half_period();

        if (nack) return std::unexpected(I2cError::Nack);
        return {};
    }

    std::expected<uint8_t, I2cError> read_byte(bool send_ack) {
        uint8_t received = 0;
        hal_.set_sda_high_z();

        for (uint8_t i = 0; i < 8; ++i) {
            received <<= 1;
            hal_.delay_half_period();

            if (auto res = wait_scl_high(); !res) return res;
            if (hal_.read_sda()) {
                received |= 0x01;
            }
            hal_.delay_half_period();
            hal_.set_scl_low();
        }

        if (send_ack) {
            hal_.set_sda_low();
        } else {
            hal_.set_sda_high_z();
        }
        hal_.delay_half_period();

        if (auto res = wait_scl_high(); !res) return res;
        hal_.delay_half_period();
        hal_.set_scl_low();
        hal_.set_sda_high_z();
        hal_.delay_half_period();

        return received;
    }

    std::expected<void, I2cError> write(uint8_t address, std::span<const uint8_t> data) {
        auto res = start();
        if (!res) return res;

        res = write_byte(static_cast<uint8_t>(address << 1));
        if (!res) {
            stop();
            return res;
        }

        for (uint8_t b : data) {
            res = write_byte(b);
            if (!res) {
                stop();
                return res;
            }
        }
        return stop();
    }

    std::expected<void, I2cError> read(uint8_t address, std::span<uint8_t> buffer) {
        auto res = start();
        if (!res) return res;

        res = write_byte(static_cast<uint8_t>((address << 1) | 0x01));
        if (!res) {
            stop();
            return res;
        }

        for (size_t i = 0; i < buffer.size(); ++i) {
            bool send_ack = (i + 1 < buffer.size());
            auto byte_res = read_byte(send_ack);
            if (!byte_res) {
                stop();
                return std::unexpected(byte_res.error());
            }
            buffer[i] = *byte_res;
        }
        return stop();
    }

    void recover_bus() {
        hal_.set_sda_high_z();
        hal_.set_scl_high_z();
        hal_.delay_half_period();

        for (uint8_t i = 0; i < 9; ++i) {
            if (hal_.read_sda()) break;
            hal_.set_scl_low();
            hal_.delay_half_period();
            hal_.set_scl_high_z();
            hal_.delay_half_period();
        }

        hal_.set_sda_low();
        hal_.delay_half_period();
        hal_.set_scl_high_z();
        hal_.delay_half_period();
        hal_.set_sda_high_z();
        hal_.delay_half_period();
    }

private:
    std::expected<void, I2cError> wait_scl_high() {
        hal_.set_scl_high_z();
        uint32_t start_time = hal_.current_time_us();

        while (!hal_.read_scl()) {
            if ((hal_.current_time_us() - start_time) >= stretch_timeout_us_) {
                return std::unexpected(I2cError::SclTimeout);
            }
        }
        return {};
    }

    Hal hal_;
    uint32_t stretch_timeout_us_;
};

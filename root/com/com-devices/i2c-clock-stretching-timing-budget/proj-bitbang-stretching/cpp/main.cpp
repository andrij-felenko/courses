#include <cstdint>
#include <chrono>
#include <expected>
#include <span>
#include <concepts>

enum class I2cError : int8_t {
    Timeout = -1,
    NackAddress = -2,
    NackData = -3,
    BusBusy = -4
};

/* Концепт для низькорівневого апаратного адаптера виводів GPIO */
template <typename T>
concept I2cHalPinAdapter = requires(T hal, uint32_t us) {
    { hal.scl_drive_low() } -> std::same_as<void>;
    { hal.scl_release() }   -> std::same_as<void>;
    { hal.scl_read() }      -> std::same_as<bool>;
    { hal.sda_drive_low() } -> std::same_as<void>;
    { hal.sda_release() }   -> std::same_as<void>;
    { hal.sda_read() }      -> std::same_as<bool>;
    { hal.delay_us(us) }    -> std::same_as<void>;
};

template <I2cHalPinAdapter Hal>
class BitbangI2cMaster {
public:
    explicit constexpr BitbangI2cMaster(Hal& hal, uint32_t half_period_us = 5, 
                                        uint32_t timeout_us = 35000) noexcept
        : hal_(hal), half_period_us_(half_period_us), timeout_us_(timeout_us) {}

    /* Запис послідовності байтів у ведений пристрій */
    std::expected<void, I2cError> write(uint8_t addr_7bit, std::span<const uint8_t> data) noexcept {
        auto res = start();
        if (!res) return res;

        /* Байт адреси з бітом запису (R/W = 0) */
        uint8_t addr_byte = static_cast<uint8_t>(addr_7bit << 1);
        bool ack = false;
        if (auto w_res = write_byte(addr_byte, ack); !w_res) {
            stop();
            return w_res;
        }
        if (!ack) {
            stop();
            return std::unexpected(I2cError::NackAddress);
        }

        for (const uint8_t byte : data) {
            if (auto w_res = write_byte(byte, ack); !w_res) {
                stop();
                return w_res;
            }
            if (!ack) {
                stop();
                return std::unexpected(I2cError::NackData);
            }
        }

        return stop();
    }

    /* Зчитування послідовності байтів із веденого пристрою */
    std::expected<void, I2cError> read(uint8_t addr_7bit, std::span<uint8_t> buffer) noexcept {
        auto res = start();
        if (!res) return res;

        /* Байт адреси з бітом читання (R/W = 1) */
        uint8_t addr_byte = static_cast<uint8_t>((addr_7bit << 1) | 0x01);
        bool ack = false;
        if (auto w_res = write_byte(addr_byte, ack); !w_res) {
            stop();
            return w_res;
        }
        if (!ack) {
            stop();
            return std::unexpected(I2cError::NackAddress);
        }

        const size_t len = buffer.size();
        for (size_t i = 0; i < len; ++i) {
            bool send_ack = (i + 1 < len); /* Для останнього байта шлемо NACK */
            if (auto r_res = read_byte(buffer[i], send_ack); !r_res) {
                stop();
                return r_res;
            }
        }

        return stop();
    }

    /* Процедура 9-тактового аварійного розблокування завислої шини */
    void recover_bus() noexcept {
        hal_.sda_release();
        hal_.scl_release();
        hal_.delay_us(half_period_us_);

        for (uint8_t i = 0; i < 9; ++i) {
            if (hal_.sda_read()) break;
            hal_.scl_drive_low();
            hal_.delay_us(half_period_us_);
            hal_.scl_release();
            hal_.delay_us(half_period_us_);
        }
        stop();
    }

private:
    Hal& hal_;
    uint32_t half_period_us_;
    uint32_t timeout_us_;

    std::expected<void, I2cError> scl_release_and_wait() noexcept {
        hal_.scl_release();
        uint32_t elapsed = 0;
        while (!hal_.scl_read()) {
            hal_.delay_us(1);
            if (++elapsed >= timeout_us_) {
                return std::unexpected(I2cError::Timeout);
            }
        }
        return {};
    }

    std::expected<void, I2cError> start() noexcept {
        hal_.sda_release();
        if (auto res = scl_release_and_wait(); !res) return std::unexpected(I2cError::BusBusy);
        
        hal_.delay_us(half_period_us_);
        hal_.sda_drive_low();
        hal_.delay_us(half_period_us_);
        hal_.scl_drive_low();
        return {};
    }

    std::expected<void, I2cError> stop() noexcept {
        hal_.sda_drive_low();
        hal_.delay_us(half_period_us_);
        if (auto res = scl_release_and_wait(); !res) return res;
        hal_.delay_us(half_period_us_);
        hal_.sda_release();
        hal_.delay_us(half_period_us_);
        return {};
    }

    std::expected<void, I2cError> write_byte(uint8_t byte, bool& ack) noexcept {
        for (int8_t bit = 7; bit >= 0; --bit) {
            if ((byte >> bit) & 1) {
                hal_.sda_release();
            } else {
                hal_.sda_drive_low();
            }
            hal_.delay_us(half_period_us_);

            if (auto res = scl_release_and_wait(); !res) return res;
            hal_.delay_us(half_period_us_);
            hal_.scl_drive_low();
        }

        hal_.sda_release();
        hal_.delay_us(half_period_us_);
        if (auto res = scl_release_and_wait(); !res) return res;
        hal_.delay_us(half_period_us_ / 2);

        ack = !hal_.sda_read();

        hal_.delay_us(half_period_us_ / 2);
        hal_.scl_drive_low();
        return {};
    }

    std::expected<void, I2cError> read_byte(uint8_t& byte, bool send_ack) noexcept {
        uint8_t val = 0;
        hal_.sda_release();

        for (int8_t bit = 7; bit >= 0; --bit) {
            hal_.delay_us(half_period_us_);
            if (auto res = scl_release_and_wait(); !res) return res;
            hal_.delay_us(half_period_us_ / 2);

            if (hal_.sda_read()) {
                val |= static_cast<uint8_t>(1 << bit);
            }
            hal_.delay_us(half_period_us_ / 2);
            hal_.scl_drive_low();
        }

        if (send_ack) {
            hal_.sda_drive_low();
        } else {
            hal_.sda_release();
        }
        hal_.delay_us(half_period_us_);

        if (auto res = scl_release_and_wait(); !res) return res;
        hal_.delay_us(half_period_us_);
        hal_.scl_drive_low();
        hal_.sda_release();

        byte = val;
        return {};
    }
};

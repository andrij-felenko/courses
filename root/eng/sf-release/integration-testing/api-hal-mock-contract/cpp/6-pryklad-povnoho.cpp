#include "hal_interfaces_contract.hpp"
#include <cassert>

class Bmp280Sensor {
public:
    explicit Bmp280Sensor(embedded::hal::II2cDriver& i2c, uint16_t address)
        : i2c_(i2c), address_(address) {}

    std::expected<int32_t, embedded::hal::Status> readTemperature() {
        std::array<uint8_t, 3> raw_data{};
        auto status = i2c_.memRead(address_, 0xFA, 1, raw_data, std::chrono::milliseconds(100));
        if (status != embedded::hal::Status::Ok) {
            return std::unexpected(status);
        }
        int32_t temp = (static_cast<int32_t>(raw_data[0]) << 12) |
                       (static_cast<int32_t>(raw_data[1]) << 4) |
                       (raw_data[2] >> 4);
        return temp;
    }

private:
    embedded::hal::II2cDriver& i2c_;
    uint16_t address_;
};

void runBmp280Test() {
    embedded::hal::testing::I2cDriverMock mock(0x76);
    mock.setRegister(0xFA, 0x80);
    mock.setRegister(0xFB, 0x00);
    mock.setRegister(0xFC, 0x00);

    Bmp280Sensor sensor(mock, 0x76);

    auto result = sensor.readTemperature();
    assert(result.has_value());
    assert(*result == (0x80 << 12));

    /* Інжектуємо помилку відсутності відповіді NACK */
    mock.injectStatus(embedded::hal::Status::Nack);
    auto failed_result = sensor.readTemperature();
    assert(!failed_result.has_value());
    assert(failed_result.error() == embedded::hal::Status::Nack);
}

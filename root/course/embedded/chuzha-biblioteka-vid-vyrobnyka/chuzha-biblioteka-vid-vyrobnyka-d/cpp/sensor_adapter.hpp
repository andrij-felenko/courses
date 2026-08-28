/* =================== Файл: sensor_adapter.hpp =================== */
#pragma once

#include <cstdint>
#include <expected>
#include <span>
#include <memory>

enum class SensorError : uint8_t {
    CommunicationFailed,
    DeviceNotFound,
    InvalidParameter,
    Timeout
};

struct EnvironmentSample {
    float temperature_celsius;
    float pressure_hpa;
};

/* Чистий системний інтерфейс I2C */
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual bool read_bytes(uint8_t dev_addr, uint8_t reg, std::span<uint8_t> dst) = 0;
    virtual bool write_bytes(uint8_t dev_addr, uint8_t reg, std::span<const uint8_t> src) = 0;
};

/* Інтерфейс датчика середовища */
class IEnvironmentSensor {
public:
    virtual ~IEnvironmentSensor() = default;
    virtual std::expected<void, SensorError> initialize() = 0;
    virtual std::expected<EnvironmentSample, SensorError> read_sample() = 0;
};

/* Фабрика створення адаптера */
std::unique_ptr<IEnvironmentSensor> create_bme280_adapter(II2cBus& bus, uint8_t i2c_addr);

/* =================== Файл: sensor_adapter.cpp =================== */
#include "sensor_adapter.hpp"

/* Вендорський C-заголовок заховано всередині одиниці трансляції */
extern "C" {
    #include "bme280.h"
}

namespace {

class Bme280Adapter final : public IEnvironmentSensor {
public:
    explicit Bme280Adapter(II2cBus& bus, uint8_t i2c_addr)
        : bus_(bus), i2c_addr_(i2c_addr) {
        dev_.intf_ptr = this;
        dev_.read = c_read_bridge;
        dev_.write = c_write_bridge;
        dev_.delay_us = c_delay_bridge;
        dev_.intf = BME280_I2C_INTF;
    }

    ~Bme280Adapter() override {
        /* RAII: гарантований перевід у режим низького енергоспоживання */
        bme280_set_sensor_mode(BME280_POWERMODE_SLEEP, &dev_);
    }

    /* Заборона копіювання: intf_ptr жорстко прив'язаний до адреси цього екземпляра */
    Bme280Adapter(const Bme280Adapter&) = delete;
    Bme280Adapter& operator=(const Bme280Adapter&) = delete;

    std::expected<void, SensorError> initialize() override {
        int8_t rslt = bme280_init(&dev_);
        if (rslt == BME280_E_DEV_NOT_FOUND) return std::unexpected(SensorError::DeviceNotFound);
        if (rslt != BME280_OK) return std::unexpected(SensorError::CommunicationFailed);

        struct bme280_settings settings{};
        settings.osr_h = BME280_OVERSAMPLING_1X;
        settings.osr_p = BME280_OVERSAMPLING_16X;
        settings.osr_t = BME280_OVERSAMPLING_2X;
        settings.filter = BME280_FILTER_COEFF_16;
        bme280_set_sensor_settings(BME280_SEL_ALL_SETTINGS, &settings, &dev_);
        bme280_set_sensor_mode(BME280_POWERMODE_NORMAL, &dev_);

        return {};
    }

    std::expected<EnvironmentSample, SensorError> read_sample() override {
        struct bme280_data comp_data{};
        int8_t rslt = bme280_get_sensor_data(BME280_ALL, &comp_data, &dev_);
        if (rslt != BME280_OK) return std::unexpected(SensorError::CommunicationFailed);

        return EnvironmentSample{
            .temperature_celsius = comp_data.temperature,
            .pressure_hpa = comp_data.pressure / 100.0f
        };
    }

private:
    static int8_t c_read_bridge(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return BME280_E_NULL_PTR;
        auto* self = static_cast<Bme280Adapter*>(intf_ptr);
        std::span<uint8_t> dst(data, len);
        return self->bus_.read_bytes(self->i2c_addr_, reg_addr, dst) ? BME280_OK : BME280_E_COMM_FAIL;
    }

    static int8_t c_write_bridge(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return BME280_E_NULL_PTR;
        auto* self = static_cast<Bme280Adapter*>(intf_ptr);
        std::span<const uint8_t> src(data, len);
        return self->bus_.write_bytes(self->i2c_addr_, reg_addr, src) ? BME280_OK : BME280_E_COMM_FAIL;
    }

    static void c_delay_bridge(uint32_t period_us, void *intf_ptr) {
        (void)intf_ptr;
        /* Системна реалізація затримки */
    }

    II2cBus& bus_;
    uint8_t i2c_addr_;
    struct bme280_dev dev_{};
};

} // namespace

std::unique_ptr<IEnvironmentSensor> create_bme280_adapter(II2cBus& bus, uint8_t i2c_addr) {
    return std::make_unique<Bme280Adapter>(bus, i2c_addr);
}

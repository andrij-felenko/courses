#pragma once

#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include "esp_err.h"
#include "driver/i2c_master.h"
#include "esp_adc/adc_oneshot.h"

namespace iot {

/// Структура фізичних показників довкілля та живлення
struct SensorMeasurements {
    float temperature_c{0.0f};      // Температура (°C)
    float humidity_percent{0.0f};   // Відносна вологість (%)
    uint16_t battery_mv{0};         // Напруга батареї (мВ)
    uint32_t sample_sequence{0};    // Лічильник вимірювань
};

/// Упакована бінарна структура корисного навантаження для передачі мережею
#pragma pack(push, 1)
struct SensorPayload {
    uint32_t sequence_id;   // Ідентифікатор вимірювання
    int16_t temp_raw;       // Температура x100
    uint16_t hum_raw;       // Вологість x100
    uint16_t vbat_raw;      // Напруга живлення у мВ
    uint8_t status_flags;   // Прапорці стану вузла
};
#pragma pack(pop)

/// Клас для керування периферією I2C та зчитування АЦП
class SensorNode {
public:
    explicit SensorNode(gpio_num_t sda_pin = GPIO_NUM_6,
                        gpio_num_t scl_pin = GPIO_NUM_7,
                        adc_channel_t vbat_adc_channel = ADC_CHANNEL_2);
    ~SensorNode();

    SensorNode(const SensorNode&) = delete;
    SensorNode& operator=(const SensorNode&) = delete;

    SensorNode(SensorNode&&) noexcept;
    SensorNode& operator=(SensorNode&&) noexcept;

    /// Ініціалізація шини I2C та драйвера АЦП
    [[nodiscard]] esp_err_t initialize() noexcept;

    /// Зчитування вимірювань з апаратних датчиків
    [[nodiscard]] std::optional<SensorMeasurements> read_measurements(uint32_t sequence_counter) noexcept;

    /// Кодування вимірювань у компактний байтовий масив
    [[nodiscard]] static std::array<uint8_t, sizeof(SensorPayload)> encode_payload(const SensorMeasurements& data) noexcept;

private:
    gpio_num_t sda_pin_;
    gpio_num_t scl_pin_;
    adc_channel_t vbat_channel_;

    i2c_master_bus_handle_t i2c_bus_handle_{nullptr};
    i2c_master_dev_handle_t sensor_dev_handle_{nullptr};
    adc_oneshot_unit_handle_t adc_handle_{nullptr};
    adc_cali_handle_t adc_cali_handle_{nullptr};

    bool initialized_{false};

    esp_err_t read_i2c_sensor(float& out_temp, float& out_hum) noexcept;
    esp_err_t read_battery_voltage(uint16_t& out_mv) noexcept;
};

} // namespace iot
